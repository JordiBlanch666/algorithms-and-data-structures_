"""
Encapsulación — segundo pilar de la POO.

Los atributos privados (__ prefijo) solo se modifican a través
de métodos controlados, protegiendo la integridad del objeto.
"""


class CuentaBancaria:
    def __init__(self, titular: str, saldo_inicial: float = 0.0):
        self._titular = titular          # protegido: uso interno
        self.__saldo = saldo_inicial     # privado: acceso solo por métodos

    # ── Propiedades (getters) ─────────────────────────────────────────────────

    @property
    def titular(self) -> str:
        return self._titular

    @property
    def saldo(self) -> float:
        return self.__saldo

    # ── Operaciones controladas ───────────────────────────────────────────────

    def depositar(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo.")
        self.__saldo += monto
        print(f"  Depósito ${monto:.2f} → saldo: ${self.__saldo:.2f}")

    def retirar(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo.")
        if monto > self.__saldo:
            raise ValueError("Saldo insuficiente.")
        self.__saldo -= monto
        print(f"  Retiro  ${monto:.2f} → saldo: ${self.__saldo:.2f}")

    def __repr__(self) -> str:
        return f"CuentaBancaria(titular='{self._titular}', saldo=${self.__saldo:.2f})"


if __name__ == "__main__":
    cuenta = CuentaBancaria("Jordi Blanch", 500.0)
    print(cuenta)
    cuenta.depositar(1000)
    cuenta.retirar(200)

    # Demostración de encapsulación: el atributo privado no es accesible
    try:
        print(cuenta.__saldo)          # AttributeError esperado
    except AttributeError as e:
        print(f"\n  Encapsulación activa: {e}")

    print(f"\n  Saldo via property: ${cuenta.saldo:.2f}")
