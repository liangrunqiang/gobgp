#!/usr/bin/env python
from control_plane.gobgp.api import *
from control_plane.gobgp.control.net_base import *
from control_plane.gobgp.control.bgp_vrf import *

import grpc
import socket
import sys
import queue
import time
import threading

_TIMEOUT_SECONDS = 1000


def make_define_set_ext_community(name, com_list):
    return gobgp_pb2.DefinedSet(
                defined_type=gobgp_pb2.EXT_COMMUNITY,
                name=name,
                list=com_list
            )

def make_policy_ext_community(name, define_set_name):
    return gobgp_pb2.Policy(
                    name=name,
                    statements=[
                        gobgp_pb2.Statement(
                            name=name,
                            conditions=gobgp_pb2.Conditions(
                                ext_community_set=gobgp_pb2.MatchSet(
                                    type=gobgp_pb2.MatchSet.Type.ANY,
                                    name=define_set_name
                                )
                            ),
                            actions=gobgp_pb2.Actions(
                                route_action=gobgp_pb2.RouteAction.ACCEPT
                            )
                        )
                    ]
                )


def make_neigh_vrf_policy(stub, vrf_name=''):
    try:
        vrf_info = list_vrf_internal(vrf_name)
        if not len(vrf_info):
            raise Exception("vrf not found")

        irt = vrf_info[vrf_name]['import_rt'][0]
        ert = vrf_info[vrf_name]['export_rt'][0]
    except:
        import_rt = vrf_name.split(',')[0]
        export_rt = vrf_name.split(',')[1]
        irt = attribute_pb2.TwoOctetAsSpecificExtended(asn=int(import_rt.split('')[0]), local_admin=int(import_rt.split(':')[1]))
        ert = attribute_pb2.TwoOctetAsSpecificExtended(asn=int(export_rt.split(':')[0]), local_admin=int(export_rt.split(':')[1]))
    stub.AddDefinedSet(
        gobgp_pb2.AddDefinedSetRequest(
            defined_set=make_define_set_ext_community(vrf_name+'_import_set', 
            ['rt:^%d:%d$' % (irt.asn, irt.local_admin)])
        )
    )
    stub.AddDefinedSet(
        gobgp_pb2.AddDefinedSetRequest(
            defined_set=make_define_set_ext_community(vrf_name+'_export_set', 
            ['rt:^%d:%d$' % (ert.asn, ert.local_admin)])
        )
    )
    #stub.AddPolicy(
    #    gobgp_pb2.AddPolicyRequest(
    #        policy=make_policy_ext_community(vrf_name+'_import_policy', vrf_name+'_import_set')
    #    )
    #)
    #stub.AddPolicy(
    #    gobgp_pb2.AddPolicyRequest(
    #        policy=make_policy_ext_community(vrf_name+'_export_policy', vrf_name+'_export_set')
    #    )
    #)
    return gobgp_pb2.ApplyPolicy(
        import_policy=gobgp_pb2.PolicyAssignment(
            name=vrf_name+'_import',
            direction=gobgp_pb2.PolicyDirection.IMPORT,
            default_action=gobgp_pb2.RouteAction.REJECT,
            policies=[make_policy_ext_community(vrf_name+'_export_policy', vrf_name+'_export_set')]
        ),
        export_policy=gobgp_pb2.PolicyAssignment(
            name=vrf_name+'_export',
            direction=gobgp_pb2.PolicyDirection.EXPORT,
            default_action=gobgp_pb2.RouteAction.REJECT,
            policies=[make_policy_ext_community(vrf_name+'_import_policy', vrf_name+'_import_set')]
        )
    )