"""
Linear Search — O(n) time, O(1) space. Works on any list, sorted or not.

How it works: check every element from left to right until you find the target
or reach the end. Simple, but slow on large lists.

When to use it:
  - The list is unsorted and you can't sort it first.
  - The list is very small (under ~10 elements) — overhead of sorting + binary
    search isn't worth it.
  - You only need to search once — sorting just to binary search once is wasteful.

Best case O(1): target is the first element.
Worst case O(n): target is the last element or not present at all.
"""


def linear_search(lst: list, target) -> int:
    """Return the index of the first occurrence of target, or -1 if not found."""
    for i, element in enumerate(lst):
        if element == target:
            return i   # early exit — no need to check the rest
    return -1


# Aliases so both old and new import styles work.
lineal = linear_search
busqueda_lineal = linear_search


if __name__ == "__main__":
    numbers = [4, 2, 7, 1, 9, 3]
    target = 7

    idx = linear_search(numbers, target)
    if idx != -1:
        print(f"'{target}' found at index {idx}.")
    else:
        print(f"'{target}' is not in the list.")
