# Networking Toolkit

An interactive command-line (CLI) tool in Python for studying and practicing **Computer Networking Fundamentals**. It covers the 8 course modules with working tools: a subnet calculator, real DNS lookups, cryptographic hashing and 12 step-by-step troubleshooting guides.

---

## Modules

| # | Module | Tools |
|---|--------|-------|
| M1 | History and topologies | Bus, Star, Ring, Mesh, Tree, Cisco 3-layer model |
| M2 | OSI and TCP/IP models | 7 OSI layers, encapsulation, OSI vs TCP/IP comparison |
| M3 | Communication protocols | HTTP/S, DNS, DHCP, FTP, SMTP, SSH, TCP, UDP with detailed steps |
| M3b | DNS and name resolution | Real resolution, reverse DNS, hierarchy, record types |
| M4 | IP addressing and subnetting | IPv4/IPv6 calculator, subnet splitter, binary/CIDR converters |
| M6 | Cybersecurity | CIA triad, attack types, step-by-step TLS handshake, VLANs |
| M7 | Cryptography | SHA-256/MD5/BLAKE2, HMAC, Caesar cipher, RSA concepts, Base64 |
| TS | Troubleshooting (12 guides) | Interactive diagnosis, from no connectivity to advanced commands |

---

## Installation and usage

No external dependencies. Just Python 3.8+.

```bash
git clone https://github.com/JordiBlanch666/algorithms-and-data-structures_.git
cd algorithms-and-data-structures_/projects/networking_toolkit
python main.py
```

---

## Examples

### Subnet calculator

```
Input: 192.168.10.45/26

Network address:        192.168.10.0
Broadcast:              192.168.10.63
First host IP:          192.168.10.1
Last host IP:           192.168.10.62
Subnet mask:            255.255.255.192
Wildcard:               0.0.0.63
Usable hosts:           62

IP (binary):   11000000.10101000.00001010.00101101
Mask:          11111111.11111111.11111111.11000000
```

### Real DNS resolution

```
Domain: github.com

IPv4 (A record):        140.82.112.4
Resolution time:        12.3 ms

Process:
  [1] Local cache — checked the OS cache
  [2] Recursive resolver — asked the configured DNS server
  [3] Root server — asked who handles .com
  [4] TLD server — pointed to github.com's authoritative server
  [5] Final answer — 140.82.112.4
```

### Hash calculator

```
Text: Hello world

MD5:     3e25960a79dbc69b674cd4ec67a72c62
SHA-1:   7b502c3a1f48c8609ae212cdfb639dee39673f5e
SHA-256: 64ec88ca00b268e5ba1a35678a1b5316d212f4f3...
SHA-512: b7f783baed8297f0db917462184ff4f0...
```

---

## Project structure

```
networking_toolkit/
├── main.py                   # Main menu
└── modules/
    ├── utils.py              # Colors, menus, standard output helpers
    ├── topologies.py         # M1: Network topologies
    ├── osi_model.py          # M2: OSI and TCP/IP models
    ├── protocols.py          # M3: Communication protocols
    ├── dns_tool.py           # M3b: DNS and name resolution
    ├── subnetting.py         # M4: IP addressing and subnetting
    ├── security.py           # M6: Cybersecurity
    ├── crypto_basics.py      # M7: Cryptography
    └── troubleshooting.py    # T1–T12: Diagnostic guides
```

---

## Troubleshooting guides

| # | Guide | What it covers |
|---|-------|----------------|
| T1 | No connectivity | Interactive tree: physical → IP → gateway → DNS |
| T2 | Slow network | Latency, traceroute, packet loss, QoS |
| T3 | IP / DHCP | DORA, IP conflicts, manual static IP |
| T4 | DNS | Cache flush, alternative DNS, nslookup, dig |
| T5 | HTTP / HTTPS | Error codes, curl, security headers |
| T6 | Security | nmap, netstat, tcpdump, firewall, logs |
| T7 | SSL certificates | Expiry, CA chain, Let's Encrypt, TLS 1.3 |
| T8 | WiFi and signal | dBm, channels, 2.4 vs 5 GHz, interference |
| T9 | Email / spam | SPF, DKIM, DMARC, blacklists, SMTP logs |
| T10 | Everyday problems | VPN, IP conflicts, site down, SSH |
| T11 | Practical security | Checklist: 2FA, passwords, 3-2-1 backups |
| T12 | Advanced commands | ping, traceroute, nmap, tcpdump, iperf3 |

---

## Technologies

- **Python 3.8+** — no external dependencies
- `ipaddress` — IPv4/IPv6 calculations
- `hashlib` — MD5, SHA-1, SHA-256, SHA-512, SHA-3, BLAKE2
- `socket` — real DNS resolution
- `hmac` — message authentication
- `base64` — encoding

---

## Author

**Jordi Yashua Contreras Blanch**  
Software Engineering · Computer Networking Fundamentals
