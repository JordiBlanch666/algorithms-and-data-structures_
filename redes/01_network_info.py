"""
Network Info — where does my machine sit on the network?

Before you can understand how computers communicate, you need to understand
how they identify themselves. Every device on a network has:

  Hostname  — a human-readable name (e.g. "Jordi-laptop")
  IP address — a numeric address the network actually uses (e.g. 192.168.1.5)

This script uses Python's built-in 'socket' module to answer those questions.
No external libraries needed — socket is part of the standard library.

Key concept: DNS (Domain Name System) is the phone book of the internet.
It translates hostnames like "google.com" into IP addresses like "142.250.80.46".
socket.gethostbyname() does that lookup for us.
"""

import socket


def get_local_info() -> dict:
    """Return the machine's hostname and local IP address."""
    hostname = socket.gethostname()

    # gethostbyname resolves the hostname to an IP.
    # On most systems this gives you the LAN IP (e.g. 192.168.x.x).
    ip_address = socket.gethostbyname(hostname)

    return {"hostname": hostname, "ip_address": ip_address}


def resolve_domain(domain: str) -> str:
    """
    Ask DNS to translate a domain name into an IP address.
    This is exactly what your browser does before loading a website.
    """
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        # gaierror = "getaddrinfo error" — DNS lookup failed.
        # Could be no internet, typo in the domain, or DNS server down.
        return "Could not resolve (no internet or invalid domain)"


def reverse_lookup(ip: str) -> str:
    """
    Go the other direction: IP address → hostname.
    Not all IPs have a reverse record, so we handle the failure gracefully.
    """
    try:
        # gethostbyaddr returns (hostname, alias_list, address_list)
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        return "No reverse DNS record found"


if __name__ == "__main__":
    print("══ Network Info ════════════════════════════════════\n")

    info = get_local_info()
    print(f"  Hostname:      {info['hostname']}")
    print(f"  Local IP:      {info['ip_address']}")

    print("\n  ── DNS Resolution ──────────────────────────────")
    domains = ["google.com", "github.com", "python.org"]
    for domain in domains:
        ip = resolve_domain(domain)
        print(f"  {domain:<20} →  {ip}")

    print("\n  ── Reverse Lookup ──────────────────────────────")
    test_ip = resolve_domain("google.com")
    print(f"  {test_ip} → {reverse_lookup(test_ip)}")
