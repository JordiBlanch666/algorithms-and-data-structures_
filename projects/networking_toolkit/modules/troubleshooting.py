from .utils import (header, section, step, substep, result, sep, info,
                    warn, ok, callout, ask, pause, C, cc, menu)

# ── Troubleshooting: 12 interactive guides ────────────────────────────────────

def _yes_no(question):
    """Return True if the user answers yes."""
    print(f"\n  {cc(C.BYELLOW, '?')}  {question}")
    raw = input(f"  {cc(C.BCYAN, '[y/n]')}: ").strip().lower()
    return raw in ("y", "yes", "s", "si", "sí", "1")


# ── T1: No connectivity ───────────────────────────────────────────────────────
def ts1_no_connectivity():
    header("T1 · No Internet connectivity", "Troubleshooting · Step-by-step diagnosis")
    step(1, "Check the physical connection",
         "Make sure the Ethernet cable is plugged in properly or that WiFi is on.\n"
         "Command: ip link (Linux) / ipconfig (Windows)")

    if not _yes_no("Is the port's activity light on / is the WiFi icon connected?"):
        callout("warn", "Physical problem",
                "Check the cable, try another port on the switch, or restart the WiFi access point.")
        pause()
        return

    step(2, "Check the IP address",
         "ip addr (Linux) / ipconfig (Windows)\n"
         "Find your IP. If it starts with 169.254.x.x → APIPA (DHCP failed).")

    if not _yes_no("Does your device have a valid IP (not 169.254.x.x)?"):
        callout("warn", "DHCP failure",
                "Try: ipconfig /release && ipconfig /renew (Windows)\n"
                "     dhclient -r && dhclient (Linux)\n"
                "If it persists: check that the router's DHCP server is enabled.")
        pause()
        return

    step(3, "Ping the gateway",
         "ip route (Linux) / ipconfig (Windows) → look for 'Default Gateway'.\n"
         "Then: ping <gateway IP>")

    if not _yes_no("Does the gateway answer the ping?"):
        callout("warn", "Local network problem",
                "Restart the router/switch. Check the VLAN. See if a firewall is blocking ICMP.")
        pause()
        return

    step(4, "Ping a public IP (no DNS)",
         "ping 8.8.8.8 (Google DNS)\n"
         "This checks Internet connectivity WITHOUT using DNS.")

    if not _yes_no("Does 8.8.8.8 answer the ping?"):
        callout("warn", "Routing / ISP problem",
                "Your LAN is fine but you can't reach the Internet.\n"
                "Check: the router's NAT settings, whether your ISP has an outage,\n"
                "or whether the router has wrong routes.")
        pause()
        return

    step(5, "DNS test",
         "ping google.com → if it fails but 8.8.8.8 worked, the problem is DNS.")

    if not _yes_no("Does google.com (by name) answer the ping?"):
        callout("warn", "DNS problem",
                "Try setting DNS manually:\n"
                "  Windows: Network → Adapter → TCP/IP → DNS: 8.8.8.8\n"
                "  Linux:   /etc/resolv.conf → nameserver 8.8.8.8\n"
                "If it works by IP but not by name → your ISP's DNS has problems.")
        pause()
        return

    ok("Full connectivity! If something still fails, it may be the application (T5) or a firewall (T6).")
    pause()


# ── T2: Slow network ──────────────────────────────────────────────────────────
def ts2_slow_network():
    header("T2 · Slow or intermittent network", "Troubleshooting")

    section("Latency and packet-loss diagnosis")
    step(1, "Measure latency to the gateway",
         "ping -c 20 <gateway>  (Linux)\n"
         "ping -n 20 <gateway>  (Windows)\n"
         "Look at: min/avg/max and % packet loss")
    step(2, "Trace the route (traceroute)",
         "traceroute google.com  (Linux/Mac)\n"
         "tracert   google.com  (Windows)\n"
         "Find the hop with high latency or losses (*)")
    step(3, "Check interface collisions and errors",
         "ip -s link show <interface>  (Linux)\n"
         "netstat -e (Windows)\n"
         "Look for: errors, dropped, overruns")
    step(4, "Check bandwidth",
         "Use speedtest-cli (speedtest.net) to compare real throughput with your plan.")
    step(5, "Review QoS and congestion",
         "Many devices transmitting at the same time → congestion.\n"
         "Check whether a process is using all the bandwidth (e.g. backups, torrents).")

    callout("info", "Rules of thumb",
            "Latency < 20ms: excellent\n"
            "Latency 20–100ms: acceptable\n"
            "Latency > 150ms: problems for VoIP/gaming\n"
            "Packet loss > 1%: unacceptable for most applications")
    pause()


