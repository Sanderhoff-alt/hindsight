/**
 * Keep the STAGED runtime current on its own.
 *
 * `install` copies this package into ~/.hindsight/coding-agents and points every wired agent's
 * hooks at that copy (installer.ts `stageRuntime`). Nothing ever refreshed it: the only update
 * path was the user remembering to re-run `install`, so a machine could sit several versions
 * behind indefinitely — bugs stayed fixed only for people who happened to re-install.
 *
 * Once per `CHECK_INTERVAL_MS`, at session start, this asks npm for the published version and —
 * when it is newer than the staged one — spawns a DETACHED
 * `npx @vectorize-io/hindsight-coding-agents@<version> update`, which re-stages the runtime and
 * touches no host config (see the `update` branch in installer.ts). Fire-and-forget: the current
 * session keeps running the version it already loaded and the next one starts on the new code.
 *
 * Deliberately narrow:
 *   - it runs ONLY from the staged copy. A checkout or an `npx` run is somebody's development or
 *     one-off invocation, and overwriting it with a published build would destroy their work.
 *   - it replaces ONLY a runtime it can prove npx downloaded (`installOrigin` below). A copy staged
 *     from `npm i -g`, from a project dependency, or from a local checkout belongs to whoever
 *     manages that source: updating it behind their back would leave `npm ls -g` reporting a
 *     version that is no longer what runs, or would silently overwrite a developer's built dist.
 *   - it needs `npx` and `npm` on PATH — npx is how the updater is fetched, npm is how the
 *     version is looked up. Without them there is nothing to spawn or ask, so it says so once a
 *     day rather than failing a spawn each time.
 *   - it stages only. Rewiring hosts unattended would mean choosing which agents to install for,
 *     and that is the user's call (`install` spells it out for exactly this reason).
 *   - `autoUpdate: false` in ~/.hindsight/coding-agent.json (or HINDSIGHT_AUTO_UPDATE=false) turns
 *     it off entirely, for pinned or air-gapped setups.
 *
 * Known window: `stageRuntime` replaces dist/ wholesale, so a hook that happens to spawn during
 * that copy can fail to load its entry point. Already-running processes are unaffected (node has
 * read the bundle by then), the window is milliseconds once a day, and the cost of losing it is
 * one turn without memory — the same outcome as any other hook failure. Serialising against every
 * possible concurrent hook spawn would need a lock every hook takes on every turn, which is a
 * worse trade than the window it closes.
 */
