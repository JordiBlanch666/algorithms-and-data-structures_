from .utils import (header, section, step, result, sep,
                    callout, pause, C, cc, menu)

# ── Module 6: Cybersecurity ───────────────────────────────────────────────────

def cia_triad():
    header("CIA Triad", "Module 6 · The three pillars of security")
    step(1, "Confidentiality",
         "Only authorized people can see the information.\n"
         "Protected by: encryption (TLS, AES), access control (RBAC), MFA authentication.")
    step(2, "Integrity",
         "Data has not been modified without authorization.\n"
         "Protected by: hashing (SHA-256), digital signatures (RSA/ECDSA), checksums.")
    step(3, "Availability",
         "Systems are accessible when they're needed.\n"
         "Protected by: redundancy, backups, anti-DDoS, clustering, monitoring.")

    sep()
    section("Examples of failure in each pillar")
    examples = [
        ("Confidentiality", "Someone intercepts HTTP traffic and reads your passwords.\n"
                            "An employee opens HR files without permission."),
        ("Integrity",       "A MITM attacker alters a file while it's in transit.\n"
                            "A virus modifies a system executable."),
        ("Availability",    "A DDoS attack floods the server and makes it unreachable.\n"
                            "A hard drive fails and there is no backup."),
    ]
    for pillar, example in examples:
        result(pillar, "")
        print(f"    {cc(C.DIM, example)}")
        print()
    pause()


def attack_types():
    header("Common Attack Types", "Module 6 · Cybersecurity")

    attacks = [
        ("Phishing", "Fake emails or websites designed to steal credentials.\n"
                     "Variants: spear phishing (targeted), whaling (executives), smishing (SMS).",
         "Check URLs, don't click suspicious links, use MFA."),
        ("MITM (Man in the Middle)", "The attacker sits between two parties and can read or alter the data.\n"
                                     "Example: ARP spoofing on public Wi-Fi.",
         "Use HTTPS+HSTS and valid certificates; avoid public Wi-Fi without a VPN."),
        ("DDoS (Distributed Denial of Service)", "Flooding a server with traffic until it's overwhelmed and goes down.\n"
                                                 "Botnet: thousands of compromised devices attacking at once.",
         "CDN, rate limiting, anti-DDoS services (Cloudflare, AWS Shield)."),
        ("SQL Injection", "Injecting SQL code into form fields to manipulate the database.\n"
                          "' OR '1'='1 — the classic SQL injection string.",
         "Prepared statements, input validation, a WAF."),
        ("XSS (Cross-Site Scripting)", "Injecting malicious JavaScript into a web page.\n"
                                       "It can steal session cookies or redirect the user.",
         "Escape HTML, Content Security Policy (CSP), HttpOnly cookies."),
        ("Brute force / Dictionary", "Trying thousands of passwords until one works.\n"
                                     "Dictionary: a list of common passwords (rockyou.txt has 14M).",
         "Long passwords, MFA, lockout after failed attempts, CAPTCHA."),
        ("Ransomware", "Malware that encrypts your files and demands a ransom to decrypt them.\n"
                       "Spreads through phishing, exposed RDP and unpatched vulnerabilities.",
         "Offline backups, don't open suspicious attachments, keep systems patched."),
        ("ARP Spoofing", "Sending fake ARP replies so the attacker's MAC is linked to the gateway's IP.\n"
                         "Result: all traffic flows through the attacker (MITM).",
         "Dynamic ARP inspection on switches, VPNs, encrypted traffic."),
    ]

    for name, desc, defense in attacks:
        sep()
        print(f"  {cc(C.BRED + C.BOLD, '◉ ' + name)}")
        print(f"  {cc(C.DIM, desc)}")
        print(f"  {cc(C.BGREEN, '  Defense:')} {cc(C.DIM, defense)}")

    pause()


def https_explained():
    header("How does HTTPS protect your data?", "Module 6 · TLS handshake step by step")
    step(1, "TCP handshake",   "A TCP connection to port 443 is established (SYN, SYN-ACK, ACK).")
    step(2, "ClientHello",
         "The client sends:\n"
         "  • Supported TLS versions (TLS 1.2, TLS 1.3)\n"
         "  • A list of cipher suites (e.g. TLS_AES_256_GCM_SHA384)\n"
         "  • A client random number")
    step(3, "ServerHello",
         "The server replies with:\n"
         "  • The chosen cipher suite\n"
         "  • A server random number\n"
         "  • Its X.509 certificate signed by a CA")
    step(4, "Certificate verification",
         "The client checks that:\n"
         "  a) The CA that signed the certificate is trusted (it's in the OS trust store)\n"
         "  b) The certificate's CN/SAN matches the domain being visited\n"
         "  c) The certificate isn't expired or revoked (OCSP)")
    step(5, "Key exchange",
         "TLS 1.3 uses ECDHE (Elliptic Curve Diffie-Hellman Ephemeral):\n"
         "  • Both sides independently compute a shared secret\n"
         "  • Nobody in between can compute it (only the two endpoints)\n"
         "  • 'Ephemeral' = a new key per session → Forward Secrecy")
    step(6, "Session key derivation",
         "From the shared secret + the random numbers they derive:\n"
         "  • A client→server encryption key (AES-256)\n"
         "  • A server→client encryption key (AES-256)\n"
         "  • Integrity keys (MAC keys)")
    step(7, "Secure channel",
         "From here on, all data is encrypted with AES-GCM.\n"
         "  • AES encrypts the data (confidentiality)\n"
         "  • GCM verifies it wasn't altered (integrity)\n"
         "  • ECDHE guarantees Forward Secrecy")

    callout("info", "Forward Secrecy",
            "Even if someone later obtains the server's private key,\n"
            "they CANNOT decrypt past sessions — because session keys\n"
            "are ephemeral and unique to each connection.")
    pause()


def vlans_and_segmentation():
    header("VLANs and Network Segmentation", "Module 5 · Layer 2 security")
    step(1, "What is a VLAN?",
         "Virtual LAN: logically divides one physical network into several isolated networks.\n"
         "Devices in different VLANs can't see each other without a router.")
    step(2, "Why use VLANs?",
         "• Security: keep the accounting VLAN separate from the production VLAN\n"
         "• Performance: smaller broadcast domains\n"
         "• Management: group devices logically without moving cables")
    step(3, "Management VLAN",
         "Always create a separate VLAN to manage switches and routers.\n"
         "Never manage network devices from the user VLAN.")
    step(4, "Trunk vs. access ports",
         "Access port: connects one end device. Carries a single VLAN.\n"
         "Trunk port: connects switches to each other. Carries several VLANs (802.1Q tagging).")
    step(5, "Inter-VLAN routing",
         "Two VLANs need a router or layer 3 switch to talk to each other.\n"
         "Router-on-a-stick: one router with sub-interfaces, one per VLAN.")

    callout("info", "Segmentation as a defense",
            "If an attacker compromises a device on the guest VLAN,\n"
            "they can't reach the servers on the production VLAN.\n"
            "The principle of least privilege applied to the network.")
    pause()


def run():
    while True:
        opts = [
            "CIA triad (Confidentiality, Integrity, Availability)",
            "Common attacks (Phishing, MITM, DDoS, SQLi, XSS, Ransomware...)",
            "How does HTTPS protect your data? (TLS handshake step by step)",
            "VLANs and network segmentation",
        ]
        choice = menu("Module 6 · Cybersecurity", opts)
        if choice == -1:
            break
        [cia_triad, attack_types, https_explained, vlans_and_segmentation][choice]()
