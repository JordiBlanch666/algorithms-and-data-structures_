import os
import sys

# ── ANSI colors ──────────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    # Foreground
    BLACK  = "\033[30m"
    RED    = "\033[31m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    BLUE   = "\033[34m"
    MAGENTA= "\033[35m"
    CYAN   = "\033[36m"
    WHITE  = "\033[37m"
    # Bright
    BRED   = "\033[91m"
    BGREEN = "\033[92m"
    BYELLOW= "\033[93m"
    BBLUE  = "\033[94m"
    BMAGENTA="\033[95m"
    BCYAN  = "\033[96m"
    BWHITE = "\033[97m"
    # Background
    BG_BLACK  = "\033[40m"
    BG_BLUE   = "\033[44m"
    BG_GREEN  = "\033[42m"

def _supports_color():
    return sys.stdout.isatty() and os.name != "nt" or os.environ.get("FORCE_COLOR")

USE_COLOR = True  # Windows Terminal / VS Code soportan ANSI

def cc(color, text):
    return f"{color}{text}{C.RESET}" if USE_COLOR else text

# ── Impresión estandarizada ───────────────────────────────────────────────────
SEP = "─" * 64

def header(title, subtitle=""):
    print(f"\n{cc(C.BOLD + C.BBLUE, '┌' + '─'*62 + '┐')}")
    print(f"{cc(C.BOLD + C.BBLUE, '│')} {cc(C.BOLD + C.BWHITE, title.center(62))} {cc(C.BOLD + C.BBLUE, '│')}")
    if subtitle:
        print(f"{cc(C.BOLD + C.BBLUE, '│')} {cc(C.DIM, subtitle.center(62))} {cc(C.BOLD + C.BBLUE, '│')}")
    print(f"{cc(C.BOLD + C.BBLUE, '└' + '─'*62 + '┘')}\n")

def section(title):
    print(f"\n{cc(C.BOLD + C.BCYAN, '── ' + title + ' ' + '─'*(max(0, 52 - len(title))))}\n")

def step(n, title, text=""):
    bullet = cc(C.BOLD + C.BBLUE, f"[{n}]")
    print(f"  {bullet} {cc(C.BOLD, title)}")
    if text:
        for line in text.splitlines():
            print(f"      {cc(C.DIM, line)}")

def substep(letter, title, text=""):
    bullet = cc(C.BMAGENTA, f"  {letter}.")
    print(f"  {bullet} {cc(C.BOLD, title)}")
    if text:
        for line in text.splitlines():
            print(f"       {cc(C.DIM, line)}")

def info(msg):    print(f"  {cc(C.BBLUE, 'ℹ')}  {msg}")
def ok(msg):      print(f"  {cc(C.BGREEN, '✔')}  {msg}")
def warn(msg):    print(f"  {cc(C.BYELLOW, '⚠')}  {msg}")
def error(msg):   print(f"  {cc(C.BRED, '✘')}  {msg}")
def result(k, v): print(f"  {cc(C.CYAN, k+':'):<28} {cc(C.BWHITE, str(v))}")
def sep():        print(f"\n  {cc(C.DIM, SEP)}\n")

def callout(kind, label, text):
    colors = {"info": C.BBLUE, "warn": C.BYELLOW, "ok": C.BGREEN, "danger": C.BRED}
    c = colors.get(kind, C.DIM)
    print(f"\n  {cc(c, '▌')} {cc(C.BOLD + c, label.upper())}")
    for line in text.splitlines():
        print(f"  {cc(c, '▌')} {cc(C.DIM, line)}")
    print()

def ask(prompt, options=None):
    if options:
        for i, opt in enumerate(options, 1):
            print(f"    {cc(C.BCYAN, str(i)+'.')} {opt}")
        while True:
            try:
                raw = input(f"\n  {cc(C.BYELLOW, '›')} Opción: ").strip()
                idx = int(raw) - 1
                if 0 <= idx < len(options):
                    return idx, options[idx]
            except (ValueError, KeyboardInterrupt):
                pass
            warn("Opción inválida, intenta de nuevo.")
    else:
        try:
            return input(f"\n  {cc(C.BYELLOW, '›')} {prompt}: ").strip()
        except KeyboardInterrupt:
            return ""

def menu(title, options, back_label="Volver al menú principal"):
    """Muestra menú y retorna el índice seleccionado (0-based). -1 = volver."""
    all_opts = options + [back_label]
    header(title)
    for i, opt in enumerate(all_opts, 1):
        if i == len(all_opts):
            print(f"    {cc(C.DIM, str(i) + '.')} {cc(C.DIM, opt)}")
        else:
            print(f"    {cc(C.BCYAN, str(i) + '.')} {opt}")
    while True:
        try:
            raw = input(f"\n  {cc(C.BYELLOW, '›')} Selecciona: ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(all_opts):
                return idx if idx < len(options) else -1
        except (ValueError, KeyboardInterrupt):
            return -1
        warn("Opción inválida.")

def pause():
    try:
        input(f"\n  {cc(C.DIM, '[Presiona Enter para continuar...]')}")
    except KeyboardInterrupt:
        pass

def clear():
    os.system("cls" if os.name == "nt" else "clear")
