from .utils import (header, section, step, substep, result, sep, info,
                    warn, ok, callout, ask, pause, C, cc, menu)

# ── Troubleshooting: 12 guías interactivas ────────────────────────────────────

def _yes_no(question):
    """Retorna True si el usuario dice sí."""
    print(f"\n  {cc(C.BYELLOW, '?')}  {question}")
    raw = input(f"  {cc(C.BCYAN, '[s/n]')}: ").strip().lower()
    return raw in ("s", "si", "sí", "y", "yes", "1")


# ── T1: Sin conectividad ──────────────────────────────────────────────────────
def ts1_sin_conectividad():
    header("T1 · Sin conectividad a Internet", "Troubleshooting · Diagnóstico paso a paso")
    step(1, "Verificar conexión física",
         "Comprueba que el cable Ethernet esté bien conectado o que el WiFi está activo.\n"
         "Comando: ip link (Linux) / ipconfig (Windows)")

    if not _yes_no("¿Tienes luz de actividad en el puerto / ícono WiFi conectado?"):
        callout("warn", "Problema físico",
                "Revisa el cable, cambia de puerto en el switch, o reinicia el punto de acceso WiFi.")
        pause()
        return

    step(2, "Verificar dirección IP",
         "ip addr (Linux) / ipconfig (Windows)\n"
         "Busca tu IP. Si empieza con 169.254.x.x → APIPA (DHCP falló).")

    if not _yes_no("¿Tu dispositivo tiene una IP válida (no 169.254.x.x)?"):
        callout("warn", "Fallo de DHCP",
                "Prueba: ipconfig /release && ipconfig /renew (Windows)\n"
                "         dhclient -r && dhclient (Linux)\n"
                "Si persiste: verifica que el servidor DHCP del router esté activo.")
        pause()
        return

    step(3, "Hacer ping al gateway",
         "ip route (Linux) / ipconfig (Windows) → busca 'Default Gateway'.\n"
         "Luego: ping <IP del gateway>")

    if not _yes_no("¿El ping al gateway responde?"):
        callout("warn", "Problema de red local",
                "Reinicia el router/switch. Verifica VLAN. Revisa si hay firewall bloqueando ICMP.")
        pause()
        return

    step(4, "Ping a IP pública (sin DNS)",
         "ping 8.8.8.8 (Google DNS)\n"
         "Esto verifica conectividad a Internet SIN usar DNS.")

    if not _yes_no("¿El ping a 8.8.8.8 responde?"):
        callout("warn", "Problema de enrutamiento / ISP",
                "Tu LAN está bien pero no llegas a Internet.\n"
                "Verifica: configuración NAT del router, si tu ISP tiene una interrupción,\n"
                "o si el router tiene rutas incorrectas.")
        pause()
        return

    step(5, "Prueba de DNS",
         "ping google.com → si falla pero 8.8.8.8 funcionó, el problema es DNS.")

    if not _yes_no("¿El ping a google.com (por nombre) responde?"):
        callout("warn", "Problema de DNS",
                "Prueba cambiar DNS manualmente:\n"
                "  Windows: Red → Adaptador → TCP/IP → DNS: 8.8.8.8\n"
                "  Linux:   /etc/resolv.conf → nameserver 8.8.8.8\n"
                "Si funciona con IP pero no con nombre → DNS del ISP tiene problemas.")
        pause()
        return

    ok("¡Conectividad completa! Si hay problemas, quizá es a nivel de la aplicación (T5) o firewall (T6).")
    pause()


# ── T2: Red lenta ─────────────────────────────────────────────────────────────
def ts2_red_lenta():
    header("T2 · Red lenta o intermitente", "Troubleshooting")

    section("Diagnóstico de latencia y pérdida de paquetes")
    step(1, "Medir latencia al gateway",
         "ping -c 20 <gateway>  (Linux)\n"
         "ping -n 20 <gateway>  (Windows)\n"
         "Observa: min/avg/max y % packet loss")
    step(2, "Trazar la ruta (traceroute)",
         "traceroute google.com  (Linux/Mac)\n"
         "tracert   google.com  (Windows)\n"
         "Identifica en qué salto hay alta latencia o pérdidas (*)")
    step(3, "Verificar colisiones y errores de interfaz",
         "ip -s link show <interfaz>  (Linux)\n"
         "netstat -e (Windows)\n"
         "Busca: errors, dropped, overruns")
    step(4, "Verificar ancho de banda",
         "Usa speedtest-cli (speedtest.net) para medir throughput real vs contratado.")
    step(5, "Revisar QoS y congestión",
         "Si hay muchos dispositivos transmitiendo simultáneamente → congestión.\n"
         "Revisa si algún proceso consume todo el ancho de banda (ej: backup, torrent).")

    callout("info", "Reglas empíricas",
            "Latencia < 20ms: excelente\n"
            "Latencia 20–100ms: aceptable\n"
            "Latencia > 150ms: problemas para VoIP/gaming\n"
            "Pérdida de paquetes > 1%: inaceptable para la mayoría de aplicaciones")
    pause()


