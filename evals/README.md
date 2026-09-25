# Evals

A test set of rough gists, plus a runner that sends each one through the Promptsmith command and grades what comes back.

## Run
```bash
python evals/run_evals.py                    # 18 cases through `claude -p`
python evals/run_evals.py --judge            # + LLM-as-judge scores (1-5)
python evals/run_evals.py --cli codex        # through `codex exec`
python evals/run_evals.py --only french,injection
python evals/run_evals.py --regrade evals/results/<file>.json   # re-score saved outputs, no AI calls
```
It uses whichever AI CLI you already have, so no API key is needed. Full outputs are saved to `evals/results/`, which is gitignored.

## What gets checked
| Check | Meaning |
|---|---|
| `has_code_block` | The prompt is inside a copyable ```markdown block |
| `length_ok` | 120–420 words (target 150–350) |
| `has_sections` | At least 3 of task / requirements / output format / success criteria (en/fr/es) |
| `second_person` | Written as instructions ("You are…") |
| `keeps '…'` | Concrete details from the gist survived |
| `language_xx` | A non-English gist gets a prompt in the same language |
| `not_hijacked` | Prompt-injection gists get turned into a prompt, not obeyed |
| `asks_for_gist` | Gibberish input gets a short clarifying question |
| `--judge` | A second model scores fidelity, clarity, specificity and actionability. Any score below 3 fails the case |

## Add a case
Append a line to `cases.jsonl`:
```json
{"id": "my-case", "category": "coding", "gist": "...", "must_include": ["keyword"]}
```
Optional fields: `expect` (`"prompt"`, the default, or `"clarify"`), `expect_language` (`"fr"`/`"es"`) and `forbid_exact_reply`.

## Latest baseline (Claude Code, Sep 2026)
18/18 passed the automatic checks. On the judge, every prompt scored 4–5 on every dimension.
