import hashlib
import hmac
import base64
import os
import secrets
from .utils import (header, section, step, result, sep, info, warn, ok,
                    callout, ask, pause, C, cc, menu)

# ── Módulo 7: Criptografía ────────────────────────────────────────────────────

def calcular_hash():
    header("Calculadora de Hashes", "Módulo 7 · Integridad de datos")
    info("El hashing convierte cualquier dato en un resumen de tamaño fijo. Es de una sola vía.")
    sep()

    texto = ask("Texto a hashear")
    if not texto:
        return

    data = texto.encode("utf-8")
    sep()
    section("Resultados")

    algos = [
        ("MD5",     hashlib.md5,    "128 bits · INSEGURO para contraseñas, útil para checksums rápidos"),
        ("SHA-1",   hashlib.sha1,   "160 bits · Obsoleto (vulnerable a colisiones desde 2017)"),
        ("SHA-256", hashlib.sha256, "256 bits · Estándar actual · Bitcoin, TLS, código firmado"),
        ("SHA-512", hashlib.sha512, "512 bits · Mayor seguridad, más lento"),
        ("SHA3-256",hashlib.sha3_256,"256 bits · Sucesor de SHA-2, diferente diseño interno (Keccak)"),
        ("BLAKE2b", hashlib.blake2b, "Variable · Más rápido que SHA-256, seguro, usado en archivos"),
    ]

    for name, fn, note in algos:
        digest = fn(data).hexdigest()
        print(f"  {cc(C.BCYAN, name + ':')}")
        print(f"    {cc(C.BYELLOW, digest)}")
        print(f"    {cc(C.DIM, note)}")
        print()

    callout("info", "Propiedad de avalancha",
            "Cambia UNA letra en el texto y el hash cambia COMPLETAMENTE.\n"
            "Prueba: 'hola' vs 'Hola' → hashes totalmente distintos.\n"
            "Esto garantiza que no puedes adivinar el texto original desde el hash.")
    pause()


def verificar_integridad():
    header("Verificar Integridad de Archivo / Texto", "Módulo 7 · Comparación de hashes")
    info("Comprueba si dos textos (o el hash de un archivo) son idénticos.")
    sep()
    t1 = ask("Texto / hash original")
    t2 = ask("Texto / hash a comparar")
    if not t1 or not t2:
        return

    # Comparar como hashes directos
    if hmac.compare_digest(t1.lower().strip(), t2.lower().strip()):
        ok("Los hashes SON idénticos. Integridad verificada.")
    else:
        # Hashear ambos con SHA-256 y comparar
        h1 = hashlib.sha256(t1.encode()).hexdigest()
        h2 = hashlib.sha256(t2.encode()).hexdigest()
        if hmac.compare_digest(h1, h2):
            ok("Los textos son idénticos (SHA-256 coincide).")
        else:
            warn("Los datos son DIFERENTES. El contenido fue modificado o los hashes no coinciden.")
            result("SHA-256 de entrada 1", h1)
            result("SHA-256 de entrada 2", h2)

    callout("info", "¿Por qué hmac.compare_digest?",
            "Previene timing attacks: comparar carácter a carácter puede revelar info\n"
            "al medir cuánto tarda la comparación. compare_digest tarda siempre lo mismo.")
    pause()


def cifrado_cesar():
    header("Cifrado César (educativo)", "Módulo 7 · Criptografía clásica")
    info("El cifrado César desplaza cada letra N posiciones en el alfabeto.")
    info("Ejemplo con desplazamiento 3: A→D, B→E, Z→C")
    info("Históricamente usado por Julio César para mensajes militares.")
    callout("warn", "Advertencia",
            "Este cifrado es trivialmente rompible (solo 25 combinaciones posibles).\n"
            "Se muestra solo para ilustrar el concepto de sustitución monoalfabética.")
    sep()

    texto = ask("Texto")
    raw_n  = ask("Desplazamiento (1–25)")
    try:
        n = int(raw_n) % 26
    except ValueError:
        warn("Número inválido.")
        pause()
        return

    def caesar(text, shift):
        result_chars = []
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result_chars.append(chr((ord(ch) - base + shift) % 26 + base))
            else:
                result_chars.append(ch)
        return "".join(result_chars)

    cifrado    = caesar(texto, n)
    descifrado = caesar(cifrado, -n)

    sep()
    result("Original",   texto)
    result("Cifrado",    cifrado)
    result("Descifrado", descifrado)

    sep()
    section("Análisis de fuerza bruta (todas las 25 combinaciones)")
    for i in range(1, 26):
        print(f"  [{i:>2}] {cc(C.DIM, caesar(texto, i))}")
    pause()


