"""
Bubble Sort — O(n²) average/worst, O(n) best case, O(1) space.

How it works: repeatedly compare adjacent elements and swap them if they're
in the wrong order. Each full pass "bubbles" the largest unsorted element
to its correct position at the end.

Why learn this first? Not because it's fast (it isn't), but because it's the
most intuitive sorting algorithm — you can trace every swap by hand. Once you
understand why it's slow, the improvements in Insertion and Merge Sort make sense.

The early-exit flag (swapped) is a key optimization: if we complete a full pass
with no swaps, the list is already sorted. This makes best-case O(n) instead of O(n²).
"""


def bubble_sort(lst: list) -> list:
    arr = lst.copy()   # never mutate the caller's list
    n = len(arr)

    for i in range(n - 1):
        swapped = False

        # After each outer iteration i, the last i elements are already
        # in their final position — no need to compare them again.
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # Short-circuit: if nothing moved, the list is sorted.
        if not swapped:
            break

    return arr


# Keep the old name as an alias so other modules that import 'burbuja' still work.
burbuja = bubble_sort


if __name__ == "__main__":
    numbers = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original: {numbers}")
    print(f"Sorted:   {bubble_sort(numbers)}")