import { spawn as realSpawn } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { homedir, tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { Config } from "./config";
import { describeError, log } from "./log";
import { binOnPath } from "./util";

export const PACKAGE_NAME = "@vectorize-io/hindsight-coding-agents";

/** What `npm view` may hand back before the value is allowed anywhere near a spawn: strictly
 *  digits.digits.digits with an optional pre-release suffix. See npmViewVersion for why this is
 *  a whitelist rather than "whatever isNewer can chew". */
const RELEASE_RE = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?$/;

/** How often the registry is asked. One session a day pays ~1.2s (the npm CLI startup behind
 *  `npm view`, not the request — cold and warm cache measure the same); the rest read a
 *  timestamp off disk and move on. */
export const CHECK_INTERVAL_MS = 24 * 60 * 60 * 1000;

/** Version-check budget. A slow or unreachable registry must not delay a session start, and this
 *  runs before the user has typed anything. Bounds the spawned `npm view` — npm CLI startup plus
 *  the request, measured at ~1.2s where a bare registry fetch takes ~0.9s. */
const NPM_VIEW_TIMEOUT_MS = 5000;

/** Hard wall on the whole lookup, past the spawn timeout. The spawn timeout SIGTERMs npm itself,
 *  but `close` — unlike `exit` — waits for the stdio pipes to drain, and a grandchild that
 *  inherited this pipe would stall the promise past the kill with nobody left to reap it. npm
 *  view spawns no children today; this deadline is what keeps that true from mattering: it
 *  force-settles the lookup as failed and SIGKILLs the direct child, so the update lock is
 *  released on the spot instead of being held to LOCK_STALE_MS. */
const NPM_VIEW_HARD_DEADLINE_MS = NPM_VIEW_TIMEOUT_MS + 1000;

/** Where the last check's timestamp lives — inside the staged runtime, so it is removed with it. */
export function stateFile(runtimeDir: string): string {
  return join(runtimeDir, ".update-check.json");
}

/** The directory this module is running out of (the package root, one level above dist/). */
function packageRoot(): string {
  return join(dirname(fileURLToPath(import.meta.url)), "..");
}

/** Where `install` stages the runtime — the one copy this may replace. Kept as a literal rather
 *  than imported from installer.ts, which would pull the whole installer into every hook bundle. */
function stagedRuntimeDir(): string {
  return join(homedir(), ".hindsight", "coding-agents");
}

/** Same directory, compared through realpath — a symlinked or differently-spelled HOME must not
 *  read as "not the staged copy" and silently disable updates. */
function sameDir(a: string, b: string): boolean {
  try {
    return realpathSync(a) === realpathSync(b);
  } catch {
    return a === b;
  }
}

/** Version of the package this code belongs to, or "" when it cannot be read. */
export function stagedVersion(pkgRoot: string): string {
  try {
    const pkg = JSON.parse(readFileSync(join(pkgRoot, "package.json"), "utf8")) as {
      version?: string;
    };
    return typeof pkg.version === "string" ? pkg.version : "";
  } catch {
    return "";
  }
}

/**
 * Is `candidate` a later release than `current`?
 *
 * A deliberately small comparison rather than a semver dependency: this package ships
 * zero-dependency (the installer must run from a bare `npx`), and the only question asked here is
 * "did the release number go up". NOT `util.ts`'s `semverGte`, which answers a different question
 * for capability probes: it is true on equality and strips pre-release suffixes, so it would both
 * re-update a machine that is already current and drag a release onto its own release candidate. A PRERELEASE suffix loses to the same numbers without one, which
 * is what keeps a machine on `1.2.0` from being pulled onto `1.2.0-rc.1`; two prereleases of the
 * same version compare as equal, so neither drags the other around.
 */
export function isNewer(candidate: string, current: string): boolean {
  const parse = (v: string): { nums: number[]; pre: boolean } => {
    const [core = "", ...rest] = v.trim().split("-");
    return {
      nums: core.split(".").map((n) => Number.parseInt(n, 10)),
      pre: rest.length > 0,
    };
  };
  const a = parse(candidate);
  const b = parse(current);
  if (a.nums.length !== 3 || b.nums.length !== 3) return false;
  if (a.nums.some(Number.isNaN) || b.nums.some(Number.isNaN)) return false;
  for (let i = 0; i < 3; i++) {
    if (a.nums[i] !== b.nums[i]) return a.nums[i] > b.nums[i];
  }
  // Same numbers: only a release can supersede a prerelease of itself.
  return b.pre && !a.pre;
}

/** Whether enough time has passed since the last check. An unreadable/absent state file reads as
 *  "never checked", so a first run always checks and a corrupted one self-heals. */
function dueForCheck(file: string, now: number): boolean {
  try {
    const state = JSON.parse(readFileSync(file, "utf8")) as { lastCheck?: number };
    return typeof state.lastCheck !== "number" || now - state.lastCheck >= CHECK_INTERVAL_MS;
  } catch {
    return true;
  }
}

/** Written by installer.ts `stageRuntime`, naming the directory this runtime was copied from. */
const ORIGIN_FILE = ".install-origin.json";

/**
 * May this runtime be replaced automatically?
 *
 * Only when it was staged from an npx download — the documented install path, where no other tool
 * is tracking the version. `npm i -g` and a project dependency are managed by npm (an unattended
 * re-stage would leave `npm ls -g` naming a version that is no longer what runs, with no way for
 * the user to reconcile the two), and a checkout is a developer's build, which a published release
 * would silently overwrite.
 *
 * Missing marker = no. It is written on every `install`/`update` from the version that introduced
 * auto-update onward, and a machine has to re-install once to get this code at all — so a runtime
 * old enough to lack the marker is also too old to be running this check. Failing closed here
 * costs one manual install; failing open costs somebody their working tree.
 */
export function selfUpdatable(runtimeDir: string): boolean {
  try {
    const origin = JSON.parse(readFileSync(join(runtimeDir, ORIGIN_FILE), "utf8")) as {
      source?: string;
    };
    if (typeof origin.source !== "string" || !origin.source) return false;
    // npx unpacks into a `_npx/<hash>/node_modules/...` cache directory; nothing else does.
    return origin.source.split(/[\\/]/).includes("_npx");
  } catch {
    return false; // absent or unreadable — see above, this fails closed on purpose
  }
}

/**
 * Serialise updaters across concurrent sessions.
 *
 * The 24h stamp is not enough on its own: several agents starting within the same second all read
 * "due" before any of them has written it, so they all spawn an updater. Two `update` runs racing
 * means two `stageRuntime` calls, and staging is `rmSync(dist)` then `cpSync` — one process can
 * delete the directory the other is half way through writing, leaving a runtime with missing entry
 * points and every hook broken until a manual re-install. That burst is not hypothetical: this is
 * a plugin for machines that routinely run five agents at once.
 *
 * Same shape as deepen.ts's per-bank lock, and for the same reason — a TTL alone would wedge the
 * updater for its whole window after a crash, so the holder's pid decides liveness. The pid stored
 * is the detached CHILD's, because the copy happens in the child and outlives this process.
 *
 * In the OS temp dir, deliberately: it is scratch, and a reboot clearing it can only cost one
 * redundant check.
 */
const LOCK_STALE_MS = 10 * 60 * 1000;

function lockFile(): string {
  return join(tmpdir(), "hindsight-coding-agent", "auto-update.lock");
}

function acquireUpdateLock(file: string, now: number): boolean {
  try {
    const held = JSON.parse(readFileSync(file, "utf8")) as { pid?: number; ts?: number };
    if (held.ts && now - held.ts < LOCK_STALE_MS) {
      let holderAlive = false;
      if (held.pid) {
        try {
          process.kill(held.pid, 0);
          holderAlive = true;
        } catch {
          /* ESRCH: the holder died — the lock is stale NOW, not in LOCK_STALE_MS */
        }
      }
      if (holderAlive) return false;
    }
  } catch {
    /* no/unreadable lock — free */
  }
  try {
    mkdirSync(dirname(file), { recursive: true });
    writeFileSync(file, JSON.stringify({ pid: process.pid, ts: now }));
    return true;
  } catch {
    // Cannot claim the lock, so we cannot prove we are the only updater. Skip rather than race.
    return false;
  }
}

/** Hand the lock to the detached child, whose staging is what actually needs guarding. */
function holdLockFor(file: string, pid: number | undefined, now: number): void {
  try {
    if (pid === undefined) return releaseUpdateLock(file);
    writeFileSync(file, JSON.stringify({ pid, ts: now }));
  } catch {
    /* best-effort */
  }
}

function releaseUpdateLock(file: string): void {
  try {
    unlinkSync(file);
  } catch {
    /* already gone */
  }
}

/**
 * Stamp the check BEFORE acting on its result.
 *
 * The spawned update can fail — offline, a registry hiccup, a read-only home — and re-checking on
 * every session start until it succeeds would turn one broken machine into a request per session.
 * Recording the attempt bounds the retry to once per interval whatever the outcome.
 */
function stampCheck(file: string, now: number, latest: string): void {
  try {
    writeFileSync(file, JSON.stringify({ lastCheck: now, latest }));
  } catch {
    /* best-effort: an unwritable state file means we re-check next session, nothing worse */
  }
}

/** Ask npm for the published version, or "" if it cannot be determined.
 *
 * `npm view <pkg> version --json`, deliberately NOT a bare fetch of
 * `https://registry.npmjs.org/<pkg>/latest`: the update this triggers is `npx <pkg>@<version>`,
 * and npx resolves through the user's npm config — registry mirror, proxy, private registry
 * auth in .npmrc. A hardcoded registry.npmjs.org fetch desynchronises the two: on a mirrored
 * machine the check times out while npx works fine (auto-update silently never fires), and
 * where the two registries are reachable but differ, the check can pin `@<version>` to
 * something the configured registry cannot resolve yet. Going through npm itself makes the
 * check and the install read the same registry by construction. Costs a real npm invocation
 * (once per CHECK_INTERVAL_MS, inside NPM_VIEW_TIMEOUT_MS) — measured ~0.3s over a bare fetch.
 *
 * Deliberately run in the caller's cwd rather than a pinned homedir: `npm view` reads the
 * project-level .npmrc and package.json sitting in it, exactly as the `npx` update spawn does
 * (it inherits the same cwd), so the check and the install stay consistent. The cost is cwd
 * sensitivity — a broken project package.json or a project .npmrc pointing at an unreachable
 * private registry makes this fail — but that is the same verdict npx would reach, which is the
 * point. Do not "fix" this by chdir-ing; it would reintroduce the two-source desync.
 *
 * History: the bare-fetch era also carried a 406 bug — the abbreviated-packument accept header
 * is only served on the packument (`/<pkg>`), not `/<pkg>/latest` — whose "" was read as "no
 * newer version". The lesson transfers: any failure here must read as "no newer version", never
 * as "unknown, try harder next session".
 *
 * Every failure path also logs its reason at info, from HERE rather than from the caller: only
 * the leaf has the "why" (exit code, signal, the stdout that did not parse), the caller only
 * sees "", and the state file's `latest: ""` is indistinguishable from "already current" —
 * without the line, "auto-update never works on my machine" is unfalsifiable. This restores the
 * symmetry every other did-nothing exit already has (managed outside npx, not on PATH, update
 * spawn failed). Exactly one line per lookup, by structure: the reason rides done(), so the
 * settled guard covers the log as well — Node reports a spawn failure as error FOLLOWED BY
 * close, and the trailing event must not add a second, wronger line. Bounded cost: after the
 * 24h gate and the lock, at most one line per machine per day. Level is info, not warn:
 * offline is a normal state, not something to act on.
 */
export async function npmViewVersion(
  pkg: string,
  spawnImpl: typeof realSpawn = realSpawn
): Promise<string> {
  return new Promise((resolve) => {
    let out = "";
    let settled = false;
    let deadline: ReturnType<typeof setTimeout> | undefined;
    const done = (v: string, reason?: string) => {
      if (settled) return;
      settled = true;
      if (deadline) clearTimeout(deadline);
      if (reason) log.info("auto-update", `version check failed: ${reason}`);
      resolve(v);
    };
    try {
      const child = spawnImpl("npm", ["view", pkg, "version", "--json"], {
        timeout: NPM_VIEW_TIMEOUT_MS,
        stdio: ["ignore", "pipe", "ignore"],
        windowsHide: true,
      });
      child.stdout?.setEncoding("utf8");
      child.stdout?.on("data", (d: string) => {
        out += d;
      });
      // A pipe socket's 'error' with no listener is an uncaught exception — an async event
      // the try/catch around the spawn cannot see. This runs in a session-start hook process,
      // where "an update check must never break a session" is the module's first invariant.
      child.stdout?.on("error", (e) => done("", describeError(e)));
      // ENOENT (no npm — or Windows, where the binary is npm.cmd and spawn without a shell
      // cannot see it), EACCES. Node follows this with close(-2); done's guard keeps that
      // trailing event from logging "exited -2" about a process that never ran.
      child.on("error", (e) => done("", describeError(e)));
      // close, not exit: the stdout data must have finished arriving before the parse. The
      // grandchild-pipe stall this can wait on is what NPM_VIEW_HARD_DEADLINE_MS covers.
      child.on("close", (code, signal) => {
        // `timeout`'s kill arrives as close(null, "SIGTERM"), so the signal is part of the story.
        if (code !== 0) return done("", `npm view exited ${code ?? signal}`);
        try {
          const v = JSON.parse(out.trim()) as unknown;
          // --json on a single field is a quoted string; anything else (an array when npm
          // matches multiple, an object on an old npm) is not a version we can pin. The raw
          // stdout riding the failure line is the only clue separating "npm's --json output
          // changed" from a network failure.
          if (typeof v !== "string")
            return done("", `unparsable npm output: ${out.trim().slice(0, 80)}`);
          // A whitelist, not "looks parseable". Today the value lands in one argv entry, where
          // it is inert — but it is destined for a command line the moment a Windows shell
          // wrapper lands (npm.cmd, deliberately deferred to its own issue), and isNewer does
          // NOT stop hostile strings: parseInt("3 && calc") is 3, so isNewer("1.2.3 && calc",
          // "1.0.0") is true. A tainted mirror, a hijacked private registry or one MITM is
          // enough to deliver the payload, so nothing crosses to the spawn without matching.
          if (!RELEASE_RE.test(v)) return done("", `not a release: ${v.slice(0, 40)}`);
          done(v);
        } catch {
          done("", `unparsable npm output: ${out.trim().slice(0, 80)}`);
        }
      });
      // The backstop timer only ever fires when nothing above could: the process and its pipe
      // are gone past the kill. SIGKILL may race an already-dead child (ESRCH) — ignore it.
      // Deliberately NOT unref'd: in the stall this exists for, this timer is what keeps the
      // hook process alive long enough to settle the promise and release the update lock; the
      // normal path clears it inside done() within ~1.2s. Don't "optimize" it away.
      deadline = setTimeout(() => {
        try {
          child.kill("SIGKILL");
        } catch {
          /* already dead */
        }
        done("", "npm view never exited — hard deadline");
      }, NPM_VIEW_HARD_DEADLINE_MS);
    } catch (e) {
      done("", describeError(e));
    }
  });
}

export interface AutoUpdateOptions {
  /** Package root to treat as "where this code runs from" (tests). */
  pkgRoot?: string;
  /** The staged runtime directory this may update (tests); defaults to ~/.hindsight/coding-agents. */
  runtimeDir?: string;
  /** Cross-process updater lock (tests); defaults to one in the OS temp dir. */
  lockFile?: string;
  /** Seams for the two ownership guards (tests). */
  selfUpdatable?: (runtimeDir: string) => boolean;
  binOnPath?: (bin: string) => boolean;
  spawn?: typeof realSpawn;
  /** Version lookup seam (tests); defaults to the real `npm view`. */
  npmView?: (pkg: string) => Promise<string>;
  now?: number;
}

/**
 * Check for a newer release and, if there is one, spawn the detached updater. Awaitable so tests
 * (and callers that want to) can observe it; production call sites fire and forget. Never throws.
 *
 * Returns the version an update was started for, or "" when nothing was done.
 */
export async function maybeAutoUpdate(
  cfg: Pick<Config, "autoUpdate">,
  opts: AutoUpdateOptions = {}
): Promise<string> {
  try {
    if (!cfg.autoUpdate) return "";
    // The survey's own headless session must not race the runtime out from under its parent.
    if (process.env.HINDSIGHT_DISABLE_HOOKS) return "";

    const pkgRoot = opts.pkgRoot ?? packageRoot();
    const runtime = opts.runtimeDir ?? stagedRuntimeDir();
    if (!existsSync(runtime)) return "";
    // Only the staged copy updates itself — see the module doc.
    if (!sameDir(pkgRoot, runtime)) return "";

    const now = opts.now ?? Date.now();
    const file = stateFile(runtime);
    if (!dueForCheck(file, now)) return "";

    const current = stagedVersion(pkgRoot);
    if (!current) return ""; // cannot tell what is installed — never guess and overwrite it
    // Both guards sit after the interval gate and stamp like any other "checked, nothing to do"
    // outcome, so each states its reason at most once a day instead of on every session start.
    if (!(opts.selfUpdatable ?? selfUpdatable)(runtime)) {
      log.info("auto-update", "runtime is managed outside npx — leaving its version alone");
      stampCheck(file, now, "");
      return "";
    }
    // Probed BEFORE the registry call: with no npx there is nothing to spawn, and with no npm
    // there is no version to look up — either way, asking npm for a version we could not install
    // anyway is a request for nothing. npx and npm ship together, so this is usually one verdict.
    const binOk = opts.binOnPath ?? binOnPath;
    if (!binOk("npx") || !binOk("npm")) {
      log.info("auto-update", "npx/npm is not on PATH — skipping the update check");
      stampCheck(file, now, "");
      return "";
    }

    // Claimed before the registry call, so a burst of simultaneous session starts makes ONE
    // request and can only ever produce one updater.
    const lock = opts.lockFile ?? lockFile();
    if (!acquireUpdateLock(lock, now)) return "";
    try {
      const latest = await (opts.npmView ?? npmViewVersion)(PACKAGE_NAME);
      stampCheck(file, now, latest);
      if (!latest || !isNewer(latest, current)) {
        releaseUpdateLock(lock);
        return "";
      }

      log.info("auto-update", `updating the Hindsight runtime ${current} -> ${latest}`);
      const child = (opts.spawn ?? realSpawn)(
        "npx",
        ["-y", `${PACKAGE_NAME}@${latest}`, "update"],
        {
          detached: true,
          stdio: "ignore",
          windowsHide: true,
        }
      );
      // A spawn failure (no npx on PATH, EACCES) arrives asynchronously as an 'error' event; an
      // unhandled one would take the session start down with it.
      child.on("error", (e) => {
        log.warn("auto-update", `update spawn failed: ${e.message}`);
        releaseUpdateLock(lock);
      });
      child.unref();
      holdLockFor(lock, child.pid, now);
      return latest;
    } catch (e) {
      releaseUpdateLock(lock);
      throw e;
    }
  } catch {
    return ""; // an update check must never break a session
  }
}
