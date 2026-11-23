import ipaddress
from .utils import (header, section, result, sep, info, warn, ok,
                    callout, ask, pause, C, cc, menu)

# ── Module 4: IP addressing and subnetting ────────────────────────────────────

def _ip_class(ip: ipaddress.IPv4Address) -> str:
    first = int(str(ip).split(".")[0])
    if first < 128:   return "A  (0.0.0.0  – 127.255.255.255)"
    if first < 192:   return "B  (128.0.0.0 – 191.255.255.255)"
    if first < 224:   return "C  (192.0.0.0 – 223.255.255.255)"
    if first < 240:   return "D  (Multicast)"
    return              "E  (Experimental)"

def _ip_scope(ip: ipaddress.IPv4Address) -> str:
    if ip.is_private:    return "Private (RFC 1918)"
    if ip.is_loopback:   return "Loopback (127.x)"
    if ip.is_link_local: return "Link-local (APIPA 169.254.x)"
    if ip.is_multicast:  return "Multicast (224–239.x)"
    return "Public (routable on the Internet)"

def subnet_calculator():
    header("IPv4 Subnet Calculator", "Module 4 · IP addressing")
    section("Enter an IP address with a CIDR prefix")
    info("Example: 192.168.1.0/24  or  10.0.0.45/8")
    raw = ask("IP/CIDR")
    if not raw:
        return
    try:
        # strict=False: accepts a host address inside the network (e.g. 192.168.1.45/24)
        net = ipaddress.IPv4Network(raw, strict=False)
        ip  = ipaddress.IPv4Address(raw.split("/")[0])
    except ValueError as e:
        warn(f"Invalid input: {e}")
        pause()
        return

    sep()
    section("Results")
    result("Network address",     str(net.network_address))
    result("Broadcast address",   str(net.broadcast_address))
    result("First host IP",       str(net.network_address + 1))
    result("Last host IP",        str(net.broadcast_address - 1))
    result("Subnet mask",         str(net.netmask))
    result("Wildcard (inverse)",  str(net.hostmask))
    result("CIDR prefix",         f"/{net.prefixlen}")
    result("Total addresses",     f"{net.num_addresses:,}")
    result("Usable hosts",        f"{max(0, net.num_addresses - 2):,}")

    sep()
    section("Analysis of the address you entered")
    result("Address entered",     str(ip))
    result("Class",               _ip_class(ip))
    result("Scope",               _ip_scope(ip))
    result("Is network address?", "Yes" if ip == net.network_address else "No")
    result("Is broadcast?",       "Yes" if ip == net.broadcast_address else "No")

    sep()
    section("Binary representation")
    parts = str(ip).split(".")
    binary = ".".join(f"{int(p):08b}" for p in parts)
    mask_b = ".".join(f"{int(p):08b}" for p in str(net.netmask).split("."))
    print(f"  {'IP (binary)':<24} {cc(C.BYELLOW, binary)}")
    print(f"  {'Mask (binary)':<24} {cc(C.BCYAN,  mask_b)}")
    print(f"  {'Network bits':<24} {cc(C.BGREEN,  str(net.prefixlen))}")
    print(f"  {'Host bits':<24} {cc(C.BMAGENTA, str(32 - net.prefixlen))}")

    callout("info", "Subnetting rule",
            f"With /{net.prefixlen} you have {32 - net.prefixlen} host bits.\n"
            f"2^{32 - net.prefixlen} = {net.num_addresses:,} total addresses\n"
            f"2^{32 - net.prefixlen} - 2 = {max(0, net.num_addresses - 2):,} usable hosts\n"
            "(minus 1 network address and 1 broadcast address)")
    pause()


def split_network():
    header("Split a Network into Subnets", "Module 4 · Subnetting")
    info("Calculates how to divide a network into N equal subnets.")
    raw_net = ask("Base network (e.g. 192.168.0.0/24)")
    if not raw_net:
        return
    raw_n = ask("How many subnets do you need?")
    if not raw_n:
        return
    try:
        base = ipaddress.IPv4Network(raw_net, strict=True)
        n    = int(raw_n)
        assert n >= 1
    except Exception:
        warn("Invalid input.")
        pause()
        return

    # Extra network bits needed for at least n subnets
    extra_bits = 0
    while (1 << extra_bits) < n:
        extra_bits += 1

    try:
        subnets = list(base.subnets(prefixlen_diff=extra_bits))
    except ValueError as e:
        warn(str(e))
        pause()
        return

    sep()
    section(f"{raw_net} split into {len(subnets)} subnets (/{base.prefixlen + extra_bits})")
    for i, s in enumerate(subnets[:32], 1):  # show at most 32
        hosts = max(0, s.num_addresses - 2)
        print(f"  {cc(C.BCYAN, f'Subnet {i:>3}')}  "
              f"{cc(C.BWHITE, str(s)):<22}  "
              f"Network: {str(s.network_address):<16} "
              f"Broadcast: {str(s.broadcast_address):<16} "
              f"Hosts: {hosts:>6,}")
    if len(subnets) > 32:
        info(f"... and {len(subnets) - 32} more subnets.")

    callout("info", "Extra bits used",
            f"{n} subnets need {extra_bits} extra network bits.\n"
            f"New prefix: /{base.prefixlen} + {extra_bits} = /{base.prefixlen + extra_bits}\n"
            f"Hosts per subnet: 2^{32 - base.prefixlen - extra_bits} - 2 = {max(0, (1 << (32 - base.prefixlen - extra_bits)) - 2):,}")
    pause()


