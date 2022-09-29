#!/usr/bin/env python
from bgp_peer import *
from bgp_path import *
from bgp_vrf import *
import threading
import time

is_running = 0

def find_peer():
    while is_running:
        auto_discover_peer()
        time.sleep(30)

if __name__ == '__main__':
    t = threading.Thread(target=find_peer, arg=())
    t.start()
