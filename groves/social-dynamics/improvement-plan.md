# Social Dynamics — Improvement Plan

Deferred changes surfaced by the efficacy research
(`research/does-low-stakes-simulation-build-boundary-skills.md`). Items #1–#3 from that
review are already applied (recognition scoring, over-assertion failure modes, grove-level
principle broadened to calibrated assertiveness). What remains, in priority order:

## 1. Grader-calibration artifact — do first
**Why:** the research finding is that the LLM grader *is* the mechanism — it's the "feedback"
in instruction → modeling → rehearsal → feedback. If it mis-grades (rewards a smooth line
that would land badly, or flags a healthy boundary as "needy"), the drill trains the wrong
reflex. Its validity is currently unvalidated, so it silently underwrites everything else.
**What:** add `drills/dating-frame/calibration.md` — a small gold-standard set: worked
example responses, their correct grade on each rubric dimension, and *why*. Anchors the
grader to `principles.md` and gives a way to spot drift when the simulator is regenerated.
**Effort:** low. **Leverage:** high (de-risks the whole grove).

## 2. Score recognition explicitly in the live drill
**Why:** recognition is rung 1 and the highest-yield capacity for the target profile (the
appeaser who doesn't register the crossing). `principles.md` now names it and `rubric.md`
adds a **Detection** dimension — but the live simulator artifact
(`drills/dating-frame/artifacts/soc-dynamic-gemini-first-attempt.md`) predates this and
doesn't yet throw *ambiguous/soft* crossings or grade whether they were flagged.
**What:** revise the simulator prompt to include soft-test scenarios and to grade Detection.
**Effort:** low–medium. **Leverage:** high (it's the rung this profile fails first).

## 3. Second drill: `drills/saying-no/` (work / family)
**Why:** the "swallowing boundary-crossings" profile shows up *most* outside dating —
guilt-trips, unreasonable asks at work. Dating-frame is a narrow instance of a broad problem;
the principles are already drill-agnostic, so the seam exists.
**What:** new drill folder (context + rubric + simulator artifact) for non-dating boundary
pressure. Reuse `principles.md`; define drill-specific dimensions.
**Effort:** medium. **Leverage:** medium (coverage of the real target contexts).

## 4. Activate the leak-log as a real-world rep loop
**Why:** `context.md` notes an Anki leak-log as a *future* seam. The research now motivates
it: text can't train performance-under-arousal (rung 3, "Regulation") — transfer needs real
reps (rung 4). A log of real-world attempts/misses that feeds back into drill scenarios
closes the loop the simulator structurally can't.
**What:** promote the leak-log from "someday" to an actual capture → review → feed-back-into-
drills flow. This is what turns the grove from a scaffold into something with a path to
real-world transfer.
**Effort:** medium–high. **Leverage:** medium (it's the ceiling-raiser, but only useful once
1–3 are solid).
