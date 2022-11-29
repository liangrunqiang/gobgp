#!/usr/bin/env python
from control_plane.gobgp.api import *
from control_plane.gobgp.control.bgp_policy import *
from control_plane.gobgp.control.net_base import *

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

def run_scan_host(all_ip, peer_port):
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
                        t = threading.Thread(target=scan_host, args=(int2ip(host), peer_port, ))
                        t.start()
                        create_task = 1
    build_all_task = 1

def list_peer_info(stub, addr=''):
    if addr == '':
        peers = stub.ListPeer(
            gobgp_pb2.ListPeerRequest(
            ),
            _TIMEOUT_SECONDS,
        )
    else:
        peers = stub.ListPeer(
            gobgp_pb2.ListPeerRequest(
                address=addr
            ),
            _TIMEOUT_SECONDS,
        )

    exists_peer = []
    for peer in peers:
        peer_info = getattr(peer, 'peer')
        peer_conf = getattr(peer_info, 'conf')
        peer_addr = getattr(peer_conf, 'neighbor_address')
        exists_peer.append(peer_addr)
    print(exists_peer)
    return exists_peer

def list_peer_internal(addr=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)
        list_peer_info(stub, addr=addr)

def add_peer_internal(active_bgp, local_ip, afi_safis, peer_group='', peer_asn=1, peer_port=179, route_reflector_client=False, route_server_client=False, graceful_restart=0, just_vrf=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)
        
        exists_peer = list_peer_info(stub)
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
            if not len(just_vrf):
                policy=gobgp_pb2.ApplyPolicy()
            else:
                policy=make_neigh_vrf_policy(stub, vrf_name=just_vrf)
            if len(peer_group):
                peer_conf=gobgp_pb2.PeerConf(
                            peer_group=peer_group,
                            neighbor_address=nei_addr,
                            peer_asn=peer_asn
                        )
            else:
                peer_conf = gobgp_pb2.PeerConf(
                            neighbor_address=nei_addr,
                            peer_asn=peer_asn
                        )
            stub.AddPeer(
                gobgp_pb2.AddPeerRequest(
                    peer=gobgp_pb2.Peer(
                        apply_policy=policy,
                        conf=peer_conf,
                        transport=gobgp_pb2.Transport(
                            remote_port=peer_port
                        ),
                        route_reflector=gobgp_pb2.RouteReflector(
                            route_reflector_client=route_reflector_client
                        ),
                        route_server=gobgp_pb2.RouteServer(
                            route_server_client=route_server_client
                        ),
                        graceful_restart=gobgp_pb2.GracefulRestart(
                            enabled=(graceful_restart>0),
                            longlived_enabled=(graceful_restart>0),
                            restart_time=graceful_restart
                        ),
                        afi_safis=afi_safis
                    )
                ),
                _TIMEOUT_SECONDS,
            )

family_list = {
    'ipv4':[gobgp_pb2.Family.AFI_IP, gobgp_pb2.Family.SAFI_UNICAST],
    'ipv6':[gobgp_pb2.Family.AFI_IP6, gobgp_pb2.Family.SAFI_UNICAST],
    'l3vpn':[gobgp_pb2.Family.AFI_IP, gobgp_pb2.Family.SAFI_MPLS_VPN],
    'l2vpn':[gobgp_pb2.Family.AFI_L2VPN, gobgp_pb2.Family.SAFI_EVPN],
    'rtc':[gobgp_pb2.Family.AFI_IP, gobgp_pb2.Family.SAFI_ROUTE_TARGET_CONSTRAINTS]
}
def make_peer_family(proto_list, graceful_restart=0):
    afi_safis = []
    for p in proto_list:
        afi_safis.append(
            gobgp_pb2.AfiSafi(
                config=gobgp_pb2.AfiSafiConfig(
                    family=gobgp_pb2.Family(
                        afi=family_list[p][0],
                        safi=family_list[p][1]
                    ),
                    enabled=True
                ),
                mp_graceful_restart=gobgp_pb2.MpGracefulRestart(
                    config=gobgp_pb2.MpGracefulRestartConfig(enabled=(graceful_restart>0))
                ),
                long_lived_graceful_restart=gobgp_pb2.LongLivedGracefulRestart(
                    config=gobgp_pb2.LongLivedGracefulRestartConfig(enabled=(graceful_restart>0), restart_time=graceful_restart)
                )
            )
        )
    print(afi_safis)
    return afi_safis


def auto_discover_peer(peer_port=179, peer_asn=1, graceful_restart=0, interface=''):
    #all_net_card, _, _ = get_physical_netcard()
    #all_net, local_ip = get_net(all_net_card)
    all_net, local_ip = get_net([interface])
    run_scan_host(all_net, peer_port)
    while (not build_all_task) or (scan_done < scan_task):
        time.sleep(1)
    add_peer_internal(active_bgp, local_ip, 
        make_peer_family(['ipv4', 'ipv6', 'l3vpn', 'l2vpn', 'rtc'], graceful_restart=graceful_restart),
        peer_asn=peer_asn,
        peer_port=peer_port,
        graceful_restart=graceful_restart)


