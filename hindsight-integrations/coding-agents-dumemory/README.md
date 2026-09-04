# dumemory-coding-agents

Long-term project memory for **coding agents**, backed by
[DuMemory](https://cloud.memory.bj.baidubce.com). One package, several agents: a shared
reflect-and-inject core with a thin entry point per agent (**opencode**, **opencode 2**,
**Kilo CLI**, **Cline CLI**, **pi**, **Prime Agent**, **DeepSeek Harness**, **Claude Code**,
**Codex CLI**, **DeepAgents Dcode**, **Antigravity CLI**, **Cursor CLI**, **GitHub Copilot CLI**,
**Devin CLI**, **Grok Build**, **Qwen Code**). Ingestion is fully automatic — there is no setup
command: a repo's git history and conversations flow into its memory bank in the background as you
work.

The premise: most of a real fix is derivable from the code, but the _last mile_ often hinges on a
project-specific decision that isn't in the code at all — a rounding rule, a retry allowlist, a
tie-break policy. Those decisions live in git history and past conversations. This package puts them
in front of the agent at the moment it starts working, and keeps a curated set of **knowledge pages**
(architecture, conventions, in-flight initiatives) that future sessions start from.

## Install

<!-- skill:begin title="Install / update" -->

```bash
npx @baiducloud/dumemory-coding-agents install all          # every detected agent, wired natively
npx @baiducloud/dumemory-coding-agents install claude-code  # or just one
npx @baiducloud/dumemory-coding-agents uninstall all        # removes exactly what install added
npx @baiducloud/dumemory-coding-agents update               # refresh the runtime only, no rewiring
```

`install` takes an explicit target — `all`, or one or more harness names. A bare
`npx @baiducloud/dumemory-coding-agents install` changes nothing and prints the choice, so wiring every agent on
the machine is never something that happens by accident. **Updating is the same `install`
command again** — it re-copies the runtime in place.

Day to day you should not have to: once a day, a session start checks npm and re-stages a newer
runtime in the background (`autoUpdate`, on by default — set it to `false` to pin the version you
have). That is the `update` command above, which refreshes the copy every wired agent already
points at and deliberately touches no host config; re-run `install` yourself after a release that
adds a new hook, or to wire another agent.

<!-- skill:end -->

On a terminal it asks for your **API token**; scripted installs pass `--api-token <token>` (see
[Where memory lives](#where-memory-lives)). It is asked only once, and never again on re-install.

### Per agent

Same command, only the harness name changes. Run after installing the package globally.

#### Claude Code

```bash
npx @baiducloud/dumemory-coding-agents install claude-code
```

3 hooks in `~/.claude/settings.json`, MCP via `claude mcp add` (user scope), and the companion skill.

#### Codex CLI

```bash
npx @baiducloud/dumemory-coding-agents install codex
```

3 hooks in `~/.codex/hooks.json` plus `[mcp_servers]` in `config.toml` (needs `codex_hooks = true`).

#### DeepAgents Dcode

```bash
npx @baiducloud/dumemory-coding-agents install dcode
```

The installer registers this package as a local marketplace with Dcode, then invokes Dcode's own
`plugin install` command. The package is a native Agent Plugin: its root `plugin.json` contributes the shared skill, the
Hooks V2 `SessionStart`, `UserPromptSubmit`, and `Stop` lifecycle, and the namespaced
`dumemory_*` MCP server. Enable the plugin through Dcode's normal plugin manager; no Dcode config
patcher or compatibility bridge is required.

Dcode namespaces a plugin's MCP tools, so they appear as
`plugin__dumemory-coding-…__dumemory_…` rather than under their bare names — the agent resolves
them from the tool guide either way. In headless runs (`dcode -n`) Dcode allows the read-only
DuMemory tools and gates the two that write (`dumemory_ingest_document`,
`dumemory_capture_initiative`) behind an approval it has no UI for; use the interactive TUI to
capture an initiative or ingest a document. For the same reason the one-time codebase survey runs
under another installed agent's CLI when there is one, exactly as it does for Cursor, Copilot,
Devin, Grok Build, Cline, Kilo and Prime Agent.

#### opencode

```bash
npx @baiducloud/dumemory-coding-agents install opencode
```

A plugin entry in `~/.config/opencode/opencode.json` — native tools, no MCP needed.

#### opencode 2

```bash
npx @baiducloud/dumemory-coding-agents install opencode2
```

opencode v2 (`npm @opencode-ai/cli@beta`) installs its `opencode2` binary **alongside** v1 and
rewrote the plugin API, so it is a harness of its own. It writes the same plugin entry to the same
`~/.config/opencode/opencode.json` — the two CLIs share that file, and v1 rejects the whole config
when it encounters v2-shaped plugins, while v2 rejects v1 plugins. The installer detects which you
have (or wires both) and generates a single entry whose wrapper inspects its host at runtime,
loading the correct implementation while keeping the file valid for both. Beyond the shim, the
injection, the native `dumemory_*` tools and session write-back are identical.

#### Kilo CLI

```bash
npx @baiducloud/dumemory-coding-agents install kilo
```

A plugin entry in `~/.config/kilo/kilo.json` — native tools, no MCP needed.

#### Cursor CLI

```bash
npx @baiducloud/dumemory-coding-agents install cursor-cli
```

3 hooks in `~/.cursor/hooks.json` and MCP via `~/.cursor/mcp.json`.

#### GitHub Copilot CLI

```bash
npx @baiducloud/dumemory-coding-agents install copilot-cli
```

3 hooks in `~/.copilot/hooks.json` and MCP via `~/.copilot/mcp-servers/dumemory-coding-agents.json`.

#### Grok Build

```bash
npx @baiducloud/dumemory-coding-agents install grok-build
```

Configured in Grok Build's global config file (`~/.grok/config.toml`): hooks under
`[features] hooks = true` and `~/.grok/hooks.json`, plus `[mcp_servers]` in `config.toml`.

#### Qwen Code

```bash
npx @baiducloud/dumemory-coding-agents install qwen-code
```

Configured in Qwen Code's global settings (`~/.qwen/settings.json`), which speaks the same hook
protocol as Claude Code: `UserPromptSubmit`, `SessionStart`, and `Stop` hooks under the `"hooks"`
key, plus MCP tools registered into the user scope via `qwen mcp add` and the companion skill in
`~/.qwen/skills`. Ingestion, reflect, session-start knowledge pages and session write-back all work
identically.

#### Antigravity CLI

```bash
npx @baiducloud/dumemory-coding-agents install agy
```

Lifecycle hooks, MCP, and the `DuMemory · <bank>` status line.

#### Devin CLI

```bash
npx @baiducloud/dumemory-coding-agents install devin-cli
```

3 hooks in `~/.devin/hooks.json` and MCP via `~/.devin/mcp.json`.

#### Cline CLI

```bash
npx @baiducloud/dumemory-coding-agents install cline-cli
```

A native Cline plugin registered in `~/.cline/plugins.json` and MCP via `~/.cline/mcp.json`.

#### pi

```bash
npx @baiducloud/dumemory-coding-agents install pi
```

An extension entry in `~/.pi/agent/settings.json`, plus the companion skill in
`~/.pi/agent/skills` — native tools, no MCP needed.

This command is the only supported route, for pi and for Prime Agent below. Installing us as a pi
package (`pi install npm:@baiducloud/dumemory-coding-agents`) is deliberately not wired: both
hosts read the same `pi` key of a package's `package.json`, and that key can only name one entry —
whichever host it did not name would load the other's bundle and report itself as the wrong agent,
taking that harness's config section and stamping every document it retains with it. So the package
carries no `pi` key at all, and each host is pointed at its own bundle by the install command above.

#### Prime Agent

```bash
npx @baiducloud/dumemory-coding-agents install prime-agent
```

Prime Agent is a fork of pi, so it is wired the same way: an extension entry, here in
`~/.prime/agent/settings.json`, plus the companion skill in `~/.prime/agent/skills` — native tools,
no MCP needed. Installing both is fine and expected:
each host loads its own entry from its own settings file, and like every other pair of agents they
**share one bank per repo** (the default `coding-agent::{gitProject}`), so what you tell pi is there
when you open Prime Agent. Separate entries are what keeps each side attributable — its own
`harnesses.<name>` config section, and its own agent stamped on every document it retains.

#### DeepSeek Harness

```bash
npx @baiducloud/dumemory-coding-agents install dsh
```

A Cordis plugin row in `$DSH_HOME/cordis.patch.yml` (`~/.dsh` by default), which every dsh profile
composes — native tools, no MCP needed. Two dsh-specific notes: one dsh process serves **several
repositories** (its Web UI opens each session in whatever directory you pick), so the bank is
resolved per session workspace rather than once per process; and dsh has no plugin-facing notice
channel, so the seed line goes to the plugin log rather than the UI. Everything model-facing —
recalled memory, the knowledge preamble, the `dumemory_*` tools — is unaffected. If you prefer the
published-package route, `dsh plugin --profile web add @baiducloud/dumemory-coding-agents` works
too: the package ships the profile patch layer, so nothing else needs editing.

Uninstall the same way: `npx @baiducloud/dumemory-coding-agents uninstall claude-code` (or `uninstall all`).

**Devin CLI needs Node 22.5 or newer.** Its hooks pass only a session id — the conversation itself
lives in `~/.local/share/devin/cli/sessions.db` — so reading it depends on Node's built-in
`node:sqlite`. Installing `devin-cli` checks for this first and refuses (with the reason) rather
than wiring hooks that could never retain anything. Every other agent works on any supported Node.

`install` copies what it needs into `~/.dumemory/coding-agents` and points each agent's wiring
there, so nothing depends on where you ran it from. **Updating** is the same command again — it
re-copies the runtime in place, leaving the wiring valid and every new session on the new version.

`install` merges the native wiring (hooks + MCP registration where the host wants them) into each
agent's own config, preserving everything already there; it is idempotent (re-run after moving the
package) and backs up any pre-existing file it touches as `<file>.dumemory-backup`. `uninstall`
removes only our entries. On Claude Code the install also ships a **companion skill**
(`~/.claude/skills/dumemory-coding-agent`) that teaches the agent how this memory works — what
"store this in dumemory" should do, the tool surface, per-repo configuration, debugging — so users
can ask the agent itself. Manual wiring per harness, if you prefer:

**opencode** and **opencode 2** install directly — point `opencode.json` at the package dir:

```json
{ "plugin": ["/path/to/dumemory-coding-agents"] }
```

One entry, both CLIs: v1 resolves that directory through `package.json` `main`, v2 through its
`index.js`, so each loads its own plugin.

**Claude Code** and **Codex** get their full three-hook + MCP wiring from this package's own
installer — `npx @baiducloud/dumemory-coding-agents install claude-code` / `install codex`. This package's `bin`
entries (`dumemory-claude-hook`, `dumemory-codex-hook`,
`dumemory-cursor-hook`) are the individual injection-only `UserPromptSubmit` entrypoints for a
minimal, hand-wired setup.

Adding an agent: hook-based → write a `HookSpec` entry point (see `src/cursor-hook.ts`) and register
a `hookAdapter` in `src/harness/registry.ts`; persistent-plugin → implement `HarnessAdapter`
(`src/core/types.ts`) fully (see `src/harness/opencode.ts`), or bind the host's own plugin API to
`RuntimeCore` directly when it is not an opencode fork (see `src/cline.ts`, `src/dsh.ts`).

## Importing existing conversations

A fresh install starts from git history alone and knows nothing of what you already discussed with
your agent. `--import-conversations` re-extracts the transcripts the agent wrote on this machine, as
new documents:

```bash
cd /path/to/your/repo
npx @baiducloud/dumemory-coding-agents install claude-code --import-conversations   # or: install codex --import-conversations
```

This costs tokens roughly in proportion to the history imported, and it is safe to re-run (ingestion
dedups by document id).

**How sessions are matched.** A conversation is imported only when the session itself records the
directory it ran in — never inferred from a file or folder name. Claude Code writes that directory
on its entries, Codex in its `session_meta` header and DeepSeek Harness in its session-log header,
and pi and Prime Agent in their session header, so all five can be attributed exactly, including
sessions started in a subdirectory of the repo. Guessing was tempting (Claude names its history
folders after the project path) but unsafe: `/` and `.` both encode to `-`, so `repo-sub` is either
the subdirectory `repo/sub` or an unrelated sibling repo — and a wrong guess files someone else's
conversation into your bank. Sessions that record nothing are skipped and the count is reported.
DeepSeek Harness logs are Zstandard-framed JSONL under `$DSH_HOME/sessions`, which needs Node 22.15+
to read; an older Node skips the import with that reason rather than silently importing nothing.
Dcode's transcripts record no directory at all — the working directory lives only in its LangGraph
checkpoint database — so the repo comes from `dcode threads list --json`, a declared, versioned
command contract rather than that internal schema; with the `dcode` CLI unavailable the import is
skipped with that reason. The other harnesses (opencode, opencode 2, Kilo, Cursor, Cline, Copilot, Devin) keep
history in internal SQLite databases with unversioned schemas and are skipped with a reason.

**One bank per repo.** Memory is keyed by repository (`coding-agent::{gitProject}`) and shared by
every agent, so switching agents mid-project keeps the same memory. For per-agent banks instead:

```jsonc
{ "bankIdTemplate": "{harness}::{gitProject}" } // one bank per agent per repo
```

## Where memory lives

Memory is stored in **Baidu AI Cloud**. `install` asks for an API token on a terminal; scripted
installs pass it as a flag:

```bash
npx @baiducloud/dumemory-coding-agents install claude-code --api-token <token>
```

Re-running `install` never re-asks: a config that already names a server is left alone.

To reach **your own deployment** of the same API instead, point `--api-url` at it — everything
downstream of the URL is identical, so a self-hosted server needs no other setting:

```bash
npx @baiducloud/dumemory-coding-agents install claude-code --api-url https://memory.internal:8888 --api-token <token>
```

<!-- skill:begin title="Server settings" -->

| field        | env                    | default                                    | meaning                        |
| ------------ | ---------------------- | ------------------------------------------ | ------------------------------ |
| `serverMode` | `DUMEMORY_SERVER_MODE` | `cloud`                                    | `cloud` — the only mode        |
| `apiUrl`     | `DUMEMORY_API_URL`     | `https://cloud.memory.bj.baidubce.com/api` | base URL of the API to talk to |
| `apiToken`   | `DUMEMORY_API_TOKEN`   | —                                          | bearer token; required         |

<!-- skill:end -->

<!-- skill:begin -->

## Configuration

Configuration is **one JSON file**: `~/.dumemory/coding-agent.json`. Layering, later wins per field:

1. built-in defaults
2. environment variables — `DUMEMORY_API_URL`, `DUMEMORY_API_TOKEN`, and one per scalar setting
   (`DUMEMORY_<FIELD_IN_CAPS>`), for containers and CI that inject config rather than write a file
3. the file's top level
4. its `harnesses.<name>` section — per-agent override
5. its `banks.<resolvedBankId>` section — per-repo override, applied after the bank is resolved
   (see [Per-repo opt-in/out](#per-repo-opt-inout--banksbankid))

Environment variables are a **fallback**: the file wins wherever it sets a value, so adding env to
an existing setup changes nothing. The two list-valued settings, `retainTags` and `optInPaths`, take
a comma-separated value (`DUMEMORY_RETAIN_TAGS="project:{gitProject},env:work"`); entries are
trimmed and blanks dropped.
The map-valued settings (`mapPathToBank`, `harnesses`, `banks`, `retainMetadata`) are file-only —
per-key branching doesn't survive flattening into one variable. `maxParallelRetains` is available
as `DUMEMORY_MAX_PARALLEL_RETAINS` for containers and CI.

`DUMEMORY_CONFIG` moves the file itself — point it at another path for a container or a test
harness where `$HOME` is not the right anchor. It is still exactly one file; only its location
changes. (The other variables that are not settings are `DUMEMORY_LOG_FILE`, `DUMEMORY_DIAG_FILE`
and `DUMEMORY_LOG_LEVEL` — see [Diagnostics & logging](#diagnostics--logging).)

### When a change takes effect

Config is read when a process starts — the file is not watched — so when an edit applies depends on
what reads it:

| host                                                                                                        | reads the file                                                      | an edit applies            |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | -------------------------- |
| hook harnesses (Claude Code, Codex CLI, Cursor CLI, GitHub Copilot CLI, Grok Build, Antigravity CLI, Devin) | once per hook invocation — each hook is its own short-lived process | on your next prompt        |
| persistent plugins (opencode, opencode 2, Kilo CLI, Cline CLI, pi, Prime Agent, DeepSeek Harness)           | once per workspace, when the host loads the plugin                  | after restarting the agent |
| the MCP server behind the `dumemory_*` tools                                                                | once at startup                                                     | in your next session       |

`apiToken` is the exception. Every host re-reads it when the server rejects a request, so enabling
authentication or rotating the key is picked up on the next call with nothing to restart —
otherwise a rotation would leave a long-running agent failing every memory call until it was
restarted. Everything else follows the table: `apiUrl`, `disabled`, bank routing, `gitIngest`, and
the survey and knowledge-page settings.

`dumemory_diagnose` reports both sides of that gap — what the file says now, and what the running
client is actually using.

### Opt-in only

By default every project gets memory — that is what makes the plugin zero-setup. If you would
rather nothing be remembered until you say so, turn memory off everywhere and name the projects
that may use it:

```jsonc
{
  "optInOnly": true,
  "optInPaths": ["~/work/client-x", "~/oss"],
}
```

Anything outside those paths is **inert**: no bank is created, nothing is retained, no seed runs,
and the agent behaves exactly as it would without the plugin. Approving costs nothing else —
`optInPaths` says _which projects_, not _which bank_, so an approved repo keeps its usual
`coding-agent::{gitProject}` name. Paths are prefixes, so approving `~/work` approves every repo
under it while each still gets its own bank.

A `mapPathToBank` entry counts as opted in too, since routing a path to a named bank already
declares that project. A bare `bankId` does not: it names a bank rather than a project, so it
cannot say which work may be remembered, and a privacy switch has to fail closed.

There is no per-repo opt-in file, for the same reason there is no repo-carried config at all: a
cloned repository must not be able to turn memory on.

There is deliberately no repo-carried config file — per-repo bank routing is `mapPathToBank`,
per-agent differences are `harnesses.<name>`.

Each entry point knows which harness it _is_ (the opencode plugin is loaded by opencode, the codex
hook by Codex...), so one shared config serves several agents side by side:

```jsonc
{
  "apiUrl": "https://cloud.memory.bj.baidubce.com/api",
  "harnesses": {
    "opencode": { "reflectTimeoutMs": 60000 },
    "claude-code": { "disabled": true }, // e.g. memory off for Claude only
  },
}
```

### Reference

| field                   | default                                    | meaning                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ----------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apiUrl`                | `https://cloud.memory.bj.baidubce.com/api` | DuMemory API base URL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `apiToken`              | —                                          | bearer token (Baidu AI Cloud). Picked up without restarting the agent: a long-lived host re-reads it after a rejected request, so enabling auth or rotating the key mid-session recovers on the next call                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `bankId`                | —                                          | **explicit static bank**; unset ⇒ per-repo dynamic resolution (below)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `dynamicBankId`         | dynamic iff no `bankId`                    | force dynamic (`true`) or static (`false`) resolution                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `bankIdTemplate`        | `"coding-agent::{gitProject}"`             | dynamic bank id format; the default makes every agent share one bank per repo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `mapPathToBank`         | —                                          | absolute path → bank; **longest prefix wins**; linked worktrees inherit their main checkout's mapping; overrides everything                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `optInOnly`             | `false`                                    | run memory ONLY in opted-in projects — everything else is inert, with no bank created; see [Opt-in only](#opt-in-only)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `optInPaths`            | —                                          | directories opted in, matched as prefixes with `~` expanded; each repo beneath and its linked worktrees are approved while keeping their own dynamic bank                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `resolveWorktrees`      | `true`                                     | linked worktrees inherit the main checkout's bank identity, path approval, and mapping                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `retainTags`            | —                                          | extra tags on every document written by the integration, e.g. `["project:{gitProject}"]` — see **Recording where a memory came from** below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `retainMetadata`        | —                                          | extra metadata on every document written by the integration, e.g. `{"repo": "{gitProject}"}`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `manageBankConfig`      | `true`                                     | let the plugin shape the bank's own configuration — the retain strategies it writes under, the `knowledge` entity-label group, and, on a bank that has none, the missions. Writing is strictly **additive**: it adds what the bank does not define and never overwrites what is there, so your control-plane edits survive. Set `false` to keep it out of the bank config entirely — see **A bank you shape yourself** below                                                                                                                                                                                                                                                                                                                                                                  |
| `observationScopes`     | `"shared"`                                 | how consolidation groups observations: `"shared"` (default) = ONE global scope per bank, so every agent on a repo builds one set of beliefs; also `"combined"` (the server default), `"per_tag"`, `"all_combinations"`, `[["t"]]`; `"per_source"` adds a scope per `source:` kind alongside the global one, so commit knowledge and conversation knowledge consolidate apart                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `disabled`              | `false`                                    | hard off-switch (inert plugin/hook — a no-memory baseline)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `reflectTimeoutMs`      | `28000`                                    | **automatic** session-reflect timeout, honoured verbatim by every agent — there is no per-agent cap. The default fits inside the 30s prompt-hook timeout this package installs, with headroom for the rest of the hook's work; raising it on a hook-based agent can therefore let the host kill the hook mid-reflect, while a persistent-plugin agent has no such window. On timeout the session runs without reflect (recorded)                                                                                                                                                                                                                                                                                                                                                              |
| `reflectToolTimeoutMs`  | `330000`                                   | timeout for the agent-invoked `dumemory_reflect` tool — a call the agent waits on, whose high-budget synthesis on a populated bank runs for minutes. Defaults above the server's own reflect wall timeout (`DUMEMORY_API_REFLECT_WALL_TIMEOUT`, 300s) so the server decides when to give up. Unset, it inherits an explicitly raised `reflectTimeoutMs`, but a short one never lowers it                                                                                                                                                                                                                                                                                                                                                                                                      |
| `reflectBudget`         | `"high"`                                   | reflect budget for the `dumemory_reflect` tool: `"low"`, `"mid"` or `"high"`. Drop it on a large bank where high-budget synthesis exceeds the server's wall timeout. The automatic session-start reflect always uses `"low"` to fit its hook window and is unaffected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `autoReflect`           | `true`                                     | inject a one-time reflect synthesis on the session's **first prompt**. `false` = tool-only reflect: nothing is injected; the agent searches knowledge pages first and reflects only when they are too shallow                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `pageRefreshEveryTurns` | `10`                                       | refetch the knowledge pages and re-inject the page roster + tool guide every N user turns                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `pageTriggerType`       | `"auto-refresh"`                           | when NEW knowledge pages refresh, i.e. what keeping them current costs — `"auto-refresh"` after every consolidation that produced new material, `"cron"` on `pageTriggerCron` only, `"manual"` never on their own. Auto-refresh is the most current and the most expensive: one synthesis per page per consolidation. Maps to the page's `trigger.refresh_after_consolidation` in the DuMemory API (`true` for auto-refresh, `false` for manual)                                                                                                                                                                                                                                                                                                                                              |
| `pageTriggerCron`       | —                                          | schedule for `pageTriggerType: "cron"` — UTC, standard 5-field cron, e.g. `"0 3 * * *"`. Sets the page's `trigger.refresh_cron`, which the API treats as mutually exclusive with `refresh_after_consolidation`; a scheduled refresh is skipped when nothing changed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `autoSeed`              | `true`                                     | SessionStart: auto-seed a cold repo's bank from git history                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `seedLimit`             | `300`                                      | auto-seed: most-recent-N-commits cap                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `codebaseSurvey`        | `true`                                     | SessionStart: headless survey of a cold repo's structure, run under the current harness's own CLI (claude/codex/antigravity/opencode), falling back to any available agent                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `surveyModel`           | `haiku`                                    | model for the survey — Claude recipe only (`claude -p --model`); other agents use their configured default                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `surveyBudgetUsd`       | `2`                                        | survey spend cap — Claude recipe only (`claude -p --max-budget-usd`); other agents rely on their read-only sandbox                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `surveyRefreshCommits`  | `20`                                       | re-run the survey at SessionStart once this many commits have accrued since the last one, so the structural pages track an architecture that keeps moving (`0` = survey a cold repo only, never again)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `retainSessions`        | `true`                                     | session write-back, honored by every harness: hook harnesses write the transcript on Stop, plugin harnesses (opencode, opencode 2, Kilo) upsert it every turn plus an idle flush that captures the reply the per-turn pass can't see. Set `false` — globally, per harness, or per bank — to stop writing transcripts (the background history import stops with it) while recall, git ingest and the memory tools keep working                                                                                                                                                                                                                                                                                                                                                                 |
| `maxParallelRetains`    | `10`                                       | cap on concurrent retain-related requests: drain()'s per-op polls plus deepen's chat/git retain pools. The API rate-limits bursts, not single requests — if you see 429s, lower this rather than raising it                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `logLevel`              | `"info"`                                   | plugin-log verbosity (`"debug"` \| `"info"` \| `"warn"` \| `"error"`); `DUMEMORY_LOG_LEVEL` env overrides                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `autoUpdate`            | `true`                                     | keep the installed runtime current by itself: once a day a session start asks the registry npm is configured to use (via `npm view`, so a mirror or a private registry is honoured) for the published version and, when it is newer, re-stages `~/.dumemory/coding-agents` in the background. It rewires no host config, so a release adding a **new** hook entry point still needs a manual `install`. Set `false` to pin the installed version; `disabled` stops it too, since an inert plugin should stay inert. Only ever replaces a runtime installed the documented way, via `npx` — a copy installed with `npm i -g`, vendored as a project dependency, or built from a checkout is left to whoever manages it (update those the way you installed them), and it needs `npx` on `PATH` |
| `gitIngest`             | `"message"`                                | git depth for seeding AND staying current (same engine): `"message"` = commit messages only (one doc, re-upserted when HEAD moves); `"full"` = messages + per-commit full diffs (progressive, newest first); `"none"` = git off                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `harnesses.<name>`      | —                                          | per-harness override of any field above                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `harness`               | `opencode`                                 | **deepen engine only**: which session format `--conversations` is read as                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

`pageTriggerType`/`pageTriggerCron` decide only **when** a page refreshes. **How** it refreshes
belongs to the server: DuMemory creates a knowledge page with a delta refresh (each pass edits the
page instead of rebuilding it) that doesn't reflect over sibling pages, and these settings merge
over those defaults rather than replacing them.

**These settings apply to pages created from here on.** Changing them does not migrate the pages a
repo already has: a page keeps the trigger it was created with, so a bank seeded before you set
`"manual"` keeps refreshing on every consolidation. To move an existing page, change its trigger
through the API (`PATCH /knowledge-base/nodes/{id}`), an SDK, or the control plane — or delete it
and let the next session seed it again.

### A bank you shape yourself — `manageBankConfig`

Pointed at a bank, this plugin gives it the shape its ingestion needs: retain strategies for the
kinds of document it writes (`git`, `gitlog`, `conversation`, `document`, `survey`), a `knowledge`
entity-label group that routes facts to the knowledge pages, and — on a bank that has no missions of
its own — the coding missions.

**It only ever adds what is missing.** A strategy you defined, an edit you made to one of the
plugin's, a reworded label group, a mission you rewrote in the control plane: each is left exactly
as it is, on every session, forever. What the bank already says wins. The cost of that promise is
that a plugin release which _rewords_ an existing strategy or label does not reach a bank that
already has it. To take the current default back, clear that override on the bank (delete the
strategy, or the whole `retain_strategies` entry, in the control plane): the next session finds the
bank silent there and seeds it again.

Set `manageBankConfig: false` to keep the plugin out of the bank's configuration altogether — the
right setting for a bank you share with non-coding work, or one you configure yourself. That bank
should then define the five strategies above itself. Note that the miss is **silent**: the server
does not reject a retain naming a strategy the bank lacks, it logs a warning and extracts with the
bank's own configuration — so a commit diff, a session transcript and a survey marker would all get
the same generic treatment instead of the extraction each needs. Knowledge pages are seeded either
way; `pageTriggerType` governs what they cost.

Like every field here it can be set per bank, which is usually where it belongs:

```json
{
  "bankId": "my-global-bank",
  "banks": { "my-global-bank": { "manageBankConfig": false } }
}
```

### Per-repo opt-in/out — `banks.<bankId>`

Per-repo control lives in the SAME file, keyed by the **resolved bank id** (shown in the session
banner) and applied AFTER bank resolution — so it works regardless of where the repo lives, and
survives directory moves:

```jsonc
{
  "banks": {
    "coding-agent::secret-client": { "disabled": true }, // blacklist: no memory at all
    "coding-agent::old-name": { "bank": "team::shared" }, // rename / converge banks
    "coding-agent::big-mono": { "gitIngest": "full", "retainSessions": false },
  },
}
```

Any behavioral field can be overridden per bank, and `bank` **renames the destination** (single
hop: the section is selected by the resolved id, the target is literal — several ids may converge
on one shared bank, and the target's own section is not consulted). Other bank-resolution fields
are ignored inside a bank section.

#### Recipe: two repos, one shared bank

Two ways, by what the natural key is:

**By resolved id** — you know the repo names; works wherever the repos live (and keeps working if
they move). Both ids converge on one literal target:

```jsonc
{
  "banks": {
    "coding-agent::backend": { "bank": "team::product" },
    "coding-agent::frontend": { "bank": "team::product" },
  },
}
```

**By path prefix** — the repos live under one directory; a single `mapPathToBank` entry covers
every repo (present and future) beneath it:

```jsonc
{
  "mapPathToBank": { "/Users/me/work/client-x": "client-x-memory" },
}
```

Rule of thumb: converge by **id** for a hand-picked set of repos; map by **path** when a folder is
the boundary ("everything I clone under `work/client-x` shares memory").

### Bank resolution

Coding memory is **per repository**. Resolution order for the working directory:

1. `mapPathToBank` — longest matching absolute-path prefix (mapping a repo root covers every
   subdirectory; deeper mappings win; overrides even an explicit `bankId`).
2. Static — `bankId` set (or `dynamicBankId: false`).
3. Dynamic — `bankIdTemplate` with placeholders:
   - `{gitProject}` — worktree-aware repo name: `git rev-parse --git-common-dir` resolves every
     linked worktree to the **main** worktree's basename, so all worktrees of a repo share one bank
     (bare repos use the bare dir name). **Outside a repo** there is nothing for git to resolve, so
     it falls back to the basename of the directory the **session started in** — an agent that
     `cd`s into a subdirectory keeps writing to one bank, and a subdirectory gets its own bank only
     when you deliberately start a session there
   - `{project}` — plain working-directory basename
   - `{harness}` — the entry point asking (`opencode`, `claude-code`, `codex`, `antigravity-cli`, `cursor-cli`, `copilot-cli`)
   - `{channel}` / `{user}` — `$DUMEMORY_CHANNEL_ID` / `$DUMEMORY_USER_ID`

The default `"coding-agent::{gitProject}"` is **harness-neutral**, so opencode, Claude Code, and Codex
all share one memory per repo — use `"{harness}-{gitProject}"` to split per agent instead.

### Recording where a memory came from

With a bank per repo, the bank _is_ the answer to "where did this come from". On a deliberately
**shared** bank — one bank holding cross-project knowledge so facts recall everywhere — it isn't:
every memory looks alike. `retainTags` and `retainMetadata` stamp that provenance onto conversations,
git history and diffs, survey lifecycle documents, initiative markers, and documents saved through
`dumemory_ingest_document`:

```jsonc
{
  "bankId": "shared", // one bank for everything
  "retainTags": ["project:{gitProject}", "env:work"],
  "retainMetadata": { "repo": "{gitProject}" },
}
```

Recalls can then filter by `project:<repo>`, and every document shows which repository it came out
of. Both accept the same placeholders as `bankIdTemplate` — `{gitProject}`, `{project}`,
`{harness}`, `{channel}`, `{user}` — plus `{bankId}`, `{sessionId}` and `{timestamp}`.
`{gitProject}` is worktree-aware here too, so every linked worktree of a repo stamps one name.
`{sessionId}` resolves to `unknown` for documents that do not originate from an agent session.

The plugin's own `source:` and `harness:` tags are reserved: entries in those namespaces are ignored
with a warning, so a document's agent attribution always reflects the agent that actually wrote it.

### One set of beliefs per repo

Every document this integration writes carries provenance tags — `source:chat`, `harness:<id>`,
`knowledge:<kind>`, plus anything from `retainTags`. Those tags say **who wrote** a memory; they are
what filters recall and draws each document's agent logo, and they stay on the facts.

They are not, however, a good boundary for observations. Consolidation's own default (`combined`)
builds one observation set per distinct tag set, so the same repository worked on by two agents
would grow two parallel sets of beliefs — one per harness — that never merge, each blind to the
other, at double the consolidation cost. Which agent happened to be typing does not change whether
a convention or a decision is true.

So the integration retains with `observationScopes: "shared"`: one global, untagged observation
scope per bank, which is what a bank already is — one project's memory. Set the field to change it:

```jsonc
{
  "observationScopes": "combined", // one observation set per distinct tag set (server default)
  "banks": {
    "coding-agent::mono": { "observationScopes": "per_tag" }, // per-repo, like any behavioral field
  },
}
```

### Splitting code from conversation — `per_source`

`shared` puts every document a repo produces into one belief set. `"per_source"` keeps that set and
adds one per origin, so "what the commits say" and "what was decided in conversation" can be asked
apart:

```jsonc
{ "observationScopes": "per_source" }
```

Each document consolidates into the global scope **plus** one named for each `source:` tag it
carries — `[[], ["source:chat"]]` for a session transcript, `[[], ["source:git"]]` for a commit
diff. Read an axis back with `tags: ["source:git"], tags_match: "exact"`, and the merged view with
`tags: [], tags_match: "exact"`.

A document carrying two `source:` tags gets a scope for each, and that is deliberate rather than
duplication. The commit-message seed is tagged `source:git` and `source:git-log`, so
`source:git-log` is fed only by the seed — what the commit _messages_ say — while `source:git` also
collects every per-commit diff under `gitIngest: "full"`. Two questions, two answers, each
deduplicated within itself by consolidation. A fact belonging to more than one axis is the point.

This cannot be expressed as a scope list. The server treats an explicit `list[list[str]]` as
unconditional — it is not filtered against the memory's own tags — so a configured
`[[], ["source:git"], ["source:chat"]]` writes every document into all three, and the `source:git`
scope fills with beliefs built from chat transcripts. Only a per-document decision separates them.

It costs one extra consolidation pass per document, and it reads only `source:`, so a volatile
provenance tag never becomes a scope. The global scope is still written first and unchanged, so the
untagged observations knowledge pages read are unaffected.

`"per_tag"` and `"all_combinations"` split further still, and an explicit `[["project:demo"], …]`
declares the scopes literally. `DUMEMORY_OBSERVATION_SCOPES` sets the scalar modes; a scope list is
file-only. Changing this does not rewrite observations already consolidated under the old scoping —
they stay where they were built, and new work accrues under the new setting.

<!-- skill:end -->

## Ingestion internals (no CLI)

There is no user-facing ingest command — the deepen engine (`dist/deepen.js`) is spawned by every
session start and does only the missing work: bank configuration, conversation import (dedup by
document id), the one-time gitlog seed, the next per-commit diff batch (newest first, bounded per
run), then knowledge pages once extraction has drained. Harnesses that need deterministic ingestion
(benchmarks, e2e suites) run the same engine directly and poll `dist/status.js` until
`"synced": true` — the exact readiness contract the `dumemory_sync_status` agent tool reports.

Past-conversation import accepts a normalized interchange file (engine `--conversations` flag):
`[{ "id": "s1", "turns": [{ "role": "user", "text": "...", "timestamp?": "ISO" }, ...] }, ...]`,
chronological (a later chat can amend an earlier one). Day-to-day, conversations simply accrue from
the live session write-back — no export step.

## Companion skill (generated)

Every skills-capable host gets `skill/SKILL.md`, which teaches the agent what this integration does
and how to configure it. **It is generated — do not edit it.** This file is the single source: the
regions between `<!-- skill:begin -->` and `<!-- skill:end -->` are copied into the skill (a region
that starts mid-section names itself with `title="…"`, and heading levels are normalised so a marked
`###` becomes the skill's `##`). Only the agent-facing half — which tools to call, crediting memory,
correcting a wrong memory — lives outside it, in `skill-src/preamble.md`.

```bash
npm run skill:build   # after editing this README or the preamble
```

`src/docs-freshness.test.ts` fails when the skill is stale, and when a field of `RawConfig` is
readable from a config file but named nowhere in this README — the drift that produced #3735, where
the skill and the README each documented a different subset of the same settings.

<!-- skill:begin -->

## Diagnostics & logging

Two files, two audiences:

**Leveled plugin log** (humans debugging): `$TMPDIR/dumemory-coding-agent/plugin.log` (override
`DUMEMORY_LOG_FILE`) — timestamped `LEVEL [scope] message` lines from every component, including
the ingestion engine. Level defaults to `info`; set `"logLevel": "debug"` in config or
`DUMEMORY_LOG_LEVEL=debug` for ad-hoc debugging (at `debug`, every diag event below is mirrored
here too, so one file tells the whole story).

**Structured diag events** (machines/harnesses): every reflect and page-fetch outcome is appended
as a JSON line to `/tmp/dumemory-plugin.log` (override with `DUMEMORY_DIAG_FILE`):

```json
{
  "ts": "2026-07-27T07:05:52Z",
  "harness": "claude-code",
  "event": "reflect_ok",
  "ms": 14210,
  "chars": 792,
  "query": "..."
}
```

`reflect_failed` / `pages_failed` record the error; if you're comparing memory-on vs memory-off,
check this file — a run whose reflects failed is a no-memory run. Seed starts are logged as
`seed_started`.

### Is the memory ready yet?

`dumemory_sync_status` — the agent-facing tool, `dist/status.js` for scripts — answers exactly
that: `"synced": true` means the seeded memory is queryable. It also reports gitlog freshness, how
far per-commit deepening has got, the codebase survey's state (`surveyBaseline` is the HEAD the last
survey started from, `surveyDocs` counts the findings documents that have landed, 0–4 — a baseline
with no findings retries automatically), and the extraction operations still in flight.

### Resetting a repo's memory

Delete its bank on the server. The bank is the **only** state this integration keeps, so the next
session in that repo is a true first open — seed and survey run again from scratch. There are no
client-side files to clean up.

### Marker documents you may notice

Two document ids exist for the machinery's own bookkeeping. Both are safe to ignore and safe to
delete:

- `survey-baseline:<sha>` — reads "🛰️ researching…" while a codebase survey runs and flips to
  "✅ completed" once its findings land. It is retained under the `survey` strategy, whose marker
  rule extracts **nothing** from a status marker, and it drives the re-survey cadence
  (`surveyRefreshCommits`) and `surveyBaseline` in sync status.
- `gitlog:<repo>` — the aggregated commit-message seed document, re-upserted rather than duplicated
  when the seed runs again.

### When memory seems to be missing

Failures never break the agent: a reflect, page fetch or retain that fails degrades to an ordinary
memoryless turn and is recorded in the logs. "No memory" is therefore a log question — check the
diag file for whether `session_start` and `deepen_started` ever fired for that bank. A session that
was already running when the plugin was installed has no SessionStart behind it; its first prompt
after the install self-heals.

<!-- skill:end -->
