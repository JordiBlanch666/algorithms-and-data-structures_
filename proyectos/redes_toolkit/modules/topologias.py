from .utils import (header, section, step, result, sep, info,
                    callout, pause, C, cc, menu)

# ── Módulo 1: Topologías de red ───────────────────────────────────────────────

TOPOLOGIAS = [
    {
        "name": "Bus",
        "ascii": r"""
  [PC1]───[PC2]───[PC3]───[PC4]
  ════════════════════════════
         Cable central (bus)
""",
        "desc": "Todos los dispositivos comparten un único cable central.",
        "ventajas": ["Simple y barato de instalar", "Fácil de expandir en redes pequeñas"],
        "desventajas": ["Un corte en el cable = toda la red cae", "Colisiones frecuentes",
                        "Difícil de diagnosticar", "Rendimiento decrece al añadir dispositivos"],
        "uso": "Redes antiguas (legacy), no se usa en instalaciones nuevas.",
        "color": C.DIM,
    },
    {
        "name": "Estrella",
        "ascii": r"""
       [PC1]
         │
  [PC3]──[SW]──[PC2]
         │
       [PC4]
""",
        "desc": "Todos los dispositivos se conectan a un switch/hub central.",
        "ventajas": ["Fallo de un nodo no afecta a los demás", "Fácil de diagnosticar",
                     "Alta velocidad con switches", "La más usada en LANs modernas"],
        "desventajas": ["Dependencia del switch central — si cae, toda la red cae",
                        "Más cable que bus"],
        "uso": "Redes domésticas, oficinas, datacenters — LA topología estándar hoy.",
        "color": C.BGREEN,
    },
    {
        "name": "Anillo (Ring)",
        "ascii": r"""
    [PC1]──[PC2]
      │         │
    [PC4]──[PC3]
""",
        "desc": "Los dispositivos forman un círculo. Los datos viajan en una dirección.",
        "ventajas": ["Rendimiento predecible con Token Ring",
                     "Sin colisiones (solo un token circula)"],
        "desventajas": ["Un fallo rompe el anillo completo", "Difícil de expandir",
                        "Obsoleto en redes físicas"],
        "uso": "Legacy (Token Ring IBM). Conceptualmente usado en SONET/SDH de fibra óptica.",
        "color": C.BYELLOW,
    },
    {
        "name": "Malla (Mesh)",
        "ascii": r"""
    [A]──────[B]
     │╲       │╲
     │  ╲     │  [C]
     │    ╲   │ ╱
    [D]──────[E]
""",
        "desc": "Cada nodo se conecta a múltiples (o todos) los demás nodos.",
        "ventajas": ["Alta redundancia — múltiples rutas", "Tolerante a fallos",
                     "Sin punto único de fallo en malla completa"],
        "desventajas": ["Costosa (muchos cables / interfaces)", "Compleja de gestionar"],
        "uso": "Datacenters, backbones de ISPs, redes militares, routers BGP en Internet.",
        "color": C.BBLUE,
    },
    {
        "name": "Árbol (Tree / Jerárquica)",
        "ascii": r"""
         [Core]
        /       \\
  [Dist-1]   [Dist-2]
   /    \\      /    \\
[Acc] [Acc] [Acc] [Acc]
""",
        "desc": "Estrella de estrellas. Organización jerárquica en capas.",
        "ventajas": ["Escalable", "Fácil de gestionar por secciones",
                     "Clara separación Core → Distribución → Acceso"],
        "desventajas": ["Dependencia del nodo raíz", "Más compleja que estrella simple"],
        "uso": "Empresas y campus: modelo de 3 capas Cisco (Core, Distribution, Access).",
        "color": C.BCYAN,
    },
    {
        "name": "Híbrida",
        "ascii": r"""
  [Mesh backbone ISP]
         │
     [Router]
         │
   [Star LAN]──[PC1]
         │
       [PC2]
""",
        "desc": "Combinación de dos o más topologías.",
        "ventajas": ["Flexibilidad", "Optimiza cada segmento para su necesidad"],
        "desventajas": ["Compleja de diseñar y administrar"],
        "uso": "Prácticamente toda red real: mesh en el backbone + estrella en las LAN.",
        "color": C.BMAGENTA,
    },
]


