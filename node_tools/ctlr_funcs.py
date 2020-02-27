# coding: utf-8

"""ctlr-specific helper functions."""

import logging


logger = logging.getLogger(__name__)


def check_net_trie(trie):
    """
    Check shared state Trie is fresh and empty (mainly on startup)
    :param trie: newly instantiated ``datrie.Trie(alpha_set)``
    """
    try:
        assert trie.is_dirty()
        assert list(trie) == []
    except:
        return False
    return True


def create_state_trie(prefix='trie', ext='.dat'):
    import string
    import tempfile
    import datrie

    fd, fname = tempfile.mkstemp(suffix=ext, prefix=prefix)
    trie = datrie.Trie(string.hexdigits)
    trie.save(fname)

    return fd, fname


def load_state_trie(fname):
    import datrie

    trie = datrie.Trie.load(fname)
    return trie


def save_state_trie(trie, fname):
    trie.save(fname)


def gen_netobj_queue(deque, ipnet='172.16.0.0/12'):
    import ipaddress

    if len(deque) > 0:
        logger.debug('Using existing queue: {}'.format(deque.directory))
    else:
        logger.debug('Generating netobj queue, please be patient...')
        netobjs = list(ipaddress.ip_network(ipnet).subnets(new_prefix=30))
        for net in netobjs:
            deque.append(net)
    logger.debug('{} IPNetwork objects in queue: {}'.format(len(deque), deque.directory))


def name_generator(size=10, char_set=None):
    """
    Generate a random network name for ZT add_network_object. The
    name returned is two substrings of <size> concatenated together
    with an underscore. Default character set is lowercase ascii plus
    digits, default size is 10.
    :param size: size of each substring
    :param char_set: character set used for sub strings
    """
    import random

    if not char_set:
        import string
        chars = string.ascii_lowercase + string.digits
    else:
        chars = char_set

    str1 = ''.join(random.choice(chars) for _ in range(size))
    str2 = ''.join(random.choice(chars) for _ in range(size))
    return str1 + '_' + str2


def ipnet_get_netcfg(netobj):
    """
    Process a (python) network object into config Attrdict.
    :param subnet object: python subnet object from the netobj queue
    :return config dict: Attrdict of JSON config fragments
    """
    import ipaddress as ip
    from node_tools.helper_funcs import AttrDict

    if isinstance(netobj, ip.IPv4Network):
        net_cidr = str(netobj)
        net_pfx = '/' + str(netobj.prefixlen)
        gate_iface = ip.IPv4Interface(str(list(netobj.hosts())[0]) + net_pfx)
        host_iface = ip.IPv4Interface(str(list(netobj.hosts())[1]) + net_pfx)
        host_addr = str(host_iface.ip)
        gate_addr = str(gate_iface.ip)
        host_cidr = str(host_iface)
        gate_cidr = str(gate_iface)

        net_routes = [{"target": "{}".format(net_cidr)},
                      {"target": "0.0.0.0/0", "via": "{}".format(gate_addr)}]

        d = {
            "net_routes": "{}".format(net_routes),
            "host": "{}".format(host_cidr),
            "gateway": "{}".format(gate_cidr)
        }
        return AttrDict.from_nested_dict(d)
    else:
        raise ValueError('{} is not a valid IPv4Network object'.format(netobj))


def netcfg_get_ipnet(addr):
    """
    Process member host or gateway addr string into the (python)
    network object it belongs to.  We also assume/require the CIDR
    prefix for ``addr`` == /30 to be compatible with gen_netobj_queue().
    :param host_addr: IPv4 address string without mask
    :return <netobj>: network object for host_addr
    :raises AddressValueError:
    """
    import ipaddress as ip
    from node_tools.helper_funcs import find_ipv4_iface

    if find_ipv4_iface(addr + '/30', strip=False):
        netobj = ip.ip_network(addr + '/30', strict=False)
        return netobj
    else:
        raise ip.AddressValueError


def set_network_cfg():
    """
    """
    pass