###
#exp:
#mask_str:255.255.255.0
#ret:24
###
def exchange_mask(mask_str):#str to int
    count_bit = lambda bin_str: len([i for i in bin_str if i=='1'])
    mask_splited = mask_str.split('.')
    mask_count = [count_bit(bin(int(i))) for i in mask_splited]
    return sum(mask_count)

def ip2int(addr):
        return struct.unpack("!I", socket.inet_aton(str(addr)))[0]

def int2ip(addr):
        return socket.inet_ntoa(struct.pack("!I", int(addr)))

def get_physical_netcard():
    stats_info = psutil.net_if_stats()
    netcard = os.listdir("/sys/class/net")
    virtual_netcard = os.listdir("/sys/devices/virtual/net/")
    physical_netcard_all = list(set(netcard) ^ set(virtual_netcard))
    physical_netcard_down = []
    for key in physical_netcard_all:
        isup, _, _, _ = stats_info[key]
        if not isup:
            physical_netcard_down.append(key)
    physical_netcard_up = list(
        set(physical_netcard_all) ^ set(physical_netcard_down)
    )
    return physical_netcard_up, physical_netcard_down, physical_netcard_all

def get_net_card(ifname):
    net_card_info = []
    all_ip = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        if not k == ifname:
            continue
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                net_card_info.append((k, item[1], item[2]))
                all_ip.append(item[1])
    return net_card_info, all_ip
