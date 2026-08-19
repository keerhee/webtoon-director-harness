# Architecture

A single generative pass converges too early on the first plausible staging. This repository separates generation, specialization, critique, synthesis, and validation.

Recommended hybrid pattern:
- Supervisor: Showrunner
- Fan-out / Fan-in: three direction candidates
- Expert pool: specialist directors
- Generator / Reviewer: creators vs critic
- Pipeline: intake -> candidates -> review -> synthesis -> QA -> export

Agents communicate through artifacts so work is traceable, reproducible, debuggable, and portable across tools.
