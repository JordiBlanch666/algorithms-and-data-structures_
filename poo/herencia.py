"""
Sistema Bancario — proyecto de 2do cuatrimestre.
Demuestra encapsulación, herencia y polimorfismo en un solo módulo.
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ── Clase base abstracta ──────────────────────────────────────────────────────

class Cuenta(ABC):
    _contador = 0

    def __init__(self, titular: str, saldo_inicial: float = 0.0):
        Cuenta._contador += 1
        self.__numero = f"MX{Cuenta._contador:05d}"
        self._titular = titular
        self.__saldo = max(0.0, saldo_inicial)
        self.__historial: list[str] = []
        self._registrar(f"Cuenta abierta con saldo inicial ${saldo_inicial:.2f}")

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def numero(self) -> str:
        return self.__numero

    @property
    def titular(self) -> str:
        return self._titular

    @property
    def saldo(self) -> float:
        return self.__saldo

    @property
    def historial(self) -> list[str]:
        return list(self.__historial)

    # ── Operaciones base ──────────────────────────────────────────────────────

    def depositar(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo.")
        self.__saldo += monto
        self._registrar(f"Depósito    +${monto:>10.2f}  →  saldo ${self.__saldo:.2f}")

    def _descontar(self, monto: float) -> None:
        """Método protegido: usado por las subclases para retirar."""
        self.__saldo -= monto

    @abstractmethod
    def retirar(self, monto: float) -> None: ...

    @abstractmethod
    def tipo(self) -> str: ...

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _registrar(self, mensaje: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.__historial.append(f"[{ts}] {mensaje}")

    def __repr__(self) -> str:
        return (
            f"{self.tipo()} | {self.numero} | {self._titular} | "
            f"saldo: ${self.__saldo:.2f}"
        )


# ── Subclase: Cuenta de Ahorro ────────────────────────────────────────────────

class CuentaAhorro(Cuenta):
    def __init__(self, titular: str, saldo_inicial: float = 0.0,
                 tasa_interes: float = 0.04):
        super().__init__(titular, saldo_inicial)
        self.__tasa = tasa_interes

    def tipo(self) -> str:
        return "Ahorro"

    def retirar(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo.")
        if monto > self.saldo:
            raise ValueError(
                f"Saldo insuficiente. Disponible: ${self.saldo:.2f}"
            )
        self._descontar(monto)
        self._registrar(f"Retiro      -${monto:>10.2f}  →  saldo ${self.saldo:.2f}")

    def aplicar_interes(self) -> None:
        interes = self.saldo * self.__tasa
        self.depositar(interes)
        self._registrar(f"Interés ({self.__tasa:.0%}) aplicado: +${interes:.2f}")


# ── Subclase: Cuenta Corriente ────────────────────────────────────────────────

class CuentaCorriente(Cuenta):
    def __init__(self, titular: str, saldo_inicial: float = 0.0,
                 limite_sobregiro: float = 0.0):
        super().__init__(titular, saldo_inicial)
        self.__limite_sobregiro = limite_sobregiro

    def tipo(self) -> str:
        return "Corriente"

    def retirar(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo.")
        disponible = self.saldo + self.__limite_sobregiro
        if monto > disponible:
            raise ValueError(
                f"Límite excedido. Disponible con sobregiro: ${disponible:.2f}"
            )
        self._descontar(monto)
        self._registrar(
            f"Retiro      -${monto:>10.2f}  →  saldo ${self.saldo:.2f}"
            + ("  [SOBREGIRO]" if self.saldo < 0 else "")
        )


if __name__ == "__main__":
    print("══ Sistema Bancario ════════════════════════════════\n")

    ahorro = CuentaAhorro("Jordi Blanch", 1_000.0, tasa_interes=0.05)
    ahorro.depositar(500)
    ahorro.retirar(200)
    ahorro.aplicar_interes()

    print(ahorro)
    print("\n  Historial:")
    for linea in ahorro.historial:
        print(f"    {linea}")

    print()

    corriente = CuentaCorriente("Ana García", 200.0, limite_sobregiro=300.0)
    corriente.retirar(400)
    print(corriente)
    print("\n  Historial:")
    for linea in corriente.historial:
        print(f"    {linea}")
