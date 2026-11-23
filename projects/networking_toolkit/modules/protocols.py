import socket
from .utils import (header, section, step, result, sep, info,
                    warn, callout, ask, pause, C, cc, menu)

# ── Module 3: Communication protocols ─────────────────────────────────────────

PROTOCOLS = {
    "HTTP": {
        "port": 80, "transport": "TCP", "layer": 7,
        "full_name": "HyperText Transfer Protocol",
        "desc": "The foundation of the Web. Transfers pages, images and APIs. Not encrypted.",
        "steps": [
            ("Client opens TCP", "The browser opens a TCP connection to the server on port 80."),
            ("GET / HTTP/1.1", "The client sends a request. Example: GET /index.html HTTP/1.1\nHost: www.example.com"),
            ("Server responds", "The server replies with a status code + content.\nExample: HTTP/1.1 200 OK\nContent-Type: text/html"),
            ("Data sent", "The response body contains the HTML, images, etc."),
            ("Connection closed", "HTTP/1.0 closes when done. HTTP/1.1 uses keep-alive."),
        ],
        "codes": {"200": "OK", "301": "Moved Permanently", "404": "Not Found",
                  "403": "Forbidden", "500": "Internal Server Error", "503": "Service Unavailable"},
        "color": C.BBLUE,
    },
    "HTTPS": {
        "port": 443, "transport": "TCP", "layer": 7,
        "full_name": "HTTP Secure (HTTP + TLS)",
        "desc": "HTTP encrypted with TLS. Guarantees confidentiality and integrity. Essential today.",
        "steps": [
            ("TCP handshake", "The client connects to port 443."),
            ("TLS ClientHello", "The client sends the TLS versions and cipher suites it supports, plus a random number."),
            ("TLS ServerHello", "The server picks the cipher suite and sends its X.509 certificate."),
            ("Certificate check", "The client verifies the certificate was signed by a trusted CA and the name matches."),
            ("Key exchange", "A shared session key is negotiated (for example with ECDHE)."),
            ("Encrypted channel", "From here on, all HTTP traffic is encrypted with AES."),
        ],
        "color": C.BGREEN,
    },
    "DNS": {
        "port": 53, "transport": "UDP/TCP", "layer": 7,
        "full_name": "Domain Name System",
        "desc": "Translates domain names (google.com) into IP addresses. The Internet's phone book.",
        "steps": [
            ("Local cache", "The OS checks whether it already has the answer cached. If so → done."),
            ("Recursive resolver", "The OS asks the ISP's resolver (or 8.8.8.8, 1.1.1.1, etc.)."),
            ("Root server", "The resolver asks a root server: 'who handles .com?'"),
            ("TLD server", "The root server replies with the IP of the .com TLD server."),
            ("Authoritative server", "The TLD says: 'for google.com, ask ns1.google.com'."),
            ("Final answer", "The authoritative server replies with google.com's IP (142.250.x.x)."),
            ("Cache and deliver", "The resolver caches the answer (TTL) and returns it to the client."),
        ],
        "record_types": {
            "A": "Maps domain → IPv4",
            "AAAA": "Maps domain → IPv6",
            "MX": "The domain's mail server",
            "CNAME": "Alias for another name (canonical name)",
            "TXT": "Arbitrary text (SPF, DKIM, verifications)",
            "NS": "The domain's name servers",
            "PTR": "Reverse: IP → name (rDNS)",
            "SOA": "Start of Authority — zone parameters",
        },
        "color": C.BYELLOW,
    },
    "DHCP": {
        "port": "67 (srv) / 68 (cli)", "transport": "UDP", "layer": 7,
        "full_name": "Dynamic Host Configuration Protocol",
        "desc": "Automatically assigns IP, subnet mask, gateway and DNS to devices on the network.",
        "steps": [
            ("DISCOVER", "The client broadcasts: 'Is there a DHCP server? I need an IP.' (255.255.255.255)"),
            ("OFFER", "The DHCP server replies with an available IP: 'I can give you 192.168.1.15/24'."),
            ("REQUEST", "The client accepts the offer: 'Yes, I want 192.168.1.15'."),
            ("ACK", "The server confirms: 'Assigned. Valid for 24 hours (lease time)'."),
        ],
        "mnemonic": "DORA: Discover → Offer → Request → ACK",
        "color": C.BCYAN,
    },
    "FTP": {
        "port": "21 (control) / 20 (data)", "transport": "TCP", "layer": 7,
        "full_name": "File Transfer Protocol",
        "desc": "File transfer. Not encrypted (use SFTP or FTPS instead). Two channels: control and data.",
        "steps": [
            ("Connect to port 21", "The client connects to the control channel."),
            ("Authentication", "USER <name> / PASS <password> — in plain text."),
            ("Commands", "LIST (list), RETR (download), STOR (upload), CWD (change directory)."),
            ("Data channel", "Port 20 (active mode) or an ephemeral port (passive mode) carries the data."),
        ],
        "color": C.DIM,
    },
    "SMTP": {
        "port": "25 / 587 (submission) / 465 (SSL)", "transport": "TCP", "layer": 7,
        "full_name": "Simple Mail Transfer Protocol",
        "desc": "Sends email between servers (and from client to server).",
        "steps": [
            ("TCP connection", "The client connects to the SMTP server on port 587."),
            ("EHLO", "The client introduces itself: EHLO mydomain.com"),
            ("AUTH LOGIN", "Authenticates with a username and password in base64."),
            ("MAIL FROM / RCPT TO", "Sets the sender and the recipient."),
            ("DATA", "The client sends the message (headers + body), ending with '.'."),
            ("QUIT", "Closes the session."),
        ],
        "color": C.BMAGENTA,
    },
    "SSH": {
        "port": 22, "transport": "TCP", "layer": 7,
        "full_name": "Secure Shell",
        "desc": "Secure (encrypted) remote access. Replaced Telnet. Uses asymmetric cryptography.",
        "steps": [
            ("TCP to port 22", "The client starts the connection."),
            ("Version exchange", "Both sides negotiate the SSH version (SSH-2.0)."),
            ("Key exchange", "Diffie-Hellman is used to create an encrypted session."),
            ("Authentication", "With a password (less secure) or a public/private key pair."),
            ("Interactive shell", "The user gets encrypted remote access to the server."),
        ],
        "color": C.BGREEN,
    },
    "TCP": {
        "port": "N/A", "transport": "TCP", "layer": 4,
        "full_name": "Transmission Control Protocol",
        "desc": "Reliable transport protocol. Guarantees delivery and order with no duplicates. Connection-based.",
        "steps": [
            ("SYN →", "The client sends SYN (synchronize) with a random sequence number (ISN)."),
            ("← SYN-ACK", "The server replies with SYN+ACK and its own ISN."),
            ("ACK →", "The client confirms with ACK. The connection is established (3-way handshake)."),
            ("Transfer", "Data flows with a sliding window and retransmission when packets are lost."),
            ("FIN / FIN-ACK", "Orderly shutdown with 4 messages (FIN, ACK, FIN, ACK)."),
        ],
        "color": C.BYELLOW,
    },
    "UDP": {
        "port": "N/A", "transport": "UDP", "layer": 4,
        "full_name": "User Datagram Protocol",
        "desc": "Connectionless transport protocol. Fast but no guarantees. Ideal for streaming, gaming and DNS.",
        "steps": [
            ("No handshake", "UDP sends data right away without setting up a connection."),
            ("Independent datagrams", "Each datagram stands alone. They may arrive out of order or get lost."),
            ("No retransmission", "If a packet is lost, UDP doesn't recover it. The application must handle it."),
        ],
        "color": C.BRED,
    },
}


