#coding:utf-8
from control_plane.gobgp.api import *
from google.protobuf.any_pb2 import Any
from control_plane.gobgp.control.bgp_vrf import *
from control_plane.gobgp.control.net_base import *
import grpc

_TIMEOUT_SECONDS = 1000

def make_path_next_hop(bgp_as, hop, local_pref=0):
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
    local_pref_info = Any()
    local_pref_info.Pack(attribute_pb2.LocalPrefAttribute(
        local_pref=local_pref
    ))
    attributes = [origin, next_hop]
    if bgp_as:
        attributes.append(as_path)
    if local_pref:
        attributes.append(local_pref_info)
    return attributes

def make_path(bgp_as, prefix, prefix_len, hop, local_pref=0):
    nlri = Any()
    nlri.Pack(attribute_pb2.IPAddressPrefix(
        prefix_len=prefix_len,
        prefix=prefix,
    ))
    
    path=gobgp_pb2.Path(
                        nlri=nlri,
                        pattrs=make_path_next_hop(bgp_as, hop, local_pref),
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
    
    mc_r = Any()
    mc_r.Pack(
        attribute_pb2.EVPNInclusiveMulticastEthernetTagRoute(
            rd=make_vrf_rd_pack(vrf_info[vrf_name]['rd'].admin, vrf_info[vrf_name]['rd'].assigned),
            ethernet_tag=int(vni),
            ip_address=vtep_ip 
            #这里按照标准协议本来应该填的是ethernet_tab为0,ip_address为VTEP IP,亦即下面endpoint的tunnel ip,但是gobgp的实现这里作为prefix,不能相同,相同的话会覆盖掉
            #而且删除的时候回调的消息不包含pattrs，所以如果这里不也填上vtep ip和vni，删除的时候就不能获取相应的信息，这样的话其实pattrs都不用设置的，但是为了尽量符合标准
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


def make_path_evpn_rt5(bgp_as, vrf_name, ip_prefix, ip_len, hop):
    vrf_info = list_vrf_internal(vrf_name)
    if not len(vrf_info):
        raise Exception("vrf not found")
    
    v = 0
    rt5_info = Any()
    rt5_info.Pack(
        attribute_pb2.EVPNIPPrefixRoute(
            rd=make_vrf_rd_pack(vrf_info[vrf_name]['rd'].admin, vrf_info[vrf_name]['rd'].assigned),
            esi=attribute_pb2.EthernetSegmentIdentifier(
                type=0,
                value=v.to_bytes(4, byteorder="big")
            ),
            ethernet_tag=0,
            ip_prefix=ip_prefix,
            ip_prefix_len=ip_len,
            gw_address=hop
        )
    )

    path=gobgp_pb2.Path(
                        nlri=rt5_info,
                        pattrs=make_path_next_hop(bgp_as, '0.0.0.0'),
                        family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_L2VPN, safi=gobgp_pb2.Family.SAFI_EVPN),
                    )
    return path


def add_path_internal(bgp_as=1, vrf_name=0, local_pref=0, prefix='', prefix_len=0, hop='', mac='', vni='', path_type=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        mac = ':'.join(i.zfill(2) for i in mac.split(':'))
        if path_type == 'ipv4':
            path = make_path(bgp_as, prefix, prefix_len, hop, local_pref)
        elif path_type == 'evpn-rt2':
            path = make_path_evpn_rt2(bgp_as, vrf_name, vni, prefix, mac, hop)
        elif path_type == 'evpn-rt3':
            path = make_path_evpn_rt3(bgp_as, vrf_name, prefix, vni, hop)
        elif path_type == 'evpn-rt5':
            path = make_path_evpn_rt5(bgp_as, vrf_name, prefix, prefix_len, hop)
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

def del_path_internal(bgp_as=1, vrf_name=0, local_pref=0, prefix='', prefix_len=0, hop='', mac='', vni='', path_type=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        mac = ':'.join(i.zfill(2) for i in mac.split(':'))
        if path_type == 'ipv4':
            path = make_path(bgp_as, prefix, prefix_len, hop, local_pref)
        elif path_type == 'evpn-rt2':
            path = make_path_evpn_rt2(bgp_as, vrf_name, vni, prefix, mac, hop)
        elif path_type == 'evpn-rt3':
            path = make_path_evpn_rt3(bgp_as, vrf_name, prefix, vni, hop)
        elif path_type == 'evpn-rt5':
            path = make_path_evpn_rt5(bgp_as, vrf_name, prefix, prefix_len, hop)
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

def list_path_internal(vrf_name='', path_type='', prefix='', **argv):
    ret_path = []
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        if 'evpn' in path_type:
            family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_L2VPN, safi=gobgp_pb2.Family.SAFI_EVPN)
        else:
            family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST)
        ret = stub.ListPath(
            gobgp_pb2.ListPathRequest(
                table_type=gobgp_pb2.VRF if len(vrf_name) else gobgp_pb2.GLOBAL,
                family=family,
                name=vrf_name if len(vrf_name) else '',
                #prefixes=[gobgp_pb2.TableLookupPrefix(prefix=i, type=gobgp_pb2.TableLookupPrefix.Type.SHORTER) for i in prefix.split(',')] \
                #    if len(prefix) else [],
                #enable_filtered=1 if len(prefix) else 0
            ),
            _TIMEOUT_SECONDS,
        )
        for a in ret:
            #print(a)
            if 'evpn' in path_type:
                r = attribute_pb2.EVPNMACIPAdvertisementRoute()
                a.destination.paths[0].nlri.Unpack(r)
                nei = a.destination.paths[0].neighbor_ip
                if not nei or not len(nei) or not ip2int(nei):
                    nei = 'is_local'
                ret_path.append((str(a.destination.prefix) + str(r.labels) + nei))
            else:
                ret_path.append(a.destination.prefix)
        print(ret_path)
        return ret_path