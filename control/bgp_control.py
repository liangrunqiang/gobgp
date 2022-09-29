#!/usr/bin/env python
from bgp_peer import *
from bgp_path import *
from bgp_vrf import *
import sys
import bgp_control as this

def find_peer_usage():
    print('python3 bgp_control find_peer')
def find_peer(**args):
    auto_discover_peer()

def add_del_path_usage():
    print('python3 bgp_control add_del_path bgp_as vrf_id prefix prefix_len hop is_add')
def add_del_path(bgp_as, vrf_id, prefix, prefix_len, hop, is_add):
    if is_add:
        add_path(bgp_as, vrf_id, prefix, prefix_len, hop)



if __name__ == '__main__':
    if hasattr(this, sys.argv[1]):
        if sys.argv[2] == 'help':
            getattr(this, sys.argv[1]+'_usage')
            exit()
        try:
            getattr(this, sys.argv[1])(*(sys.argv[2:]))
        except:
            getattr(this, sys.argv[1]+'_usage')

