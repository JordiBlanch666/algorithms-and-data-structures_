from .utils import (header, section, step, substep, result, sep, info,
                    warn, ok, callout, pause, C, cc, menu)

# ── Módulo 6: Ciberseguridad ──────────────────────────────────────────────────

def triada_cia():
    header("Tríada CIA", "Módulo 6 · Los tres pilares de la seguridad")
    step(1, "Confidencialidad (Confidentiality)",
         "Solo quienes están autorizados pueden ver la información.\n"
         "Protegida con: cifrado (TLS, AES), control de acceso (RBAC), autenticación MFA.")
    step(2, "Integridad (Integrity)",
         "Los datos no han sido modificados sin autorización.\n"
         "Protegida con: hashing (SHA-256), firmas digitales (RSA/ECDSA), checksums.")
    step(3, "Disponibilidad (Availability)",
         "Los sistemas están accesibles cuando se necesitan.\n"
         "Protegida con: redundancia, backups, anti-DDoS, clustering, monitoreo.")

    sep()
    section("Ejemplos de fallo en cada pilar")
    ejemplos = [
        ("Confidencialidad", "Alguien intercepta tráfico HTTP y lee tus contraseñas.\n"
                              "Un empleado accede a archivos de RRHH sin permiso."),
        ("Integridad",       "Un atacante MITM altera el contenido de un archivo en tránsito.\n"
                              "Un virus modifica un ejecutable del sistema."),
        ("Disponibilidad",   "Un ataque DDoS satura el servidor y lo hace inaccesible.\n"
                              "Un disco duro falla y no hay backup."),
    ]
    for pilar, ejemplo in ejemplos:
        result(pilar, "")
        print(f"    {cc(C.DIM, ejemplo)}")
        print()
    pause()


def tipos_ataque():
    header("Tipos de Ataques Comunes", "Módulo 6 · Ciberseguridad")

    ataques = [
        ("Phishing", "Engaño por email o web falsa para robar credenciales.\n"
                     "Variantes: spear phishing (dirigido), whaling (CEO), smishing (SMS).",
         "Verificar URL, no hacer clic en links sospechosos, usar MFA."),
        ("MITM (Man in the Middle)", "El atacante se interpone en la comunicación y puede leer/alterar datos.\n"
                                      "Ejemplo: ARP spoofing en WiFi público.",
         "Usar HTTPS+HSTS, certificados válidos, evitar WiFi público sin VPN."),
        ("DDoS (Denial of Service)", "Inundar un servidor con tráfico hasta que se satura y cae.\n"
                                      "Botnet: miles de dispositivos comprometidos atacando simultáneamente.",
         "CDN, rate limiting, anti-DDoS (Cloudflare, AWS Shield)."),
        ("SQL Injection", "Inyectar código SQL en campos de formulario para manipular la base de datos.\n"
                           "' OR '1'='1 — frase clásica de SQL injection.",
         "Prepared statements, validación de entrada, WAF."),
        ("XSS (Cross-Site Scripting)", "Inyectar JavaScript malicioso en una página web.\n"
                                        "Puede robar cookies de sesión o redirigir al usuario.",
         "Escapar HTML, Content Security Policy (CSP), HttpOnly cookies."),
        ("Fuerza bruta / Diccionario", "Probar miles de contraseñas hasta encontrar la correcta.\n"
                                        "Diccionario: lista de contraseñas comunes (rockyou.txt tiene 14M).",
         "Contraseñas largas, MFA, bloqueo tras intentos fallidos, CAPTCHA."),
        ("Ransomware", "Malware que cifra tus archivos y pide rescate para descifrarlos.\n"
                        "Se propaga por phishing, RDP expuesto, vulnerabilidades sin parchear.",
         "Backups offline, no abrir adjuntos sospechosos, parchear sistemas."),
        ("ARP Spoofing", "Enviar respuestas ARP falsas para asociar la MAC del atacante a la IP del gateway.\n"
                          "Resultado: todo el tráfico pasa por el atacante (MITM).",
         "ARP inspection dinámica en switches, VPNs, cifrado del tráfico."),
    ]

    for name, desc, defensa in ataques:
        sep()
        print(f"  {cc(C.BRED + C.BOLD, '◉ ' + name)}")
        print(f"  {cc(C.DIM, desc)}")
        print(f"  {cc(C.BGREEN, '  Defensa:')} {cc(C.DIM, defensa)}")

    pause()


