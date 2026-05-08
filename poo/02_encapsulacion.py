"""
Encapsulation — second pillar of OOP.

Private attributes (__ prefix) can only be modified through controlled
methods, protecting the integrity of the object's internal state.
"""


class BankAccount:
    def __init__(self, holder: str, initial_balance: float = 0.0):
        self._holder = holder            # protected: internal use
        self.__balance = initial_balance  # private: only accessible via methods

    # ── Properties (getters) ──────────────────────────────────────────────────

    @property
    def holder(self) -> str:
        return self._holder

    @property
    def balance(self) -> float:
        return self.__balance

    # ── Controlled operations ─────────────────────────────────────────────────

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.__balance += amount
        print(f"  Deposit  +${amount:.2f} → balance: ${self.__balance:.2f}")

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.__balance:
            raise ValueError("Insufficient funds.")
        self.__balance -= amount
        print(f"  Withdraw -${amount:.2f} → balance: ${self.__balance:.2f}")

    def __repr__(self) -> str:
        return f"BankAccount(holder='{self._holder}', balance=${self.__balance:.2f})"


if __name__ == "__main__":
    account = BankAccount("Jordi Blanch", 500.0)
    print(account)
    account.deposit(1000)
    account.withdraw(200)

    # Demonstrating encapsulation: the private attribute is not directly accessible
    try:
        print(account.__balance)       # AttributeError expected
    except AttributeError as e:
        print(f"\n  Encapsulation active: {e}")

    print(f"\n  Balance via property: ${account.balance:.2f}")