# ── T3: IP / DHCP ─────────────────────────────────────────────────────────────
def ts3_dhcp():
    header("T3 · Problemas de IP / DHCP", "Troubleshooting")
    step(1, "Identificar IP asignada",
         "ipconfig /all (Windows) / ip addr (Linux)\n"
         "Si la IP es 169.254.x.x → el DHCP NO respondió (APIPA).")
    step(2, "Liberar y renovar IP",
         "Windows: ipconfig /release → ipconfig /renew\n"
         "Linux:   dhclient -r eth0 → dhclient eth0\n"
         "Mac:     sudo ipconfig set en0 DHCP")
    step(3, "Verificar servidor DHCP",
         "Accede al panel del router → verifica que DHCP está activo.\n"
         "Revisa el pool de IPs disponibles (si está lleno, no asigna más).")
    step(4, "Asignar IP estática manualmente",
         "Si DHCP no funciona temporalmente:\n"
         "  IP:      192.168.1.99 (una libre en tu red)\n"
         "  Máscara: 255.255.255.0\n"
         "  Gateway: 192.168.1.1\n"
         "  DNS:     8.8.8.8")
    step(5, "Verificar conflicto de IP",
         "Si dos dispositivos tienen la misma IP → conflicto.\n"
         "Usa: arp -a (todos los MAC/IP de la red local)\n"
         "     arping <IP>  para detectar duplicados.")

    callout("info", "Proceso DHCP (DORA)",
            "Discover → Offer → Request → ACK\n"
            "El cliente hace DISCOVER en broadcast (255.255.255.255).\n"
            "Si el servidor DHCP no responde → fallo en DISCOVER o el servidor está caído.")
    pause()


# ── T4: DNS ───────────────────────────────────────────────────────────────────
def ts4_dns():
    header("T4 · Problemas de DNS", "Troubleshooting")
    step(1, "Confirmar que el problema es DNS (no Internet)",
         "ping 8.8.8.8   → ¿responde? (Internet SÍ funciona)\n"
         "ping google.com → ¿falla?   (DNS es el problema)")
    step(2, "Verificar DNS configurado",
         "ipconfig /all (Windows) → busca 'DNS Servers'\n"
         "cat /etc/resolv.conf (Linux)")
    step(3, "Probar DNS alternativo",
         "Cambia temporalmente a 8.8.8.8 o 1.1.1.1\n"
         "Si funciona → el DNS de tu ISP está caído")
    step(4, "Limpiar caché DNS",
         "Windows: ipconfig /flushdns\n"
         "Linux:   sudo systemd-resolve --flush-caches\n"
         "Mac:     sudo dscacheutil -flushcache")
    step(5, "Consulta manual con nslookup / dig",
         "nslookup google.com 8.8.8.8\n"
         "dig @8.8.8.8 google.com\n"
         "Prueba distintos servidores DNS para aislar el problema.")

    callout("info", "DNS públicos confiables",
            "Google:     8.8.8.8  /  8.8.4.4\n"
            "Cloudflare: 1.1.1.1  /  1.0.0.1  (más rápido)\n"
            "Quad9:      9.9.9.9  (filtrado de malware)\n"
            "OpenDNS:    208.67.222.222")
    pause()


# ── T5: HTTP / HTTPS ──────────────────────────────────────────────────────────
def ts5_http():
    header("T5 · Problemas de HTTP / HTTPS", "Troubleshooting")
    step(1, "Identificar el código de error",
         "4xx = error del CLIENTE\n"
         "5xx = error del SERVIDOR\n"
         "Más comunes: 400 (bad request), 401 (no autorizado), 403 (prohibido),\n"
         "             404 (no encontrado), 500 (error interno), 502 (bad gateway), 503 (no disponible)")
    step(2, "Probar con curl",
         "curl -I https://dominio.com\n"
         "Muestra el código de estado y cabeceras sin descargar el cuerpo.")
    step(3, "Verificar HTTPS / TLS",
         "openssl s_client -connect dominio.com:443\n"
         "Muestra el certificado, cadena CA y fecha de vencimiento.")
    step(4, "Revisar cabeceras de seguridad",
         "curl -I https://dominio.com | grep -i 'strict\\|content-security\\|x-frame'\n"
         "HSTS, CSP, X-Frame-Options protegen contra ataques comunes.")
    step(5, "Verificar proxy o firewall",
         "¿Hay un proxy corporativo? Verifica las variables http_proxy / https_proxy.\n"
         "Un firewall puede bloquear el puerto 443 en ciertas redes.")

    callout("info", "Diferencia HTTP vs HTTPS en tráfico",
            "HTTP: datos en texto plano → cualquiera en la red los lee.\n"
            "HTTPS: datos cifrados con TLS → nadie en el camino los lee.\n"
            "Siempre usa HTTPS. Chrome muestra 'No seguro' en sitios HTTP desde 2018.")
    pause()


