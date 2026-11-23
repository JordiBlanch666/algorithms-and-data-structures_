import socket
import time
from .utils import (header, section, step, result, sep, info, warn,
                    callout, ask, pause, C, cc, menu)

# ── Module 3b: DNS and name resolution ────────────────────────────────────────

def resolve_domain():
    header("Resolve Domain → IP", "Module 3b · DNS")
    raw = ask("Domain (e.g. google.com, facebook.com)")
    if not raw:
        return
    domain = raw.strip().lower()

    info(f"Resolving '{domain}'...")
    try:
        t0 = time.time()
        results = socket.getaddrinfo(domain, None)
        ms = (time.time() - t0) * 1000
    except socket.gaierror as e:
        warn(f"DNS error: {e}")
        pause()
        return

    sep()
    ips_v4 = sorted(set(r[4][0] for r in results if r[0] == socket.AF_INET))
    ips_v6 = sorted(set(r[4][0] for r in results if r[0] == socket.AF_INET6))

    result("Domain queried", domain)
    result("Resolution time", f"{ms:.1f} ms")

    if ips_v4:
        result("IPv4 (A records)", ", ".join(ips_v4))
    if ips_v6:
        result("IPv6 (AAAA records)", ", ".join(ips_v6[:3]))

    # Canonical name
    try:
        canonical = socket.getfqdn(domain)
        if canonical != domain:
            result("Canonical FQDN", canonical)
    except Exception:
        pass

    sep()
    section("What happened behind the scenes")
    steps = [
        ("Local cache",          f"The OS looked for '{domain}' in its cache. If found: straight to step 7."),
        ("Hosts file",           "It checked /etc/hosts (or C:\\Windows\\System32\\drivers\\etc\\hosts)."),
        ("System resolver",      "It asked the configured DNS server (your router's or ISP's)."),
        ("Root server",          "The resolver asked one of the 13 root servers: 'who handles this TLD?'"),
        ("TLD server",           "The root pointed to the TLD server (e.g. .com, .net)."),
        ("Authoritative server", f"The TLD pointed to the authoritative DNS server for '{domain}'."),
        ("Final answer",         f"The authoritative server returned: {', '.join(ips_v4[:2]) if ips_v4 else 'N/A'}"),
    ]
    for i, (t, d) in enumerate(steps, 1):
        step(i, t, d)

    callout("info", "Why UDP?",
            "DNS uses UDP port 53 by default (faster, less overhead).\n"
            "It only switches to TCP when the answer exceeds 512 bytes (zone transfers, DNSSEC).")
    pause()


def reverse_dns():
    header("Reverse DNS (PTR)", "Module 3b · rDNS")
    info("Turns an IP into a domain name (if the administrator configured a PTR record).")
    raw = ask("IP address")
    if not raw:
        return
    try:
        t0 = time.time()
        hostname = socket.gethostbyaddr(raw.strip())
        ms = (time.time() - t0) * 1000
        sep()
        result("IP queried",  raw.strip())
        result("Hostname",    hostname[0])
        result("Aliases",     ", ".join(hostname[1]) or "none")
        result("All IPs",     ", ".join(hostname[2]))
        result("Time",        f"{ms:.1f} ms")
    except socket.herror as e:
        warn(f"No PTR record for {raw}: {e}")
    pause()


def dns_hierarchy():
    header("DNS Hierarchy", "Module 3b · Structure")
    info("DNS is a distributed tree. The root sits at the top; domains hang below it.")
    sep()

    levels = [
        (".", "Root", "13 groups of root servers run by ICANN, NASA, ARIN, etc.\n"
                      "They know who handles each TLD (.com, .net, .org, .mx, .es…)"),
        (".com / .org / .mx", "TLD (Top Level Domain)", "Managed by registries (Verisign for .com).\n"
                                                        "They know which server is authoritative for each domain."),
        ("google.com", "Second-level domain (SLD)", "The one you register with a registrar (GoDaddy, Namecheap…).\n"
                                                    "You control its DNS zone."),
        ("www.google.com / mail.google.com", "Subdomain", "Defined in your DNS zone. Points to specific servers."),
    ]

    for i, (example, level, desc) in enumerate(levels, 1):
        step(i, f"{level}  →  {cc(C.BYELLOW, example)}", desc)

    sep()
    section("Types of DNS servers")
    kinds = [
        ("Recursive resolver",   "Does the work of finding the complete answer (your ISP or 8.8.8.8)."),
        ("Root server",          "The starting point. Only knows about TLDs. 13 IP addresses (A–M.ROOT-SERVERS.NET)."),
        ("TLD server",           "Knows the name servers for every domain under its TLD."),
        ("Authoritative server", "Holds the definitive answer for a domain. Your actual DNS server."),
        ("Caching server",       "Stores answers temporarily according to each record's TTL."),
    ]
    for name, desc in kinds:
        result(name, desc)

    callout("info", "TTL (Time To Live)",
            "Every DNS record has a TTL in seconds.\n"
            "With TTL=300, the resolver caches it for 5 minutes.\n"
            "Lower the TTL before changing servers so the change propagates quickly.")
    pause()


def dns_records():
    header("DNS Record Types", "Module 3b · DNS zone")
    records = [
        ("A",     "Name → IPv4",                   "example.com → 93.184.216.34"),
        ("AAAA",  "Name → IPv6",                   "example.com → 2606:2800:220:1:248:1893:25c8:1946"),
        ("CNAME", "Alias → canonical name",        "www → example.com (points one name to another)"),
        ("MX",    "Mail server",                   "example.com → mail.example.com (with priority)"),
        ("TXT",   "Arbitrary text",                "SPF: v=spf1 include:_spf.google.com ~all"),
        ("NS",    "Name servers",                  "example.com → ns1.provider.com"),
        ("PTR",   "IP → name (rDNS)",              "34.216.184.93.in-addr.arpa → example.com"),
        ("SOA",   "Start of Authority",            "Administrator, refresh interval, serial number"),
        ("SRV",   "Specific service + port",       "_sip._tcp.example.com → sipserver.example.com:5060"),
        ("CAA",   "Allowed certificate authorities", "0 issue 'letsencrypt.org'"),
    ]

    sep()
    print(f"  {cc(C.BOLD, 'Type'):<12} {cc(C.BOLD, 'Purpose'):<32} {cc(C.BOLD, 'Example')}")
    print(f"  {'─'*10} {'─'*30} {'─'*36}")
    for rtype, func, example in records:
        print(f"  {cc(C.BCYAN, rtype):<20} {func:<32} {cc(C.DIM, example)}")
    pause()


def run():
    while True:
        opts = [
            "Resolve a domain → IP (real DNS lookup)",
            "Reverse DNS: IP → hostname (PTR)",
            "DNS hierarchy (Root → TLD → SLD)",
            "DNS record types (A, AAAA, MX, CNAME, TXT…)",
        ]
        choice = menu("Module 3b · DNS and Name Resolution", opts)
        if choice == -1:
            break
        [resolve_domain, reverse_dns, dns_hierarchy, dns_records][choice]()
