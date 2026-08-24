"""
Quiz App - PART 4 of 4: Menus, Input and Wiring
Owner: Person 4

This file handles:
- Main menu
- Player input
- Category selection
- Quiz settings
- Answer input
- Results
- Leaderboard
- Player statistics
- Resetting saved scores

Run the whole app with:

    python main.py
"""

import sys

from questions import (
    count_questions,
    get_categories,
    get_questions,
    validate_questions,
)

from quiz_logic import SKIPPED, Quiz

from scoreboard import (
    clear_scores,
    format_leaderboard,
    format_result_card,
    format_review,
    player_stats,
    save_result,
)


LETTERS = ["A", "B", "C", "D"]
DEFAULT_LENGTH = 5


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def ask(prompt: str) -> str:
    """Read input safely and handle Ctrl+C / Ctrl+D."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")
        sys.exit(0)


def ask_int(prompt: str, low: int, high: int, default: int) -> int:
    """Read a number within the given range."""
    while True:
        raw = ask(
            f"{prompt} [{low}-{high}, default {default}]: "
        )

        if not raw:
            return default

        if raw.isdigit() and low <= int(raw) <= high:
            return int(raw)

        print(f"  Please type a number between {low} and {high}.")


def ask_menu(title: str, options: list) -> int:
    """Display a numbered menu and return the selected 0-based index."""
    print(f"\n{title}")

    for i, label in enumerate(options, start=1):
        print(f"  {i}. {label}")

    while True:
        raw = ask("Choose: ")

        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1

        print(f"  Type 1-{len(options)}.")


def ask_answer(option_count: int):
    """
    Read the player's answer.

    Returns:
        0-based option index
        SKIPPED if the player skips
        None if the player quits
    """
    valid = LETTERS[:option_count]

    while True:
        raw = ask(
            f"Your answer ({'/'.join(valid)}, s=skip, q=quit): "
        ).upper()

        if raw in valid:
            return valid.index(raw)

        if raw.isdigit() and 1 <= int(raw) <= option_count:
            return int(raw) - 1

        if raw == "S":
            return SKIPPED

        if raw == "Q":
            return None

        print(
            f"  Type {' / '.join(valid)}, "
            "or s to skip, or q to quit."
        )


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def banner() -> None:
    """Display the application banner."""
    print()
    print("*" * 46)
    print("*{:^44}*".format("PYTHON QUIZ APP"))
    print("*{:^44}*".format("4-person group project"))
    print("*" * 46)


# ---------------------------------------------------------------------------
# Category selection
# ---------------------------------------------------------------------------

def choose_category() -> str:
    """Ask the player which question category they want."""
    categories = get_categories()

    labels = ["All categories"] + [
        f"{category} ({count_questions(category)} questions)"
        for category in categories
    ]

    picked = ask_menu("Pick a category:", labels)

    if picked == 0:
        return "All"

    return categories[picked - 1]


# ---------------------------------------------------------------------------
# Quiz
# ---------------------------------------------------------------------------

def play(player: str) -> None:
    """Run one complete quiz for the player."""

    category = choose_category()
    pool = get_questions(category)

    if not pool:
        print("No questions in that category yet.")
        return

    default_length = min(DEFAULT_LENGTH, len(pool))

    length = ask_int(
        "How many questions?",
        1,
        len(pool),
        default_length,
    )

    quiz = Quiz(
        pool,
        shuffle_questions=True,
        shuffle_options=True,
    )

    print(
        f"\nStarting: {category} - "
        f"{length} of {len(pool)} questions. "
        "Good luck!\n"
    )

    asked = 0

    while not quiz.is_finished and asked < length:

        question = quiz.current_question
        options = quiz.current_options

        print(
            f"Q{asked + 1}/{length}  "
            f"[{question.category} - {question.difficulty}]"
        )

        print(f"  {question.text}")

        for letter, option in zip(LETTERS, options):
            print(f"    {letter}) {option}")

        choice = ask_answer(len(options))

        if choice is None:
            print("  Quiz ended early.\n")
            break

        record = quiz.submit(choice)
        asked += 1

        if record.is_correct:
            print(f"  Correct! ({record.seconds}s)")

        elif record.skipped:
            print(
                f"  Skipped. "
                f"The answer was {record.correct_option}."
            )

        else:
            print(
                f"  Wrong. "
                f"The answer was {record.correct_option}."
            )

        if question.explanation:
            print(f"  {question.explanation}")

        print()

    # ---------------------------------------------------------------
    # Calculate final result
    # ---------------------------------------------------------------

    summary = quiz.summary()

    summary["total"] = len(quiz.records)

    if summary["total"]:
        summary["percentage"] = round(
            100 * summary["score"] / summary["total"],
            1,
        )
    else:
        summary["percentage"] = 0.0

    if not quiz.records:
        print("Nothing answered - no score saved.\n")
        return

    # ---------------------------------------------------------------
    # Display results
    # ---------------------------------------------------------------

    print(format_result_card(
        player,
        summary,
        category,
    ))

    print()

    print(format_review(
        quiz.wrong_records()
    ))

    print()

    # ---------------------------------------------------------------
    # Save result
    # ---------------------------------------------------------------

    save_result(
        player,
        summary["score"],
        summary["total"],
        category,
        summary["seconds"],
    )

    print("Score saved.\n")

    print(format_leaderboard(
        5,
        category,
    ))


# ---------------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------------

def show_leaderboard() -> None:
    """Display the leaderboard for a selected category."""

    categories = get_categories()

    picked = ask_menu(
        "Leaderboard for:",
        ["All categories"] + categories,
    )

    if picked == 0:
        category = "All"
    else:
        category = categories[picked - 1]

    print()
    print(format_leaderboard(10, category))


# ---------------------------------------------------------------------------
# Player statistics
# ---------------------------------------------------------------------------

def show_my_stats(player: str) -> None:
    """Display statistics for the current player."""

    stats = player_stats(player)

    print()

    if not stats["games"]:
        print(f"No games recorded for {player} yet.")
        return

    print(f"STATS for {player}")
    print(f"  Games played : {stats['games']}")
    print(f"  Best score   : {stats['best']}%")
    print(f"  Average      : {stats['average']}%")
    print(f"  Last played  : {stats['last']}")


# ---------------------------------------------------------------------------
# Reset scores
# ---------------------------------------------------------------------------

def reset_history() -> None:
    """Ask for confirmation before deleting saved scores."""

    answer = ask(
        "Delete all saved scores? (yes/no): "
    ).lower()

    if answer in {"y", "yes"}:
        removed = clear_scores()
        print(f"Removed {removed} saved result(s).")
    else:
        print("Cancelled.")


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def main() -> None:
    """Start and control the quiz application."""

    banner()

    # Check the question bank before starting.
    problems = validate_questions()

    if problems:
        print("\nWARNING - the question bank has problems:")

        for problem in problems:
            print("  -", problem)

        print()

    # Get player's name.
    player = ask("Your name: ") or "Anonymous"

    print(f"Welcome, {player}!")

    # Main menu.
    menu = [
        "Start a quiz",
        "Leaderboard",
        "My stats",
        "Reset all scores",
        "Quit",
    ]

    while True:

        choice = ask_menu(
            "MAIN MENU",
            menu,
        )

        if choice == 0:
            play(player)

        elif choice == 1:
            show_leaderboard()

        elif choice == 2:
            show_my_stats(player)

        elif choice == 3:
            reset_history()

        else:
            print(
                f"\nThanks for playing, {player}!"
            )
            break


# ---------------------------------------------------------------------------
# Program entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()