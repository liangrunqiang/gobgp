import sys
sys.path.append('..')
from api import *
import grpc

_TIMEOUT_SECONDS = 1000

def add_vrf(add_as=1, vrf=0):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = gobgp_pb2_grpc.GobgpApiStub(channel)
        stub.AddVrf(
            gobgp_pb2.AddVrfRequest(
                vrf=gobgp_pb2.Vrf(
                    id=vrf
                )
            ),
            _TIMEOUT_SECONDS,
        )

