"""
Banking System — 2nd semester OOP project.
Demonstrates encapsulation, inheritance, and polymorphism in one cohesive module.
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ── Abstract base class ───────────────────────────────────────────────────────

class Account(ABC):
    _counter = 0

    def __init__(self, holder: str, initial_balance: float = 0.0):
        Account._counter += 1
        self.__number = f"MX{Account._counter:05d}"
        self._holder = holder
        self.__balance = max(0.0, initial_balance)
        self.__history: list[str] = []
        self._log(f"Account opened with initial balance ${initial_balance:.2f}")

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def number(self) -> str:
        return self.__number

    @property
    def holder(self) -> str:
        return self._holder

    @property
    def balance(self) -> float:
        return self.__balance

    @property
    def history(self) -> list[str]:
        return list(self.__history)

    # ── Base operations ───────────────────────────────────────────────────────

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.__balance += amount
        self._log(f"Deposit    +${amount:>10.2f}  →  balance ${self.__balance:.2f}")

    def _deduct(self, amount: float) -> None:
        """Protected: used by subclasses to reduce the balance."""
        self.__balance -= amount

    @abstractmethod
    def withdraw(self, amount: float) -> None: ...

    @abstractmethod
    def account_type(self) -> str: ...

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.__history.append(f"[{ts}] {message}")

    def __repr__(self) -> str:
        return (
            f"{self.account_type()} | {self.number} | {self._holder} | "
            f"balance: ${self.__balance:.2f}"
        )


# ── Subclass: Savings Account ─────────────────────────────────────────────────

class SavingsAccount(Account):
    def __init__(self, holder: str, initial_balance: float = 0.0,
                 interest_rate: float = 0.04):
        super().__init__(holder, initial_balance)
        self.__interest_rate = interest_rate

    def account_type(self) -> str:
        return "Savings"

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.balance:
            raise ValueError(
                f"Insufficient funds. Available: ${self.balance:.2f}"
            )
        self._deduct(amount)
        self._log(f"Withdraw   -${amount:>10.2f}  →  balance ${self.balance:.2f}")

    def apply_interest(self) -> None:
        interest = self.balance * self.__interest_rate
        self.deposit(interest)
        self._log(f"Interest ({self.__interest_rate:.0%}) applied: +${interest:.2f}")


# ── Subclass: Checking Account ────────────────────────────────────────────────

class CheckingAccount(Account):
    def __init__(self, holder: str, initial_balance: float = 0.0,
                 overdraft_limit: float = 0.0):
        super().__init__(holder, initial_balance)
        self.__overdraft_limit = overdraft_limit

    def account_type(self) -> str:
        return "Checking"

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        available = self.balance + self.__overdraft_limit
        if amount > available:
            raise ValueError(
                f"Limit exceeded. Available with overdraft: ${available:.2f}"
            )
        self._deduct(amount)
        self._log(
            f"Withdraw   -${amount:>10.2f}  →  balance ${self.balance:.2f}"
            + ("  [OVERDRAFT]" if self.balance < 0 else "")
        )


if __name__ == "__main__":
    print("══ Banking System ══════════════════════════════════\n")

    savings = SavingsAccount("Jordi Blanch", 1_000.0, interest_rate=0.05)
    savings.deposit(500)
    savings.withdraw(200)
    savings.apply_interest()

    print(savings)
    print("\n  History:")
    for entry in savings.history:
        print(f"    {entry}")

    print()

    checking = CheckingAccount("Ana García", 200.0, overdraft_limit=300.0)
    checking.withdraw(400)
    print(checking)
    print("\n  History:")
    for entry in checking.history:
        print(f"    {entry}")
