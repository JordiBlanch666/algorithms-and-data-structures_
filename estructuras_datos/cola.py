"""
Queue — FIFO: First In, First Out.

A queue models any real-world waiting line: the first person to arrive is
the first to be served. Printers, task schedulers, web servers — they all
use queues internally.

We use collections.deque (double-ended queue) instead of a plain list because:
  - list.pop(0) is O(n) — it shifts every element left.
  - deque.popleft() is O(1) — it's designed for efficient front removal.

This is a common interview gotcha: "why not just use a list?"
The answer is the O(n) vs O(1) difference for front operations.

Key operations (all O(1)):
  enqueue(x)  — add to the back
  dequeue()   — remove from the front
  front()     — peek at the front without removing
"""

from collections import deque


class Queue:
    def __init__(self):
        # deque is the right tool here — O(1) append and popleft.
        self._data: deque = deque()

    def enqueue(self, item) -> None:
        """Add an item to the back of the queue."""
        self._data.append(item)

    def dequeue(self):
        """Remove and return the front item."""
        if self.is_empty():
            raise IndexError("Queue is empty.")
        return self._data.popleft()   # O(1) — that's why we use deque

    def front(self):
        """Return the front item without removing it."""
        if self.is_empty():
            raise IndexError("Queue is empty.")
        return self._data[0]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Queue({list(self._data)})"


# Aliases so existing code that imports the Spanish names still works.
Cola = Queue


if __name__ == "__main__":
    # Simulate a service queue — first come, first served.
    queue = Queue()
    customers = ["Ana", "Carlos", "María", "Luis"]

    print("Customers joining the queue:")
    for customer in customers:
        queue.enqueue(customer)
        print(f"  + {customer} joined  (queue size: {len(queue)})")

    print(f"\nServing ({len(queue)} waiting):")
    while not queue.is_empty():
        served = queue.dequeue()
        print(f"  ✓ {served} served")