def show_protocol():
    header("Protocol Reference", "Module 3 · Communication")
    section("Available protocols")
    for name, p in PROTOCOLS.items():
        print(f"  {cc(p['color'], f'{name:<10}')} Port {str(p['port']):<22} {p['full_name']}")
    print()
    raw = ask("Protocol name (e.g. HTTP, DNS, DHCP)")
    name = raw.upper().strip()
    if name not in PROTOCOLS:
        warn(f"'{name}' not found. Options: {', '.join(PROTOCOLS.keys())}")
        pause()
        return

    p = PROTOCOLS[name]
    header(f"{name} · {p['full_name']}", p["desc"])

    result("Port",       str(p["port"]))
    result("Transport",  p["transport"])
    result("OSI layer",  str(p["layer"]))
    sep()

    section("How it works, step by step")
    for i, (title, text) in enumerate(p["steps"], 1):
        step(i, title, text)

    if "mnemonic" in p:
        callout("info", "Mnemonic", p["mnemonic"])

    if "codes" in p:
        sep()
        section("HTTP status codes")
        for code, meaning in p["codes"].items():
            result(code, meaning)

    if "record_types" in p:
        sep()
        section("DNS record types")
        for rtype, meaning in p["record_types"].items():
            result(rtype, meaning)

    pause()


