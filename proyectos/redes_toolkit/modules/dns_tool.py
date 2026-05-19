import socket
import time
from .utils import (header, section, step, result, sep, info, warn, ok,
                    callout, ask, pause, C, cc, menu)

# ── Módulo 3b: DNS y resolución de nombres ────────────────────────────────────

def resolver_dominio():
    header("Resolver Dominio → IP", "Módulo 3b · DNS")
    raw = ask("Dominio (ej: google.com, facebook.com)")
    if not raw:
        return
    domain = raw.strip().lower()

    info(f"Resolviendo '{domain}'...")
    try:
        t0 = time.time()
        results = socket.getaddrinfo(domain, None)
        ms = (time.time() - t0) * 1000
    except socket.gaierror as e:
        warn(f"Error de DNS: {e}")
        pause()
        return

    sep()
    ips_v4 = sorted(set(r[4][0] for r in results if r[0] == socket.AF_INET))
    ips_v6 = sorted(set(r[4][0] for r in results if r[0] == socket.AF_INET6))

    result("Dominio consultado", domain)
    result("Tiempo de resolución", f"{ms:.1f} ms")

    if ips_v4:
        result("IPv4 (registros A)", ", ".join(ips_v4))
    if ips_v6:
        result("IPv6 (registros AAAA)", ", ".join(ips_v6[:3]))

    # Canonicalname
    try:
        canonical = socket.getfqdn(domain)
        if canonical != domain:
            result("FQDN canónico", canonical)
    except Exception:
        pass

    sep()
    section("Proceso de resolución que ocurrió detrás de escena")
    pasos = [
        ("Caché local",           f"El SO buscó '{domain}' en su caché. Si lo tenía: directo al paso 7."),
        ("Hosts file",            "Revisó /etc/hosts (o C:\\Windows\\System32\\drivers\\etc\\hosts)."),
        ("Resolver del sistema",  "Preguntó al servidor DNS configurado (de tu router o ISP)."),
        ("Servidor raíz",         "El resolver preguntó a uno de los 13 root servers: '¿quién maneja el TLD?'"),
        ("Servidor TLD",          f"El root indicó el servidor del TLD (ej: .com, .net)."),
        ("Servidor autoritativo", f"El TLD indicó el servidor DNS autoritativo de '{domain}'."),
        ("Respuesta final",       f"El autoritativo devolvió: {', '.join(ips_v4[:2]) if ips_v4 else 'N/A'}"),
    ]
    for i, (t, d) in enumerate(pasos, 1):
        step(i, t, d)

    callout("info", "¿Por qué UDP?",
            "DNS usa UDP puerto 53 por defecto (más rápido, menos overhead).\n"
            "Solo cambia a TCP cuando la respuesta supera 512 bytes (zona transfer, DNSSEC).")
    pause()


def dns_inverso():
    header("DNS Inverso (PTR)", "Módulo 3b · rDNS")
    info("Convierte una IP en nombre de dominio (si el administrador configuró el registro PTR).")
    raw = ask("Dirección IP")
    if not raw:
        return
    try:
        t0 = time.time()
        hostname = socket.gethostbyaddr(raw.strip())
        ms = (time.time() - t0) * 1000
        sep()
        result("IP consultada",   raw.strip())
        result("Hostname",        hostname[0])
        result("Aliases",         ", ".join(hostname[1]) or "ninguno")
        result("Todas las IPs",   ", ".join(hostname[2]))
        result("Tiempo",          f"{ms:.1f} ms")
    except socket.herror as e:
        warn(f"Sin registro PTR para {raw}: {e}")
    pause()


