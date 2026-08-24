"""
Quiz App - PART 3 of 4: Scoreboard, History and Reports
Owner: Person 3

Job
---
Everything that outlives a single quiz: save results to disk, load them back,
rank them, and format the text blocks the UI prints (result card, review of
wrong answers, leaderboard table).

Storage is a plain JSON file called scores.json, created next to this file the
first time somebody plays. This file never calls input().

Public contract:
    save_result(...)        -> dict (the row that was stored)
    load_scores()           -> list of dict, newest first
    top_scores(...)         -> list of dict, best first
    player_stats(name)      -> dict
    format_leaderboard(...) -> str
    format_result_card(...) -> str
    format_review(...)      -> str
    clear_scores()          -> int (rows deleted)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

SCORE_FILE = Path(__file__).resolve().with_name("scores.json")


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
def load_scores(path: Path = SCORE_FILE) -> List[dict]:
    """Every saved result, newest first. Returns [] if the file is missing/corrupt."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return sorted(data, key=lambda row: row.get("played_at", ""), reverse=True)


def save_result(
    player: str,
    score: int,
    total: int,
    category: str = "All",
    seconds: float = 0.0,
    path: Path = SCORE_FILE,
) -> dict:
    """Append one result to scores.json and return the row that was written."""
    row = {
        "player": (player or "Anonymous").strip()[:20],
        "score": int(score),
        "total": int(total),
        "percentage": round(100 * score / total, 1) if total else 0.0,
        "category": category or "All",
        "seconds": round(float(seconds), 2),
        "played_at": datetime.now().isoformat(timespec="seconds"),
    }

    rows = load_scores(path)
    rows.append(row)

    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2)
    except OSError as exc:
        print(f"(warning: could not save score - {exc})")

    return row


def clear_scores(path: Path = SCORE_FILE) -> int:
    """Wipe the history. Returns how many rows were removed."""
    removed = len(load_scores(path))
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([], fh)
    except OSError:
        return 0
    return removed


# ---------------------------------------------------------------------------
# Ranking / stats
# ---------------------------------------------------------------------------
def top_scores(
    limit: int = 5,
    category: Optional[str] = None,
    path: Path = SCORE_FILE,
) -> List[dict]:
    """Best results first: highest percentage, then fastest time."""
    rows = load_scores(path)

    if category and category.lower() != "all":
        rows = [r for r in rows if str(r.get("category", "")).lower() == category.lower()]

    rows.sort(key=lambda r: (-r.get("percentage", 0), r.get("seconds", 9e9)))
    return rows[:limit]


def player_stats(name: str, path: Path = SCORE_FILE) -> dict:
    """Summary for one player across every quiz they have taken."""
    rows = [r for r in load_scores(path) if str(r.get("player", "")).lower() == name.lower()]
    if not rows:
        return {"player": name, "games": 0, "best": 0.0, "average": 0.0, "last": None}

    percentages = [r.get("percentage", 0) for r in rows]
    return {
        "player": name,
        "games": len(rows),
        "best": max(percentages),
        "average": round(sum(percentages) / len(percentages), 1),
        "last": rows[0].get("played_at"),
    }


# ---------------------------------------------------------------------------
# Text the UI prints
# ---------------------------------------------------------------------------
def format_leaderboard(
    limit: int = 5,
    category: Optional[str] = None,
    path: Path = SCORE_FILE,
) -> str:
    """Leaderboard as a ready-to-print table."""
    rows = top_scores(limit, category, path)
    scope = f" - {category}" if category and category.lower() != "all" else ""

    if not rows:
        return f"LEADERBOARD{scope}\nNo scores yet. Be the first to play!"

    lines = [
        f"LEADERBOARD{scope}",
        f"{'#':<3}{'Player':<14}{'Score':<8}{'%':<8}{'Time':<8}{'Category':<12}Date",
        "-" * 70,
    ]
    for i, r in enumerate(rows, start=1):
        played = str(r.get("played_at", ""))[:10]
        lines.append(
            f"{i:<3}"
            f"{str(r.get('player', '?'))[:13]:<14}"
            f"{str(r.get('score', 0)) + '/' + str(r.get('total', 0)):<8}"
            f"{str(r.get('percentage', 0)) + '%':<8}"
            f"{str(r.get('seconds', 0)) + 's':<8}"
            f"{str(r.get('category', 'All'))[:11]:<12}"
            f"{played}"
        )
    return "\n".join(lines)


def format_result_card(player: str, summary: dict, category: str = "All") -> str:
    """The 'you scored X' block shown right after a quiz."""
    bar_width = 20
    filled = int(round(bar_width * summary.get("percentage", 0) / 100))
    bar = "#" * filled + "." * (bar_width - filled)

    return "\n".join(
        [
            "=" * 46,
            f"  RESULTS for {player}  ({category})",
            "=" * 46,
            f"  Score      : {summary.get('score', 0)} / {summary.get('total', 0)}",
            f"  Percentage : {summary.get('percentage', 0)}%  [{bar}]",
            f"  Grade      : {summary.get('grade', '-')}",
            f"  Wrong      : {summary.get('wrong', 0)}    Skipped: {summary.get('skipped', 0)}",
            f"  Time taken : {summary.get('seconds', 0)} seconds",
            "=" * 46,
        ]
    )


def format_review(wrong_records: List[Any]) -> str:
    """Walk the player through what they got wrong. Takes Part 2's AnswerRecords."""
    if not wrong_records:
        return "Perfect run - nothing to review!"

    lines = [f"REVIEW ({len(wrong_records)} to look at)", "-" * 46]
    for i, r in enumerate(wrong_records, start=1):
        lines.append(f"{i}. {r.question.text}")
        lines.append(f"   your answer : {r.chosen_option}")
        lines.append(f"   correct     : {r.correct_option}")
        if getattr(r.question, "explanation", ""):
            lines.append(f"   why         : {r.question.explanation}")
        lines.append("")
    return "\n".join(lines).rstrip()


if __name__ == "__main__":
    # Person 3 can test this file alone with a temporary file:
    #   python scoreboard.py
    demo_path = Path(__file__).resolve().with_name("scores_demo.json")
    clear_scores(demo_path)
    save_result("Asha", 8, 10, "Python", 42.5, demo_path)
    save_result("Bilal", 6, 10, "Science", 51.0, demo_path)
    save_result("Chen", 10, 10, "Python", 61.2, demo_path)
    print(format_leaderboard(5, None, demo_path))
    print()
    print(player_stats("Asha", demo_path))
    demo_path.unlink(missing_ok=True)
