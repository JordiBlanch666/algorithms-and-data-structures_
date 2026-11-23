from .utils import (header, step, result, sep, info, warn,
                    callout, ask, pause, C, cc, menu)

# ── Module 2: OSI and TCP/IP models ───────────────────────────────────────────

OSI_LAYERS = [
    {
        "n": 7, "name": "Application",
        "pdu": "Data / Message",
        "desc": "The layer you interact with directly. Defines how applications access the network.",
        "protocols": ["HTTP", "HTTPS", "FTP", "SMTP", "POP3", "IMAP", "DNS", "DHCP", "SSH", "Telnet", "SNMP", "NTP"],
        "devices": ["Computers, servers, applications"],
        "example": "When you open Chrome and type a URL, the browser uses HTTP/HTTPS (layer 7).",
        "color": C.BMAGENTA,
    },
    {
        "n": 6, "name": "Presentation",
        "pdu": "Data",
        "desc": "Translates, encrypts and compresses data so the receiver understands the sender's format.",
        "protocols": ["SSL/TLS", "JPEG", "MPEG", "ASCII", "Unicode", "XDR"],
        "devices": ["Codecs, TLS encryption"],
        "example": "When HTTPS encrypts data with TLS before sending it, that's layer 6.",
        "color": C.BBLUE,
    },
    {
        "n": 5, "name": "Session",
        "pdu": "Data",
        "desc": "Establishes, manages and terminates sessions (conversations) between applications.",
        "protocols": ["NetBIOS", "RPC", "PPTP", "SIP"],
        "devices": ["Application gateways"],
        "example": "During a Zoom video call, layer 5 keeps the session alive.",
        "color": C.BCYAN,
    },
    {
        "n": 4, "name": "Transport",
        "pdu": "Segment (TCP) / Datagram (UDP)",
        "desc": "Reliable end-to-end delivery. Handles ports, flow control and retransmission.",
        "protocols": ["TCP", "UDP", "SCTP"],
        "devices": ["Layer 4 firewalls, load balancers"],
        "example": "TCP guarantees every packet of a web page arrives in order. UDP prefers speed (streaming).",
        "color": C.BGREEN,
    },
    {
        "n": 3, "name": "Network",
        "pdu": "Packet",
        "desc": "Routing between different networks. Uses IP addresses to find the path to the destination.",
        "protocols": ["IP (v4/v6)", "ICMP", "IGMP", "OSPF", "BGP", "RIP", "ARP"],
        "devices": ["Routers, layer 3 switches"],
        "example": "When you ping, the router uses the destination IP to choose which interface to send the packet out of.",
        "color": C.BYELLOW,
    },
    {
        "n": 2, "name": "Data Link",
        "pdu": "Frame",
        "desc": "Reliable transfer within the same local network. Uses MAC addresses and detects errors with CRC.",
        "protocols": ["Ethernet", "Wi-Fi (802.11)", "PPP", "VLAN (802.1Q)", "STP", "ARP"],
        "devices": ["Switches, bridges, Wi-Fi access points"],
        "example": "A switch uses its MAC table to know which physical port to send a frame to.",
        "color": C.BRED,
    },
    {
        "n": 1, "name": "Physical",
        "pdu": "Bits",
        "desc": "Transmits raw bits over the physical medium. Defines voltages, frequencies and connectors.",
        "protocols": ["Physical Ethernet", "USB", "Bluetooth", "DSL", "802.11 radio"],
        "devices": ["Hubs, repeaters, cables, fiber optics, NICs"],
        "example": "When you plug in an Ethernet cable, layer 1 turns bits into electrical signals.",
        "color": C.DIM,
    },
]

TCPIP_LAYERS = [
    {
        "n": 4, "name": "Application",
        "osi_equiv": "OSI layers 5, 6, 7",
        "protocols": ["HTTP/S", "FTP", "SMTP", "DNS", "DHCP", "SSH"],
    },
    {
        "n": 3, "name": "Transport",
        "osi_equiv": "OSI layer 4",
        "protocols": ["TCP", "UDP"],
    },
    {
        "n": 2, "name": "Internet",
        "osi_equiv": "OSI layer 3",
        "protocols": ["IP", "ICMP", "ARP"],
    },
    {
        "n": 1, "name": "Network Access",
        "osi_equiv": "OSI layers 1 and 2",
        "protocols": ["Ethernet", "Wi-Fi", "PPP"],
    },
]


