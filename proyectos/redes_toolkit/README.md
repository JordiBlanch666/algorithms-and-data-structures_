# Redes Toolkit

Herramienta de línea de comandos (CLI) en Python para estudiar y practicar **Fundamentos de Redes Computacionales** de forma interactiva. Cubre los 8 módulos del curso con herramientas funcionales: calculadora de subredes, consultas DNS reales, hashing criptográfico, y 12 guías de troubleshooting paso a paso.

---

## Módulos incluidos

| # | Módulo | Herramientas |
|---|--------|-------------|
| M1 | Historia y topologías | Bus, Estrella, Anillo, Malla, Árbol, modelo 3 capas Cisco |
| M2 | Modelos OSI y TCP/IP | 7 capas OSI, encapsulación, comparación OSI vs TCP/IP |
| M3 | Protocolos de comunicación | HTTP/S, DNS, DHCP, FTP, SMTP, SSH, TCP, UDP con pasos detallados |
| M3b | DNS y resolución de nombres | Resolución real, DNS inverso, jerarquía, tipos de registros |
| M4 | Direccionamiento IP y Subnetting | Calculadora IPv4/IPv6, divisor de subredes, conversores binario/CIDR |
| M6 | Ciberseguridad | Tríada CIA, tipos de ataques, TLS handshake paso a paso, VLANs |
| M7 | Criptografía | SHA-256/MD5/BLAKE2, HMAC, cifrado César, RSA conceptual, Base64 |
| TS | Troubleshooting (12 guías) | Diagnóstico interactivo desde sin conectividad hasta comandos avanzados |

---

## Instalación y uso

No requiere dependencias externas. Solo Python 3.8+.

```bash
git clone https://github.com/JordiBlanch666/algorithms-and-data-structures_.git
cd algorithms-and-data-structures_/proyectos/redes_toolkit
python main.py
```

---

## Ejemplos de uso

### Calculadora de subredes

```
Entrada: 192.168.10.45/26

Dirección de red:       192.168.10.0
Broadcast:              192.168.10.63
Primera IP de host:     192.168.10.1
Última IP de host:      192.168.10.62
Máscara de subred:      255.255.255.192
Wildcard:               0.0.0.63
Hosts utilizables:      62

IP (binario):  11000000.10101000.00001010.00101101
Máscara:       11111111.11111111.11111111.11000000
```

### Resolución DNS real

```
Dominio: github.com

IPv4 (registro A):      140.82.112.4
Tiempo de resolución:   12.3 ms

Proceso:
  [1] Caché local — buscó en caché del SO
  [2] Resolver recursivo — consultó al DNS configurado
  [3] Servidor raíz — preguntó quién maneja .com
  [4] Servidor TLD — indicó el autoritativo de github.com
  [5] Respuesta final — 140.82.112.4
```

### Calculadora de hashes

```
Texto: Hola mundo

MD5:     ac5af69e4a3afd07fbbfd09955e06ef7
SHA-1:   f3a55620975aaac73ec05cba64e58ffe21c7734f
SHA-256: ca8f60b2cc7f05837d98b208b57fb6481553fc5...
SHA-512: 17e71f6ae96ae0e890b1e40b1f93d7d3...
```

---

## Estructura del proyecto

```
redes_toolkit/
├── main.py                   # Menú principal
└── modules/
    ├── utils.py              # Colores, menús, impresión estándar
    ├── topologias.py         # M1: Topologías de red
    ├── osi_model.py          # M2: Modelo OSI y TCP/IP
    ├── protocolos.py         # M3: Protocolos de comunicación
    ├── dns_tool.py           # M3b: DNS y resolución de nombres
    ├── subnetting.py         # M4: IP y subnetting
    ├── seguridad.py          # M6: Ciberseguridad
    ├── criptografia.py       # M7: Criptografía
    └── troubleshooting.py    # T1–T12: Guías de diagnóstico
```

---

## Guías de Troubleshooting

| # | Guía | Qué cubre |
|---|------|-----------|
| T1 | Sin conectividad | Árbol interactivo: físico → IP → gateway → DNS |
| T2 | Red lenta | Latencia, traceroute, pérdida de paquetes, QoS |
| T3 | IP / DHCP | DORA, conflictos de IP, IP estática manual |
| T4 | DNS | Flush caché, DNS alternativo, nslookup, dig |
| T5 | HTTP / HTTPS | Códigos de error, curl, cabeceras de seguridad |
| T6 | Seguridad | nmap, netstat, tcpdump, firewall, logs |
| T7 | Certificados SSL | Vencimiento, cadena CA, Let's Encrypt, TLS 1.3 |
| T8 | WiFi y señal | dBm, canales, 2.4 vs 5 GHz, interferencias |
| T9 | Correo / spam | SPF, DKIM, DMARC, blacklists, logs SMTP |
| T10 | Problemas cotidianos | VPN, conflictos IP, sitio caído, SSH |
| T11 | Seguridad práctica | Checklist: 2FA, contraseñas, backups 3-2-1 |
| T12 | Comandos avanzados | ping, traceroute, nmap, tcpdump, iperf3 |

---

## Tecnologías

- **Python 3.8+** — sin dependencias externas
- `ipaddress` — cálculos IPv4/IPv6
- `hashlib` — MD5, SHA-1, SHA-256, SHA-512, SHA-3, BLAKE2
- `socket` — resolución DNS real
- `hmac` — autenticación de mensajes
- `base64` — codificación

---

## Autor

**Jordi Yashua Contreras Blanch**  
Ingeniería en Software · Fundamentos de Redes Computacionales
