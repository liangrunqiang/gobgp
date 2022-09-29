#!/usr/bin/env python
from bgp_peer import *
from bgp_path import *
from bgp_vrf import *
import sys
import bgp_control as this

def find_peer():
    auto_discover_peer()

def add_del_path(bgp_as, prefix, prefix_len, hop, is_add):
    if is_add:
        add_path(bgp_as, prefix, prefix_len, hop)

if __name__ == '__main__':
    if hasattr(this, sys.argv[1]):
        getattr(this, sys.argv[1])(sys.argv[2:])
    else:
        print('Usage:')