def show_full_osi():
    header("OSI Model — 7 Layers", "Module 2 · Network architecture")
    for layer in OSI_LAYERS:
        title = f"Layer {layer['n']} · {layer['name']}"
        print(f"\n  {cc(layer['color'] + C.BOLD, title)}")
        result("PDU",       layer["pdu"])
        result("Protocols", ", ".join(layer["protocols"]))
        result("Devices",   ", ".join(layer["devices"]))
        info(layer["desc"])
        print(f"  {cc(C.DIM, '  Example: ' + layer['example'])}")
        print(f"  {cc(C.DIM, '-'*60)}")
    pause()


def layer_detail():
    header("OSI Layer Detail", "Module 2")
    print()
    for l in OSI_LAYERS:
        print(f"    {cc(C.BCYAN, str(l['n']) + '.')} {l['name']}")
    print()
    raw = ask("Layer number (1–7)")
    try:
        n = int(raw)
        layer = next(l for l in OSI_LAYERS if l["n"] == n)
    except (ValueError, StopIteration):
        warn("Invalid layer.")
        pause()
        return

    header(f"Layer {layer['n']} · {layer['name']}", layer["desc"])

    step(1, "PDU (Protocol Data Unit)", f"At this layer the data is called: {layer['pdu']}")
    step(2, "Protocols")
    for p in layer["protocols"]:
        print(f"      • {p}")
    step(3, "Devices / Technologies")
    for d in layer["devices"]:
        print(f"      • {d}")
    step(4, "Practical example", layer["example"])

    # Position in the stack
    sep()
    info("Position in the OSI stack:")
    for l in OSI_LAYERS:
        marker = f" ◄── {cc(C.BGREEN, 'HERE')}" if l["n"] == layer["n"] else ""
        c = layer["color"] if l["n"] == layer["n"] else C.DIM
        layer_name = f"Layer {l['n']} · {l['name']}"
        print(f"    {cc(c, layer_name)}{marker}")
    pause()


def compare_osi_tcpip():
    header("OSI vs. TCP/IP", "Module 2 · Model comparison")
    info("OSI has 7 layers (theory/reference). TCP/IP has 4 (the one actually used).")
    sep()

    print(f"  {'OSI (7 layers)':<35} {'TCP/IP (4 layers)'}")
    print(f"  {'─'*33} {'─'*33}")
    osi_to_tcpip = {
        7: "Application", 6: "Application", 5: "Application",
        4: "Transport",
        3: "Internet",
        2: "Network Access", 1: "Network Access",
    }
    colors = {
        "Application": C.BMAGENTA, "Transport": C.BGREEN,
        "Internet": C.BYELLOW, "Network Access": C.BRED,
    }
    for l in OSI_LAYERS:
        tc = osi_to_tcpip[l["n"]]
        label = f"[{l['n']}] {l['name']}"
        print(f"  {cc(l['color'], label): <45} {cc(colors[tc], tc)}")

    sep()
    callout("info", "Why does OSI exist if we use TCP/IP?",
            "OSI is the universal theoretical model used to TEACH and TROUBLESHOOT.\n"
            "TCP/IP is the practical model the Internet actually implements.\n"
            "When a technician says 'it's a layer 3 problem', they're using OSI terms.")
    pause()


def encapsulation():
    header("Encapsulation Process", "Module 2 · How data travels")
    info("When you send data, each layer adds its own header (encapsulation).")
    info("When you receive it, each layer removes its header (decapsulation).")
    sep()

    steps = [
        ("Application (7)", "User data: 'GET /index.html HTTP/1.1'",
         "The browser builds the HTTP request."),
        ("Transport (4)", "[TCP Header | HTTP Data]",
         "TCP adds: source port, destination port, sequence number."),
        ("Network (3)", "[IP Header | TCP Header | HTTP Data]",
         "IP adds: source IP (192.168.1.10), destination IP (93.184.216.34)."),
        ("Data Link (2)", "[Eth Header | IP Header | TCP | Data | CRC]",
         "Ethernet adds: source MAC, destination MAC, CRC check."),
        ("Physical (1)", "11001010 01101100 10110100 ... (bits)",
         "Bytes become electrical signals / pulses of light."),
    ]

    for i, (layer, pdu, desc) in enumerate(steps, 1):
        step(i, layer, desc)
        print(f"      {cc(C.BYELLOW, pdu)}")
        print()

    callout("info", "Postal analogy",
            "Write a letter (data) → put it in an envelope (TCP) → write the address (IP)\n"
            "→ the mail carrier loads it on a truck with a route (Ethernet) → the truck drives (physical).")
    pause()


def run():
    while True:
        opts = [
            "Show all OSI layers (full summary)",
            "Show details of one layer (1–7)",
            "Compare OSI vs. TCP/IP",
            "Encapsulation process step by step",
        ]
        choice = menu("Module 2 · OSI and TCP/IP Models", opts)
        if choice == -1:
            break
        [show_full_osi, layer_detail, compare_osi_tcpip, encapsulation][choice]()
