from .utils import (header, section, step, substep, result, sep, info,
                    callout, ask, pause, C, cc, menu)

# ── Módulo 2: Modelos OSI y TCP/IP ───────────────────────────────────────────

OSI_LAYERS = [
    {
        "n": 7, "name": "Aplicación", "tag": "Application",
        "pdu": "Datos / Mensaje",
        "desc": "La capa con la que interactúas directamente. Define cómo las aplicaciones acceden a la red.",
        "protocols": ["HTTP", "HTTPS", "FTP", "SMTP", "POP3", "IMAP", "DNS", "DHCP", "SSH", "Telnet", "SNMP", "NTP"],
        "devices": ["Computadoras, servidores, aplicaciones"],
        "example": "Cuando abres Chrome y escribes una URL, el browser usa HTTP/HTTPS (capa 7).",
        "color": C.BMAGENTA,
    },
    {
        "n": 6, "name": "Presentación", "tag": "Presentation",
        "pdu": "Datos",
        "desc": "Traduce, cifra y comprime los datos. Garantiza que el receptor entienda el formato del emisor.",
        "protocols": ["SSL/TLS", "JPEG", "MPEG", "ASCII", "Unicode", "XDR"],
        "devices": ["Codecs, cifrado TLS"],
        "example": "Cuando HTTPS cifra los datos con TLS antes de enviarlos, eso es capa 6.",
        "color": C.BBLUE,
    },
    {
        "n": 5, "name": "Sesión", "tag": "Session",
        "pdu": "Datos",
        "desc": "Establece, gestiona y termina sesiones (conversaciones) entre aplicaciones.",
        "protocols": ["NetBIOS", "RPC", "PPTP", "SIP"],
        "devices": ["Gateways de aplicación"],
        "example": "Cuando haces una videollamada de Zoom, la capa 5 mantiene la sesión activa.",
        "color": C.BCYAN,
    },
    {
        "n": 4, "name": "Transporte", "tag": "Transport",
        "pdu": "Segmento (TCP) / Datagrama (UDP)",
        "desc": "Entrega confiable de datos de extremo a extremo. Gestiona puertos, control de flujo y retransmisión.",
        "protocols": ["TCP", "UDP", "SCTP"],
        "devices": ["Firewalls de capa 4, load balancers"],
        "example": "TCP garantiza que todos los paquetes de una página web lleguen en orden. UDP prefiere velocidad (streaming).",
        "color": C.BGREEN,
    },
    {
        "n": 3, "name": "Red", "tag": "Network",
        "pdu": "Paquete",
        "desc": "Enrutamiento entre redes distintas. Usa direcciones IP para encontrar el camino al destino.",
        "protocols": ["IP (v4/v6)", "ICMP", "IGMP", "OSPF", "BGP", "RIP", "ARP"],
        "devices": ["Routers, switches capa 3"],
        "example": "Cuando haces ping, el router usa la dirección IP destino para decidir por qué interfaz enviar el paquete.",
        "color": C.BYELLOW,
    },
    {
        "n": 2, "name": "Enlace de datos", "tag": "Data Link",
        "pdu": "Frame (trama)",
        "desc": "Transferencia confiable dentro de la misma red local. Usa direcciones MAC. Detecta errores con CRC.",
        "protocols": ["Ethernet", "WiFi (802.11)", "PPP", "VLAN (802.1Q)", "STP", "ARP"],
        "devices": ["Switches, bridges, puntos de acceso WiFi"],
        "example": "El switch usa la tabla MAC para saber a qué puerto físico enviar una trama.",
        "color": C.BRED,
    },
    {
        "n": 1, "name": "Física", "tag": "Physical",
        "pdu": "Bits",
        "desc": "Transmisión de bits crudos sobre el medio físico. Define voltajes, frecuencias, conectores.",
        "protocols": ["Ethernet física", "USB", "Bluetooth", "DSL", "802.11 radio"],
        "devices": ["Hubs, repetidores, cables, fibra óptica, NIC"],
        "example": "Cuando enchufas un cable Ethernet, la capa 1 convierte los bits en señales eléctricas.",
        "color": C.DIM,
    },
]

TCPIP_LAYERS = [
    {
        "n": 4, "name": "Aplicación",
        "osi_equiv": "Capas 5, 6, 7 de OSI",
        "protocols": ["HTTP/S", "FTP", "SMTP", "DNS", "DHCP", "SSH"],
    },
    {
        "n": 3, "name": "Transporte",
        "osi_equiv": "Capa 4 de OSI",
        "protocols": ["TCP", "UDP"],
    },
    {
        "n": 2, "name": "Internet",
        "osi_equiv": "Capa 3 de OSI",
        "protocols": ["IP", "ICMP", "ARP"],
    },
    {
        "n": 1, "name": "Acceso a la red",
        "osi_equiv": "Capas 1 y 2 de OSI",
        "protocols": ["Ethernet", "WiFi", "PPP"],
    },
]


