# Domain Docs

This repo uses a **single-context** domain documentation layout.

## Read when relevant

- Use root `CONTEXT.md` when interpreting or changing project concepts and terminology.
- Consult relevant decisions in `docs/adr/` when changing architecture or checking a design constraint.

If these files don't exist, proceed silently. Don't suggest creating them upfront. The `/domain-modeling` skill creates them lazily when terms or decisions actually get resolved.

## File structure

```text
/
├── CONTEXT.md
├── docs/adr/
├── src/invisible_research/
├── research/<owner>/
└── papers/<compendium>/
```

## Use the glossary's vocabulary

When output names a domain concept—in an issue title, refactor proposal, hypothesis, or test name—use the term defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the required concept isn't in the glossary, reconsider whether the language belongs to the project or note the gap for `/domain-modeling`.

## Flag ADR conflicts

If output contradicts an existing ADR, surface the conflict explicitly instead of silently overriding it.
