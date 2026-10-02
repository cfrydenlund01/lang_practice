# Reinvented GUI implementation plan

## Goal and boundaries

Keep the Tkinter GUI as the primary experience. On launch, Home should offer a clear **Continue learning** path that chooses a useful mix of review, vocabulary, conjugation, and sentences. The learner can always choose a focused tab, open a lesson, request help, change support level, or stop. Sentence difficulty should use both persistent learning evidence and short-lived session context.

This plan implements the guided experience, sentence readiness, progress views, Settings, and Doctor. Other product ideas remain in `ideas.md`; they are not delivery criteria for this plan. Do not replace the GUI with a terminal interface or rewrite the app around a new framework.

## Agent workflow and model policy

- Execute steps in order. Give each step to one bounded agent with a fresh context; hand off through `plan.md`, `runbook.md`, and the changed code. Avoid concurrent edits to the same persistence or GUI files. A coordinator checks the step's acceptance criteria before starting the next one.
- At the start of a step, read this plan, the latest runbook entry, and only the relevant source/tests. At the end, update `runbook.md` with work completed, changed files, tests and manual checks, decisions, problems, possible corrections, and the next step's starting point. Do not use the full conversation as the handoff.
- Model assignments below are starting choices. Prefer GPT-5.6 Terra for bounded work and GPT-5.6 Sol for intertwined design and code. Use the listed reasoning effort first. Increase to Sol `xhigh` only for a concrete unresolved problem. Consider GPT-6 Astra only if Sol at `xhigh` has failed to resolve a documented, narrow blocker; record the attempted approaches and delegate only that blocker. No planned step requires Astra.
- Keep changes incremental and runnable. Preserve existing learner data and current direct-practice controls. Add tests for scheduling, migrations, scoring, and other behavior that can silently mislead a learner. Use manual GUI checks for layout, focus, and interaction.