def jerarquia_dns():
    header("Jerarquía del Sistema DNS", "Módulo 3b · Estructura")
    info("El DNS es un árbol distribuido. La raíz está arriba; los dominios debajo.")
    sep()

    niveles = [
        (".", "Raíz (Root)", "13 grupos de servidores raíz operados por ICANN, NASA, ARIN, etc.\n"
                             "Saben quién maneja cada TLD (.com, .net, .org, .mx, .es…)"),
        (".com / .org / .mx", "TLD (Top Level Domain)", "Gestionados por registros (Verisign para .com).\n"
                                                         "Saben qué servidor es autoritativo para cada dominio."),
        ("google.com", "Dominio de segundo nivel (SLD)", "El que tú registras con un registrar (GoDaddy, Namecheap…).\n"
                                                           "Tú controlas su zona DNS."),
        ("www.google.com / mail.google.com", "Subdominio", "Definido en tu zona DNS. Apunta a servidores específicos."),
    ]

    for i, (ejemplo, nivel, desc) in enumerate(niveles, 1):
        step(i, f"{nivel}  →  {cc(C.BYELLOW, ejemplo)}", desc)

    sep()
    section("Tipos de servidores DNS")
    tipos = [
        ("Resolver recursivo", "Hace el trabajo de buscar la respuesta completa (tu ISP o 8.8.8.8)."),
        ("Servidor raíz",      "Punto de partida. Solo sabe de TLDs. 13 direcciones IP (A–M.ROOT-SERVERS.NET)."),
        ("Servidor TLD",       "Sabe los NS de cada dominio bajo su TLD."),
        ("Servidor autoritativo", "Tiene la respuesta definitiva para el dominio. Tu servidor DNS real."),
        ("Servidor caché",     "Guarda respuestas temporalmente según el TTL del registro."),
    ]
    for nombre, desc in tipos:
        result(nombre, desc)

    callout("info", "TTL (Time To Live)",
            "Cada registro DNS tiene un TTL en segundos.\n"
            "Si TTL=300, el resolver lo cachea 5 minutos.\n"
            "Baja el TTL antes de cambiar servidores para que la propagación sea rápida.")
    pause()


def registros_dns():
    header("Tipos de Registros DNS", "Módulo 3b · Zona DNS")
    records = [
        ("A",     "Nombre → IPv4",                 "ejemplo.com → 93.184.216.34"),
        ("AAAA",  "Nombre → IPv6",                 "ejemplo.com → 2606:2800:220:1:248:1893:25c8:1946"),
        ("CNAME", "Alias → nombre canónico",        "www → ejemplo.com (redirige un nombre a otro)"),
        ("MX",    "Servidor de correo",             "ejemplo.com → mail.ejemplo.com (con prioridad)"),
        ("TXT",   "Texto arbitrario",               "SPF: v=spf1 include:_spf.google.com ~all"),
        ("NS",    "Servidores de nombres",          "ejemplo.com → ns1.proveedor.com"),
        ("PTR",   "IP → nombre (rDNS)",             "34.216.184.93.in-addr.arpa → ejemplo.com"),
        ("SOA",   "Start of Authority",             "Administrador, refresh interval, número de serie"),
        ("SRV",   "Servicio específico + puerto",   "_sip._tcp.ejemplo.com → sipserver.ejemplo.com:5060"),
        ("CAA",   "Autoridades de certificados",    "0 issue 'letsencrypt.org'"),
    ]

    sep()
    print(f"  {cc(C.BOLD, 'Tipo'):<12} {cc(C.BOLD, 'Función'):<32} {cc(C.BOLD, 'Ejemplo')}")
    print(f"  {'─'*10} {'─'*30} {'─'*36}")
    for rtype, func, example in records:
        print(f"  {cc(C.BCYAN, rtype):<20} {func:<32} {cc(C.DIM, example)}")
    pause()


def run():
    while True:
        opts = [
            "Resolver dominio → IP (consulta DNS real)",
            "DNS inverso: IP → hostname (PTR)",
            "Jerarquía del sistema DNS (Root → TLD → SLD)",
            "Tipos de registros DNS (A, AAAA, MX, CNAME, TXT…)",
        ]
        choice = menu("Módulo 3b · DNS y Resolución de Nombres", opts)
        if choice == -1:
            break
        [resolver_dominio, dns_inverso, jerarquia_dns, registros_dns][choice]()