# ── T6: Seguridad ─────────────────────────────────────────────────────────────
def ts6_seguridad():
    header("T6 · Diagnóstico de Seguridad de Red", "Troubleshooting")
    step(1, "Escanear puertos abiertos",
         "nmap -sS -p 1-1024 <IP>           (escaneo rápido)\n"
         "nmap -A <IP>                        (detección de SO y versiones)\n"
         "Solo en redes/sistemas que tengas autorización de escanear.")
    step(2, "Verificar conexiones activas",
         "netstat -tulnp (Linux) — muestra qué proceso escucha en qué puerto\n"
         "ss -tulnp      (Linux, más moderno)\n"
         "netstat -ano   (Windows)")
    step(3, "Detectar tráfico sospechoso",
         "tcpdump -i eth0 -n    (Linux — captura paquetes en tiempo real)\n"
         "Wireshark              (interfaz gráfica — filtra por IP, protocolo, etc.)")
    step(4, "Verificar reglas de firewall",
         "iptables -L -n -v     (Linux)\n"
         "ufw status verbose    (Ubuntu)\n"
         "netsh advfirewall show allprofiles (Windows)")
    step(5, "Revisar intentos de acceso fallidos",
         "tail -f /var/log/auth.log         (Debian/Ubuntu)\n"
         "tail -f /var/log/secure           (CentOS/RHEL)\n"
         "Busca: 'Failed password', 'Invalid user' → posible fuerza bruta")

    callout("danger", "Tríada CIA",
            "Confidencialidad: ¿solo quienes deben ven los datos?\n"
            "Integridad:       ¿los datos no han sido modificados?\n"
            "Disponibilidad:   ¿el sistema está accesible cuando se necesita?")
    pause()


# ── T7: Certificados SSL ──────────────────────────────────────────────────────
def ts7_ssl():
    header("T7 · Problemas con Certificados SSL/TLS", "Troubleshooting")
    step(1, "Verificar fecha de vencimiento",
         "openssl s_client -connect dominio.com:443 2>/dev/null | openssl x509 -noout -dates\n"
         "Chrome: candado → Certificado → Válido hasta:")
    step(2, "Verificar que el CN coincide",
         "El CN (Common Name) o SAN debe coincidir con el dominio visitado.\n"
         "Error: 'NET::ERR_CERT_COMMON_NAME_INVALID' → el cert es de otro dominio.")
    step(3, "Verificar la cadena de CA",
         "El certificado debe estar firmado por una CA de confianza (Let's Encrypt, DigiCert, etc.).\n"
         "Error: 'NET::ERR_CERT_AUTHORITY_INVALID' → CA desconocida o certificado autofirmado.")
    step(4, "Renovar certificado con Let's Encrypt",
         "certbot renew --dry-run    (probar)\n"
         "certbot renew              (renovar)\n"
         "Let's Encrypt caduca cada 90 días. Configura auto-renovación con cron.")
    step(5, "Verificar versión de TLS",
         "openssl s_client -tls1_2 -connect dominio.com:443\n"
         "TLS 1.0 y 1.1 están deprecated. Usa TLS 1.2 mínimo, TLS 1.3 recomendado.")

    callout("info", "Herramientas online",
            "SSL Labs: ssllabs.com/ssltest → análisis completo de configuración TLS\n"
            "Why No Padlock: whynopadlock.com → detecta mixed content (HTTP dentro de HTTPS)")
    pause()


