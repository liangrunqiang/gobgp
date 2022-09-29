from api import *
from google.protobuf.any_pb2 import Any
import grpc
import sys

_TIMEOUT_SECONDS = 1000

def add_path(add_as=1, prefix='', prefix_len=0, vrf_id=0):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)
        nlri = Any()
        nlri.Pack(attribute_pb2.IPAddressPrefix(
            prefix_len=prefix_len,
            prefix=prefix,
        ))
        origin = Any()
        origin.Pack(attribute_pb2.OriginAttribute(
            origin=2,  # INCOMPLETE
        ))
        as_segment = attribute_pb2.AsSegment(
            # type=2,  # "type" causes syntax error
            numbers=[add_as],
        )
        as_segment.type = 2  # SEQ
        as_path = Any()
        as_path.Pack(attribute_pb2.AsPathAttribute(
            segments=[as_segment],
        ))
        attributes = [origin, as_path]

        if not vrf_id:
            stub.AddPath(
                gobgp_pb2.AddPathRequest(
                    table_type=gobgp_pb2.GLOBAL,
                    path=gobgp_pb2.Path(
                        nlri=nlri,
                        pattrs=attributes,
                        family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST),
                    )
                ),
                _TIMEOUT_SECONDS,
            )
        else:
            stub.AddPath(
                gobgp_pb2.AddPathRequest(
                    table_type=gobgp_pb2.GLOBAL,
                    vrf_id=vrf_id,
                    path=gobgp_pb2.Path(
                        nlri=nlri,
                        pattrs=attributes,
                        family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST),
                    )
                ),
                _TIMEOUT_SECONDS,
            )

