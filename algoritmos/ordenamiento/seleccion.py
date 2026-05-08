"""
Selection Sort — O(n²) all cases, O(1) space.

How it works: divide the list into a sorted left part and an unsorted right part.
On each pass, find the minimum element in the unsorted part and move it to the
end of the sorted part.

Key tradeoff: Selection Sort always does exactly n*(n-1)/2 comparisons regardless
of input — it can't short-circuit like Bubble Sort. But it does fewer swaps:
at most n-1, compared to O(n²) for Bubble Sort. That makes it useful when
writes are expensive (e.g., writing to flash memory).

Unlike Insertion Sort, Selection Sort is NOT stable — equal elements may change
their relative order during sorting.
"""


def selection_sort(lst: list) -> list:
    arr = lst.copy()
    n = len(arr)

    for i in range(n - 1):
        # Find the index of the smallest element in the unsorted portion.
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j

        # Swap it into position i — the boundary between sorted and unsorted.
        # If min_idx == i, the element is already in place; swap is a no-op.
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

    return arr


# Alias for backward compatibility.
seleccion = selection_sort


if __name__ == "__main__":
    numbers = [29, 10, 14, 37, 13]
    print(f"Original: {numbers}")
    print(f"Sorted:   {selection_sort(numbers)}")
