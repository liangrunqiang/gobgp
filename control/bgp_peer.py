#!/usr/bin/env python
from api import *
from net_base import *

import grpc
import socket
import sys
import queue
import time
import threading

_TIMEOUT_SECONDS = 1000


active_bgp = queue.Queue()
scan_lock = threading.Lock()
scan_thread = 0
scan_task = 0
scan_done = 0
build_all_task = 0

def scan_host(ip, port):
    global active_bgp
    global scan_lock
    global scan_thread
    global scan_done
    print('scan', ip)
    s = socket.socket()
    try:
        s.settimeout(3)
        s.connect((ip, port))
        s.close()
        active_bgp.put(ip)
    except:
        pass
    with scan_lock:
        if scan_thread > 0:
            scan_thread -= 1
        scan_done += 1

def run_scan_host(all_ip):
    global scan_lock
    global scan_thread
    global scan_task
    global build_all_task
    for a in all_ip:
        i1 = ip2int(a[1])
        i2 = ip2int(a[2])
        min_ip = ((i1 & i2)+1)
        max_ip = (ip2int(min_ip) + (2 << (32-exchange_mask(a[2])-1)) - 2)
        range_list = [i for i in range(min_ip, max_ip)]
        for host in range_list:
            create_task = 0
            while not create_task:
                with scan_lock:
                    if scan_thread < 100:
                        scan_thread += 1
                        scan_task += 1
                        t = threading.Thread(target=scan_host, args=(int2ip(host), 179, ))
                        t.start()
                        create_task = 1
    build_all_task = 1

def add_peer(active_bgp, local_ip):
    channel = grpc.insecure_channel('localhost:50051')
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    peers = stub.ListPeer(
        gobgp_pb2.ListPeerRequest(
        ),
        _TIMEOUT_SECONDS,
    )

    exists_peer = []
    for peer in peers:
        peer_info = getattr(peer, 'peer')
        peer_conf = getattr(peer_info, 'conf')
        exists_peer.append(getattr(peer_conf, 'neighbor_address'))

    while 1:
        if active_bgp.empty():
            break
        nei_addr = active_bgp.get()
        if nei_addr in local_ip:
            print(nei_addr, 'is local addr')
            continue
        if nei_addr in exists_peer:
            print(nei_addr, 'is already in peers')
            continue
        print('add peer:', nei_addr)
        stub.AddPeer(
            gobgp_pb2.AddPeerRequest(
                peer=gobgp_pb2.Peer(
                    conf=gobgp_pb2.PeerConf(
                        neighbor_address=nei_addr,
                        peer_asn=1
                    )
                )
            ),
            _TIMEOUT_SECONDS,
        )

def auto_discover_peer():
    all_net_card, _, _ = get_physical_netcard
    all_net, local_ip = get_net(all_net_card)
    run_scan_host(all_net)
    while (not build_all_task) or (scan_done < scan_task):
        time.sleep(1)
    add_peer(active_bgp, local_ip)
