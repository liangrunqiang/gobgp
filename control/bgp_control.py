#!/usr/bin/env python
from control_plane.gobgp.control.bgp_peer import *
from control_plane.gobgp.control.bgp_path import *
from control_plane.gobgp.control.bgp_vrf import *
from control_plane.gobgp.control import bgp_control as this
from control_plane.eflyconf import gen
import sys, argparse
import signal
import traceback

def is_int(a):
    if isinstance(a, int):
        return a
    if not a.isdigit():
        raise Exception('%s is not interger' % a)
    return int(a)
def is_str(a):
    if not isinstance(a, str):
        raise Exception('%s is not string' % a)
    return str(a)

def make_arg_current(arg_type, argv):
    for i in arg_type:
        if i in argv:
            argv[i] = getattr(this, "is_"+str(arg_type[i][1]))(argv[i])
        else:
            argv[i] = arg_type[i][0]
    return argv

"""@fun_gen(name='str', rd='str', id='int')""" 
func_arg_require = {}
def fun_gen(**a1):
    global func_arg_require
    def func_deco(func):
        func_arg_require[func.__name__] = a1
        def wrapper(**argv):
            print('args1:', argv)
            argv = make_arg_current(a1, argv)
            print('args2:', argv)
            try:
                func(**argv)
            except:
                gen.print_log_info(str(traceback.format_exc()))
        return wrapper
    return func_deco


@fun_gen(
    peer_asn=[1,'int'],
    peer_port=[179,'int'],
    interface=['','str'],
    graceful_restart=[0,'int'])
def find_peer(**argv):
    auto_discover_peer(**argv)

@fun_gen(
    peer_group=['','str'],
    peer_asn=[1,'int'],
    peer_addr=['','str'],
    peer_port=[179,'int'],
    peer_proto=['ipv4','str'],
    reflector_client=['','str'],
    route_server_client=['','str'],
    graceful_restart=[0,'int'],
    just_vrf=['','str']
)
def add_peer(**argv):
    add_peer_byhand(**argv)


@fun_gen()
def show_peer(**argv):
    list_peer_internal()

 
@fun_gen(
    bgp_as=[0,'int'], 
    vrf_name=['','str'], 
    local_pref=[0,'int'],
    prefix=['','str'], 
    prefix_len=[0,'int'], 
    hop=['0.0.0.0','str'],
    mac=['','str'],
    vni=['','str'],
    path_type=['ipv4','str']
)
def add_path(**argv):
    add_path_internal(**argv)


@fun_gen(
    bgp_as=[0,'int'], 
    vrf_name=['','str'], 
    local_pref=[0,'int'],
    prefix=['','str'], 
    prefix_len=[0,'int'], 
    hop=['0.0.0.0','str'],
    mac=['','str'],
    vni=['','str'],
    path_type=['ipv4','str']
)
def del_path(**argv):
    del_path_internal(**argv)


@fun_gen(vrf_name=['','str'], path_type=['','str'])
def show_path(**argv):
    list_path_internal(**argv)


@fun_gen(name=['','str'])
def show_vrf(**argv):
    list_vrf_internal(**argv)


@fun_gen(
    name=['','str'], 
    rd=['','str'], 
    import_rt=['','str'], 
    export_rt=['','str'], 
    id=[0,'int'])
def add_vrf(**argv):
    add_vrf_internal(**argv)


@fun_gen(name=['','str'])
def del_vrf(**argv):
    del_vrf_internal(**argv)


@fun_gen(read_history=['no','str'])
def watch(**argv):
    watch_internal(**argv)


gobgp_start_flag = 0
bgp_lock = threading.Lock()
def gobgp_start(restart=0):
    global gobgp_start_flag
    if gen.get_pid("gobgpd") == 0 or restart:
        with bgp_lock:
            os.system('/bin/bash /etc/vpc/bgp_init') ##这里一定要确保gobgpd启动完毕
            if restart:
                set_bgp_state_monitor()
    gobgp_start_flag = 1


def set_bgp_state_monitor():
    add_peer_byhand(peer_asn=10000, peer_addr='1.1.1.1', peer_proto='ipv4')  #not use, just to flag bgp if is restart


def get_bgp_state(peer='1.1.1.1'):
    global gobgp_start_flag
    while not gobgp_start_flag:
        time.sleep(1)
    try:
        return len(list_peer_internal(addr=peer))
    except:
        return False


def set_bgp_check(get_state_func):
    def checking():
        while get_state_func():
            time.sleep(10)
            with bgp_lock:
                if not get_bgp_state():
                    signal.alarm(1)
    t = threading.Thread(target=checking, args=())
    t.setDaemon(True)
    t.start()
    return t
    

def main_func():
    if len(sys.argv) > 1 and hasattr(this, sys.argv[1]):
        opera = sys.argv[1]
        del sys.argv[1]
        parser = argparse.ArgumentParser(description="")
        args = func_arg_require[opera]
        for opt in args:
            parser.add_argument("--"+str(opt), help="", default=args[opt][0])
        args_val = parser.parse_args()
        args_build = {}
        for opt in args:
            args_build[opt] = getattr(args_val, opt)
        getattr(this, opera)(**args_build)
    else:
        if len(sys.argv) > 1:
            print('unknow opera : %s' % sys.argv[1])
        else:
            print('miss opera')
        print('vaild opera:')
        for opt in func_arg_require:
            print('\t\t %s ' % opt)

if __name__ == '__main__':
    print('bgp in main------------------------------------------------------')
    main_func()
else:
    if os.path.exists('/etc/vpc/bgp_init'):
        gobgp_start()

