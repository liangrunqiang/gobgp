#!/usr/bin/env python
from control_plane.gobgp.api import *
from google.protobuf.any_pb2 import Any
import grpc

_TIMEOUT_SECONDS = 1000

def make_vrf_rd_pack(admin, asn):
    rd_p = Any()
    rd_p.Pack(attribute_pb2.RouteDistinguisherTwoOctetASN(
        admin=int(admin),
        assigned=int(asn),
    ))
    return rd_p

def make_vrf_rt_pack(asn, local_admin):
    rt_p = Any()
    rt_p.Pack(attribute_pb2.TwoOctetAsSpecificExtended(
        is_transitive=True,
        sub_type=2,
        asn=int(asn),
        local_admin=int(local_admin),
    ))
    return rt_p

def add_vrf_internal(name='', rd='', import_rt='', export_rt='', id=0):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)

        imports = []
        for a in import_rt.split(','):
            imports.append(make_vrf_rt_pack(a.split(':')[0], a.split(':')[1]))
        exports = []
        for a in export_rt.split(','):
            exports.append(make_vrf_rt_pack(a.split(':')[0], a.split(':')[1]))

        stub.AddVrf(
            gobgp_pb2.AddVrfRequest(
                vrf=gobgp_pb2.Vrf(
                    name=name,
                    rd=make_vrf_rd_pack(rd.split(':')[0], rd.split(':')[1]),
                    import_rt=imports,
                    export_rt=exports,
                    id=id,
                )
            ),
            _TIMEOUT_SECONDS,
        )

def del_vrf_internal(name=''):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)
        stub.DeleteVrf(
            gobgp_pb2.DeleteVrfRequest(
                name=name
            ),
            _TIMEOUT_SECONDS,
        )

def list_vrf_internal(name=''):
    all_vrf = {}
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)
        ret = stub.ListVrf(
            gobgp_pb2.ListVrfRequest(
                name=name
            ),
            _TIMEOUT_SECONDS,
        )
        for r in ret:
            vrf = r.vrf
            rd = attribute_pb2.RouteDistinguisherTwoOctetASN()
            vrf.rd.Unpack(rd)
            imports = []
            exports = []
            for i in vrf.import_rt:
                rt = attribute_pb2.TwoOctetAsSpecificExtended()
                i.Unpack(rt)
                imports.append(rt)
            for e in vrf.export_rt:
                rt = attribute_pb2.TwoOctetAsSpecificExtended()
                e.Unpack(rt)
                exports.append(rt)
            print(vrf.name, vrf.id, 
                '%d:%d' % (rd.admin, rd.assigned),
                ['%d:%d' % (i.asn, i.local_admin) for i in imports],
                ['%d:%d' % (i.asn, i.local_admin) for i in imports])
            all_vrf[name] = {"id":int(vrf.id), 
                    "rd":rd,
                    "import_rt":imports,
                    "export_rt":exports}
            print(all_vrf)
    return all_vrf