# ── T3: IP / DHCP ─────────────────────────────────────────────────────────────
def ts3_dhcp():
    header("T3 · IP / DHCP problems", "Troubleshooting")
    step(1, "Find the assigned IP",
         "ipconfig /all (Windows) / ip addr (Linux)\n"
         "If the IP is 169.254.x.x → DHCP did NOT answer (APIPA).")
    step(2, "Release and renew the IP",
         "Windows: ipconfig /release → ipconfig /renew\n"
         "Linux:   dhclient -r eth0 → dhclient eth0\n"
         "Mac:     sudo ipconfig set en0 DHCP")
    step(3, "Check the DHCP server",
         "Open the router's admin panel → make sure DHCP is enabled.\n"
         "Check the available IP pool (if it's full, no more addresses are handed out).")
    step(4, "Set a static IP manually",
         "If DHCP is temporarily down:\n"
         "  IP:      192.168.1.99 (a free one on your network)\n"
         "  Mask:    255.255.255.0\n"
         "  Gateway: 192.168.1.1\n"
         "  DNS:     8.8.8.8")
    step(5, "Check for an IP conflict",
         "If two devices have the same IP → conflict.\n"
         "Use: arp -a (every MAC/IP on the local network)\n"
         "     arping <IP>  to detect duplicates.")

    callout("info", "DHCP process (DORA)",
            "Discover → Offer → Request → ACK\n"
            "The client sends DISCOVER as a broadcast (255.255.255.255).\n"
            "If the DHCP server doesn't answer → DISCOVER failed or the server is down.")
    pause()


# ── T4: DNS ───────────────────────────────────────────────────────────────────
def ts4_dns():
    header("T4 · DNS problems", "Troubleshooting")
    step(1, "Confirm the problem is DNS (not the Internet)",
         "ping 8.8.8.8   → does it answer? (the Internet DOES work)\n"
         "ping google.com → does it fail?  (DNS is the problem)")
    step(2, "Check the configured DNS",
         "ipconfig /all (Windows) → look for 'DNS Servers'\n"
         "cat /etc/resolv.conf (Linux)")
    step(3, "Try another DNS server",
         "Switch to 8.8.8.8 or 1.1.1.1 temporarily\n"
         "If it works → your ISP's DNS is down")
    step(4, "Flush the DNS cache",
         "Windows: ipconfig /flushdns\n"
         "Linux:   sudo systemd-resolve --flush-caches\n"
         "Mac:     sudo dscacheutil -flushcache")
    step(5, "Query manually with nslookup / dig",
         "nslookup google.com 8.8.8.8\n"
         "dig @8.8.8.8 google.com\n"
         "Try different DNS servers to isolate the problem.")

    callout("info", "Reliable public DNS",
            "Google:     8.8.8.8  /  8.8.4.4\n"
            "Cloudflare: 1.1.1.1  /  1.0.0.1  (faster)\n"
            "Quad9:      9.9.9.9  (malware filtering)\n"
            "OpenDNS:    208.67.222.222")
    pause()


