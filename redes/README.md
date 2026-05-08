# Networking Fundamentals

Second semester — Software Engineering · Hybridge

Four progressive scripts that cover how computers find each other,
connect, and exchange data. All use Python's standard library — no pip required.

## Scripts

| # | File | Concept | What it does |
|---|------|---------|--------------|
| 1 | `01_network_info.py` | DNS & addressing | Resolves hostnames to IPs, reverse lookup |
| 2 | `02_tcp_client_server.py` | TCP sockets | Echo server + client over localhost |
| 3 | `03_http_client.py` | HTTP protocol | Makes real GET requests, parses responses |
| 4 | `04_port_scanner.py` | Ports & services | Concurrent scanner with thread pool |

## Concepts covered

| Concept | Where you see it |
|---------|-----------------|
| IP addressing | `01_network_info.py` — `gethostbyname()` |
| DNS resolution | `01_network_info.py` — forward & reverse lookup |
| TCP handshake | `02_tcp_client_server.py` — `bind / listen / accept / connect` |
| Client-server model | `02_tcp_client_server.py` — two roles, one script |
| HTTP request/response | `03_http_client.py` — status codes, headers, body |
| REST APIs | `03_http_client.py` — JSON from JSONPlaceholder |
| Well-known ports | `04_port_scanner.py` — port→service lookup table |
| Concurrency | `04_port_scanner.py` — `ThreadPoolExecutor` for parallel scanning |

## How to run

```bash
# Network info (requires internet)
python redes/01_network_info.py

# TCP server/client — open two terminals
python redes/02_tcp_client_server.py server   # terminal 1
python redes/02_tcp_client_server.py client   # terminal 2

# HTTP client (requires internet)
python redes/03_http_client.py

# Port scanner (localhost only — safe)
python redes/04_port_scanner.py
```
