"""
Quiz App - PART 1 of 4: The Question Bank
Owner: Person 1

Job
---
Own all quiz *content* and hand clean, validated Question objects to everyone else.
Nobody else edits this file, and this file imports nothing from the project.

Public contract (do not rename - the other 3 files depend on these):
    class Question          -> .text .options .answer_index .category .difficulty
                               .explanation .answer
    QUESTIONS               -> list of Question
    get_categories()        -> list of str
    get_questions(...)      -> list of Question
    validate_questions()    -> list of str  (empty list means the bank is healthy)
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Question:
    """One multiple-choice question with exactly 4 options."""

    text: str
    options: List[str]
    answer_index: int          # 0..3 -> which entry of `options` is correct
    category: str = "General"
    difficulty: str = "easy"   # easy | medium | hard
    explanation: str = ""

    @property
    def answer(self) -> str:
        """The correct option as text (handy after the options get shuffled)."""
        return self.options[self.answer_index]


# ---------------------------------------------------------------------------
# The bank. Person 1 grows this list; everything else keeps working.
# ---------------------------------------------------------------------------
QUESTIONS: List[Question] = [
    # ----- Python -----
    Question(
        "Which keyword defines a function in Python?",
        ["func", "def", "define", "function"],
        1,
        "Python",
        "easy",
        "def name(args): starts a function definition.",
    ),
    Question(
        "Which of these types is immutable?",
        ["list", "dict", "set", "tuple"],
        3,
        "Python",
        "easy",
        "Tuples cannot be changed after creation; the other three can.",
    ),
    Question(
        "What does len([1, 2, 3]) return?",
        ["2", "3", "4", "None"],
        1,
        "Python",
        "easy",
        "len() counts the items in the list - here, 3.",
    ),
    Question(
        "What is the result of 2 ** 3 in Python?",
        ["6", "8", "9", "23"],
        1,
        "Python",
        "easy",
        "** is exponentiation, so 2 ** 3 = 8.",
    ),
    Question(
        "Which list method removes and returns the last item?",
        ["remove()", "delete()", "pop()", "discard()"],
        2,
        "Python",
        "medium",
        "list.pop() removes the last item and returns it.",
    ),

    # ----- Science -----
    Question(
        "What is the chemical formula for water?",
        ["CO2", "H2O", "O2", "NaCl"],
        1,
        "Science",
        "easy",
        "Two hydrogen atoms bonded to one oxygen atom.",
    ),
    Question(
        "Which planet is known as the Red Planet?",
        ["Venus", "Jupiter", "Mars", "Mercury"],
        2,
        "Science",
        "easy",
        "Iron oxide (rust) in the soil gives Mars its red colour.",
    ),
    Question(
        "Which gas do plants absorb during photosynthesis?",
        ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"],
        2,
        "Science",
        "easy",
        "Plants take in CO2 and release oxygen.",
    ),
    Question(
        "What is the largest organ of the human body?",
        ["Liver", "Brain", "Skin", "Lungs"],
        2,
        "Science",
        "medium",
        "Skin is the largest organ by both surface area and weight.",
    ),
    Question(
        "Roughly how fast does light travel in a vacuum?",
        ["3,000 km/s", "30,000 km/s", "300,000 km/s", "3,000,000 km/s"],
        2,
        "Science",
        "hard",
        "About 299,792 km per second - usually rounded to 300,000 km/s.",
    ),

    # ----- Geography -----
    Question(
        "What is the capital city of Japan?",
        ["Osaka", "Tokyo", "Kyoto", "Seoul"],
        1,
        "Geography",
        "easy",
        "Tokyo has been the capital of Japan since 1868.",
    ),
    Question(
        "Which is the largest ocean on Earth?",
        ["Atlantic", "Indian", "Arctic", "Pacific"],
        3,
        "Geography",
        "easy",
        "The Pacific covers about a third of the planet's surface.",
    ),
    Question(
        "Which is the largest hot desert in the world?",
        ["Gobi", "Sahara", "Kalahari", "Thar"],
        1,
        "Geography",
        "medium",
        "The Sahara spans roughly 9.2 million square kilometres.",
    ),
    Question(
        "Mount Everest sits on the border of Nepal and which country?",
        ["India", "Bhutan", "China", "Pakistan"],
        2,
        "Geography",
        "medium",
        "The northern side of Everest lies in Tibet, China.",
    ),
    Question(
        "Egypt is located mainly on which continent?",
        ["Asia", "Europe", "Africa", "South America"],
        2,
        "Geography",
        "easy",
        "Most of Egypt is in north-east Africa; the Sinai Peninsula is in Asia.",
    ),

    # ----- History -----
    Question(
        "Who was the first President of the United States?",
        ["Thomas Jefferson", "George Washington", "Abraham Lincoln", "John Adams"],
        1,
        "History",
        "easy",
        "George Washington served from 1789 to 1797.",
    ),
    Question(
        "In which year did World War II end?",
        ["1918", "1939", "1945", "1950"],
        2,
        "History",
        "easy",
        "The war ended in 1945 with the surrender of Germany and Japan.",
    ),
    Question(
        "In which year did the Titanic sink?",
        ["1905", "1912", "1920", "1931"],
        1,
        "History",
        "medium",
        "The Titanic struck an iceberg and sank in April 1912.",
    ),
    Question(
        "Which leader led India's non-violent independence movement?",
        ["Mahatma Gandhi", "Nelson Mandela", "Winston Churchill", "Che Guevara"],
        0,
        "History",
        "easy",
        "Gandhi built a mass non-violent movement known as satyagraha.",
    ),
    Question(
        "Which British Prime Minister was nicknamed the Iron Lady?",
        ["Theresa May", "Margaret Thatcher", "Queen Victoria", "Indira Gandhi"],
        1,
        "History",
        "medium",
        "Margaret Thatcher, Prime Minister from 1979 to 1990.",
    ),
]


# ---------------------------------------------------------------------------
# Helpers the other files call
# ---------------------------------------------------------------------------
def get_categories() -> List[str]:
    """Every category in the bank, alphabetically, no duplicates."""
    return sorted({q.category for q in QUESTIONS})


def get_difficulties() -> List[str]:
    """Difficulty levels present in the bank, easiest first."""
    order = {"easy": 0, "medium": 1, "hard": 2}
    found = {q.difficulty for q in QUESTIONS}
    return sorted(found, key=lambda d: order.get(d, 99))


def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Question]:
    """
    Filtered copy of the bank.

    category / difficulty are case-insensitive; None or "all" means "no filter".
    limit trims the list (shuffling is the quiz engine's job, not ours).
    """
    picked = list(QUESTIONS)

    if category and category.lower() != "all":
        picked = [q for q in picked if q.category.lower() == category.lower()]

    if difficulty and difficulty.lower() != "all":
        picked = [q for q in picked if q.difficulty.lower() == difficulty.lower()]

    if limit is not None:
        picked = picked[:limit]

    return picked


def count_questions(category: Optional[str] = None) -> int:
    """How many questions are available for a category."""
    return len(get_questions(category))


def validate_questions() -> List[str]:
    """
    Self-check the bank. Returns a list of human-readable problems;
    an empty list means everything is fine.
    """
    problems: List[str] = []

    for i, q in enumerate(QUESTIONS, start=1):
        label = f"Q{i} ({q.text[:40]})"

        if len(q.options) != 4:
            problems.append(f"{label}: has {len(q.options)} options, expected 4")
        if not 0 <= q.answer_index < len(q.options):
            problems.append(f"{label}: answer_index {q.answer_index} is out of range")
        if len(set(q.options)) != len(q.options):
            problems.append(f"{label}: duplicate options")
        if not q.text.strip():
            problems.append(f"{label}: empty question text")
        if q.difficulty not in {"easy", "medium", "hard"}:
            problems.append(f"{label}: unknown difficulty '{q.difficulty}'")

    seen = set()
    for q in QUESTIONS:
        key = q.text.strip().lower()
        if key in seen:
            problems.append(f"Duplicate question text: {q.text[:50]}")
        seen.add(key)

    return problems


if __name__ == "__main__":
    # Person 1 can test this file alone:  python questions.py
    issues = validate_questions()
    print(f"{len(QUESTIONS)} questions across {len(get_categories())} categories.")
    for cat in get_categories():
        print(f"  {cat:<12} {count_questions(cat)} questions")
    print("Validation:", "OK" if not issues else f"{len(issues)} problem(s)")
    for issue in issues:
        print("  -", issue)
