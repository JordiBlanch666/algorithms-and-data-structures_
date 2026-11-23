from .utils import (header, step, result, sep, info,
                    callout, pause, C, cc, menu)

# ── Module 1: Network topologies ──────────────────────────────────────────────

TOPOLOGIES = [
    {
        "name": "Bus",
        "ascii": r"""
  [PC1]───[PC2]───[PC3]───[PC4]
  ════════════════════════════
         Central cable (bus)
""",
        "desc": "Every device shares a single central cable.",
        "pros": ["Simple and cheap to install", "Easy to extend in small networks"],
        "cons": ["One cable break = the whole network goes down", "Frequent collisions",
                 "Hard to troubleshoot", "Performance drops as devices are added"],
        "use": "Old (legacy) networks; not used in new installations.",
        "color": C.DIM,
    },
    {
        "name": "Star",
        "ascii": r"""
       [PC1]
         │
  [PC3]──[SW]──[PC2]
         │
       [PC4]
""",
        "desc": "Every device connects to a central switch/hub.",
        "pros": ["A failed node doesn't affect the others", "Easy to troubleshoot",
                 "High speed with switches", "The most common topology in modern LANs"],
        "cons": ["Depends on the central switch — if it fails, the whole network fails",
                 "Uses more cable than a bus"],
        "use": "Homes, offices, data centers — THE standard topology today.",
        "color": C.BGREEN,
    },
    {
        "name": "Ring",
        "ascii": r"""
    [PC1]──[PC2]
      │         │
    [PC4]──[PC3]
""",
        "desc": "Devices form a circle. Data travels in one direction.",
        "pros": ["Predictable performance with Token Ring",
                 "No collisions (only one token circulates)"],
        "cons": ["A single failure breaks the whole ring", "Hard to extend",
                 "Obsolete in physical networks"],
        "use": "Legacy (IBM Token Ring). Conceptually used in SONET/SDH fiber networks.",
        "color": C.BYELLOW,
    },
    {
        "name": "Mesh",
        "ascii": r"""
    [A]──────[B]
     │╲       │╲
     │  ╲     │  [C]
     │    ╲   │ ╱
    [D]──────[E]
""",
        "desc": "Each node connects to several (or all) other nodes.",
        "pros": ["High redundancy — multiple paths", "Fault tolerant",
                 "No single point of failure in a full mesh"],
        "cons": ["Expensive (many cables / interfaces)", "Complex to manage"],
        "use": "Data centers, ISP backbones, military networks, BGP routers on the Internet.",
        "color": C.BBLUE,
    },
    {
        "name": "Tree (Hierarchical)",
        "ascii": r"""
         [Core]
        /       \\
  [Dist-1]   [Dist-2]
   /    \\      /    \\
[Acc] [Acc] [Acc] [Acc]
""",
        "desc": "A star of stars. Hierarchical organization in layers.",
        "pros": ["Scalable", "Easy to manage section by section",
                 "Clear Core → Distribution → Access separation"],
        "cons": ["Depends on the root node", "More complex than a simple star"],
        "use": "Companies and campuses: Cisco's 3-layer model (Core, Distribution, Access).",
        "color": C.BCYAN,
    },
    {
        "name": "Hybrid",
        "ascii": r"""
  [ISP mesh backbone]
         │
     [Router]
         │
   [Star LAN]──[PC1]
         │
       [PC2]
""",
        "desc": "A combination of two or more topologies.",
        "pros": ["Flexibility", "Each segment is optimized for its needs"],
        "cons": ["Complex to design and manage"],
        "use": "Practically every real network: mesh in the backbone + star in the LANs.",
        "color": C.BMAGENTA,
    },
]


def show_all():
    header("Network Topologies", "Module 1 · Fundamentals")
    for top in TOPOLOGIES:
        print(f"\n  {cc(top['color'] + C.BOLD, '══ ' + top['name'] + ' ══')}")
        print(cc(C.BYELLOW, top["ascii"]))
        info(top["desc"])
        print(f"  {cc(C.BGREEN, '✔ Pros:')}")
        for v in top["pros"]:
            print(f"    • {v}")
        print(f"  {cc(C.BRED, '✘ Cons:')}")
        for d in top["cons"]:
            print(f"    • {d}")
        result("Real-world use", top["use"])
        print(f"\n  {cc(C.DIM, '─'*60)}")
    pause()


def comparison_table():
    header("Topology Comparison Table", "Module 1")
    sep()
    print(f"  {cc(C.BOLD, 'Topology'):<18} "
          f"{cc(C.BOLD, 'Cost'):<12} "
          f"{cc(C.BOLD, 'Redundancy'):<16} "
          f"{cc(C.BOLD, 'Scalability'):<18} "
          f"{cc(C.BOLD, 'Used today')}")
    print(f"  {'─'*16} {'─'*10} {'─'*14} {'─'*16} {'─'*20}")

    table = [
        ("Bus",     "Low",      "None",      "Low",       "Obsolete"),
        ("Star",    "Medium",   "Partial",   "High",      "Home/office LAN"),
        ("Ring",    "Medium",   "Medium",    "Medium",    "Legacy / SONET"),
        ("Mesh",    "High",     "Very high", "Medium",    "Data center / ISP"),
        ("Tree",    "Medium",   "Medium",    "Very high", "Company / campus"),
        ("Hybrid",  "Variable", "Variable",  "High",      "Every real network"),
    ]

    colors = [C.DIM, C.BGREEN, C.BYELLOW, C.BBLUE, C.BCYAN, C.BMAGENTA]
    for (row, c) in zip(table, colors):
        name, cost, redundancy, scale, use = row
        print(f"  {cc(c, name):<26} {cost:<12} {redundancy:<16} {scale:<18} {cc(C.DIM, use)}")
    pause()


def three_layer_model():
    header("Cisco 3-Layer Model", "Module 1 · Enterprise architecture")
    step(1, "Core layer",
         "Maximum speed, no complex policies.\n"
         "High-end switches (Cisco Catalyst 9000, Nexus).\n"
         "Connects buildings / data centers to each other.")
    step(2, "Distribution layer",
         "Aggregates traffic from the access layer.\n"
         "Applies routing policies, QoS and ACLs.\n"
         "Connects VLANs to each other.")
    step(3, "Access layer",
         "Connects end devices (PCs, phones, printers).\n"
         "Provides PoE for IP phones and access points.\n"
         "Configures VLANs per port.")

    sep()
    callout("info", "Collapsed layers",
            "Small networks 'collapse' the 3 layers into 2 (Distribution + Access)\n"
            "or even a single switch. The 3-layer model applies to medium/large companies.")
    pause()


def run():
    while True:
        opts = [
            "Show all topologies (Bus, Star, Ring, Mesh, Tree, Hybrid)",
            "Topology comparison table",
            "Cisco 3-layer model (Core, Distribution, Access)",
        ]
        choice = menu("Module 1 · Network Topologies", opts)
        if choice == -1:
            break
        [show_all, comparison_table, three_layer_model][choice]()
