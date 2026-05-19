import ipaddress
from .utils import (header, section, step, result, sep, info, warn, ok,
                    callout, ask, pause, C, cc)

# ── Módulo 4: Direccionamiento IP y subnetting ────────────────────────────────

def _ip_class(ip: ipaddress.IPv4Address) -> str:
    first = int(str(ip).split(".")[0])
    if first < 128:   return "A  (0.0.0.0  – 127.255.255.255)"
    if first < 192:   return "B  (128.0.0.0 – 191.255.255.255)"
    if first < 224:   return "C  (192.0.0.0 – 223.255.255.255)"
    if first < 240:   return "D  (Multicast)"
    return              "E  (Experimental)"

def _ip_scope(ip: ipaddress.IPv4Address) -> str:
    if ip.is_private:    return "Privada (RFC 1918)"
    if ip.is_loopback:   return "Loopback (127.x)"
    if ip.is_link_local: return "Link-local (APIPA 169.254.x)"
    if ip.is_multicast:  return "Multicast (224–239.x)"
    return "Pública (enrutable por Internet)"

def calcular_subred():
    header("Calculadora de Subredes IPv4", "Módulo 4 · Direccionamiento IP")
    section("Ingresa la dirección IP con prefijo CIDR")
    info("Ejemplo: 192.168.1.0/24  o  10.0.0.45/8")
    raw = ask("IP/CIDR")
    if not raw:
        return
    try:
        # strict=False: acepta hosts dentro de la red (ej: 192.168.1.45/24)
        net = ipaddress.IPv4Network(raw, strict=False)
        ip  = ipaddress.IPv4Address(raw.split("/")[0])
    except ValueError as e:
        warn(f"Entrada inválida: {e}")
        pause()
        return

    sep()
    section("Resultados")
    result("Dirección de red",    str(net.network_address))
    result("Dirección de broadcast", str(net.broadcast_address))
    result("Primera IP de host",  str(net.network_address + 1))
    result("Última IP de host",   str(net.broadcast_address - 1))
    result("Máscara de subred",   str(net.netmask))
    result("Wildcard (inversa)",  str(net.hostmask))
    result("Prefijo CIDR",        f"/{net.prefixlen}")
    result("Total de hosts",      f"{net.num_addresses:,}")
    result("Hosts utilizables",   f"{max(0, net.num_addresses - 2):,}")

    sep()
    section("Análisis de la dirección host ingresada")
    result("Dirección ingresada", str(ip))
    result("Clase",               _ip_class(ip))
    result("Alcance",             _ip_scope(ip))
    result("¿Es host de red?",    "Sí" if ip == net.network_address else "No")
    result("¿Es broadcast?",      "Sí" if ip == net.broadcast_address else "No")

    sep()
    section("Representación binaria")
    partes = str(ip).split(".")
    binario = ".".join(f"{int(p):08b}" for p in partes)
    mask_b  = ".".join(f"{int(p):08b}" for p in str(net.netmask).split("."))
    print(f"  {'IP (binario)':<24} {cc(C.BYELLOW, binario)}")
    print(f"  {'Máscara (binario)':<24} {cc(C.BCYAN,  mask_b)}")
    print(f"  {'Bits de red':<24} {cc(C.BGREEN,  str(net.prefixlen))}")
    print(f"  {'Bits de host':<24} {cc(C.BMAGENTA, str(32 - net.prefixlen))}")

    callout("info", "Regla de subnetting",
            f"Con /{net.prefixlen} tienes {32 - net.prefixlen} bits de host.\n"
            f"2^{32 - net.prefixlen} = {net.num_addresses:,} direcciones totales\n"
            f"2^{32 - net.prefixlen} - 2 = {max(0, net.num_addresses - 2):,} hosts utilizables\n"
            "(se restan 1 dirección de red y 1 broadcast)")
    pause()


def dividir_red():
    header("Dividir Red en Subredes", "Módulo 4 · Subnetting")
    info("Calcula cómo subdividir una red en N subredes iguales.")
    raw_net = ask("Red base (ej: 192.168.0.0/24)")
    if not raw_net:
        return
    raw_n = ask("¿Cuántas subredes necesitas?")
    if not raw_n:
        return
    try:
        base = ipaddress.IPv4Network(raw_net, strict=True)
        n    = int(raw_n)
        assert n >= 1
    except Exception:
        warn("Entrada inválida.")
        pause()
        return

    subnets = list(base.subnets(prefixlen_diff=None))
    # Calcular prefixlen necesario para al menos n subredes
    bits_extra = 0
    while (1 << bits_extra) < n:
        bits_extra += 1

    try:
        subnets = list(base.subnets(prefixlen_diff=bits_extra))
    except ValueError as e:
        warn(str(e))
        pause()
        return

    sep()
    section(f"División de {raw_net} en {len(subnets)} subredes (/{base.prefixlen + bits_extra})")
    for i, s in enumerate(subnets[:32], 1):  # máx 32 en pantalla
        hosts = max(0, s.num_addresses - 2)
        print(f"  {cc(C.BCYAN, f'Subred {i:>3}')}  "
              f"{cc(C.BWHITE, str(s)):<22}  "
              f"Red: {str(s.network_address):<16} "
              f"Broadcast: {str(s.broadcast_address):<16} "
              f"Hosts: {hosts:>6,}")
    if len(subnets) > 32:
        info(f"... y {len(subnets) - 32} subredes más.")

    callout("info", "Bits adicionales usados",
            f"Para {n} subredes se necesitan {bits_extra} bits adicionales de red.\n"
            f"Nuevo prefijo: /{base.prefixlen} + {bits_extra} = /{base.prefixlen + bits_extra}\n"
            f"Hosts por subred: 2^{32 - base.prefixlen - bits_extra} - 2 = {max(0, (1 << (32 - base.prefixlen - bits_extra)) - 2):,}")
    pause()


