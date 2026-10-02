"""Pure mixed-session decisions and short-lived session bookkeeping.

The caller supplies a catalog, due rows, durable snapshots, a clock, and a
random chooser. Tkinter is deliberately absent from this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from random import Random
from typing import Callable, Mapping, Sequence

from .data import guided_sentences, present_tense_patterns, vocabulary_items
from .models import AttemptEvent, ReadinessSnapshot
from .review_db import ReviewDB, ReviewItem
from .sentence_readiness import (
    SUPPORT_LEVELS, SessionTargetEvidence, TargetKey,
    recommend_sentence_support, sentence_target_keys,
)


@dataclass(frozen=True)
class PlannerItem:
    language: str
    exercise_id: str
    skill: str
    direction: str
    item_id: str
    prompt: str

    @property
    def key(self) -> TargetKey:
        return self.skill, self.direction, self.item_id

    @property
    def concept(self) -> tuple[str, str]:
        return self.skill, self.item_id


@dataclass(frozen=True)
class PlannerRecommendation:
    destination_exercise_id: str | None
    skill: str | None
    direction: str | None
    item_id: str | None
    support_level: str | None
    reason: str
    source: str
    language: str
    queue_id: int | None = None
    repair_target: TargetKey | None = None

    @property
    def key(self) -> TargetKey | None:
        if self.skill is None or self.direction is None or self.item_id is None:
            return None
        return self.skill, self.direction, self.item_id


@dataclass(frozen=True)
class SessionRecap:
    completed: int
    first_try_successes: int
    first_try_attempts: int
    helped_attempts: int
    skipped: int
    targets_to_revisit: tuple[TargetKey, ...]


@dataclass
class SessionState:
    """Ephemeral pacing and repair context for one language in one launch."""

    session_id: str
    language: str
    goal: int = 12
    new_item_limit: int = 4
    completed: int = 0
    ended: bool = False
    focused_exercise_id: str | None = None
    support_override: str | None = None
    new_concepts: set[tuple[str, str]] = field(default_factory=set)
    presented: set[TargetKey] = field(default_factory=set)
    completed_due_ids: set[int] = field(default_factory=set)
    recent_trouble: dict[TargetKey, SessionTargetEvidence] = field(default_factory=dict)
    trouble_seen: dict[TargetKey, None] = field(default_factory=dict)
    repair_attempted: set[TargetKey] = field(default_factory=set)
    last_key: TargetKey | None = None
    events: list[AttemptEvent] = field(default_factory=list)
    skipped_count: int = 0

    def __post_init__(self) -> None:
        if not self.session_id or not self.language:
            raise ValueError("A session needs an ID and language")
        if self.goal < 1 or self.new_item_limit < 0:
            raise ValueError("Session goal must be positive and new-item limit nonnegative")

    def choose_focused_mode(self, exercise_id: str | None) -> None:
        self.focused_exercise_id = exercise_id

    def adjust_support(self, level: str | None) -> None:
        if level is not None and level not in SUPPORT_LEVELS:
            raise ValueError(f"Unknown support level: {level}")
        self.support_override = level

    def end_early(self) -> None:
        self.ended = True

    def record_result(
        self,
        recommendation: PlannerRecommendation,
        event: AttemptEvent | None = None,
        *,
        trouble_target: TargetKey | None = None,
    ) -> None:
        """Consume one recommendation. ``event=None`` means the learner skipped it."""

        if recommendation.language != self.language or (event and event.language != self.language):
            raise ValueError("Cannot mix languages in a planner session")
        if recommendation.source == "empty":
            raise ValueError("An empty recommendation has no result")
        if event and (event.session_id != self.session_id or
                      any(prior.event_id == event.event_id for prior in self.events)):
            raise ValueError("Event belongs to another session or was already counted")
        if event and recommendation.key and (
            event.skill, event.direction, event.item_id
        ) != recommendation.key:
            raise ValueError("Event does not match the recommended target")

        self.completed += 1
        self.last_key = recommendation.key
        if recommendation.key:
            self.presented.add(recommendation.key)
        if recommendation.queue_id is not None:
            self.completed_due_ids.add(recommendation.queue_id)
        if recommendation.source == "new" and recommendation.skill and recommendation.item_id:
            self.new_concepts.add((recommendation.skill, recommendation.item_id))
        target = trouble_target or recommendation.repair_target or recommendation.key
        if recommendation.source == "repair" and recommendation.repair_target:
            self.repair_attempted.add(recommendation.repair_target)

        if event is None:
            self.skipped_count += 1
        else:
            self.events.append(event)
            if target:
                miss = event.outcome != "correct" or event.first_try_correct is False
                helped = bool(event.support_used)
                if miss or helped:
                    self.trouble_seen[target] = None
                    previous = self.recent_trouble.get(target, SessionTargetEvidence())
                    self.recent_trouble[target] = SessionTargetEvidence(
                        previous.misses + int(miss), previous.help_uses + int(helped)
                    )
                elif target in self.recent_trouble and event.first_try_correct is True:
                    del self.recent_trouble[target]

    def recap(self) -> SessionRecap:
        first = [event for event in self.events if event.first_try_correct is not None]
        return SessionRecap(
            completed=self.completed,
            first_try_successes=sum(event.first_try_correct is True and not event.support_used for event in first),
            first_try_attempts=len(first),
            helped_attempts=sum(bool(event.support_used) for event in self.events),
            skipped=self.skipped_count + sum(event.outcome == "skipped" for event in self.events),
            targets_to_revisit=tuple(self.trouble_seen),
        )


_PEOPLE = (
    "first_singular", "second_singular", "third_singular",
    "first_plural", "second_plural", "third_plural",
)


def catalog_for_language(language: str) -> tuple[PlannerItem, ...]:
    """Build stable destinations from authored content, excluding generated sentences."""

    items: list[PlannerItem] = []
    for word in vocabulary_items(language=language):
        items.extend((
            PlannerItem(language, "flashcard", "vocabulary", "target_to_english", word.id, word.french),
            PlannerItem(language, "flashcard", "vocabulary", "english_to_target", word.id, word.english),
        ))
    for verb in present_tense_patterns(language):
        items.extend(
            PlannerItem(language, "conjugation", "verb_form", "target_form", verb.form_id(person),
                        f"{verb.infinitive} · {verb.pronouns[index]}")
            for index, person in enumerate(_PEOPLE)
        )
    items.extend(
        PlannerItem(language, "sentence", "sentence_translation", "target_to_english", sentence.id, sentence.french)
        for sentence in guided_sentences(language)
    )
    keys = [item.key for item in items]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Duplicate planner target in {language} catalog")
    return tuple(items)


def load_planner_inputs(
    db: ReviewDB, language: str, *, now: datetime, due_limit: int = 100
) -> tuple[tuple[PlannerItem, ...], list[ReviewItem], dict[TargetKey, ReadinessSnapshot]]:
    """Read current durable inputs once; planning itself remains pure."""

    catalog = catalog_for_language(language)
    due = db.due_items(language=language, limit=due_limit, now=now)
    snapshots = {
        item.key: db.readiness_snapshot(language=language, skill=item.skill,
                                        direction=item.direction, item_id=item.item_id)
        for item in catalog
    }
    return catalog, due, snapshots


def recommend_next(
    catalog: Sequence[PlannerItem],
    due_items: Sequence[ReviewItem],
    snapshots: Mapping[TargetKey, ReadinessSnapshot],
    state: SessionState,
    *,
    now: datetime,
    choose: Callable[[Sequence[PlannerItem]], PlannerItem] | None = None,
) -> PlannerRecommendation:
    """Choose due work, a targeted repair, or bounded new material.

    Due rows have priority at session start. After a miss, a different
    sentence or direction may repair the target; a consumed due row cannot
    immediately loop back through the same session.
    """

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Planner clock must be timezone-aware")
    if state.ended or state.completed >= state.goal:
        return _empty(state, "Your session is complete. You can stop or choose a focused mode.")
    if any(item.language != state.language for item in catalog):
        raise ValueError("Planner catalog contains another language")
    if any(row.language and row.language != state.language for row in due_items):
        raise ValueError("Due work contains another language")
    choose = choose or Random(0).choice
    catalog_by_key = {item.key: item for item in catalog}

    if state.completed:
        repair = _repair_candidate(catalog, state, choose)
        if repair:
            item, trouble = repair
            return _recommend(item, state, snapshots, "repair",
                              f"Practice {trouble[2]} in a different prompt after a recent miss or hint.",
                              repair_target=trouble)

    for row in due_items:
        if row.id in state.completed_due_ids:
            continue
        parts = row.item_key.split("\x1f")
        if len(parts) == 5 and parts[0] == "v2" and parts[1] == state.language:
            key: TargetKey = parts[2], parts[3], parts[4]
            item = catalog_by_key.get(key)
            if item and _allowed(item, state) and key not in state.presented and key != state.last_key:
                return _recommend(item, state, snapshots, "due",
                                  "This target is due for review based on earlier practice.", queue_id=row.id)
            if item is None and state.focused_exercise_id in (None, "review"):
                return PlannerRecommendation("review", None, None, None, None,
                                             "An earlier practice item is due for review.",
                                             "due", state.language, row.id)
        elif state.focused_exercise_id in (None, "review"):
            return PlannerRecommendation("review", None, None, None, None,
                                         "An earlier review item is due; its detailed proficiency is unknown.",
                                         "due", state.language, row.id)

    if state.focused_exercise_id is None and len(state.new_concepts) >= state.new_item_limit:
        return _empty(state, "Today's new-item limit is reached. You can review a focused mode or stop.")
    new = [item for item in catalog if _allowed(item, state)
           and item.key not in state.presented and item.key != state.last_key
           and item.concept not in state.new_concepts
           and (item.key not in snapshots or snapshots[item.key].last_attempt_at is None)]
    if not new:
        return _empty(state, "There is no due or new work in this session. Choose a focused mode or finish.")

    # Pacing makes room for vocabulary, forms, and a validated sentence without
    # allowing the larger vocabulary catalog to crowd out the other skills.
    preferred = ("vocabulary", "verb_form", "sentence_translation")[state.completed % 3]
    paced = [item for item in new if item.skill == preferred] or new
    item = choose(paced)
    if item not in paced:
        raise ValueError("Chooser returned an item outside the candidate pool")
    return _recommend(item, state, snapshots, "new",
                      "A new target fits today's small learning load.")


def _allowed(item: PlannerItem, state: SessionState) -> bool:
    return state.focused_exercise_id in (None, item.exercise_id)


def _repair_candidate(
    catalog: Sequence[PlannerItem],
    state: SessionState,
    choose: Callable[[Sequence[PlannerItem]], PlannerItem],
) -> tuple[PlannerItem, TargetKey] | None:
    for trouble in reversed(tuple(state.recent_trouble)):
        if trouble in state.repair_attempted:
            continue
        # An authored sentence gives the same target useful context. Otherwise
        # use the opposite vocabulary direction, if one is available.
        sentences = {
            sentence.id for sentence in guided_sentences(state.language)
            if trouble in sentence_target_keys(sentence)
        }
        alternatives = [item for item in catalog if _allowed(item, state)
                        and item.key not in state.presented and item.key != state.last_key
                        and ((item.skill == "sentence_translation" and item.item_id in sentences)
                             or (trouble[0] == "vocabulary" and item.skill == "vocabulary"
                                 and item.item_id == trouble[2] and item.key != trouble))]
        if alternatives:
            # Prefer context before another isolated card.
            contextual = [item for item in alternatives if item.skill == "sentence_translation"]
            pool = contextual or alternatives
            item = choose(pool)
            if item not in pool:
                raise ValueError("Chooser returned an item outside the repair pool")
            return item, trouble
    return None


def _recommend(
    item: PlannerItem, state: SessionState,
    snapshots: Mapping[TargetKey, ReadinessSnapshot], source: str, reason: str,
    queue_id: int | None = None,
    repair_target: TargetKey | None = None,
) -> PlannerRecommendation:
    support = None
    if item.skill == "sentence_translation":
        sentence = next(sentence for sentence in guided_sentences(state.language) if sentence.id == item.item_id)
        support = recommend_sentence_support(
            sentence, snapshots, state.recent_trouble, state.support_override
        ).presentation_level
    return PlannerRecommendation(item.exercise_id, item.skill, item.direction, item.item_id,
                                 support, reason, source, state.language, queue_id, repair_target)


def _empty(state: SessionState, reason: str) -> PlannerRecommendation:
    return PlannerRecommendation(None, None, None, None, None, reason, "empty", state.language)
