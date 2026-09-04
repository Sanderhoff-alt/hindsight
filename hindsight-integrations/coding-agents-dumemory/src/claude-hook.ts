#!/usr/bin/env node
/**
 * dumemory-claude-hook — the Claude Code entry point (a `UserPromptSubmit` hook).
 *
 * Configured in Claude Code's settings.json (`~/.claude/settings.json`):
 *   { "hooks": { "UserPromptSubmit": [ { "commands": [
 *       { "type": "command", "command": "dumemory-claude-hook" } ] } ] } }
 *
 * Emits nothing on standard stdout; injections travel via `hookEventName: "UserPromptSubmit"`
 * JSON payloads (`{ hookSpecificOutput: { additionalContext: "..." } }`). Failures log to stderr,
 * outcomes recorded in the diagnostic file. Config: the layered files (~/.dumemory/coding-agent.json
 * etc.) and env overrides documented in README.md.
 */
import { runHarnessPrompt } from "./harness/hook-lifecycle";

void runHarnessPrompt("claude-code");
