from api import *
from google.protobuf.any_pb2 import Any
from control.bgp_vrf import list_vrf_internal, make_vrf_rd_pack, make_vrf_rt_pack
from control.net_base import ip2int
import grpc
import sys

_TIMEOUT_SECONDS = 1000

def make_path_next_hop(bgp_as, hop):
    origin = Any()
    origin.Pack(attribute_pb2.OriginAttribute(
        origin=2,  # INCOMPLETE
    ))
    as_segment = attribute_pb2.AsSegment(
        # type=2,  # "type" causes syntax error
        numbers=[bgp_as],
    )
    as_segment.type = 2  # SEQ
    as_path = Any()
    as_path.Pack(attribute_pb2.AsPathAttribute(
        segments=[as_segment],
    ))
    next_hop = Any()
    next_hop.Pack(attribute_pb2.NextHopAttribute(
        next_hop=hop,
    ))
    if bgp_as:
        attributes = [origin, as_path, next_hop]
    else:
        attributes = [origin, next_hop]
    return attributes

def make_path(bgp_as, prefix, prefix_len, hop):
    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=prefix_len,
        prefix=prefix,
    ))
    
    path=gobgp_pb2.Path(
                        nlri=nlri,
                        pattrs=make_path_next_hop(bgp_as, hop),
                        family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST),
                    )
    return path


def make_path_evpn_rt2(bgp_as, vrf_name, vni, ip, mac, hop):
    vrf_info = list_vrf_internal(vrf_name)
    if not len(vrf_info):
        raise Exception("vrf not found")

    """ rtc_uc = []
    for i in vrf_info[vrf_name]['export_rt']:
        rtc_uc.append(
            attribute_pb2.RouteTargetMembershipNLRI(
                rt=make_vrf_rt_pack(i.asn, i.local_admin))
            ) """

    v = 0
    mac_ip = Any()
    mac_ip.Pack(
        attribute_pb2.EVPNMACIPAdvertisementRoute(
            rd=make_vrf_rd_pack(vrf_info[vrf_name]['rd'].admin, vrf_info[vrf_name]['rd'].assigned),
            esi=attribute_pb2.EthernetSegmentIdentifier(
                type=0,
                value=v.to_bytes(4, byteorder="big")
            ),
            ethernet_tag=0,
            mac_address=mac,
            ip_address=ip,
            labels=list(map(int,vni.split(',')))
        )
    )
    
    path=gobgp_pb2.Path(
                        nlri=mac_ip,
                        pattrs=make_path_next_hop(bgp_as, hop),
                        family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_L2VPN, safi=gobgp_pb2.Family.SAFI_EVPN),
                    )
    return path

def make_path_evpn_rt3(bgp_as, vrf_name, vtep_ip, vni, hop):
    vrf_info = list_vrf_internal(vrf_name)
    if not len(vrf_info):
        raise Exception("vrf not found")
    
    v = 0
    mc_r = Any()
    mc_r.Pack(
        attribute_pb2.EVPNInclusiveMulticastEthernetTagRoute(
            rd=make_vrf_rd_pack(vrf_info[vrf_name]['rd'].admin, vrf_info[vrf_name]['rd'].assigned),
            ethernet_tag=0,
            ip_address=vtep_ip
        )
    )

    endpoint = Any()
    endpoint.Pack(
        attribute_pb2.PmsiTunnelAttribute(
            flags=0,
            type=6,
            label=int(vni),
            id=ip2int(vtep_ip).to_bytes(4, byteorder="big")
        )
    )

    path=gobgp_pb2.Path(
                        nlri=mc_r,
                        pattrs=make_path_next_hop(bgp_as, hop) + [endpoint],
                        family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_L2VPN, safi=gobgp_pb2.Family.SAFI_EVPN),
                    )
    return path



def add_path_internal(bgp_as=1, vrf_name=0, prefix='', prefix_len=0, hop='', mac='', vni='', path_type=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        mac = ':'.join(i.zfill(2) for i in mac.split(':'))
        if path_type == 'ipv4':
            path = make_path(bgp_as, prefix, prefix_len, hop)
        elif path_type == 'evpn-rt2':
            path = make_path_evpn_rt2(bgp_as, vrf_name, vni, prefix, mac, hop)
        elif path_type == 'evpn-rt3':
            path = make_path_evpn_rt3(bgp_as, vrf_name, prefix, vni, hop)
        else:
            raise Exception("unknow route type")
        if not len(vrf_name):
            stub.AddPath(
                gobgp_pb2.AddPathRequest(
                    table_type=gobgp_pb2.GLOBAL,
                    path=path
                ),
                _TIMEOUT_SECONDS,
            )
        else:
            stub.AddPath(
                gobgp_pb2.AddPathRequest(
                    table_type=gobgp_pb2.VRF,
                    vrf_id=vrf_name,
                    path=path
                ),
                _TIMEOUT_SECONDS,
            )

def del_path_internal(bgp_as=1, vrf_name=0, prefix='', prefix_len=0, hop='', mac='', vni='', path_type=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        mac = ':'.join(i.zfill(2) for i in mac.split(':'))
        if path_type == 'ipv4':
            path = make_path(bgp_as, prefix, prefix_len, hop)
        elif path_type == 'evpn-rt2':
            path = make_path_evpn_rt2(bgp_as, vrf_name, vni, prefix, mac, hop)
        else:
            raise Exception("unknow route type")
        if not len(vrf_name):
            stub.DeletePath(
                gobgp_pb2.DeletePathRequest(
                    table_type=gobgp_pb2.GLOBAL,
                    path=path
                ),
                _TIMEOUT_SECONDS,
            )
        else:
            stub.DeletePath(
                gobgp_pb2.DeletePathRequest(
                    table_type=gobgp_pb2.VRF,
                    vrf_id=vrf_name,
                    path=path
                ),
                _TIMEOUT_SECONDS,
            )

def list_path_internal(vrf_name='', path_type=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        if 'evpn' in path_type:
            family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_L2VPN, safi=gobgp_pb2.Family.SAFI_EVPN)
        else:
            family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST)
        if not len(vrf_name):
            ret = stub.ListPath(
                gobgp_pb2.ListPathRequest(
                    table_type=gobgp_pb2.GLOBAL,
                    family=family,
                    name="",
                ),
                _TIMEOUT_SECONDS,
            )
        else:
            ret = stub.ListPath(
                gobgp_pb2.ListPathRequest(
                    table_type=gobgp_pb2.VRF,
                    family=family,
                    name=vrf_name,
                ),
                _TIMEOUT_SECONDS,
            )
        for a in ret:
            if 'evpn' in path_type:
                r = attribute_pb2.EVPNMACIPAdvertisementRoute()
                a.destination.paths[0].nlri.Unpack(r)
                print(a.destination.prefix, r.labels)
            else:
                print(a.destination.prefix)