def https_explicado():
    header("¿Cómo HTTPS protege tus datos?", "Módulo 6 · TLS handshake paso a paso")
    step(1, "TCP Handshake",   "Se establece la conexión TCP al puerto 443 (SYN, SYN-ACK, ACK).")
    step(2, "ClientHello",
         "El cliente envía:\n"
         "  • Versiones TLS soportadas (TLS 1.2, TLS 1.3)\n"
         "  • Lista de cipher suites (ej: TLS_AES_256_GCM_SHA384)\n"
         "  • Número aleatorio del cliente (client random)")
    step(3, "ServerHello",
         "El servidor responde:\n"
         "  • Cipher suite elegida\n"
         "  • Número aleatorio del servidor (server random)\n"
         "  • Su certificado X.509 firmado por una CA")
    step(4, "Verificación del certificado",
         "El cliente verifica:\n"
         "  a) La CA que firmó el certificado es de confianza (está en el truststore del OS)\n"
         "  b) El CN/SAN del certificado coincide con el dominio visitado\n"
         "  c) El certificado no está expirado ni revocado (OCSP)")
    step(5, "Key Exchange",
         "Con TLS 1.3 se usa ECDHE (Elliptic Curve Diffie-Hellman Ephemeral):\n"
         "  • Ambos lados calculan independientemente un secreto compartido\n"
         "  • Nadie en el camino puede calcularlo (solo los dos extremos)\n"
         "  • 'Ephemeral' = nueva llave por sesión → Forward Secrecy")
    step(6, "Derivación de llaves de sesión",
         "Del secreto compartido + los randoms se derivan:\n"
         "  • Llave de cifrado cliente→servidor (AES-256)\n"
         "  • Llave de cifrado servidor→cliente (AES-256)\n"
         "  • Llaves de integridad (MAC keys)")
    step(7, "Canal seguro",
         "A partir de aquí, todos los datos van cifrados con AES-GCM.\n"
         "  • AES cifra los datos (confidencialidad)\n"
         "  • GCM verifica que no fueron alterados (integridad)\n"
         "  • ECDHE garantiza Forward Secrecy")

    callout("info", "Forward Secrecy",
            "Incluso si en el futuro alguien obtiene la llave privada del servidor,\n"
            "NO puede descifrar sesiones pasadas — porque las llaves de sesión\n"
            "son efímeras y únicas por conexión.")
    pause()


def vlans_y_segmentacion():
    header("VLANs y Segmentación de Red", "Módulo 5 · Seguridad de capa 2")
    step(1, "¿Qué es una VLAN?",
         "Virtual LAN: divide lógicamente una red física en múltiples redes aisladas.\n"
         "Los dispositivos en distintas VLANs no se ven entre sí sin un router.")
    step(2, "¿Por qué usar VLANs?",
         "• Seguridad: VLAN de contabilidad separada de VLAN de producción\n"
         "• Rendimiento: reduce el dominio de broadcast\n"
         "• Administración: agrupa dispositivos lógicamente sin mover cables")
    step(3, "VLAN de gestión",
         "Siempre crea una VLAN separada para administrar switches y routers.\n"
         "Nunca administres dispositivos de red desde la VLAN de usuarios.")
    step(4, "Trunk vs Access ports",
         "Access port: conecta un dispositivo final. Solo una VLAN.\n"
         "Trunk port: conecta switches entre sí. Lleva múltiples VLANs (802.1Q tagging).")
    step(5, "Inter-VLAN routing",
         "Para que dos VLANs se comuniquen necesitas un router o switch L3.\n"
         "Router-on-a-stick: un router con sub-interfaces, una por VLAN.")

    callout("info", "Segmentación como defensa",
            "Si un atacante compromete un dispositivo en la VLAN de invitados,\n"
            "no puede acceder a los servidores en la VLAN de producción.\n"
            "Principio de mínimo privilegio aplicado a la red.")
    pause()


def run():
    while True:
        opts = [
            "Tríada CIA (Confidencialidad, Integridad, Disponibilidad)",
            "Tipos de ataques comunes (Phishing, MITM, DDoS, SQLi, XSS, Ransomware...)",
            "¿Cómo HTTPS protege tus datos? (TLS handshake paso a paso)",
            "VLANs y segmentación de red",
        ]
        choice = menu("Módulo 6 · Ciberseguridad", opts)
        if choice == -1:
            break
        [triada_cia, tipos_ataque, https_explicado, vlans_y_segmentacion][choice]()