# ── T8: WiFi ──────────────────────────────────────────────────────────────────
def ts8_wifi():
    header("T8 · Problemas de WiFi y Señal", "Troubleshooting")
    step(1, "Verificar potencia de señal",
         "Windows: netsh wlan show interfaces → Signal\n"
         "Linux:   iwconfig wlan0 / iw dev wlan0 link\n"
         "Ideal: > -65 dBm. Problemático: < -80 dBm.")
    step(2, "Analizar canales en uso",
         "Muchos routers en el mismo canal → interferencia.\n"
         "Windows: netsh wlan show networks mode=bssid\n"
         "Linux:   iwlist scan | grep Channel\n"
         "Elige un canal con menos ocupación (1, 6 o 11 en 2.4GHz).")
    step(3, "2.4 GHz vs 5 GHz",
         "2.4 GHz: mayor alcance, más interferencia, velocidad máx ~300 Mbps\n"
         "5 GHz:   menor alcance, menos interferencia, velocidad hasta ~1.3 Gbps\n"
         "Si estás cerca del router y hay interferencia → prueba 5 GHz.")
    step(4, "Revisar obstrucciones físicas",
         "Paredes de concreto, electrodomésticos, microondas y teléfonos inalámbricos\n"
         "interfieren con 2.4 GHz. El router cerca de microondas = desastre.")
    step(5, "Reiniciar adaptador WiFi",
         "Windows: Device Manager → Disable/Enable adaptador WiFi\n"
         "Linux:   ip link set wlan0 down && ip link set wlan0 up")
    pause()


# ── T9: Correo / spam ─────────────────────────────────────────────────────────
def ts9_correo():
    header("T9 · Problemas de Correo y Spam", "Troubleshooting")
    step(1, "Verificar puertos del servidor de correo",
         "SMTP salida: 587 (STARTTLS) o 465 (SSL)\n"
         "POP3:       110 (plain) o 995 (SSL)\n"
         "IMAP:       143 (STARTTLS) o 993 (SSL)\n"
         "telnet <servidor> <puerto>  → verifica conectividad")
    step(2, "Revisar registros SPF, DKIM y DMARC",
         "SPF:   TXT v=spf1 include:_spf.google.com ~all\n"
         "DKIM:  TXT selector._domainkey → firma digital de correos\n"
         "DMARC: TXT v=DMARC1; p=quarantine; rua=mailto:...\n"
         "Sin estos registros → tus correos van a SPAM.")
    step(3, "Verificar blacklists",
         "Si tu IP está en una lista negra de spam:\n"
         "mxtoolbox.com → Blacklist Check\n"
         "Pide deslistado si es una IP limpia.")
    step(4, "Revisar logs del servidor SMTP",
         "/var/log/mail.log (Debian/Ubuntu)\n"
         "/var/log/maillog  (CentOS/RHEL)\n"
         "Busca: relay denied, authentication failed, connection refused")
    pause()


# ── T10: Problemas cotidianos ─────────────────────────────────────────────────
def ts10_cotidiano():
    header("T10 · Problemas Cotidianos de Red", "Troubleshooting")
    problemas = [
        ("No carga una página específica (otras sí)",
         "Problema con el servidor de destino o con el DNS para ese dominio.\n"
         "Prueba: curl -I https://sitio.com desde terminal.\n"
         "Verifica en downdetector.com si el sitio está caído globalmente."),
        ("La red va lenta solo en ciertas horas",
         "Congestión en el ISP (hora pico) o en tu red local.\n"
         "Verifica con speedtest-cli. Compara velocidad contratada vs real."),
        ("El router asigna la misma IP a otro dispositivo",
         "Conflicto de IPs. Asigna IPs estáticas por MAC (DHCP reservations)\n"
         "en el panel del router para dispositivos críticos."),
        ("VPN conectada pero no navega",
         "Split tunneling mal configurado. El gateway de VPN no está enrutando.\n"
         "Verifica: ip route (Linux) / route print (Windows)."),
        ("No puedo conectarme a un servidor por SSH",
         "Verifica: puerto 22 abierto (nmap), firewall del servidor (iptables/ufw),\n"
         "que el demonio SSH está corriendo (systemctl status sshd)."),
    ]
    for i, (prob, sol) in enumerate(problemas, 1):
        step(i, prob, sol)
    pause()


