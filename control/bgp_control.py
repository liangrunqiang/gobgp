#!/usr/bin/env python
from control_plane.gobgp.control.bgp_peer import *
from control_plane.gobgp.control.bgp_path import *
from control_plane.gobgp.control.bgp_vrf import *
from control_plane.gobgp.control.bgp_policy import *
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
            gen.print_log_info(func.__name__)
            gen.print_log_info('args1:'+str(argv))
            argv = make_arg_current(a1, argv)
            gen.print_log_info('args2:'+str(argv))
            try:
                return func(**argv)
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


@fun_gen(vrf_name=['','str'], path_type=['','str'], prefix=['','str'])
def show_path(**argv):
    return list_path_internal(**argv)


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
def check_path_exist(**argv):
    if 'vrf' not in argv['vrf_name']:
        argv['vrf_name'] = 'vrf_' + argv['vrf_name']
    path_info = list_path_internal(**argv)
    path_type = argv['path_type']
    vrf_id = argv['vrf_name'].split('_')[1]
    if path_type == 'evpn-rt2':
        if '[type:macadv][rd:%s:%s][etag:0][mac:%s][ip:%s][%s][hop:%s]is_local' \
            % (vrf_id, vrf_id, argv['mac'], argv['prefix'], argv['vni'], argv['hop']) not in path_info:
            return 0
    if path_type == 'evpn-rt3':
        if '[type:multicast][rd:%s:%s][etag:%s][ip:%s][][hop:0.0.0.0]is_local' \
            % (vrf_id, vrf_id, argv['vni'], argv['prefix']) not in path_info:
            return 0
    if path_type == 'evpn-rt5':
        if '[type:Prefix][rd:%s:%s][etag:0][prefix:%s/%d][][hop:0.0.0.0]is_local' \
            % (vrf_id, vrf_id, argv['prefix'], argv['prefix_len']) not in path_info:
            return 0
    return 1

 
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


def add_del_path(**argv):
    is_add = (argv['is_add'] > 0)
    argv.pop('is_add')
    if 'is_check' in argv:
        if argv['is_check']:
            argv.pop('is_check')
            if is_add != check_path_exist(**argv):
                raise gen.Check_error('bgp path %s not expect' % str(argv))
            return
        argv.pop('is_check')
    if is_add:
        add_path(**argv)
    else:
        del_path(**argv)


@fun_gen(name=['','str'])
def show_vrf(**argv):
    return list_vrf_internal(**argv)


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


def add_del_vrf(**argv):
    is_add = (argv['is_add'] > 0)
    argv.pop('is_add')
    if 'is_check' in argv:
        if argv['is_check']:
            check_args = {'name':argv['name']}
            if is_add != len(show_vrf(**check_args)):
                raise gen.Check_error('bgp vrf %s not expect' % str(argv['name']))
            return
        argv.pop('is_check')
    if is_add:
        add_vrf(**argv)
    else:
        del_vrf(**argv)
    


@fun_gen(name=['','str'])
def show_policy(**argv):
    list_policy_internal(**argv)


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

