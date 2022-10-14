#!/usr/bin/env python
from bgp_peer import *
from bgp_path import *
from bgp_vrf import *
import sys, argparse
import bgp_control as this

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
        argv[i] = getattr(this, "is_"+str(arg_type[i][1]))(argv[i])
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
            func(**argv)
        return wrapper
    return func_deco


@fun_gen()
def find_peer(**argv):
    auto_discover_peer()


@fun_gen()
def show_peer(**argv):
    list_peer_internal()

 
@fun_gen(
    bgp_as=[0,'int'], 
    vrf_name=['','str'], 
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


@fun_gen()
def watch(**argv):
    watch_internal()


if __name__ == '__main__':
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

