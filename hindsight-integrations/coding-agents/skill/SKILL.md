---
name: hindsight-coding-agent
description: How this machine's Hindsight coding-agent memory works — the plugin behind the 🧠 banner. Use when the user says "store/remember this in hindsight", asks what the memory/knowledge pages are, wants to configure per-repo memory (disable, rename banks, git depth), or something memory-related looks broken.
---

# Hindsight Coding-Agent Memory

This machine runs the `hindsight-coding-agents` plugin: long-term project memory for coding
sessions, backed by a Hindsight server. You (the agent) are already wired into it — this skill
explains what happens automatically, which tools you have, and how to configure or debug it.

## What happens automatically (no action needed)

- **Per-repo memory bank**: each repository resolves to a bank (shown in the session banner:
  `↳ memory bank “coding-agent::<repo>”`). Worktrees share the main repo's bank.
- **Ingestion builds itself**: on first open, the bank is seeded from recent commit messages and a
  read-only codebase survey; every session start, a background engine tops it up (new commits, new
  conversations) and keeps 5 knowledge pages current. There is NO ingest command to run.
- **Session synthesis**: the first prompt of a session triggers one deep memory synthesis
  (`reflect`) injected into context. Later turns inject nothing automatically.
- **Write-back**: the session transcript is retained into the bank automatically at session end
  (per-turn on opencode). The user never needs to "save" a conversation.

## Storing things deliberately

When the user says "store this in hindsight" / "remember this":

- The **current conversation** is captured automatically at session end — say so; no tool needed.
- An **external document, notes, or durable findings** → `hindsight_ingest_document(title, content)`.
- A **new feature/initiative being started** → `hindsight_capture_initiative(title, summary)`,
  right after the plan is agreed and before code is written.
- A **plan that materially changed** (goal, scope, or rationale — including mid-implementation) →
  call `hindsight_capture_initiative` again with `relates_to_page_id` set to that initiative's page
  id, summarising the _current_ intent. Same page, updated plan — never a second page. Trivial
  course-corrections don't count.

## Retrieving

- `hindsight_search_knowledge_pages(query)` — FIRST STOP for project questions (components,
  conventions, past decisions, initiatives). Server-side hybrid search, fast.
- `hindsight_read_knowledge_page(page_id)` / `hindsight_list_knowledge_pages` — read pages fully.
- `hindsight_reflect(query)` — deep reasoning over the whole memory for WHY questions and exact
  decided values; slower (seconds), use deliberately.
- Credit visibly whenever memory informs an answer: start that part with
  `🧠 From Hindsight memory (<page>): …` — and never credit memory that didn't contribute.

## Correcting wrong or stale memory

If you verify that something Hindsight served is wrong or outdated (the code, git, or an external
source contradicts it), FIX THE RECORD — don't just ignore it. Call
`hindsight_ingest_document` with:

- **title**: `Correction: <topic>` (e.g. `Correction: retry policy 4xx set`)
- **content**: (1) what memory claimed, (2) what is verifiably true now, (3) the evidence you
  checked (file/commit/output). Quote exact values verbatim.

Newer facts supersede older ones in retrieval, so one clear correction permanently outranks the
stale memory. Do this whenever you catch a wrong injected memory, a stale knowledge-page claim, or
an outdated decision — silent disregard leaves the trap armed for the next session.

## Configuration — ONE file: `~/.hindsight/coding-agent.json`

The file is the normal configuration surface. Scalar fields can also be supplied through their
`HINDSIGHT_<FIELD_IN_CAPS>` environment variable (for example,
`HINDSIGHT_DYNAMIC_BANK_ID`, `HINDSIGHT_BANK_ID_TEMPLATE`, `HINDSIGHT_OPT_IN_PATHS`, and
`HINDSIGHT_MAX_PARALLEL_RETAINS`); file values win over environment values. `HINDSIGHT_CONFIG`
relocates the file. `HINDSIGHT_DIAG_FILE`, `HINDSIGHT_LOG_FILE`, and `HINDSIGHT_LOG_LEVEL` control
diagnostics. Map-valued fields (`mapPathToBank`, `harnesses`, `banks`, and `retainMetadata`) are
file-only. Layering, later wins: defaults → environment → file → `harnesses.<name>` →
`banks.<resolvedBankId>`.

```jsonc
{
  "apiUrl": "http://localhost:8888", // your Hindsight server
  "apiToken": "…", // Hindsight Cloud only
  "gitIngest": "message", // "message" | "full" (per-commit diffs) | "none"
  "dynamicBankId": true,
  "bankIdTemplate": "coding-agent::{gitProject}",
  "resolveWorktrees": true,
  "optInOnly": false,
  "optInPaths": ["~/work/client-x"],
  "retainTags": ["project:{gitProject}"],
  "retainMetadata": { "repo": "{gitProject}" },
  "harnesses": { "claude-code": { "disabled": true } }, // per-agent override of anything
  "mapPathToBank": { "/Users/me/work/client-x": "client-x-memory" }, // path-prefix → bank
  "banks": {
    // per-repo control, keyed by RESOLVED bank id
    "coding-agent::secret": { "disabled": true }, // blacklist a repo
    "coding-agent::old": { "bank": "team::shared" }, // rename / converge banks (single hop)
    "coding-agent::mono": { "gitIngest": "full", "retainSessions": false },
  },
}
```

