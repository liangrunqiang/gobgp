import psutil
import os
import struct
import socket

def mac2int(mac_str):
    return int(mac_str.translate(None, ":.- "), 16)

def int2mac(mac):
    mac_hex = "{:012x}".format(mac)
    mac_str = ":".join(mac_hex[i:i+2] for i in range(0, len(mac_hex), 2))
    return mac_str

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(str(addr)))[0]

def ip62int(addr6):
    return struct.unpack('!QQ', socket.inet_pton(socket.AF_INET6, addr6))

def ip6_add_ip4(prefix, ip4):
    v6hi, v6lo = struct.unpack('!QQ', socket.inet_pton(socket.AF_INET6, prefix))
    v4 = struct.unpack('!I', socket.inet_pton(socket.AF_INET, ip4))[0]
    return socket.inet_ntop(socket.AF_INET6, struct.pack('!QQ', v6hi, v6lo + v4))

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", int(addr)))
def int2ip6(ip_hi, ip_lo):
    ip_lo = int(struct.unpack('Q', struct.pack('Q', ip_lo))[0])
    ip_hi = int(struct.unpack('Q', struct.pack('Q', ip_hi))[0])
    return IPy.IP((ip_hi << 64) + ip_lo).strCompressed()

def h_int2ip6(ip_hi, ip_lo):
    ip_lo = int(struct.unpack('!Q', struct.pack('Q', ip_lo))[0])
    ip_hi = int(struct.unpack('!Q', struct.pack('Q', ip_hi))[0])
    return IPy.IP((ip_hi << 64) + ip_lo).strCompressed()

def h_int2ip(addr):
    return socket.inet_ntoa(struct.pack("I", int(addr)))

def ip_fix_stype(addr):
    addr = str(addr)
    if ':' in addr:
        if addr == '::':
            return addr
        addr6_int = ip62int(addr)
        return int2ip6(addr6_int[0], addr6_int[1])
    else:
        return addr

def n2h_16(n):
    return socket.ntohs(n)

def n2h_32(n):
    return socket.ntohl(n)

def n2h_64(n):
    return struct.unpack("!Q", struct.pack("Q", n))[0]

def ip_to_int(a, b, c, d): 
    return (a << 24) + (b << 16) + (c << 8) + d

def mac_to_ipv6_linklocal(mac):
    # Remove the most common delimiters; dots, dashes, etc.
    mac_value = int(mac.translate(None, ' .:-'), 16)

    # Split out the bytes that slot into the IPv6 address
    # XOR the most significant byte with 0x02, inverting the 
    # Universal / Local bit
    high2 = mac_value >> 32 & 0xffff ^ 0x0200
    high1 = mac_value >> 24 & 0xff
    low1 = mac_value >> 16 & 0xff
    low2 = mac_value & 0xffff

    addr6 = 'fe80::{:04x}:{:02x}ff:fe{:02x}:{:04x}'.format(high2, high1, low1, low2)
    ##因为中间可能有0，所以需要转换一下把0消掉
    addr6_int = ip62int(addr6)
    return int2ip6(addr6_int[0], addr6_int[1])


###
#arg:ip1(ip begin) ip2(ip_end)
#exp:192.168.1.0 192.168.1.255
#ret:255.255.255.0
###
def get_mask(ip1, ip2):
    i1 = ip1.split('.')
    i2 = ip2.split('.')
    il1 = []
    il2 = []
    for i in i1:
        il1.append(int(i))
    for i in i2:
        il2.append(int(i))
    "ip1 and ip2 are lists of 4 integers 0-255 each" 
    m = 0xFFFFFFFF^ip_to_int(*il1)^ip_to_int(*il2) 
    net_mask = [(m & (0xFF << (8*n))) >> 8*n for n in (3, 2, 1, 0)]
    ret = ''
    for i in net_mask:
        if len(ret) > 0:
            ret = ret + '.'
        ret = ret + str(i)
    return ret


###
#exp:
#ip:192.168.1.100
#mask:255.255.255.0
#ret:192.168.1.0/24
###
def get_net(ip, mask):
    return IP(ip).make_net(mask).strNormal()


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

###
#exp:
#mask_str:24
#ret:255.255.255.0
###

def exchange_maskint(mask_int):#int to str
  mask_int = int(mask_int)
  bin_arr = ['0' for i in range(32)]
  for i in range(mask_int):
    bin_arr[i] = '1'
  tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
  tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
  return '.'.join(tmpmask)
  

def is_same_net(ip1, ip2, mask):
    try:
        if len(ip1) == 0 or len(ip2) == 0:
            return 0
        # mask = str(mask)
        # if mask.isdigit():
        #     mask = exchange_maskint(mask)
        net1 = IP(ip1).make_net(mask).strNormal()
        net2 = IP(ip2).make_net(mask).strNormal()
        if net1 == net2:
            return 1
        else:
            return 0
    except Exception as e:
        return 0



def get_interface_mac(interface):
    DEVICE_NAME_LEN = 15
    MAC_START = 18
    MAC_END = 24
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, 
        struct.pack('256s', interface[:DEVICE_NAME_LEN]))
    a = ''
    for char in info[MAC_START:MAC_END]:
        a = a + str(char)
    return a
    #return ''.join(['%02x' % ord(char)
    #    for char in info[MAC_START:MAC_END]])

def get_interface_mac_str(interface):
    DEVICE_NAME_LEN = 15
    MAC_START = 18
    MAC_END = 24
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, 
        struct.pack('256s', interface[:DEVICE_NAME_LEN]))
    a = ''
    for char in info[MAC_START:MAC_END]:
        a = a + str(char)
    #return a
    return ':'.join(['%02x' % ord(char)
        for char in info[MAC_START:MAC_END]])



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



def get_net(ifname):
    net_card_info = []
    all_ip = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        if not k in ifname:
            continue
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                net_card_info.append((k, item[1], item[2]))
                all_ip.append(item[1])
    return net_card_info, all_ip