def mostrar_osi_completo():
    header("Modelo OSI — 7 Capas", "Módulo 2 · Arquitectura de red")
    for layer in OSI_LAYERS:
        titulo = f"Capa {layer['n']} · {layer['name']} ({layer['tag']})"
        print(f"\n  {cc(layer['color'] + C.BOLD, titulo)}")
        result("PDU",       layer["pdu"])
        result("Protocolos", ", ".join(layer["protocols"]))
        result("Dispositivos", ", ".join(layer["devices"]))
        info(layer["desc"])
        print(f"  {cc(C.DIM, '  Ejemplo: ' + layer['example'])}")
        print(f"  {cc(C.DIM, '-'*60)}")
    pause()


def ver_capa_detalle():
    header("Detalle de Capa OSI", "Módulo 2")
    print()
    for l in OSI_LAYERS:
        print(f"    {cc(C.BCYAN, str(l['n']) + '.')} {l['name']} ({l['tag']})")
    print()
    raw = ask("Número de capa (1–7)")
    try:
        n = int(raw)
        layer = next(l for l in OSI_LAYERS if l["n"] == n)
    except (ValueError, StopIteration):
        warn("Capa inválida.")
        pause()
        return

    header(f"Capa {layer['n']} · {layer['name']}", layer["desc"])

    step(1, "PDU (Protocol Data Unit)", f"En esta capa los datos se llaman: {layer['pdu']}")
    step(2, "Protocolos")
    for p in layer["protocols"]:
        print(f"      • {p}")
    step(3, "Dispositivos / Tecnologías")
    for d in layer["devices"]:
        print(f"      • {d}")
    step(4, "Ejemplo práctico", layer["example"])

    # Posición en la pila
    sep()
    info("Posición en la pila OSI:")
    for l in OSI_LAYERS:
        marker = f" ◄── {cc(C.BGREEN, 'AQUÍ')}" if l["n"] == layer["n"] else ""
        c = layer["color"] if l["n"] == layer["n"] else C.DIM
        nombre_capa = f"Capa {l['n']} · {l['name']}"
        print(f"    {cc(c, nombre_capa)}{marker}")
    pause()


def comparar_osi_tcpip():
    header("OSI vs TCP/IP", "Módulo 2 · Comparación de modelos")
    info("OSI tiene 7 capas (teórico/referencia). TCP/IP tiene 4 (el que realmente se usa).")
    sep()

    print(f"  {'OSI (7 capas)':<35} {'TCP/IP (4 capas)'}")
    print(f"  {'─'*33} {'─'*33}")
    osi_to_tcpip = {
        7: "Aplicación", 6: "Aplicación", 5: "Aplicación",
        4: "Transporte",
        3: "Internet",
        2: "Acceso a la red", 1: "Acceso a la red",
    }
    colors = {
        "Aplicación": C.BMAGENTA, "Transporte": C.BGREEN,
        "Internet": C.BYELLOW, "Acceso a la red": C.BRED,
    }
    for l in OSI_LAYERS:
        tc = osi_to_tcpip[l["n"]]
        etiqueta = f"[{l['n']}] {l['name']}"
        print(f"  {cc(l['color'], etiqueta): <45} {cc(colors[tc], tc)}")

    sep()
    callout("info", "¿Por qué existe OSI si usamos TCP/IP?",
            "OSI es el modelo teórico universal que se usa para ENSEÑAR y DIAGNOSTICAR.\n"
            "TCP/IP es el modelo práctico que realmente implementa Internet.\n"
            "Cuando un técnico dice 'problema de capa 3', está usando la nomenclatura OSI.")
    pause()


def encapsulacion():
    header("Proceso de Encapsulación", "Módulo 2 · Cómo viajan los datos")
    info("Cuando envías datos, cada capa agrega su propia cabecera (encapsulación).")
    info("Cuando los recibes, cada capa quita su cabecera (desencapsulación).")
    sep()

    steps = [
        ("Aplicación (7)", "Datos del usuario: 'GET /index.html HTTP/1.1'",
         "El browser genera la solicitud HTTP."),
        ("Transporte (4)", "[TCP Header | Datos HTTP]",
         "TCP agrega: puerto origen, puerto destino, número de secuencia."),
        ("Red (3)", "[IP Header | TCP Header | Datos HTTP]",
         "IP agrega: IP origen (192.168.1.10), IP destino (93.184.216.34)."),
        ("Enlace (2)", "[Eth Header | IP Header | TCP | Datos | CRC]",
         "Ethernet agrega: MAC origen, MAC destino, verificación CRC."),
        ("Física (1)", "11001010 01101100 10110100 ... (bits)",
         "Los bytes se convierten en señales eléctricas / fotones de luz."),
    ]

    for i, (capa, pdu, desc) in enumerate(steps, 1):
        step(i, capa, desc)
        print(f"      {cc(C.BYELLOW, pdu)}")
        print()

    callout("info", "Analogía postal",
            "Escribe una carta (datos) → la metes en un sobre (TCP) → escribes la dirección (IP)\n"
            "→ el cartero la pone en un camión con la ruta (Ethernet) → el camión rueda (física).")
    pause()


def run():
    while True:
        opts = [
            "Ver todas las capas OSI (resumen completo)",
            "Ver detalle de una capa específica (1–7)",
            "Comparar OSI vs TCP/IP",
            "Proceso de encapsulación paso a paso",
        ]
        choice = menu("Módulo 2 · Modelos OSI y TCP/IP", opts)
        if choice == -1:
            break
        [mostrar_osi_completo, ver_capa_detalle, comparar_osi_tcpip, encapsulacion][choice]()
