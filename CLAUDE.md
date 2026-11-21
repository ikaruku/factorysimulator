# Project Rules for AI

Top reference: `docs/game-plan.md`. If anything conflicts with it, that document wins. Also read `docs/standards.md`.

- **Language: English everywhere** (code, comments, documentation, UI text, commit messages, error messages). Chat with the user may follow the user's language.
- Work through the stages in order (0, 1A, 1B, 2A, 2B, 3-8). Do not start the next stage until the user declares the current one passed.
- `client` and `server` may only import from `shared`, never from each other.
- Network message types and names live only in `packages/shared/src/protocol`.
- The server owns state; game data lives in `content/`; no magic numbers (use configuration).
- One file, one responsibility, at most ~300 lines.
- TypeScript strict, no `any`.
- Naming: files `kebab-case`, classes `PascalCase`, functions/variables `camelCase`, constants `UPPER_SNAKE_CASE`.
- Commands: `pnpm dev`, `pnpm test`, `pnpm lint`, `pnpm build`.
- Conventional Commits; update `CHANGELOG.md` and READMEs each stage.
- Done means: lint and tests pass, dev runs without errors, docs updated, user has tried it.
- Secrets never go into git.