# ── T5: HTTP / HTTPS ──────────────────────────────────────────────────────────
def ts5_http():
    header("T5 · HTTP / HTTPS problems", "Troubleshooting")
    step(1, "Identify the error code",
         "4xx = CLIENT error\n"
         "5xx = SERVER error\n"
         "Most common: 400 (bad request), 401 (unauthorized), 403 (forbidden),\n"
         "             404 (not found), 500 (internal error), 502 (bad gateway), 503 (unavailable)")
    step(2, "Test with curl",
         "curl -I https://domain.com\n"
         "Shows the status code and headers without downloading the body.")
    step(3, "Check HTTPS / TLS",
         "openssl s_client -connect domain.com:443\n"
         "Shows the certificate, CA chain and expiry date.")
    step(4, "Review security headers",
         "curl -I https://domain.com | grep -i 'strict\\|content-security\\|x-frame'\n"
         "HSTS, CSP and X-Frame-Options protect against common attacks.")
    step(5, "Check for a proxy or firewall",
         "Is there a corporate proxy? Check the http_proxy / https_proxy variables.\n"
         "A firewall can block port 443 on some networks.")

    callout("info", "HTTP vs HTTPS traffic",
            "HTTP: plain-text data → anyone on the network can read it.\n"
            "HTTPS: data encrypted with TLS → nobody along the way can read it.\n"
            "Always use HTTPS. Chrome has shown 'Not secure' on HTTP sites since 2018.")
    pause()


# ── T6: Security ──────────────────────────────────────────────────────────────
def ts6_security():
    header("T6 · Network Security Diagnosis", "Troubleshooting")
    step(1, "Scan open ports",
         "nmap -sS -p 1-1024 <IP>           (quick scan)\n"
         "nmap -A <IP>                        (OS and version detection)\n"
         "Only on networks/systems you are authorized to scan.")
    step(2, "Check active connections",
         "netstat -tulnp (Linux) — shows which process listens on which port\n"
         "ss -tulnp      (Linux, more modern)\n"
         "netstat -ano   (Windows)")
    step(3, "Detect suspicious traffic",
         "tcpdump -i eth0 -n    (Linux — captures packets in real time)\n"
         "Wireshark              (GUI — filter by IP, protocol, etc.)")
    step(4, "Check firewall rules",
         "iptables -L -n -v     (Linux)\n"
         "ufw status verbose    (Ubuntu)\n"
         "netsh advfirewall show allprofiles (Windows)")
    step(5, "Review failed login attempts",
         "tail -f /var/log/auth.log         (Debian/Ubuntu)\n"
         "tail -f /var/log/secure           (CentOS/RHEL)\n"
         "Look for: 'Failed password', 'Invalid user' → possible brute force")

    callout("danger", "CIA triad",
            "Confidentiality: can only the right people see the data?\n"
            "Integrity:       has the data been left unmodified?\n"
            "Availability:    is the system reachable when it's needed?")
    pause()


# ── T7: SSL certificates ──────────────────────────────────────────────────────
def ts7_ssl():
    header("T7 · SSL/TLS Certificate Problems", "Troubleshooting")
    step(1, "Check the expiry date",
         "openssl s_client -connect domain.com:443 2>/dev/null | openssl x509 -noout -dates\n"
         "Chrome: padlock → Certificate → Valid to:")
    step(2, "Check that the CN matches",
         "The CN (Common Name) or SAN must match the domain you visited.\n"
         "Error 'NET::ERR_CERT_COMMON_NAME_INVALID' → the cert belongs to another domain.")
    step(3, "Check the CA chain",
         "The certificate must be signed by a trusted CA (Let's Encrypt, DigiCert, etc.).\n"
         "Error 'NET::ERR_CERT_AUTHORITY_INVALID' → unknown CA or self-signed certificate.")
    step(4, "Renew the certificate with Let's Encrypt",
         "certbot renew --dry-run    (test)\n"
         "certbot renew              (renew)\n"
         "Let's Encrypt certificates expire every 90 days. Set up auto-renewal with cron.")
    step(5, "Check the TLS version",
         "openssl s_client -tls1_2 -connect domain.com:443\n"
         "TLS 1.0 and 1.1 are deprecated. Use TLS 1.2 at minimum, TLS 1.3 recommended.")

    callout("info", "Online tools",
            "SSL Labs: ssllabs.com/ssltest → full analysis of the TLS setup\n"
            "Why No Padlock: whynopadlock.com → detects mixed content (HTTP inside HTTPS)")
    pause()


