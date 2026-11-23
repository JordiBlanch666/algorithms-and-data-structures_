import hashlib
import hmac
import base64
import secrets
from .utils import (header, section, step, result, sep, info, warn, ok,
                    callout, ask, pause, C, cc, menu)

# ── Module 7: Cryptography ────────────────────────────────────────────────────

def hash_calculator():
    header("Hash Calculator", "Module 7 · Data integrity")
    info("Hashing turns any data into a fixed-size digest. It only works one way.")
    sep()

    text = ask("Text to hash")
    if not text:
        return

    data = text.encode("utf-8")
    sep()
    section("Results")

    algos = [
        ("MD5",      hashlib.md5,      "128 bits · INSECURE for passwords, fine for quick checksums"),
        ("SHA-1",    hashlib.sha1,     "160 bits · Obsolete (vulnerable to collisions since 2017)"),
        ("SHA-256",  hashlib.sha256,   "256 bits · Current standard · Bitcoin, TLS, code signing"),
        ("SHA-512",  hashlib.sha512,   "512 bits · More security, slower"),
        ("SHA3-256", hashlib.sha3_256, "256 bits · SHA-2's successor, different internal design (Keccak)"),
        ("BLAKE2b",  hashlib.blake2b,  "Variable · Faster than SHA-256, secure, used for files"),
    ]

    for name, fn, note in algos:
        digest = fn(data).hexdigest()
        print(f"  {cc(C.BCYAN, name + ':')}")
        print(f"    {cc(C.BYELLOW, digest)}")
        print(f"    {cc(C.DIM, note)}")
        print()

    callout("info", "Avalanche effect",
            "Change ONE letter of the text and the hash changes COMPLETELY.\n"
            "Try it: 'hello' vs 'Hello' → totally different hashes.\n"
            "That's why you can't work out the original text from the hash.")
    pause()


def verify_integrity():
    header("Verify File / Text Integrity", "Module 7 · Hash comparison")
    info("Checks whether two texts (or a file's hash) are identical.")
    sep()
    t1 = ask("Original text / hash")
    t2 = ask("Text / hash to compare")
    if not t1 or not t2:
        return

    # Compare them directly as hashes
    if hmac.compare_digest(t1.lower().strip(), t2.lower().strip()):
        ok("The hashes ARE identical. Integrity verified.")
    else:
        # Hash both with SHA-256 and compare
        h1 = hashlib.sha256(t1.encode()).hexdigest()
        h2 = hashlib.sha256(t2.encode()).hexdigest()
        if hmac.compare_digest(h1, h2):
            ok("The texts are identical (SHA-256 matches).")
        else:
            warn("The data is DIFFERENT. The content was modified or the hashes don't match.")
            result("SHA-256 of input 1", h1)
            result("SHA-256 of input 2", h2)

    callout("info", "Why hmac.compare_digest?",
            "It prevents timing attacks: comparing character by character can leak information\n"
            "through how long the comparison takes. compare_digest always takes the same time.")
    pause()


def caesar_cipher():
    header("Caesar Cipher (educational)", "Module 7 · Classical cryptography")
    info("The Caesar cipher shifts every letter N positions in the alphabet.")
    info("Example with a shift of 3: A→D, B→E, Z→C")
    info("Historically used by Julius Caesar for military messages.")
    callout("warn", "Warning",
            "This cipher is trivially breakable (only 25 possible keys).\n"
            "It's shown only to illustrate monoalphabetic substitution.")
    sep()

    text = ask("Text")
    raw_n = ask("Shift (1–25)")
    try:
        n = int(raw_n) % 26
    except ValueError:
        warn("Invalid number.")
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

    encrypted = caesar(text, n)
    decrypted = caesar(encrypted, -n)

    sep()
    result("Original",  text)
    result("Encrypted", encrypted)
    result("Decrypted", decrypted)

    sep()
    section("Brute-force analysis (all 25 keys)")
    for i in range(1, 26):
        print(f"  [{i:>2}] {cc(C.DIM, caesar(text, i))}")
    pause()


