import socket
from .utils import (header, section, step, substep, result, sep, info,
                    warn, ok, callout, ask, pause, C, cc, menu)

# ── Módulo 3: Protocolos de comunicación ─────────────────────────────────────

PROTOCOLS = {
    "HTTP": {
        "port": 80, "transport": "TCP", "layer": 7,
        "full_name": "HyperText Transfer Protocol",
        "desc": "El protocolo base de la Web. Transfiere páginas, imágenes y APIs. No cifrado.",
        "steps": [
            ("Cliente abre TCP", "El browser establece una conexión TCP al servidor en el puerto 80."),
            ("GET / HTTP/1.1", "El cliente envía una solicitud. Ejemplo: GET /index.html HTTP/1.1\\nHost: www.ejemplo.com"),
            ("Servidor responde", "El servidor responde con código de estado + contenido.\\nEjemplo: HTTP/1.1 200 OK\\nContent-Type: text/html"),
            ("Datos enviados", "El cuerpo de la respuesta contiene el HTML, imágenes, etc."),
            ("Conexión cerrada", "Con HTTP/1.0 se cierra al terminar. HTTP/1.1 usa keep-alive."),
        ],
        "codes": {"200": "OK", "301": "Moved Permanently", "404": "Not Found",
                  "403": "Forbidden", "500": "Internal Server Error", "503": "Service Unavailable"},
        "color": C.BBLUE,
    },
    "HTTPS": {
        "port": 443, "transport": "TCP", "layer": 7,
        "full_name": "HTTP Secure (HTTP + TLS)",
        "desc": "HTTP cifrado con TLS. Garantiza confidencialidad e integridad. Indispensable hoy.",
        "steps": [
            ("TCP Handshake", "El cliente conecta al puerto 443."),
            ("TLS ClientHello", "El cliente envía versiones TLS soportadas, suites de cifrado y un número aleatorio."),
            ("TLS ServerHello", "El servidor elige la suite de cifrado y envía su certificado X.509."),
            ("Verificación cert", "El cliente verifica que el certificado lo firmó una CA de confianza y que el CN coincide."),
            ("Key Exchange", "Se negocia una clave de sesión compartida (con ECDHE, por ejemplo)."),
            ("Canal cifrado", "A partir de aquí toda la comunicación HTTP va cifrada con AES."),
        ],
        "color": C.BGREEN,
    },
    "DNS": {
        "port": 53, "transport": "UDP/TCP", "layer": 7,
        "full_name": "Domain Name System",
        "desc": "Traduce nombres de dominio (google.com) a direcciones IP. El directorio telefónico de Internet.",
        "steps": [
            ("Caché local", "El SO verifica si ya tiene la respuesta en caché. Si sí → listo."),
            ("Resolver recursivo", "El SO consulta al resolver del ISP (o 8.8.8.8, 1.1.1.1, etc.)."),
            ("Root server", "El resolver pregunta al servidor raíz: '¿quién maneja .com?'"),
            ("TLD server", "El root server responde con la IP del servidor TLD (.com)."),
            ("Authoritative server", "El TLD dice: 'para google.com pregunta a ns1.google.com'."),
            ("Respuesta final", "El authoritative server responde con la IP de google.com (142.250.x.x)."),
            ("Caché y entrega", "El resolver guarda la respuesta (TTL) y se la da al cliente."),
        ],
        "record_types": {
            "A": "Mapea dominio → IPv4",
            "AAAA": "Mapea dominio → IPv6",
            "MX": "Servidor de correo del dominio",
            "CNAME": "Alias de otro nombre (canonical name)",
            "TXT": "Texto arbitrario (SPF, DKIM, verificaciones)",
            "NS": "Servidores de nombres del dominio",
            "PTR": "Reverso: IP → nombre (rDNS)",
            "SOA": "Start of Authority — parámetros de la zona",
        },
        "color": C.BYELLOW,
    },
    "DHCP": {
        "port": "67 (srv) / 68 (cli)", "transport": "UDP", "layer": 7,
        "full_name": "Dynamic Host Configuration Protocol",
        "desc": "Asigna automáticamente IP, máscara, gateway y DNS a los dispositivos de la red.",
        "steps": [
            ("DISCOVER", "El cliente manda un broadcast: '¿Hay algún servidor DHCP? Necesito IP.' (255.255.255.255)"),
            ("OFFER", "El servidor DHCP responde con una IP disponible: 'Te ofrezco 192.168.1.15/24'."),
            ("REQUEST", "El cliente acepta la oferta: 'Sí, quiero la 192.168.1.15'."),
            ("ACK", "El servidor confirma: 'Asignada. Válida por 24 horas (lease time)'."),
        ],
        "mnemonico": "DORA: Discover → Offer → Request → ACK",
        "color": C.BCYAN,
    },
    "FTP": {
        "port": "21 (control) / 20 (datos)", "transport": "TCP", "layer": 7,
        "full_name": "File Transfer Protocol",
        "desc": "Transferencia de archivos. Sin cifrado (usa SFTP o FTPS en su lugar). Dos canales: control y datos.",
        "steps": [
            ("Conexión al puerto 21", "El cliente conecta al canal de control."),
            ("Autenticación", "USER <nombre> / PASS <contraseña> — en texto plano."),
            ("Comandos", "LIST (listar), RETR (descargar), STOR (subir), CWD (cambiar dir)."),
            ("Canal de datos", "Puerto 20 (modo activo) o puerto efímero (modo pasivo) para los datos."),
        ],
        "color": C.DIM,
    },
    "SMTP": {
        "port": "25 / 587 (submission) / 465 (SSL)", "transport": "TCP", "layer": 7,
        "full_name": "Simple Mail Transfer Protocol",
        "desc": "Envío de correo electrónico entre servidores (y de cliente a servidor).",
        "steps": [
            ("Conexión TCP", "El cliente conecta al servidor SMTP en puerto 587."),
            ("EHLO", "El cliente se presenta: EHLO midiominio.com"),
            ("AUTH LOGIN", "Autenticación con usuario y contraseña en base64."),
            ("MAIL FROM / RCPT TO", "Define remitente y destinatario."),
            ("DATA", "El cliente envía el cuerpo del correo (cabeceras + cuerpo). Termina con '.'."),
            ("QUIT", "Cierra la sesión."),
        ],
        "color": C.BMAGENTA,
    },
    "SSH": {
        "port": 22, "transport": "TCP", "layer": 7,
        "full_name": "Secure Shell",
        "desc": "Acceso remoto seguro (cifrado). Reemplazó a Telnet. Usa criptografía asimétrica.",
        "steps": [
            ("TCP al puerto 22", "El cliente inicia la conexión."),
            ("Intercambio de versiones", "Ambos lados negocian la versión SSH (SSH-2.0)."),
            ("Key exchange", "Se negocia con Diffie-Hellman para crear una sesión cifrada."),
            ("Autenticación", "Con contraseña (menos seguro) o par de llaves pública/privada."),
            ("Shell interactivo", "El usuario tiene acceso remoto cifrado al servidor."),
        ],
        "color": C.BGREEN,
    },
    "TCP": {
        "port": "N/A", "transport": "TCP", "layer": 4,
        "full_name": "Transmission Control Protocol",
        "desc": "Protocolo de transporte confiable. Garantiza entrega, orden y sin duplicados. Usa conexión.",
        "steps": [
            ("SYN →", "El cliente envía SYN (synchronize) con número de secuencia aleatorio (ISN)."),
            ("← SYN-ACK", "El servidor responde con SYN+ACK y su propio ISN."),
            ("ACK →", "El cliente confirma con ACK. La conexión está establecida (3-way handshake)."),
            ("Transferencia", "Los datos se transfieren con ventana deslizante y retransmisión si hay pérdidas."),
            ("FIN / FIN-ACK", "Cierre ordenado con 4 mensajes (FIN, ACK, FIN, ACK)."),
        ],
        "color": C.BYELLOW,
    },
    "UDP": {
        "port": "N/A", "transport": "UDP", "layer": 4,
        "full_name": "User Datagram Protocol",
        "desc": "Protocolo de transporte sin conexión. Rápido pero sin garantías. Ideal para streaming, gaming, DNS.",
        "steps": [
            ("Sin handshake", "UDP envía datos directamente sin establecer conexión."),
            ("Datagrama único", "Cada datagrama es independiente. Pueden llegar desordenados o perderse."),
            ("Sin retransmisión", "Si un paquete se pierde, UDP no lo recupera. La aplicación debe manejarlo."),
        ],
        "color": C.BRED,
    },
}