# ── T11: Seguridad práctica ────────────────────────────────────────────────────
def ts11_seguridad_practica():
    header("T11 · Seguridad Práctica", "Troubleshooting · Checklist")
    checklist = [
        ("Contraseñas fuertes", "Mínimo 12 caracteres, mayúsculas + números + símbolos.\n"
                                 "Usa un gestor: Bitwarden, KeePass. NUNCA reutilices contraseñas."),
        ("Autenticación de dos factores (2FA)", "Activa 2FA en todas tus cuentas importantes.\n"
                                                  "Preferiblemente con app (TOTP: Google Authenticator, Authy)\n"
                                                  "no con SMS (SIM swapping)."),
        ("Actualizar software regularmente", "Las vulnerabilidades conocidas (CVEs) se parchean en actualizaciones.\n"
                                              "Un sistema sin parchear es blanco fácil."),
        ("HTTPS en todo", "Nunca envíes datos sensibles por HTTP.\n"
                           "Extensión HTTPS Everywhere (Firefox) o configuración HSTS."),
        ("VPN en redes públicas", "En WiFi de café, hotel o aeropuerto → usa VPN.\n"
                                   "Un atacante en la misma red puede hacer ARP spoofing / MITM."),
        ("Backup 3-2-1", "3 copias, 2 medios distintos, 1 offsite.\n"
                          "Cifra los backups. Verifica que puedas restaurarlos."),
        ("Principio de mínimo privilegio", "No uses cuenta root/admin para tareas cotidianas.\n"
                                            "Solo eleva privilegios cuando sea necesario."),
    ]
    for i, (titulo, desc) in enumerate(checklist, 1):
        step(i, titulo, desc)
    pause()


# ── T12: Comandos avanzados ────────────────────────────────────────────────────
def ts12_comandos():
    header("T12 · Comandos de Red Avanzados", "Troubleshooting · Referencia")
    sep()
    cmds = [
        ("Conectividad básica", [
            ("ping <IP>",            "Verifica conectividad ICMP"),
            ("traceroute / tracert", "Traza la ruta de paquetes hop a hop"),
            ("mtr <destino>",        "ping + traceroute en tiempo real (Linux)"),
        ]),
        ("DNS", [
            ("nslookup <dominio>",            "Consulta DNS (Windows/Linux)"),
            ("dig <dominio>",                  "Consulta DNS detallada (Linux)"),
            ("dig +trace <dominio>",           "Traza la resolución DNS desde la raíz"),
            ("dig -x <IP>",                    "DNS inverso"),
            ("ipconfig /flushdns",             "Limpiar caché DNS (Windows)"),
        ]),
        ("Interfaces y rutas", [
            ("ip addr / ifconfig",             "Ver interfaces y sus IPs"),
            ("ip route / route -n",            "Ver tabla de enrutamiento"),
            ("ip link",                        "Estado de interfaces (up/down)"),
            ("arp -a",                         "Tabla ARP: IP ↔ MAC en la red local"),
        ]),
        ("Puertos y conexiones", [
            ("netstat -tulnp",                 "Puertos en escucha y procesos (Linux)"),
            ("ss -tulnp",                      "Versión moderna de netstat"),
            ("nmap -sS <IP>",                  "Escaneo de puertos SYN (requiere root)"),
            ("nc -zv <IP> <puerto>",           "Verificar si un puerto está abierto"),
        ]),
        ("Captura de paquetes", [
            ("tcpdump -i eth0",                "Captura paquetes en interfaz eth0"),
            ("tcpdump -i any port 80",         "Solo tráfico HTTP"),
            ("tcpdump -w captura.pcap",        "Guardar captura para Wireshark"),
        ]),
        ("Ancho de banda", [
            ("iperf3 -s",                      "Servidor de prueba de ancho de banda"),
            ("iperf3 -c <IP>",                 "Cliente → mide throughput TCP"),
            ("speedtest-cli",                  "Medir velocidad Internet"),
        ]),
    ]

    for categoria, lista in cmds:
        section(categoria)
        for cmd, desc in lista:
            print(f"  {cc(C.BYELLOW, f'{cmd:<42}')} {cc(C.DIM, desc)}")

    pause()


GUIDES = [
    ("T1  · Sin conectividad a Internet",     ts1_sin_conectividad),
    ("T2  · Red lenta o intermitente",         ts2_red_lenta),
    ("T3  · Problemas de IP / DHCP",           ts3_dhcp),
    ("T4  · Problemas de DNS",                 ts4_dns),
    ("T5  · Problemas de HTTP / HTTPS",        ts5_http),
    ("T6  · Diagnóstico de seguridad",         ts6_seguridad),
    ("T7  · Certificados SSL/TLS",             ts7_ssl),
    ("T8  · WiFi y señal inalámbrica",         ts8_wifi),
    ("T9  · Correo y spam",                    ts9_correo),
    ("T10 · Problemas cotidianos",             ts10_cotidiano),
    ("T11 · Seguridad práctica (checklist)",   ts11_seguridad_practica),
    ("T12 · Comandos avanzados de red",        ts12_comandos),
]


def run():
    while True:
        opts = [label for label, _ in GUIDES]
        choice = menu("Troubleshooting · 12 Guías de Diagnóstico", opts)
        if choice == -1:
            break
        GUIDES[choice][1]()
