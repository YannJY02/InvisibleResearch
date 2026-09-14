# Utils Index

Reusable utilities live with their owning package under `src/invisible_research/`.

Use the [command mapping](../data/data-script-mapping.md) for acquisition,
processing, and validation entry points. Keep owner-specific commands in their
research README rather than duplicating them here.

- `invisible_research.document_governance`: checks document placement, local
  links, and preserved source hashes without accessing research data or APIs.
- `invisible_research.artifacts`: content identity and Artifact Version checks.
- `invisible_research.data`: resolves locations in the external data workspace.
