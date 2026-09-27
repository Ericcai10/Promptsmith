// Unit tests for the auto-mode hook's trigger logic. Run: node --test hooks/
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { shouldEnhance, buildContext } from "./promptsmith-auto.mjs";

const HOOK = fileURLToPath(new URL("./promptsmith-auto.mjs", import.meta.url));
const run = (prompt, env = {}) =>
  execFileSync(process.execPath, [HOOK], {
    input: JSON.stringify({ hook_event_name: "UserPromptSubmit", prompt }),
    env: { ...process.env, ...env },
  }).toString();

test("enhances rough gists", () => {
  for (const p of ["redesign my home screen", "make me a workout plan", "fix my code pls", "idk make me money"])
    assert.ok(shouldEnhance(p), p);
});

test("skips follow-ups and acknowledgements", () => {
  for (const p of ["yes", "ok do it", "yes go ahead", "looks good thanks", "keep going", "sounds great, do it!"])
    assert.ok(!shouldEnhance(p), p);
});

test("skips commands, bash mode, raw: opt-out, pasted content, empties", () => {
  for (const p of ["/promptsmith redesign my app", "!ls -la", "raw: fix the thing now", "", "   ",
                   '<pasted_content id="1">\nlots\n</pasted_content id="1">'])
    assert.ok(!shouldEnhance(p), JSON.stringify(p));
});

test("skips long, already-detailed prompts", () => {
  assert.ok(!shouldEnhance("word ".repeat(80)));
});

test("emits valid hook JSON for a gist", () => {
  const out = JSON.parse(run("redesign my home screen"));
  assert.equal(out.hookSpecificOutput.hookEventName, "UserPromptSubmit");
  assert.match(out.hookSpecificOutput.additionalContext, /Promptsmith auto mode/);
});

test("emits nothing for follow-ups or when off", () => {
  assert.equal(run("ok do it"), "");
  assert.equal(run("make a game", { PROMPTSMITH_AUTO: "off" }), "");
});

test("quiet mode drops the Read-as line", () => {
  assert.match(buildContext("show"), /Read as/);
  assert.doesNotMatch(buildContext("quiet"), /Read as/);
});

test("speaks the Hermes pre_llm_call protocol", () => {
  const call = (user_message) => execFileSync(process.execPath, [HOOK], {
    input: JSON.stringify({ hook_event_name: "pre_llm_call", extra: { user_message } }),
  }).toString();
  assert.match(JSON.parse(call("redesign my home screen")).context, /Promptsmith auto mode/);
  assert.equal(call("ok do it"), "");
  assert.equal(call([{ type: "text", text: "describe this image please" }]), "");  // multimodal turn
});

test("survives garbage stdin", () => {
  const out = execFileSync(process.execPath, [HOOK], { input: "not json" }).toString();
  assert.equal(out, "");
});
