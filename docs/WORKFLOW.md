# Workflow — Opus↔Sonnet File-Based Loop

How the two-model review cycle actually works in practice.
This is the operational version of `PROJECT_PLAN.md §9`.

---

## Why File-Based Context

Switching between models (Opus for critique, Sonnet for implementation) causes context loss in live chat. The five files in `docs/phase_context/` replace live chat memory. A new model session reads these files and picks up exactly where the last session left off.

This means: **project memory lives in the repo, not in chat history.**

---

## The Five Files

| File | Role | Who writes it |
|------|------|---------------|
| `current_phase.md` | Active phase + exit criteria | Updated by whoever closes a phase |
| `review_notes.md` | Opus critique of the current phase | Opus only |
| `implementation_status.md` | Append-only progress log | Sonnet (one entry per session) |
| `open_questions.md` | Unresolved decisions | Anyone; mark OPEN/RESOLVED |
| `next_actions.md` | Immediate next steps | Updated by Sonnet at end of session |

---

## One Cycle

### Step 1: Set active phase

Update `current_phase.md`:
- phase name and number
- status: IN PROGRESS
- exit criteria checklist (specific, checkable items)

### Step 2: Opus critique

Prompt Opus with the advisor role. Opus reads:
- `CLAUDE.md`
- `PROJECT_PLAN.md`
- `current_phase.md`
- `implementation_status.md` (if exists)
- `open_questions.md`

Opus writes critique into `review_notes.md`. The critique must include: risks, scope boundaries, what not to do, implementation guidance for Sonnet.

### Step 3: Switch to Sonnet

Prompt Sonnet with the implementation role. Sonnet reads all five files before touching any code.

Sonnet implements the scoped deliverables. At the end of the session, Sonnet:
- appends to `implementation_status.md` (what was done, what remains, decisions made)
- updates `next_actions.md` (mark completed items, add new items if needed)
- writes any new unresolved decisions to `open_questions.md`

### Step 4: Opus verification

Before declaring a phase done, ask Opus to do a verification pass. Opus reads the exit criteria from `current_phase.md` and checks each item independently — not by trusting Sonnet's log, but by looking at the actual files.

If items fail: Sonnet fixes them. Opus re-checks only the failed items.

### Step 5: Close the phase

When the checklist is all green:
- Update `current_phase.md`: `Status: COMPLETE`, add `Completed:` date
- Commit all changes
- Start the next cycle with the next phase

---

## Rules for Writing to Phase Context Files

- `review_notes.md`: Opus writes, Sonnet reads. Sonnet never overwrites Opus critique mid-phase.
- `implementation_status.md`: append only. Do not edit previous entries. New entries go at the top.
- `open_questions.md`: anyone may add a question. Mark RESOLVED (never delete) once decided.
- `current_phase.md`: update status fields only. Do not change exit criteria mid-phase without a reason logged in `implementation_status.md`.
- `next_actions.md`: Sonnet maintains. Keep under 10 items. Move completed items to the Completed section (do not delete them).

---

## What Breaks This Workflow

- Adding to `review_notes.md` from Sonnet's session (mixes critique with implementation).
- Closing a phase without an Opus verification pass.
- Letting `current_phase.md` lag behind actual work (R6 from Opus review).
- Using chat memory instead of file updates ("I'll remember to add that question later").

---

## Proposal Changes

Any change to `CLAUDE.md` must go through `docs/proposals/`. See `docs/proposals/README.md`.
