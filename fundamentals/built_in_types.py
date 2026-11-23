"""
Built-in Data Structures in Python
Practical examples of lists, dictionaries, tuples and sets.
"""


# ── Lists ─────────────────────────────────────────────────────────────────────

fruits = ["apple", "banana", "cherry"]
fruits.append("mango")
fruits.insert(1, "strawberry")
fruits.remove("banana")

print("List:", fruits)
print("Comprehension — long fruit names:", [f for f in fruits if len(f) > 5])


# ── Dictionaries ──────────────────────────────────────────────────────────────

student = {
    "name": "Ana García",
    "major": "Software Engineering",
    "term": 1,
    "courses": ["Algorithms", "Calculus", "Programming"],
}

print("\nStudent:", student["name"])
print("Courses:", ", ".join(student["courses"]))

student["gpa"] = 9.2
print("GPA added:", student)


# ── Tuples (immutable) ────────────────────────────────────────────────────────

coordinates = (19.4326, -99.1332)  # Mexico City
latitude, longitude = coordinates
print(f"\nMexico City → lat: {latitude}, lon: {longitude}")


# ── Sets ──────────────────────────────────────────────────────────────────────

languages_a = {"Python", "JavaScript", "Java"}
languages_b = {"Python", "Go", "Rust", "Java"}

print("\nIn both:", languages_a & languages_b)
print("In A but not B:", languages_a - languages_b)
print("Union:", languages_a | languages_b)
