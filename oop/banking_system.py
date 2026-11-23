"""
Banking System — 2nd semester OOP integrating project.

This module ties together all four OOP pillars in one cohesive example:

  ENCAPSULATION  — __balance is private; only deposit/withdraw can touch it.
  INHERITANCE    — SavingsAccount and CheckingAccount reuse Account's logic.
  POLYMORPHISM   — withdraw() does something different in each subclass.
  ABSTRACTION    — Account is an ABC; you can't instantiate it directly.

Why a banking system? Because the rules are immediately intuitive:
you can't have a negative balance in a savings account, an overdraft
has a limit, and every transaction should leave a traceable record.
Those real constraints are what make OOP's features feel necessary,
not just academic.
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ── Abstract base class ───────────────────────────────────────────────────────

class Account(ABC):
    # Class-level counter so every account gets a unique number automatically.
    # We don't pass the number in — the class manages it internally.
    _counter = 0

    def __init__(self, holder: str, initial_balance: float = 0.0):
        Account._counter += 1
        self.__number = f"MX{Account._counter:05d}"   # private, read-only via property
        self._holder = holder                          # protected: subclasses can read it
        self.__balance = max(0.0, initial_balance)     # can't open an account with debt
        self.__history: list[str] = []
        self._log(f"Account opened with initial balance ${initial_balance:.2f}")

    # ── Properties — controlled read access ───────────────────────────────────

    @property
    def number(self) -> str:
        return self.__number

    @property
    def holder(self) -> str:
        return self._holder

    @property
    def balance(self) -> float:
        # Read-only. Nobody outside this class can set balance directly.
        return self.__balance

    @property
    def history(self) -> list[str]:
        # We return a copy so callers can't mutate our internal list.
        return list(self.__history)

    # ── Shared operations ─────────────────────────────────────────────────────

    def deposit(self, amount: float) -> None:
        # Deposit logic is identical for all account types, so it lives here
        # in the parent class. No need to duplicate it in every subclass.
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.__balance += amount
        self._log(f"Deposit    +${amount:>10.2f}  →  balance ${self.__balance:.2f}")

    def _deduct(self, amount: float) -> None:
        # Protected helper for subclasses. We expose this instead of __balance
        # because subclasses need to reduce the balance as part of withdraw(),
        # but we still don't want outside code touching it directly.
        self.__balance -= amount

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        # Each subclass MUST implement this. The rules differ:
        # savings → can't go below zero; checking → can, up to overdraft limit.
        ...

    @abstractmethod
    def account_type(self) -> str:
        # Forces subclasses to declare their own label for display purposes.
        ...

    # ── Internal logging ──────────────────────────────────────────────────────

    def _log(self, message: str) -> None:
        # Timestamped audit trail. In a real system this would write to a DB.
        ts = datetime.now().strftime("%H:%M:%S")
        self.__history.append(f"[{ts}] {message}")

    def __repr__(self) -> str:
        return (
            f"{self.account_type()} | {self.number} | {self._holder} | "
            f"balance: ${self.__balance:.2f}"
        )


# ── Savings Account ───────────────────────────────────────────────────────────

class SavingsAccount(Account):
    def __init__(self, holder: str, initial_balance: float = 0.0,
                 interest_rate: float = 0.04):
        super().__init__(holder, initial_balance)
        # The interest rate belongs only to savings accounts, not to all accounts,
        # so it's an instance attribute here, not on the parent.
        self.__interest_rate = interest_rate

    def account_type(self) -> str:
        return "Savings"

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self.balance:
            # Savings accounts don't allow overdraft — hard stop here.
            raise ValueError(
                f"Insufficient funds. Available: ${self.balance:.2f}"
            )
        self._deduct(amount)
        self._log(f"Withdraw   -${amount:>10.2f}  →  balance ${self.balance:.2f}")

    def apply_interest(self) -> None:
        # Reuses deposit() from the parent — no need to manipulate __balance directly.
        interest = self.balance * self.__interest_rate
        self.deposit(interest)
        self._log(f"Interest ({self.__interest_rate:.0%}) applied: +${interest:.2f}")


# ── Checking Account ──────────────────────────────────────────────────────────

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
        # The available amount includes the overdraft cushion.
        # Balance can go negative, but only down to -overdraft_limit.
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
    checking.withdraw(400)   # goes into overdraft — allowed by CheckingAccount
    print(checking)
    print("\n  History:")
    for entry in checking.history:
        print(f"    {entry}")
