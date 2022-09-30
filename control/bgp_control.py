#!/usr/bin/env python
from bgp_peer import *
from bgp_path import *
from bgp_vrf import *
import sys
import bgp_control as this

def usage(func):
    print('usage:')
    print('\t python %s' % func)
    print('\t args:')


def find_peer_usage():
    print('args:none')
def find_peer(**args):
    auto_discover_peer()


def add_del_path_usage():
    print('\t\t bgp_as : int')
    print('\t\t vrf_id : int')
    print('\t\t prefix : str')
    print('\t\t prefix_len : int')
    print('\t\t prefix_len : str')
    print('\t\t is_add : int')
def add_del_path(bgp_as, vrf_id, prefix, prefix_len, hop, is_add):
    bgp_as = int(bgp_as)
    vrf_id = int(vrf_id)
    prefix = str(prefix)
    prefix_len = int(prefix_len)
    hop = str(hop)
    is_add = int(is_add)
    if is_add:
        add_path(bgp_as, vrf_id, prefix, prefix_len, hop)


def show_vrf_usage():
    print('\t\t name : str')
def show_vrf(name):
    name = str(name)
    ret = list_vrf(name)
    print(ret)


def add_del_vrf_usage():
    print('\t\t name : str')
    print('\t\t rd : str')
    print('\t\t import_rt : str')
    print('\t\t export_rt : str')
    



if __name__ == '__main__':
    if hasattr(this, sys.argv[1]):
        if sys.argv[2] == 'help':
            usage(sys.argv[1])
            getattr(this, sys.argv[1]+'_usage')()
            exit()
        try:
            getattr(this, sys.argv[1])(*(sys.argv[2:]))
        except:
            usage(sys.argv[1])
            getattr(this, sys.argv[1]+'_usage')()


