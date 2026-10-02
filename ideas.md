# Product ideas

This is a design direction for the existing French and Italian desktop app. The GUI remains the main experience. A guided path should make it easy to begin, while Vocabulary, Conjugation, Sentences, and Review remain available for self-directed practice.

## Home and the default walkthrough

Make Home the first tab. It shows the active language, reviews due, a short suggestion for what to work on, and a prominent **Continue learning** button. The learner can also choose a focused lesson directly. A session should be resumable or end cleanly with a recap.

The default walkthrough is a mixed session, not a fixed rotation through tabs. A planner selects the next small step from due reviews, unfamiliar vocabulary, weak verb forms, and sentence practice. It explains its choice in plain language: “Let's practice *nous avons* once, then use it in a sentence.” The learner may skip, ask for a hint, open the relevant lesson, change difficulty, or leave the walkthrough at any time.

Keep the lesson controls visible in every mode: pronunciation, audio, conjugation table, previous/next, and category or topic selection. Use a consistent prompt, answer, feedback, and navigation layout across screens.

## What “mastered” should mean

Track the skill demonstrated, not merely exposure to an item. For vocabulary, recognition (French → English) and production (English → French) are distinct. For conjugation, track a verb, tense, and person/form; later, track use of that form in a sentence. A reveal, hint, or flip-card “known” mark is useful evidence, but should not count the same as unaided typed recall.

Use learner-facing states such as **New**, **Practicing**, **Reliable**, and **Review due**. “Mastered” can be a motivating milestone for a skill recalled unaided on spaced occasions, including a later day; it is not permanent immunity from review. A lapse schedules more practice without erasing the learner's history. Avoid a single unexplained percentage that combines recognition, production, and sentence use.

Record each attempt with a stable content ID, language, skill/direction, time, correctness, hint/reveal use, and session ID. Keep an append-only attempt history and a derived scheduling state. This makes progress explainable, supports corrections to grading rules, and avoids losing progress when displayed wording changes.

## Sentence readiness: two time scales

**Long-term state** answers “What has this learner shown over days?” It drives review dates, suggested difficulty, and which words and forms are reliable enough to reuse. This persists across sessions.

**Session state** answers “What should happen next, right now?” It tracks recently missed targets, hints used, repeated errors, and the current learning goal. It can temporarily step down from an independent sentence to a guided one, or offer a short repair drill. Ending the session clears this temporary pacing state, while its attempts remain in the long-term history.

The planner should use both. A learner can be broadly reliable with *avoir* yet need support with *nous avons* today. One successful attempt today should not instantly confer long-term mastery; one miss should not permanently demote it. Suggested levels are defaults, never locked gates.

## Sentence practice that targets the difficult part

Give each sentence structured learning targets: vocabulary IDs, verb-form IDs, and a small number of new constructions. Examples include articles, contractions, and conjunctions. Do not infer all of this from the surface text after the fact. The core target of an exercise should be explicit so feedback can say what went wrong.

Use the same sentence at several support levels:

1. **Supported:** “We have an apple.” → `Nous ___ une ___` with optional choices or hints.
2. **Guided:** “We have an apple.” → `Nous ___ une pomme.`
3. **Independent:** “We have an apple.” → a blank answer field.

For `Nous avons une pomme.`, a wrong *avons* should link to the *avoir + nous* lesson; a wrong *pomme* should link to that word. Explain *une* too, but do not automatically treat an article mistake as failure of the two main targets. Track recognition and production separately, since the current sentence exercise tests French → English rather than English → French production.

Start with a small, curated set of tagged sentences and validate their metadata. Generated sentences should retain stable identity for the underlying template and chosen items so repeated practice can build on earlier evidence.

## Missions

A mission is a short situation, such as a café or train station, built from the same tracked skills. It is a destination for learned material, not a separate scoring system. The mission previews its core words/forms and any new construction, offers Supported/Guided/Independent play, and returns missed targets to normal practice. An early mission may allow unfamiliar material with generous scaffolding; readiness should determine the suggested support level rather than bar entry.

Prototype one mission after the sentence layer works. For example, a café mission could move from recognizing menu items to producing one request and then responding to a short exchange. Its recap should identify the specific words, verb forms, and constructions to revisit.

## Navigation, settings, and progress

Proposed tabs: **Home · Vocabulary · Conjugation · Sentences · Review · Progress**. Add Missions when one is ready. Home owns the recommended walkthrough; focused tabs preserve learner control.

Use the menu bar for **Language**, **Practice** (session options), **Tools** (Settings, Doctor, data export/backup), and **Help**. Settings should include audio, default language, session length, hint preference, and sentence support level. Doctor should report audio availability, storage location, and data health, with actionable fixes.

Progress should show what is due, what is becoming reliable, and where the learner struggles by skill and direction. A session recap should distinguish attempts from first-try unaided successes, hints, and corrected mistakes. Avoid making a streak the main measure of learning.

## Suggested implementation order

1. Add stable IDs and an attempt history alongside the existing review queue. Define how reveals, hints, and manual “known” marks affect evidence.
2. Add English → French vocabulary production and per-form conjugation tracking.
3. Build the Home tab and a mixed-session planner using long-term scheduling plus session pacing.
4. Add structured sentence targets, supported/guided/independent presentation, and targeted feedback.
5. Add Progress, Settings, Doctor, and one curated mission; adjust the planner using real usage.

## Public examples considered

- [French Daily](https://github.com/alexedmon1/french-daily): a default daily mix with focused practice modes and persistent spaced reviews.
- [ZHLI](https://github.com/radleylewis/zhli): separate study directions, adjustable session choices, and a progress dashboard.
- [repeater](https://github.com/shaankhosla/repeater): persistent review state and stable card identity when source formatting changes.
- [Tartarus](https://github.com/bahman-farhadian/tartarus): automatic next-work selection backed by per-item progress and session history. Its lack of a mode picker is an intentional design choice; this app should retain direct lesson control.