def analizar_ipv6():
    header("Analizador de IPv6", "Módulo 4 · IPv6")
    info("Ingresa una dirección IPv6 (con o sin prefijo).")
    raw = ask("Dirección IPv6")
    if not raw:
        return
    try:
        if "/" in raw:
            net = ipaddress.IPv6Network(raw, strict=False)
            ip  = ipaddress.IPv6Address(raw.split("/")[0])
        else:
            ip  = ipaddress.IPv6Address(raw)
            net = None
    except ValueError as e:
        warn(str(e))
        pause()
        return

    sep()
    section("Análisis de dirección IPv6")
    result("Forma comprimida",   str(ip))
    result("Forma expandida",    ip.exploded)

    tipo = []
    if ip.is_loopback:      tipo.append("Loopback (::1)")
    if ip.is_link_local:    tipo.append("Link-local (fe80::/10)")
    if ip.is_multicast:     tipo.append("Multicast (ff00::/8)")
    if ip.is_private:       tipo.append("ULA – Unique Local (fc00::/7)")
    if ip.is_global:        tipo.append("Global unicast (enrutable)")
    if ip.is_unspecified:   tipo.append("No especificada (::)")
    result("Tipo",              ", ".join(tipo) if tipo else "Desconocido")

    if net:
        result("Red",           str(net))
        result("Total dirs",    f"2^{128-net.prefixlen}")

    callout("info", "¿Por qué IPv6?",
            "IPv4 tiene 2^32 ≈ 4,300 millones de direcciones — ya agotadas.\n"
            "IPv6 tiene 2^128 ≈ 340 undecillones.\n"
            "Suficiente para asignar millones de IPs a cada grano de arena del planeta.")
    pause()


def conversor_notacion():
    header("Conversor de Notación", "Módulo 4 · Máscaras y CIDR")
    section("¿Qué quieres convertir?")
    opts = [
        "Máscara de subred → prefijo CIDR",
        "Prefijo CIDR → máscara de subred",
        "IP decimal → binario",
        "Binario → IP decimal",
    ]
    idx, _ = ask("", opts)

    if idx == 0:
        mask = ask("Máscara (ej: 255.255.255.0)")
        try:
            net = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
            ok(f"/{net.prefixlen}  (wildcard: {net.hostmask})")
        except ValueError as e:
            warn(str(e))

    elif idx == 1:
        prefix = ask("Prefijo CIDR (número del 0 al 32)")
        try:
            net = ipaddress.IPv4Network(f"0.0.0.0/{prefix}", strict=False)
            ok(f"Máscara:   {net.netmask}")
            ok(f"Wildcard:  {net.hostmask}")
        except ValueError as e:
            warn(str(e))

    elif idx == 2:
        ip_raw = ask("IP decimal (ej: 192.168.1.1)")
        try:
            ip = ipaddress.IPv4Address(ip_raw)
            b  = ".".join(f"{x:08b}" for x in ip.packed)
            ok(f"{b}")
        except ValueError as e:
            warn(str(e))

    elif idx == 3:
        bin_raw = ask("Binario separado por puntos (ej: 11000000.10101000.00000001.00000001)")
        try:
            parts = [int(x, 2) for x in bin_raw.strip().split(".")]
            assert len(parts) == 4 and all(0 <= p <= 255 for p in parts)
            ok(f"{'.'.join(str(p) for p in parts)}")
        except Exception:
            warn("Formato inválido. Usa 4 grupos de 8 bits separados por puntos.")
    pause()


def run():
    while True:
        from .utils import menu
        opts = [
            "Calculadora de subred (IP/CIDR → Red, Broadcast, Hosts, Binario)",
            "Dividir una red en N subredes",
            "Analizador de IPv6",
            "Conversor de notación (máscara ↔ CIDR, decimal ↔ binario)",
        ]
        choice = menu("Módulo 4 · Direccionamiento IP y Subnetting", opts)
        if choice == -1:
            break
        [calcular_subred, dividir_red, analizar_ipv6, conversor_notacion][choice]()
