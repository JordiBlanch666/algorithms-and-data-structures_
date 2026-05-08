"""
Binary Search — O(log n) time, O(1) space. Requires a sorted list.

How it works: instead of checking every element, cut the search space in half
at each step. Compare the target to the middle element:
  - Equal  → found it, return the index
  - Target is larger  → search the right half
  - Target is smaller → search the left half

Why O(log n)? A list of 1,000,000 elements takes at most 20 comparisons.
A list of 1,000,000,000 takes at most 30. The algorithm barely notices
when the input grows — that's the power of logarithmic complexity.

The tradeoff: the list MUST be sorted first. If it isn't, binary search
produces wrong results silently — no error, just an incorrect answer.
Always sort before you binary search.
"""


def binary_search(lst: list, target) -> int:
    """Return the index of target in lst, or -1 if not found."""
    left, right = 0, len(lst) - 1

    while left <= right:
        # (left + right) // 2 can overflow in languages with fixed-size integers.
        # This midpoint formula is safer (though Python's int is unbounded).
        mid = (left + right) // 2

        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            left = mid + 1    # target is in the right half
        else:
            right = mid - 1   # target is in the left half

    return -1   # target is not in the list


# Aliases so both old and new import styles work.
binaria = binary_search
busqueda_binaria = binary_search


if __name__ == "__main__":
    numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    target = 23

    idx = binary_search(numbers, target)
    if idx != -1:
        print(f"'{target}' found at index {idx}.")
    else:
        print(f"'{target}' is not in the list.")

    # Show why the list must be sorted:
    unsorted = [64, 34, 25, 12, 22, 11, 90]
    wrong = binary_search(unsorted, 25)
    print(f"\nBinary search on unsorted list for 25: index {wrong}  ← unreliable!")
