from api import *

_TIMEOUT_SECONDS = 1000

def add_vrf(stub, add_as=1, vrf=0):
    stub.AddVrf(
        gobgp_pb2.AddVrfRequest(
            vrf=gobgp_pb2.Vrf(
                id=vrf
            )
        ),
        _TIMEOUT_SECONDS,
    )