def ver_protocolo():
    header("Referencia de Protocolos", "Módulo 3 · Comunicación")
    section("Protocolos disponibles")
    for name, p in PROTOCOLS.items():
        print(f"  {cc(p['color'], f'{name:<10}')} Puerto {str(p['port']):<22} {p['full_name']}")
    print()
    raw = ask("Nombre del protocolo (ej: HTTP, DNS, DHCP)")
    name = raw.upper().strip()
    if name not in PROTOCOLS:
        warn(f"'{name}' no encontrado. Opciones: {', '.join(PROTOCOLS.keys())}")
        pause()
        return

    p = PROTOCOLS[name]
    header(f"{name} · {p['full_name']}", p["desc"])

    result("Puerto",      str(p["port"]))
    result("Transporte",  p["transport"])
    result("Capa OSI",    str(p["layer"]))
    sep()

    section("Funcionamiento paso a paso")
    for i, (title, text) in enumerate(p["steps"], 1):
        step(i, title, text)

    if "mnemonico" in p:
        callout("info", "Nemónico", p["mnemonico"])

    if "codes" in p:
        sep()
        section("Códigos de estado HTTP")
        for code, meaning in p["codes"].items():
            result(code, meaning)

    if "record_types" in p:
        sep()
        section("Tipos de registros DNS")
        for rtype, meaning in p["record_types"].items():
            result(rtype, meaning)

    pause()


