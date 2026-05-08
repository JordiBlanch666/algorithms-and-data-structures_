"""
Insertion Sort — O(n²) worst case, O(n) best case, O(1) space.

How it works: imagine sorting a hand of playing cards. You pick one card at
a time and slide it left until it's in the right spot among the cards you've
already sorted. That's exactly what this algorithm does.

Why it matters:
  - Best case O(n) when the list is already nearly sorted — faster than Merge Sort
    in that specific scenario.
  - It's a stable sort: equal elements keep their original relative order.
  - Used internally by Python's Timsort (the built-in sort) for small sub-arrays.
"""


def insertion_sort(lst: list) -> list:
    arr = lst.copy()

    # We start from index 1 — index 0 is trivially "sorted" on its own.
    for i in range(1, len(arr)):
        key = arr[i]   # the card we just picked up

        # Slide elements that are greater than 'key' one position to the right,
        # making room for key to be inserted in the correct spot.
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key   # drop the card into its correct position

    return arr


# Alias for backward compatibility with existing imports.
insercion = insertion_sort


if __name__ == "__main__":
    numbers = [12, 11, 13, 5, 6]
    print(f"Original: {numbers}")
    print(f"Sorted:   {insertion_sort(numbers)}")