def ver_todas():
    header("Topologías de Red", "Módulo 1 · Fundamentos")
    for top in TOPOLOGIAS:
        print(f"\n  {cc(top['color'] + C.BOLD, '══ ' + top['name'] + ' ══')}")
        print(cc(C.BYELLOW, top["ascii"]))
        info(top["desc"])
        print(f"  {cc(C.BGREEN, '✔ Ventajas:')}")
        for v in top["ventajas"]:
            print(f"    • {v}")
        print(f"  {cc(C.BRED, '✘ Desventajas:')}")
        for d in top["desventajas"]:
            print(f"    • {d}")
        result("Uso real", top["uso"])
        print(f"\n  {cc(C.DIM, '─'*60)}")
    pause()


def comparacion_tabla():
    header("Tabla Comparativa de Topologías", "Módulo 1")
    sep()
    print(f"  {cc(C.BOLD, 'Topología'):<18} "
          f"{cc(C.BOLD, 'Coste'):<12} "
          f"{cc(C.BOLD, 'Redundancia'):<16} "
          f"{cc(C.BOLD, 'Escalabilidad'):<18} "
          f"{cc(C.BOLD, 'Uso hoy')}")
    print(f"  {'─'*16} {'─'*10} {'─'*14} {'─'*16} {'─'*20}")

    tabla = [
        ("Bus",         "Bajo",   "Ninguna",   "Baja",   "Obsoleto"),
        ("Estrella",    "Medio",  "Parcial",   "Alta",   "LAN doméstica/oficina"),
        ("Anillo",      "Medio",  "Media",     "Media",  "Legacy / SONET"),
        ("Malla",       "Alto",   "Muy alta",  "Media",  "Datacenter / ISP"),
        ("Árbol",       "Medio",  "Media",     "Muy alta","Empresa / campus"),
        ("Híbrida",     "Variable","Variable", "Alta",   "Toda red real"),
    ]

    colors = [C.DIM, C.BGREEN, C.BYELLOW, C.BBLUE, C.BCYAN, C.BMAGENTA]
    for (row, c) in zip(tabla, colors):
        name, coste, redund, escala, uso = row
        print(f"  {cc(c, name):<26} {coste:<12} {redund:<16} {escala:<18} {cc(C.DIM, uso)}")
    pause()


def modelo_3_capas():
    header("Modelo de 3 Capas Cisco", "Módulo 1 · Arquitectura empresarial")
    step(1, "Capa Core (núcleo)",
         "Velocidad máxima, sin políticas complejas.\n"
         "Switches de alta gama (Cisco Catalyst 9000, Nexus).\n"
         "Conecta los edificios / centros de datos entre sí.")
    step(2, "Capa Distribution (distribución)",
         "Agrega tráfico de la capa de acceso.\n"
         "Aplica políticas de routing, QoS, ACLs.\n"
         "Conecta VLANs entre sí.")
    step(3, "Capa Access (acceso)",
         "Conecta los dispositivos finales (PCs, teléfonos, impresoras).\n"
         "Aplica PoE para teléfonos IP y APs.\n"
         "Configura VLANs por puerto.")

    sep()
    callout("info", "Colapso de capas",
            "En redes pequeñas se 'colapsan' las 3 capas en 2 (Distribution + Access)\n"
            "o incluso en 1 solo switch. El modelo de 3 capas aplica a empresas medianas/grandes.")
    pause()


def run():
    while True:
        opts = [
            "Ver todas las topologías (Bus, Estrella, Anillo, Malla, Árbol, Híbrida)",
            "Tabla comparativa de topologías",
            "Modelo de 3 capas Cisco (Core, Distribution, Access)",
        ]
        choice = menu("Módulo 1 · Topologías de Red", opts)
        if choice == -1:
            break
        [ver_todas, comparacion_tabla, modelo_3_capas][choice]()