def find_by_port():
    header("Find Protocol by Port", "Module 3")
    raw = ask("Port number")
    try:
        port = int(raw)
    except ValueError:
        warn("Please enter a number.")
        pause()
        return

    found = [(n, p) for n, p in PROTOCOLS.items()
             if str(port) in str(p["port"])]

    if not found:
        # Fall back to the operating system's service list
        try:
            svc = socket.getservbyport(port)
            info(f"Port {port}: {svc} (source: operating system)")
        except OSError:
            warn(f"Port {port} is not in the database.")
    else:
        for name, p in found:
            result(name, f"{p['full_name']} — {p['desc']}")

    pause()


def compare_tcp_udp():
    header("TCP vs. UDP", "Module 3 · Transport protocols")
    sep()
    print(f"  {cc(C.BOLD, 'Feature'):<30} {cc(C.BYELLOW + C.BOLD, 'TCP'):<40} {cc(C.BRED + C.BOLD, 'UDP')}")
    print(f"  {'─'*28} {'─'*32} {'─'*32}")

    comparisons = [
        ("Connection",       "Yes (3-way handshake)",    "No (connectionless)"),
        ("Reliability",      "Guaranteed (ACKs)",        "Not guaranteed"),
        ("Packet order",     "Yes (sequence numbers)",   "Not guaranteed"),
        ("Speed",            "Slower (overhead)",        "Faster"),
        ("Flow control",     "Yes (sliding window)",     "No"),
        ("Used for",         "HTTP, SSH, FTP, SMTP",     "DNS, streaming, gaming, VoIP"),
        ("Header overhead",  "20 bytes min.",            "8 bytes"),
    ]

    for feature, tcp, udp in comparisons:
        print(f"  {feature:<30} {cc(C.BYELLOW, tcp):<44} {cc(C.BRED, udp)}")

    callout("info", "Rule of thumb",
            "If it must arrive COMPLETE and IN ORDER: TCP.\n"
            "If you need SPEED and losing a packet is acceptable: UDP.")
    pause()


def transmission_types():
    header("Unicast · Multicast · Broadcast", "Module 3 · Transmission types")
    step(1, "Unicast (1 → 1)", "One sender, one specific receiver.\nE.g. loading a web page: the server sends the data only to you.")
    step(2, "Multicast (1 → group)", "One sender, many subscribed receivers.\nE.g. TV streaming: the server sends ONE copy and routers replicate it.")
    step(3, "Broadcast (1 → everyone)", "The message reaches EVERY device on the local network.\nE.g. DHCP Discover — the device shouts 'Is there a DHCP server?' to the whole network.")
    sep()
    print(f"  {'Type':<15} {'Destination':<28} {'Example'}")
    print(f"  {'─'*13} {'─'*26} {'─'*30}")
    rows = [
        ("Unicast",    "One specific IP",              "HTTP request"),
        ("Multicast",  "Group (224.x.x.x)",            "Video streaming"),
        ("Broadcast",  "255.255.255.255 (whole LAN)",  "DHCP Discover / ARP"),
        ("Anycast",    "Nearest member of a group",    "DNS root servers, CDNs"),
    ]
    for t, d, e in rows:
        print(f"  {cc(C.BCYAN, t):<23} {d:<28} {cc(C.DIM, e)}")
    pause()


def run():
    while True:
        opts = [
            "Protocol details (HTTP, HTTPS, DNS, DHCP, SSH, TCP, UDP…)",
            "Find a protocol by port number",
            "Compare TCP vs. UDP",
            "Unicast vs. Multicast vs. Broadcast",
        ]
        choice = menu("Module 3 · Communication Protocols", opts)
        if choice == -1:
            break
        [show_protocol, find_by_port, compare_tcp_udp, transmission_types][choice]()