Key behavioral fields (any of them valid per-harness or per-bank): `disabled`,
`retainSessions` (transcript write-back opt-out, history import included — recall and git ingest keep working), `gitIngest`,
`reflectTimeoutMs` (AUTOMATIC session reflect, default 120000; hooks cap at 25s),
`reflectToolTimeoutMs`/`reflectBudget` (the agent-invoked `hindsight_reflect` tool: default 330000 —
above the server's 300s reflect wall timeout — and "high"), `autoReflect` (true; false = no injected
first-prompt synthesis — the agent is instead told to call `hindsight_reflect` on new goals),
`pageRefreshEveryTurns` (10),
`pageTriggerType`/`pageTriggerCron` (when NEW knowledge pages refresh: `auto-refresh` (default) after
each consolidation, `cron` on a schedule, `manual` never — existing pages keep the trigger they were
created with), `autoSeed`/`seedLimit` (true/300),
`codebaseSurvey`/`surveyModel`/`surveyBudgetUsd` (true/haiku/2), `surveyRefreshCommits` (0=off),
`maxParallelRetains` (10; lower it if bursts receive 429s), and `logLevel` ("info").

Daemon-only settings are `serverMode: "daemon"`, `apiPort` (default `9077`),
`daemonProfile` (default `coding-agent`), `daemonIdleTimeout` (unset means keep it running),
`embedVersion` (default `latest`), and `embedPackagePath` (a local checkout for development).
`apiPort` is deliberately separate from the usual self-hosted server port `8888`.

Bank routing fields are also valid at the top level:

- `bankId` selects one static bank. If it is omitted, the default is dynamic per-repository
  resolution; set `dynamicBankId: false` to force a static bank.
- `bankIdTemplate` controls dynamic IDs. It supports `{gitProject}`, `{project}`, `{harness}`,
  `{channel}`, and `{user}`. The default `coding-agent::{gitProject}` shares a repository bank
  across coding agents.
- `resolveWorktrees` defaults to `true`, so linked worktrees inherit the main repository's bank,
  mapping, and opt-in status.
- `mapPathToBank` maps absolute path prefixes to a named bank. The **longest matching prefix wins**
  and mapping a parent directory also captures every nested repository unless a more specific entry
  overrides it. It has no environment-variable form.

With `optInOnly: true`, memory is inert unless the directory is under an `optInPaths` prefix or a
`mapPathToBank` entry. A bare `bankId` does not opt a project in: it names a bank, not an approved
directory.

The resolved bank can be controlled after routing with `banks.<resolvedBankId>`:

```jsonc
{
  "banks": {
    "coding-agent::private-project": { "disabled": true },
    "coding-agent::old-name": { "bank": "team::shared" },
  },
}
```

`disabled` suppresses recall injection, retain, and session-start work for that bank. `bank` is an
exact-match alias/rename of the destination; it is the supported way to rename a resolved ID.

Config is read at process start, not watched: a hook harness picks an edit up on the next prompt, a
persistent plugin (opencode, Kilo, Cline, Prime Agent, dsh) only after the agent restarts, and the
MCP server in the next session. `apiToken` is the exception — re-read whenever the server rejects a
request, so rotating it needs no restart. `hindsight_diagnose` reports the file's token and the
running client's separately, which is how you tell a stale credential from a wrong one.

Blacklist a whole directory tree: map it to one bank and disable that bank —
`"mapPathToBank": {"~/scratch": "scratch"}` + `"banks": {"scratch": {"disabled": true}}`.

Bank resolution order: `mapPathToBank` longest prefix → static `bankId` → template
(default `coding-agent::{gitProject}`) → the matching `banks.<id>` section (its `bank` field
renames the destination). Two repos share memory by converging their `banks.<id>.bank` on one
name, or by one `mapPathToBank` prefix over their parent directory.

`{gitProject}` comes from Git's common directory. Outside a Git repository, it falls back to the
directory where the session started. Starting sessions from arbitrary non-Git parent directories can
therefore create separate, low-value banks (for example `coding-agent::tmp`); use a deliberate
`bankId`, `mapPathToBank`, or `optInOnly` policy for non-repository work.

## Install / update (for setting up another machine or harness)

```bash
npx @vectorize-io/hindsight-coding-agents install all     # every detected agent
npx @vectorize-io/hindsight-coding-agents install codex   # or specific: opencode|claude-code|codex|antigravity-cli|cursor-cli
npx @vectorize-io/hindsight-coding-agents uninstall       # removes exactly what install added
# updating is the same install command again — it re-copies the runtime in place
```

## Debugging

- **Readiness**: `hindsight_sync_status` — `synced: true` = seeded memory queryable; also shows
  gitlog freshness, per-commit deepening progress, survey state (`surveyDocs` 0–4 = findings
  present; baseline without findings retries automatically), and active extraction ops.
- **Logs**: `$TMPDIR/hindsight-coding-agent/plugin.log` (leveled; set `"logLevel": "debug"` or
  `HINDSIGHT_LOG_LEVEL=debug` to mirror every event) and `/tmp/hindsight-plugin.log` (structured
  JSONL diag events with timings: `session_start`, `reflect_ok`, `deepen_done`, `retain_ok`, …).
- **Reset a repo's memory**: delete its bank on the server — the bank is the ONLY state; the next
  session is a true first-open. No client files to clean.
- **Rule of thumb**: memory silently missing → check the diag log for whether `session_start`/
  `deepen_started` ever fired for that bank; a session started before the plugin was installed has
  no SessionStart behind it (its first prompt after install self-heals).
- **Internal marker docs you may notice** (safe to ignore, safe to delete): `survey-baseline:<sha>`
  — "🛰️ researching…" while a codebase survey runs, flipped to "✅ completed" once its findings
  land. Retained under the `survey` strategy, whose marker rule extracts NOTHING from status markers;
  powers the re-survey cadence and `surveyBaseline` in sync status. `gitlog:<repo>` is the
  aggregated commit-message seed document.
- Failures never break the agent: reflect/pages/retain failures degrade to a normal memoryless
  turn and are recorded in the logs.