def cifrado_asimetrico_concepto():
    header("Criptografía Asimétrica (RSA / ECDSA)", "Módulo 7 · Llave pública / privada")
    step(1, "El problema del intercambio de llaves",
         "Con cifrado simétrico (AES): ¿cómo le mandas la llave al receptor sin que alguien la robe?\n"
         "Respuesta: criptografía asimétrica.")
    step(2, "Par de llaves",
         "Cada participante genera UN PAR:\n"
         "  • Llave PÚBLICA: la compartes con el mundo. Cualquiera puede cifrar con ella.\n"
         "  • Llave PRIVADA: solo tú la tienes. Solo tú puedes descifrar lo que cifran con tu pública.")
    step(3, "Flujo de comunicación segura",
         "1. Bob genera su par de llaves.\n"
         "2. Bob publica su llave pública (en un certificado, en GitHub, etc.).\n"
         "3. Alice cifra el mensaje con la LLAVE PÚBLICA de Bob.\n"
         "4. Solo Bob puede descifrarlo con su LLAVE PRIVADA.\n"
         "Ni la propia Alice puede descifrar lo que cifró — eso garantiza privacidad.")
    step(4, "Firmas digitales (al revés)",
         "Para FIRMAR, Bob usa su LLAVE PRIVADA → todos verifican con su LLAVE PÚBLICA.\n"
         "Si la firma verifica → el mensaje vino de Bob y no fue alterado (integridad + autenticidad).")
    step(5, "TLS lo combina todo",
         "1. El servidor manda su certificado con llave pública.\n"
         "2. El cliente usa RSA/ECDH para intercambiar una clave de sesión.\n"
         "3. A partir de ahí, todo se cifra con AES (simétrico) — más rápido.")

    sep()
    section("Generación de par de llaves (simulación conceptual)")
    key_id = secrets.token_hex(8)
    pub_stub  = f"ssh-rsa AAAAB3NzaC1yc2E...{key_id}... usuario@host"
    priv_stub = f"-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAK...{key_id}...\n-----END RSA PRIVATE KEY-----"
    print(f"  {cc(C.BGREEN, 'Llave pública (comparte):')}  {cc(C.DIM, pub_stub)}")
    print(f"  {cc(C.BRED,   'Llave privada (NUNCA compartas):')} {cc(C.DIM, priv_stub[:60] + '...')}")

    callout("warn", "Regla de oro",
            "La llave privada NUNCA sale de tu máquina.\n"
            "Comprometerla = comprometer toda tu identidad criptográfica.")
    pause()


def hmac_demo():
    header("HMAC — Autenticación de mensajes", "Módulo 7 · Integridad + autenticación")
    info("HMAC combina una llave secreta con el hash para verificar que el mensaje viene de quien dice.")
    sep()
    mensaje = ask("Mensaje")
    llave   = ask("Llave secreta compartida")
    if not mensaje or not llave:
        return

    h = hmac.new(llave.encode(), mensaje.encode(), hashlib.sha256)
    tag = h.hexdigest()

    sep()
    result("Mensaje",   mensaje)
    result("Llave",     "*" * len(llave))
    result("HMAC-SHA256", tag)

    sep()
    # Verificar
    msg_verificar = ask("Mensaje a verificar (copia el original o modifícalo)")
    h2 = hmac.new(llave.encode(), msg_verificar.encode(), hashlib.sha256)
    if hmac.compare_digest(h.hexdigest(), h2.hexdigest()):
        ok("HMAC válido. El mensaje NO fue modificado y la llave es correcta.")
    else:
        warn("HMAC inválido. El mensaje fue alterado O la llave es diferente.")

    callout("info", "¿Dónde se usa HMAC?",
            "JWTs (tokens web), cookies de sesión, webhooks de GitHub/Stripe,\n"
            "verificación de mensajes en APIs, integridad de backups.")
    pause()


def base64_tool():
    header("Base64 — Codificación binario a texto", "Módulo 7 · Codificación")
    info("Base64 NO es cifrado. Solo convierte bytes a texto ASCII seguro para transmisión.")
    info("Se usa en: adjuntos de email (MIME), JWTs, autenticación HTTP Basic, certificados PEM.")
    sep()
    opts = ["Codificar texto → Base64", "Decodificar Base64 → texto"]
    idx, _ = ask("", opts)

    if idx == 0:
        texto = ask("Texto a codificar")
        if texto:
            encoded = base64.b64encode(texto.encode("utf-8")).decode("ascii")
            result("Base64",    encoded)
            result("Longitud original", f"{len(texto)} bytes")
            result("Longitud codificada", f"{len(encoded)} bytes (+{len(encoded)-len(texto)} overhead)")
    else:
        b64 = ask("Base64 a decodificar")
        try:
            decoded = base64.b64decode(b64 + "==").decode("utf-8")
            result("Texto", decoded)
        except Exception as e:
            warn(f"Error: {e}")
    pause()


def run():
    while True:
        opts = [
            "Calculadora de hashes (MD5, SHA-1, SHA-256, SHA-512, SHA-3, BLAKE2)",
            "Verificar integridad (comparar dos hashes / textos)",
            "Cifrado César (sustitución clásica — educativo)",
            "Criptografía asimétrica (RSA/ECDSA — conceptos paso a paso)",
            "HMAC — Autenticación de mensajes con llave compartida",
            "Base64 — Codificar y decodificar",
        ]
        choice = menu("Módulo 7 · Criptografía y Seguridad", opts)
        if choice == -1:
            break
        [calcular_hash, verificar_integridad, cifrado_cesar,
         cifrado_asimetrico_concepto, hmac_demo, base64_tool][choice]()