def buscar_por_puerto():
    header("Buscar Protocolo por Puerto", "Módulo 3")
    raw = ask("Número de puerto")
    try:
        port = int(raw)
    except ValueError:
        warn("Ingresa un número.")
        pause()
        return

    found = [(n, p) for n, p in PROTOCOLS.items()
             if str(port) in str(p["port"])]

    if not found:
        # Intentar con socket
        try:
            svc = socket.getservbyport(port)
            info(f"Puerto {port}: {svc} (fuente: sistema operativo)")
        except OSError:
            warn(f"Puerto {port} no encontrado en la base de datos.")
    else:
        for name, p in found:
            result(name, f"{p['full_name']} — {p['desc']}")

    pause()


def comparar_tcp_udp():
    header("TCP vs UDP", "Módulo 3 · Protocolos de transporte")
    sep()
    ancho = 34
    print(f"  {cc(C.BOLD, 'Característica'):<30} {cc(C.BYELLOW + C.BOLD, 'TCP'):<40} {cc(C.BRED + C.BOLD, 'UDP')}")
    print(f"  {'─'*28} {'─'*32} {'─'*32}")

    comparisons = [
        ("Conexión",         "Sí (3-way handshake)",     "No (connectionless)"),
        ("Confiabilidad",    "Garantizada (ACKs)",        "Sin garantía"),
        ("Orden de paquetes","Sí (números de secuencia)", "No garantizado"),
        ("Velocidad",        "Más lento (overhead)",      "Más rápido"),
        ("Control de flujo", "Sí (ventana deslizante)",   "No"),
        ("Uso",              "HTTP, SSH, FTP, SMTP",      "DNS, streaming, gaming, VoIP"),
        ("Overhead de cabecera", "20 bytes mín.",         "8 bytes"),
    ]

    for feature, tcp, udp in comparisons:
        print(f"  {feature:<30} {cc(C.BYELLOW, tcp):<44} {cc(C.BRED, udp)}")

    callout("info", "Regla práctica",
            "Si necesitas que llegue COMPLETO y en ORDEN: TCP.\n"
            "Si necesitas VELOCIDAD y no importa perder algún paquete: UDP.")
    pause()


def tipos_transmision():
    header("Unicast · Multicast · Broadcast", "Módulo 2 · Tipos de transmisión")
    step(1, "Unicast (1 → 1)", "Un emisor, un receptor específico.\nEj: cargar una página web. El servidor te manda los datos solo a ti.")
    step(2, "Multicast (1 → grupo)", "Un emisor, múltiples receptores suscritos.\nEj: streaming de TV. El servidor manda UNA copia; los routers la replican.")
    step(3, "Broadcast (1 → todos)", "El mensaje llega a TODOS en la red local.\nEj: DHCP Discover — el dispositivo grita '¿Hay servidor DHCP?' a toda la red.")
    sep()
    print(f"  {'Tipo':<15} {'Destino':<25} {'Ejemplo'}")
    print(f"  {'─'*13} {'─'*23} {'─'*30}")
    rows = [
        ("Unicast",    "Una IP específica",         "HTTP request"),
        ("Multicast",  "Grupo (224.x.x.x)",         "Video streaming"),
        ("Broadcast",  "255.255.255.255 (toda red)", "DHCP Discover / ARP"),
        ("Anycast",    "El más cercano del grupo",   "DNS root servers, CDN"),
    ]
    for t, d, e in rows:
        print(f"  {cc(C.BCYAN, t):<23} {d:<25} {cc(C.DIM, e)}")
    pause()


def run():
    while True:
        opts = [
            "Ver protocolo en detalle (HTTP, HTTPS, DNS, DHCP, SSH, TCP, UDP…)",
            "Buscar protocolo por número de puerto",
            "Comparar TCP vs UDP",
            "Unicast vs Multicast vs Broadcast",
        ]
        choice = menu("Módulo 3 · Protocolos de Comunicación", opts)
        if choice == -1:
            break
        [ver_protocolo, buscar_por_puerto, comparar_tcp_udp, tipos_transmision][choice]()
