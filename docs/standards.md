# Code Standards (permanent)

Derived from the "Permanent standards" and "Architecture and principles" sections of [game-plan.md](game-plan.md). Everything in this project is written in English.

## Principles

1. Single source of truth: network types and messages exist only in `shared`.
2. The server is authoritative; the client only sends input and renders results.
3. Data-driven: maps, emotes and configuration are loaded from `content/`.
4. Small modules: one file, one responsibility, at most ~300 lines.
5. World objects are entity-component based.
6. No magic numbers: centralized configuration.

`client` and `server` may use `shared`, but never each other.

## Standards

| Area             | Standard                                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------------------------- |
| Code language    | TypeScript strict, no `any`                                                                                     |
| Naming           | Files/folders `kebab-case`, classes `PascalCase`, functions/variables `camelCase`, constants `UPPER_SNAKE_CASE` |
| Text language    | English for everything: code, comments, docs, UI text, errors, commits                                          |
| Formatting       | Prettier and ESLint; one command: `pnpm lint`                                                                   |
| Commands         | `pnpm dev`, `pnpm test`, `pnpm lint`, `pnpm build`                                                              |
| Git              | `main` (stable), `dev` (work), `feature/<name>`; Conventional Commits                                           |
| Versioning       | SemVer, `CHANGELOG.md` updated every release                                                                    |
| Network protocol | Only in `shared/protocol`, versioned; mismatched versions are rejected with a clear message                     |
| Tests            | Unit tests for core logic; 30-connection bot test before release                                                |
| Documentation    | Each main folder has a short `README.md`; major decisions in `docs/decisions/`                                  |
| Assets           | GLB max 5 MB per object, textures max 2048 px (1024 px on phones), compressed                                   |
| Configuration    | `.env` and config files; secrets never in git                                                                   |

## Definition of done

`pnpm lint` and `pnpm test` pass, `pnpm dev` runs without errors, README and `CHANGELOG.md` are updated, and the user has tried the result.