# ── T8: WiFi ──────────────────────────────────────────────────────────────────
def ts8_wifi():
    header("T8 · WiFi and Signal Problems", "Troubleshooting")
    step(1, "Check signal strength",
         "Windows: netsh wlan show interfaces → Signal\n"
         "Linux:   iwconfig wlan0 / iw dev wlan0 link\n"
         "Ideal: > -65 dBm. Problematic: < -80 dBm.")
    step(2, "Analyze channels in use",
         "Many routers on the same channel → interference.\n"
         "Windows: netsh wlan show networks mode=bssid\n"
         "Linux:   iwlist scan | grep Channel\n"
         "Pick the least crowded channel (1, 6 or 11 on 2.4GHz).")
    step(3, "2.4 GHz vs 5 GHz",
         "2.4 GHz: longer range, more interference, max speed ~300 Mbps\n"
         "5 GHz:   shorter range, less interference, speeds up to ~1.3 Gbps\n"
         "If you're close to the router and there's interference → try 5 GHz.")
    step(4, "Look for physical obstructions",
         "Concrete walls, appliances, microwaves and cordless phones\n"
         "interfere with 2.4 GHz. A router next to a microwave = disaster.")
    step(5, "Restart the WiFi adapter",
         "Windows: Device Manager → Disable/Enable the WiFi adapter\n"
         "Linux:   ip link set wlan0 down && ip link set wlan0 up")
    pause()


# ── T9: Email / spam ──────────────────────────────────────────────────────────
def ts9_email():
    header("T9 · Email and Spam Problems", "Troubleshooting")
    step(1, "Check the mail server ports",
         "Outgoing SMTP: 587 (STARTTLS) or 465 (SSL)\n"
         "POP3:          110 (plain) or 995 (SSL)\n"
         "IMAP:          143 (STARTTLS) or 993 (SSL)\n"
         "telnet <server> <port>  → checks connectivity")
    step(2, "Review the SPF, DKIM and DMARC records",
         "SPF:   TXT v=spf1 include:_spf.google.com ~all\n"
         "DKIM:  TXT selector._domainkey → digital signature for emails\n"
         "DMARC: TXT v=DMARC1; p=quarantine; rua=mailto:...\n"
         "Without these records → your emails land in SPAM.")
    step(3, "Check blacklists",
         "If your IP is on a spam blacklist:\n"
         "mxtoolbox.com → Blacklist Check\n"
         "Request delisting if the IP is clean.")
    step(4, "Review the SMTP server logs",
         "/var/log/mail.log (Debian/Ubuntu)\n"
         "/var/log/maillog  (CentOS/RHEL)\n"
         "Look for: relay denied, authentication failed, connection refused")
    pause()


# ── T10: Everyday problems ────────────────────────────────────────────────────
def ts10_everyday():
    header("T10 · Everyday Network Problems", "Troubleshooting")
    problems = [
        ("One specific page won't load (others do)",
         "A problem with the destination server or with DNS for that domain.\n"
         "Try: curl -I https://site.com from a terminal.\n"
         "Check downdetector.com to see whether the site is down for everyone."),
        ("The network is slow only at certain times",
         "Congestion at the ISP (peak hours) or on your local network.\n"
         "Check with speedtest-cli. Compare your plan's speed with the real one."),
        ("The router gives the same IP to another device",
         "IP conflict. Assign static IPs by MAC (DHCP reservations)\n"
         "in the router's panel for critical devices."),
        ("VPN is connected but nothing loads",
         "Split tunneling is misconfigured. The VPN gateway isn't routing.\n"
         "Check: ip route (Linux) / route print (Windows)."),
        ("I can't connect to a server over SSH",
         "Check: port 22 is open (nmap), the server firewall (iptables/ufw),\n"
         "and that the SSH daemon is running (systemctl status sshd)."),
    ]
    for i, (problem, solution) in enumerate(problems, 1):
        step(i, problem, solution)
    pause()