def add_peer_byhand(peer_group='',peer_asn=0, peer_addr='', peer_port=179, peer_proto='', reflector_client='', route_server_client='', graceful_restart=0,just_vrf=''):
    active_bgp.put(peer_addr)
    _, local_ip = get_net(['tap1'])
    reflector_client = True if reflector_client.lower() == 'yes' else False
    route_server_client = True if route_server_client.lower() == 'yes' else False
    add_peer_internal(active_bgp, local_ip, make_peer_family(peer_proto.split(','), graceful_restart=graceful_restart), 
        peer_group,
        peer_asn,
        peer_port, 
        route_reflector_client=reflector_client, 
        route_server_client=route_server_client,
        graceful_restart=graceful_restart,
        just_vrf=just_vrf)


mval = {}
def watch_internal(read_history='', callback=False):
    global mval
    if read_history.lower() == 'yes':
        read_history = 1
    else:
        read_history = 0
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        r = stub.WatchEvent(
            gobgp_pb2.WatchEventRequest(
                table=gobgp_pb2.WatchEventRequest.Table(
                    filters=[
                        gobgp_pb2.WatchEventRequest.Table.Filter(
                            type=gobgp_pb2.WatchEventRequest.Table.Filter.ADJIN,
                            init=read_history
                        )
                    ]
                )
            ),
            _TIMEOUT_SECONDS,
        )

        def unpack_msg(msg, msg_type, ret='default'):
            global mval
            if ret in mval:
                del mval[ret]
            mval[ret] = getattr(attribute_pb2, msg_type)()
            return msg.Unpack(mval[ret])

        for a in r:
            for p in a.table.paths:
                print(p.nlri)
                if p.family.afi == gobgp_pb2.Family.AFI_IP \
                    and p.family.safi == gobgp_pb2.Family.SAFI_ROUTE_TARGET_CONSTRAINTS:
                    unpack_msg(p.nlri, 'RouteTargetMembershipNLRI')
                    v = mval['default']
                    unpack_msg(v.rt, 'TwoOctetAsSpecificExtended', 'rt')
                    rt = mval['rt']
                    print('msg vrf:')
                    print('bgp as:', v.asn, 'rt:', rt.asn, rt.local_admin)

                elif p.family.afi == gobgp_pb2.Family.AFI_L2VPN \
                    and p.family.safi == gobgp_pb2.Family.SAFI_EVPN:
                    if unpack_msg(p.nlri, 'EVPNEthernetAutoDiscoveryRoute'):
                        print(mval['default'])

                    elif unpack_msg(p.nlri, 'EVPNMACIPAdvertisementRoute'):
                        v = mval['default']
                        rd = attribute_pb2.RouteDistinguisherTwoOctetASN()
                        v.rd.Unpack(rd)
                        print('msg evpn rt2:')
                        is_del = 1
                        endpoint = ''
                        ip = v.ip_address
                        mac = v.mac_address
                        vni = v.labels
                        vrf = rd.admin
                        for pa in p.pattrs:
                            if unpack_msg(pa, 'MpReachNLRIAttribute', 'hop'):
                                endpoint = mval['hop'].next_hops[0]
                                is_del = 0
                        print(ip, mac, vni, vrf, endpoint)
                        if callback:
                            callback(msg_type='evpn-rt2', vrf=int(vrf), vni=int(vni), ip=ip, mac=mac, endpoint=endpoint, is_del=is_del)

                    elif unpack_msg(p.nlri, 'EVPNInclusiveMulticastEthernetTagRoute'):
                        v = mval['default']
                        rd = attribute_pb2.RouteDistinguisherTwoOctetASN()
                        v.rd.Unpack(rd)
                        print('msg evpn rt3:')
                        is_del = 1
                        endpoint = v.ip_address
                        vni = v.ethernet_tag
                        vrf = rd.admin
                        for pa in p.pattrs:
                            if unpack_msg(pa, 'PmsiTunnelAttribute', 'psi'):
                                endpoint = int2ip(int.from_bytes(mval['psi'].id, 'big'))
                                vni = mval['psi'].label
                                is_del = 0
                        print(endpoint, vni, vrf)
                        if callback:
                            callback(msg_type='evpn-rt3', vrf=int(vrf), vni=int(vni), endpoint=endpoint, is_del=is_del)

                    elif unpack_msg(p.nlri, 'EVPNEthernetSegmentRoute'):
                        print(mval['default'])

                    elif unpack_msg(p.nlri, 'EVPNIPPrefixRoute'):
                        v = mval['default']
                        rd = attribute_pb2.RouteDistinguisherTwoOctetASN()
                        v.rd.Unpack(rd)
                        print('msg evpn rt5:')
                        vrf = rd.admin
                        is_del = 1
                        ip_prefix = v.ip_prefix
                        ip_prefix_len = v.ip_prefix_len
                        gateway = v.gw_address
                        for pa in p.pattrs:
                            if unpack_msg(pa, 'MpReachNLRIAttribute', 'hop'):
                                is_del = 0
                        print(vrf, ip_prefix, ip_prefix_len, gateway)
                        if callback:
                            callback(msg_type='evpn-rt5', vrf=int(vrf), prefix=ip_prefix, prefix_len=ip_prefix_len, gw=gateway, is_del=is_del)

                    elif unpack_msg(p.nlri, 'EVPNIPMSIRoute'):
                        print(mval['default'])


                print('----------------------------------------')