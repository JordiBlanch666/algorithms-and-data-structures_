"""
Encapsulation — second pillar of OOP.

The idea is simple: hide the internal data of an object and only let
the outside world interact with it through controlled methods.

Why does this matter? If __balance were a plain public attribute, any
piece of code could do account.balance = -99999 with no validation.
Encapsulation prevents that by making the class the only gatekeeper
of its own state.

Python convention:
  _single_underscore  → "protected" — internal use, but technically accessible
  __double_underscore → "private" — name-mangled by Python, harder to access
"""


class BankAccount:
    def __init__(self, holder: str, initial_balance: float = 0.0):
        self._holder = holder             # _holder: other classes in the same
                                          # module can read it, but we're
                                          # signaling "don't touch from outside"

        self.__balance = initial_balance  # __balance: Python renames this to
                                          # _BankAccount__balance internally,
                                          # so account.__balance raises
                                          # AttributeError from outside the class

    # ── Properties (controlled read access) ──────────────────────────────────

    @property
    def holder(self) -> str:
        # @property lets us expose holder as if it were a plain attribute
        # (account.holder) while still being able to add logic here later
        # without changing how callers use it.
        return self._holder

    @property
    def balance(self) -> float:
        return self.__balance

    # ── Controlled write operations ───────────────────────────────────────────

    def deposit(self, amount: float) -> None:
        # Validation lives HERE, not scattered around the codebase.
        # Any code that wants to add money goes through this method —
        # which means we only need to validate in one place.
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

    # This is the proof that encapsulation is working:
    # trying to reach __balance directly from outside the class fails.
    try:
        print(account.__balance)
    except AttributeError as e:
        print(f"\n  Encapsulation active: {e}")

    # The correct way to read the balance is through the property.
    print(f"\n  Balance via property: ${account.balance:.2f}")