def ipv6_analyzer():
    header("IPv6 Analyzer", "Module 4 · IPv6")
    info("Enter an IPv6 address (with or without a prefix).")
    raw = ask("IPv6 address")
    if not raw:
        return
    try:
        if "/" in raw:
            net = ipaddress.IPv6Network(raw, strict=False)
            ip  = ipaddress.IPv6Address(raw.split("/")[0])
        else:
            ip  = ipaddress.IPv6Address(raw)
            net = None
    except ValueError as e:
        warn(str(e))
        pause()
        return

    sep()
    section("IPv6 address analysis")
    result("Compressed form",   str(ip))
    result("Expanded form",     ip.exploded)

    kinds = []
    if ip.is_loopback:      kinds.append("Loopback (::1)")
    if ip.is_link_local:    kinds.append("Link-local (fe80::/10)")
    if ip.is_multicast:     kinds.append("Multicast (ff00::/8)")
    if ip.is_private:       kinds.append("ULA – Unique Local (fc00::/7)")
    if ip.is_global:        kinds.append("Global unicast (routable)")
    if ip.is_unspecified:   kinds.append("Unspecified (::)")
    result("Type",              ", ".join(kinds) if kinds else "Unknown")

    if net:
        result("Network",          str(net))
        result("Total addresses",  f"2^{128-net.prefixlen}")

    callout("info", "Why IPv6?",
            "IPv4 has 2^32 ≈ 4.3 billion addresses — already exhausted.\n"
            "IPv6 has 2^128 ≈ 340 undecillion.\n"
            "Enough to give millions of IPs to every grain of sand on the planet.")
    pause()


def notation_converter():
    header("Notation Converter", "Module 4 · Masks and CIDR")
    section("What do you want to convert?")
    opts = [
        "Subnet mask → CIDR prefix",
        "CIDR prefix → subnet mask",
        "Decimal IP → binary",
        "Binary → decimal IP",
    ]
    idx, _ = ask("", opts)

    if idx == 0:
        mask = ask("Mask (e.g. 255.255.255.0)")
        try:
            net = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
            ok(f"/{net.prefixlen}  (wildcard: {net.hostmask})")
        except ValueError as e:
            warn(str(e))

    elif idx == 1:
        prefix = ask("CIDR prefix (a number from 0 to 32)")
        try:
            net = ipaddress.IPv4Network(f"0.0.0.0/{prefix}", strict=False)
            ok(f"Mask:      {net.netmask}")
            ok(f"Wildcard:  {net.hostmask}")
        except ValueError as e:
            warn(str(e))

    elif idx == 2:
        ip_raw = ask("Decimal IP (e.g. 192.168.1.1)")
        try:
            ip = ipaddress.IPv4Address(ip_raw)
            b  = ".".join(f"{x:08b}" for x in ip.packed)
            ok(f"{b}")
        except ValueError as e:
            warn(str(e))

    elif idx == 3:
        bin_raw = ask("Dot-separated binary (e.g. 11000000.10101000.00000001.00000001)")
        try:
            parts = [int(x, 2) for x in bin_raw.strip().split(".")]
            assert len(parts) == 4 and all(0 <= p <= 255 for p in parts)
            ok(f"{'.'.join(str(p) for p in parts)}")
        except Exception:
            warn("Invalid format. Use 4 groups of 8 bits separated by dots.")
    pause()


def run():
    while True:
        opts = [
            "Subnet calculator (IP/CIDR → network, broadcast, hosts, binary)",
            "Split a network into N subnets",
            "IPv6 analyzer",
            "Notation converter (mask ↔ CIDR, decimal ↔ binary)",
        ]
        choice = menu("Module 4 · IP Addressing and Subnetting", opts)
        if choice == -1:
            break
        [subnet_calculator, split_network, ipv6_analyzer, notation_converter][choice]()