The model choices follow [official OpenAI model guidance](https://developers.openai.com/api/docs/models): Terra balances capability and cost; Sol is the stronger GPT-5.6 option. Reasoning levels below are phase-specific estimates, not claims that a model is incapable of other work.

## Steps

### 1. Baseline and contracts

**Agent:** `gpt-5.6-terra` · **Reasoning:** `medium`

Document the current exercise flows, review schema, language switching, and test baseline in the runbook. Define the core interfaces before changing the GUI: stable exercise/item ID, skill and direction, attempt event, persistent readiness snapshot, session state, and a planner recommendation with a human-readable reason. Decide how older review rows are interpreted without inventing past attempts.

**Done when:** The contracts and migration approach are written in the runbook; the current tests pass; later steps can implement against agreed types. Keep this step small and avoid broad refactoring.

### 2. Durable learning evidence

**Agent:** `gpt-5.6-sol` · **Reasoning:** `high`

Extend `review_db.py` and related models with stable IDs and an append-only attempt history. Store language, skill, direction, item/form ID, session ID, timestamp, first-try result, hint/reveal use, and answer where relevant. Maintain or derive due-state separately from the history. Migrate the existing SQLite schema without discarding review rows; treat old rows as legacy scheduling data with unknown detailed proficiency. Keep French and Italian data separate. Ensure repeated launches and interrupted sessions are safe.

**Done when:** Migration tests cover an old-schema database, repeated migration, both languages, and read/write of new attempts. Existing practice and review still work with previously saved data.

### 3. Capture the skills the app actually tests

**Agent:** `gpt-5.6-terra` · **Reasoning:** `high`

Wire attempts from the focused practice tabs into the new event model. Add English → target-language vocabulary production alongside current recognition; keep them distinct. Record conjugation by infinitive, tense, and person rather than by displayed prompt text. Distinguish unaided first attempts, helped answers, reveals, skips, and flip-card self-ratings. Give feedback that identifies the target and links to an existing lesson or pronunciation guide when possible. Avoid double-counting repeated checks on one prompt.

**Done when:** Tests show the correct skill/direction is recorded and no prompt is counted twice accidentally. Both languages, language switching, keyboard entry, reveal, and existing lesson controls work in the GUI.

### 4. Sentence content and readiness

**Agent:** `gpt-5.6-sol` · **Reasoning:** `high`

Add structured metadata to a small, curated sentence set in each language: stable sentence ID, target vocabulary IDs, target verb-form IDs, and any explicitly taught construction. Preserve the current sentence browsing/generator path, but use only validated, tagged sentences for guided readiness until generated content can provide trustworthy metadata. Build a pure readiness function that combines persistent evidence for target skills with current-session misses and help use. It recommends **Supported**, **Guided**, or **Independent** presentation without locking any level.

Implement targeted sentence feedback: identify a missed core word or verb form and offer its lesson. Explain other sentence elements without incorrectly marking every target as failed. Avoid a general-purpose grammar parser; use authored answer variants and explicit targets.

**Done when:** Tests cover unknown skills, mixed strong/weak skills, a same-session miss, a later-session return, hinted answers, and user-selected support level. At least one complete sentence pathway works for French and Italian.

### 5. Mixed-session planner

**Agent:** `gpt-5.6-sol` · **Reasoning:** `high`

Create a planner outside Tkinter that chooses the next step from due work, new items within a session limit, recent misses, and sentence readiness. Its output includes a plain-language reason and the destination exercise. Session state should hold recent trouble spots, the current goal, and pacing; persistent history remains the source for future days. Let the learner skip, choose a focused mode, adjust support, and end early. Show a recap of first-try results, helped attempts, and specific targets to revisit.

**Done when:** Deterministic tests with fixed clock/randomness demonstrate due-first behavior, a bounded new-item load, a sensible repair step after a miss, no repeated immediate loop, correct language isolation, and an empty-queue path. A one-day success does not by itself imply lasting proficiency.

### 6. Home and unified practice presentation

**Agent:** `gpt-5.6-sol` · **Reasoning:** `high`

Make Home the first tab, showing due work, a concise recommendation, **Continue learning**, and clear links to focused tabs. Connect the planner to a guided practice view while retaining Vocabulary, Conjugation, Sentences, and Review as direct choices. Standardize the position and wording of prompt, answer, hint, feedback, lesson, audio, and navigation controls. Keep the right-side guide useful for the active item. Retain practical keyboard navigation and visible focus.

**Done when:** A learner can launch, complete a mixed session, follow a targeted sentence repair, switch to a focused lesson, return Home, and close/reopen without losing durable progress. Manually inspect at minimum window size, default size, both languages, and audio-unavailable state; record observations in the runbook.

### 7. Progress, Settings, and Doctor

**Agent:** `gpt-5.6-terra` · **Reasoning:** `medium`

Add Progress views for due counts, recent first-try performance by skill/direction, and troublesome targets. Add menu access to Settings for language, session length/new-item limit, audio preference, and default sentence support. Add Tools → Doctor for storage location and database health, TTS/playback availability, and actionable diagnostics. Keep settings changes scoped and persistent. Make the session recap and Progress use the same definitions.

**Done when:** Values survive restart, diagnostics do not mutate study history, data displayed by Progress agrees with stored attempts, and every menu item has a useful empty/error state.

### 8. Integration, accessibility, and release check

**Agent:** `gpt-5.6-sol` · **Reasoning:** `high`

Review the end-to-end learning path and migration, address discovered gaps, and update README with the new GUI workflow and data location. Check keyboard-only use, focus order, readable feedback, small-window layout, French/Italian text, optional audio failure, and database recovery behavior. Run the full suite and perform a brief manual walkthrough in each language. Record any deferred issues rather than silently changing the product scope.

**Done when:** Tests pass, manual checks are recorded, old data remains usable, the documented walkthrough matches the app, and the runbook has a final completion summary with known limitations.

## Handoff and scope checks

Every agent should state in `runbook.md` whether its acceptance criteria passed, which files changed, commands/tests run and their results, any schema or interface decision, and the next action. If a criterion fails, leave the step in progress and describe the exact blocker and a proposed correction. Do not call an untested screen complete merely because it renders.

Do not introduce a lasting proficiency badge or a scenario mode under this plan. The durable evidence and sentence metadata are foundations that may support later ideas, but this release is complete when the guided GUI and sentence readiness work well on their own.
