"""
Quiz App - PART 2 of 4: The Quiz Engine
Owner: Person 2
"""

import random
import time
from dataclasses import dataclass
from typing import Any, List, Optional

SKIPPED = -1  # chosen_index value that means "the player skipped this one"


@dataclass
class AnswerRecord:
    """What happened on a single question."""

    question: Any
    shuffled_options: List[str]
    correct_index: int
    chosen_index: int
    seconds: float = 0.0

    @property
    def skipped(self) -> bool:
        return self.chosen_index == SKIPPED

    @property
    def is_correct(self) -> bool:
        return self.chosen_index == self.correct_index

    @property
    def correct_option(self) -> str:
        return self.shuffled_options[self.correct_index]

    @property
    def chosen_option(self) -> str:
        return "(skipped)" if self.skipped else self.shuffled_options[self.chosen_index]


class Quiz:
    """One quiz run."""

    def __init__(
        self,
        questions: List[Any],
        shuffle_questions: bool = True,
        shuffle_options: bool = True,
        seed: Optional[int] = None,
    ):
        if not questions:
            raise ValueError("Quiz needs at least one question")

        rng = random.Random(seed)

        self._questions = list(questions)
        if shuffle_questions:
            rng.shuffle(self._questions)

        self._layouts: List[tuple] = []
        for q in self._questions:
            options = list(q.options)
            correct = q.answer_index
            if shuffle_options:
                order = list(range(len(options)))
                rng.shuffle(order)
                options = [q.options[i] for i in order]
                correct = order.index(q.answer_index)
            self._layouts.append((options, correct))

        self.index = 0
        self.records: List[AnswerRecord] = []
        self._t_start: Optional[float] = None
        self._t_question: Optional[float] = None

    @property
    def total(self) -> int:
        return len(self._questions)

    @property
    def number(self) -> int:
        return min(self.index + 1, self.total)

    @property
    def is_finished(self) -> bool:
        return self.index >= self.total

    @property
    def current_question(self) -> Any:
        if self.is_finished:
            raise IndexError("Quiz is already finished")
        if self._t_start is None:
            self._t_start = time.perf_counter()
        self._t_question = time.perf_counter()
        return self._questions[self.index]

    @property
    def current_options(self) -> List[str]:
        if self.is_finished:
            raise IndexError("Quiz is already finished")
        return list(self._layouts[self.index][0])

    def submit(self, chosen_index: int) -> AnswerRecord:
        if self.is_finished:
            raise IndexError("Quiz is already finished")

        options, correct = self._layouts[self.index]
        if chosen_index != SKIPPED and not 0 <= chosen_index < len(options):
            raise ValueError(f"chosen_index must be 0..{len(options) - 1} or {SKIPPED}")

        now = time.perf_counter()
        started = self._t_question or self._t_start or now
        record = AnswerRecord(
            question=self._questions[self.index],
            shuffled_options=options,
            correct_index=correct,
            chosen_index=chosen_index,
            seconds=round(now - started, 2),
        )

        self.records.append(record)
        self.index += 1
        self._t_question = None
        return record

    def skip(self) -> AnswerRecord:
        return self.submit(SKIPPED)

    def finish(self) -> None:
        while not self.is_finished:
            self.skip()

    @property
    def score(self) -> int:
        return sum(1 for r in self.records if r.is_correct)

    @property
    def wrong(self) -> int:
        return sum(1 for r in self.records if not r.is_correct and not r.skipped)

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.records if r.skipped)

    @property
    def percentage(self) -> float:
        return round(100 * self.score / self.total, 1) if self.total else 0.0

    @property
    def elapsed(self) -> float:
        return round(sum(r.seconds for r in self.records), 2)

    @property
    def grade(self) -> str:
        pct = self.percentage
        if pct >= 90:
            return "A - outstanding"
        if pct >= 75:
            return "B - strong"
        if pct >= 60:
            return "C - passing"
        if pct >= 40:
            return "D - needs work"
        return "F - try again"

    def wrong_records(self) -> List[AnswerRecord]:
        return [r for r in self.records if not r.is_correct]

    def summary(self) -> dict:
        return {
            "score": self.score,
            "total": self.total,
            "percentage": self.percentage,
            "wrong": self.wrong,
            "skipped": self.skipped,
            "seconds": self.elapsed,
            "grade": self.grade,
        }


if __name__ == "__main__":
    class FakeQuestion:
        def __init__(self, text, options, answer_index):
            self.text = text
            self.options = options
            self.answer_index = answer_index
            self.category = "Test"
            self.difficulty = "easy"
            self.explanation = "demo"

    demo = [
        FakeQuestion("1 + 1 = ?", ["1", "2", "3", "4"], 1),
        FakeQuestion("2 + 2 = ?", ["2", "3", "4", "5"], 2),
    ]

    quiz = Quiz(demo, seed=7)
    while not quiz.is_finished:
        question = quiz.current_question
        options = quiz.current_options
        correct_text = question.options[question.answer_index]
        quiz.submit(options.index(correct_text))
    print("engine OK ->", quiz.summary())
