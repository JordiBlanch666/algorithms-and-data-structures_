#!/usr/bin/env python3
"""
Networking Toolkit — reference CLI for Computer Networking Fundamentals
Based on a networking cookbook (8 modules + 12 troubleshooting guides)
"""
import sys
import os

# Make sure the project folder is on the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.utils import C, cc, clear, menu
import modules.topologies      as m1
import modules.osi_model       as m2
import modules.protocols       as m3
import modules.dns_tool        as m3b
import modules.subnetting      as m4
import modules.security        as m6
import modules.crypto_basics   as m7
import modules.troubleshooting as ts

BANNER = r"""
  ███╗   ██╗███████╗████████╗
  ████╗  ██║██╔════╝╚══██╔══╝
  ██╔██╗ ██║█████╗     ██║
  ██║╚██╗██║██╔══╝     ██║
  ██║ ╚████║███████╗   ██║
  ╚═╝  ╚═══╝╚══════╝   ╚═╝
        T O O L K I T  ·  v1.0
"""

MODULES = [
    ("M1  · History and network topologies",          m1.run),
    ("M2  · OSI and TCP/IP models",                   m2.run),
    ("M3  · Communication protocols",                 m3.run),
    ("M3b · DNS and name resolution",                 m3b.run),
    ("M4  · IP addressing and subnetting",            m4.run),
    ("M5/6· Cybersecurity (VLANs, CIA, attacks)",     m6.run),
    ("M7  · Cryptography (hashes, ciphers, HMAC)",    m7.run),
    ("TS  · Troubleshooting (12 guides)",             ts.run),
]


def splash():
    clear()
    print(cc(C.BBLUE + C.BOLD, BANNER))
    print(f"  {cc(C.DIM, 'Computer Networking Fundamentals — interactive cookbook')}")
    print(f"  {cc(C.DIM, '8 modules · DNS · Subnetting · Cryptography · Troubleshooting')}\n")


def main():
    splash()
    while True:
        try:
            opts = [label for label, _ in MODULES]
            choice = menu("Main Menu", opts, back_label="Exit")
            if choice == -1:
                print(f"\n  {cc(C.DIM, 'Goodbye.')}\n")
                sys.exit(0)
            clear()
            MODULES[choice][1]()
            clear()
            splash()
        except KeyboardInterrupt:
            print(f"\n\n  {cc(C.DIM, 'Goodbye.')}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
