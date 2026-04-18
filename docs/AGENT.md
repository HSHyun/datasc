# AGENT.md

## Scope
- Workspace: `/Users/hsh/datasc`
- Course: senior year, semester 2, Data Science
- Source docs: `/Users/hsh/datasc/pdf/`
- Main data: `/Users/hsh/datasc/data/FAF5.7.1_2018-2024.csv`
- Metadata: `/Users/hsh/datasc/data/FAF5_metadata.xlsx`
- Goal anchor: `/Users/hsh/datasc/pdf/IC_PBL시나리오.pdf`

## Read Order
- `docs/HANDOFF.md`
- `docs/EVENTS.md`
- `docs/AGENT.md`
- `docs/FEEDBACK.md`
- `docs/COMMANDS.md`

## Rules
- For non-trivial tasks, make a brief plan before editing.
- State assumptions explicitly and distinguish facts from inferences.
- Fix root causes, not symptoms.
- Verify results when applicable before calling work done.
- Reduce unnecessary questions; make reasonable reversible assumptions when risk is low.
- Do not edit code or files unless the user explicitly asks for modification or execution.
- Do record durable rules, preferences, failures, and context in `docs/` without asking for permission again.
- Do keep `docs/` synced when durable context is added elsewhere such as `memo.md`.
- Keep docs in English.
- Keep docs short and operational.
- Keep replies concise and direct.
- Do not append optional CTA lines such as "if you want, I can continue", "I can do X for you", or "let me know".
- Prefer facts, rules, paths, commands, and next actions.
- Avoid long explanations written for humans.
- Keep shared docs under `/Users/hsh/datasc/docs/`.
- Do not create ad hoc `docs/` folders inside subdirectories.
- If `docs/` or its memory files do not exist, ask for permission before creating them.
- Prefer the simplest structure that works. Avoid over-engineering.
- Favor DRY, SRP, and YAGNI when practical.
- Favor high cohesion, low coupling, explicit logic, named constants, and readability over cleverness.
- Use chapter PDFs as reference material.
- Use `IC_PBL시나리오.pdf` as the final target definition.

## Notes
- Large files: inspect schema/sample before full loading.
- Do not guess column meaning, units, or missing-value rules without evidence.
- If a durable clarification is written into `memo.md`, mirror the relevant rule or fact into `docs/`.
