#!/usr/bin/env python3
"""
Redes Toolkit — CLI de referencia para Fundamentos de Redes Computacionales
Basado en el Cookbook de Redes (8 módulos + 12 guías de troubleshooting)
"""
import sys
import os

# Asegurar que el directorio padre está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.utils import (header, section, info, sep, pause,
                            C, cc, clear, menu)
import modules.topologias      as m1
import modules.osi_model       as m2
import modules.protocolos      as m3
import modules.dns_tool        as m3b
import modules.subnetting      as m4
import modules.seguridad       as m6
import modules.criptografia    as m7
import modules.troubleshooting as ts

BANNER = r"""
  ██████╗ ███████╗██████╗ ███████╗███████╗
  ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝
  ██████╔╝█████╗  ██║  ██║█████╗  ███████╗
  ██╔══██╗██╔══╝  ██║  ██║██╔══╝  ╚════██║
  ██║  ██║███████╗██████╔╝███████╗███████║
  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚══════╝
        T O O L K I T  ·  v1.0
"""

MODULOS = [
    ("M1  · Historia y topologías de red",          m1.run),
    ("M2  · Modelos OSI y TCP/IP",                  m2.run),
    ("M3  · Protocolos de comunicación",            m3.run),
    ("M3b · DNS y resolución de nombres",           m3b.run),
    ("M4  · Direccionamiento IP y Subnetting",      m4.run),
    ("M5/6· Ciberseguridad (VLANs, CIA, ataques)",  m6.run),
    ("M7  · Criptografía (hashes, cifrado, HMAC)",  m7.run),
    ("TS  · Troubleshooting (12 guías)",            ts.run),
]


def splash():
    clear()
    print(cc(C.BBLUE + C.BOLD, BANNER))
    print(f"  {cc(C.DIM, 'Fundamentos de Redes Computacionales — Cookbook interactivo')}")
    print(f"  {cc(C.DIM, '8 módulos · DNS · Subnetting · Criptografía · Troubleshooting')}\n")


def main():
    splash()
    while True:
        try:
            opts = [label for label, _ in MODULOS]
            choice = menu("Menú Principal", opts, back_label="Salir")
            if choice == -1:
                print(f"\n  {cc(C.DIM, 'Hasta luego.')}\n")
                sys.exit(0)
            clear()
            MODULOS[choice][1]()
            clear()
            splash()
        except KeyboardInterrupt:
            print(f"\n\n  {cc(C.DIM, 'Hasta luego.')}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