# ── T11: Practical security ───────────────────────────────────────────────────
def ts11_practical_security():
    header("T11 · Practical Security", "Troubleshooting · Checklist")
    checklist = [
        ("Strong passwords", "At least 12 characters, uppercase + numbers + symbols.\n"
                             "Use a manager: Bitwarden, KeePass. NEVER reuse passwords."),
        ("Two-factor authentication (2FA)", "Turn on 2FA for all your important accounts.\n"
                                            "Preferably with an app (TOTP: Google Authenticator, Authy)\n"
                                            "rather than SMS (SIM swapping)."),
        ("Update software regularly", "Known vulnerabilities (CVEs) get patched in updates.\n"
                                      "An unpatched system is an easy target."),
        ("HTTPS everywhere", "Never send sensitive data over HTTP.\n"
                             "Turn on HTTPS-only mode in your browser or configure HSTS."),
        ("VPN on public networks", "On café, hotel or airport WiFi → use a VPN.\n"
                                   "An attacker on the same network can do ARP spoofing / MITM."),
        ("3-2-1 backups", "3 copies, 2 different media, 1 offsite.\n"
                          "Encrypt backups. Make sure you can restore them."),
        ("Principle of least privilege", "Don't use a root/admin account for everyday tasks.\n"
                                         "Only elevate privileges when you need to."),
    ]
    for i, (title, desc) in enumerate(checklist, 1):
        step(i, title, desc)
    pause()


# ── T12: Advanced commands ────────────────────────────────────────────────────
def ts12_commands():
    header("T12 · Advanced Network Commands", "Troubleshooting · Reference")
    sep()
    cmds = [
        ("Basic connectivity", [
            ("ping <IP>",            "Checks ICMP connectivity"),
            ("traceroute / tracert", "Traces the packet route hop by hop"),
            ("mtr <destination>",    "ping + traceroute in real time (Linux)"),
        ]),
        ("DNS", [
            ("nslookup <domain>",              "DNS query (Windows/Linux)"),
            ("dig <domain>",                   "Detailed DNS query (Linux)"),
            ("dig +trace <domain>",            "Traces DNS resolution from the root"),
            ("dig -x <IP>",                    "Reverse DNS"),
            ("ipconfig /flushdns",             "Flush the DNS cache (Windows)"),
        ]),
        ("Interfaces and routes", [
            ("ip addr / ifconfig",             "Show interfaces and their IPs"),
            ("ip route / route -n",            "Show the routing table"),
            ("ip link",                        "Interface status (up/down)"),
            ("arp -a",                         "ARP table: IP ↔ MAC on the local network"),
        ]),
        ("Ports and connections", [
            ("netstat -tulnp",                 "Listening ports and processes (Linux)"),
            ("ss -tulnp",                      "Modern version of netstat"),
            ("nmap -sS <IP>",                  "SYN port scan (needs root)"),
            ("nc -zv <IP> <port>",             "Check whether a port is open"),
        ]),
        ("Packet capture", [
            ("tcpdump -i eth0",                "Capture packets on eth0"),
            ("tcpdump -i any port 80",         "HTTP traffic only"),
            ("tcpdump -w capture.pcap",        "Save the capture for Wireshark"),
        ]),
        ("Bandwidth", [
            ("iperf3 -s",                      "Bandwidth test server"),
            ("iperf3 -c <IP>",                 "Client → measures TCP throughput"),
            ("speedtest-cli",                  "Measure Internet speed"),
        ]),
    ]

    for category, items in cmds:
        section(category)
        for cmd, desc in items:
            print(f"  {cc(C.BYELLOW, f'{cmd:<42}')} {cc(C.DIM, desc)}")

    pause()


GUIDES = [
    ("T1  · No Internet connectivity",         ts1_no_connectivity),
    ("T2  · Slow or intermittent network",     ts2_slow_network),
    ("T3  · IP / DHCP problems",               ts3_dhcp),
    ("T4  · DNS problems",                     ts4_dns),
    ("T5  · HTTP / HTTPS problems",            ts5_http),
    ("T6  · Security diagnosis",               ts6_security),
    ("T7  · SSL/TLS certificates",             ts7_ssl),
    ("T8  · WiFi and wireless signal",         ts8_wifi),
    ("T9  · Email and spam",                   ts9_email),
    ("T10 · Everyday problems",                ts10_everyday),
    ("T11 · Practical security (checklist)",   ts11_practical_security),
    ("T12 · Advanced network commands",        ts12_commands),
]


def run():
    while True:
        opts = [label for label, _ in GUIDES]
        choice = menu("Troubleshooting · 12 Diagnostic Guides", opts)
        if choice == -1:
            break
        GUIDES[choice][1]()
