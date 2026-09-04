#!/usr/bin/env node
/** Antigravity CLI PreInvocation hook — receives the documented workspace/prompt/event/
 * transcriptPath payload and injects DuMemory context as an ephemeral model message. */
import { runHarnessPrompt } from "./harness/hook-lifecycle";

void runHarnessPrompt("antigravity-cli");