def asymmetric_crypto_concepts():
    header("Asymmetric Cryptography (RSA / ECDSA)", "Module 7 · Public / private keys")
    step(1, "The key-exchange problem",
         "With symmetric encryption (AES): how do you send the key to the receiver without someone stealing it?\n"
         "Answer: asymmetric cryptography.")
    step(2, "Key pair",
         "Each participant generates ONE PAIR:\n"
         "  • PUBLIC key: you share it with the world. Anyone can encrypt with it.\n"
         "  • PRIVATE key: only you have it. Only you can decrypt what was encrypted with your public key.")
    step(3, "Secure communication flow",
         "1. Bob generates his key pair.\n"
         "2. Bob publishes his public key (in a certificate, on GitHub, etc.).\n"
         "3. Alice encrypts the message with Bob's PUBLIC KEY.\n"
         "4. Only Bob can decrypt it with his PRIVATE KEY.\n"
         "Not even Alice can decrypt what she encrypted — that guarantees privacy.")
    step(4, "Digital signatures (the other way around)",
         "To SIGN, Bob uses his PRIVATE KEY → everyone verifies with his PUBLIC KEY.\n"
         "If the signature checks out → the message came from Bob and wasn't altered (integrity + authenticity).")
    step(5, "TLS combines everything",
         "1. The server sends its certificate with its public key.\n"
         "2. The client uses RSA/ECDH to exchange a session key.\n"
         "3. From then on, everything is encrypted with AES (symmetric) — much faster.")

    sep()
    section("Key pair generation (conceptual simulation)")
    key_id = secrets.token_hex(8)
    pub_stub  = f"ssh-rsa AAAAB3NzaC1yc2E...{key_id}... user@host"
    priv_stub = f"-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAK...{key_id}...\n-----END RSA PRIVATE KEY-----"
    print(f"  {cc(C.BGREEN, 'Public key (share it):')}  {cc(C.DIM, pub_stub)}")
    print(f"  {cc(C.BRED,   'Private key (NEVER share it):')} {cc(C.DIM, priv_stub[:60] + '...')}")

    callout("warn", "Golden rule",
            "The private key NEVER leaves your machine.\n"
            "If it's compromised, your whole cryptographic identity is compromised.")
    pause()


def hmac_demo():
    header("HMAC — Message Authentication", "Module 7 · Integrity + authentication")
    info("HMAC combines a secret key with a hash to prove a message comes from who it claims.")
    sep()
    message = ask("Message")
    key     = ask("Shared secret key")
    if not message or not key:
        return

    h = hmac.new(key.encode(), message.encode(), hashlib.sha256)
    tag = h.hexdigest()

    sep()
    result("Message",     message)
    result("Key",         "*" * len(key))
    result("HMAC-SHA256", tag)

    sep()
    # Verify
    to_verify = ask("Message to verify (copy the original or modify it)")
    h2 = hmac.new(key.encode(), to_verify.encode(), hashlib.sha256)
    if hmac.compare_digest(h.hexdigest(), h2.hexdigest()):
        ok("Valid HMAC. The message was NOT modified and the key is correct.")
    else:
        warn("Invalid HMAC. The message was altered OR the key is different.")

    callout("info", "Where is HMAC used?",
            "JWTs (web tokens), session cookies, GitHub/Stripe webhooks,\n"
            "API message verification, backup integrity.")
    pause()


def base64_tool():
    header("Base64 — Binary-to-text encoding", "Module 7 · Encoding")
    info("Base64 is NOT encryption. It only turns bytes into ASCII text that's safe to transmit.")
    info("Used in: email attachments (MIME), JWTs, HTTP Basic auth, PEM certificates.")
    sep()
    opts = ["Encode text → Base64", "Decode Base64 → text"]
    idx, _ = ask("", opts)

    if idx == 0:
        text = ask("Text to encode")
        if text:
            encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
            result("Base64",          encoded)
            result("Original length", f"{len(text)} bytes")
            result("Encoded length",  f"{len(encoded)} bytes (+{len(encoded)-len(text)} overhead)")
    else:
        b64 = ask("Base64 to decode")
        try:
            decoded = base64.b64decode(b64 + "==").decode("utf-8")
            result("Text", decoded)
        except Exception as e:
            warn(f"Error: {e}")
    pause()


def run():
    while True:
        opts = [
            "Hash calculator (MD5, SHA-1, SHA-256, SHA-512, SHA-3, BLAKE2)",
            "Verify integrity (compare two hashes / texts)",
            "Caesar cipher (classical substitution — educational)",
            "Asymmetric cryptography (RSA/ECDSA — concepts step by step)",
            "HMAC — Message authentication with a shared key",
            "Base64 — Encode and decode",
        ]
        choice = menu("Module 7 · Cryptography and Security", opts)
        if choice == -1:
            break
        [hash_calculator, verify_integrity, caesar_cipher,
         asymmetric_crypto_concepts, hmac_demo, base64_tool][choice]()
