# Gold prompts from prompts.chat

A training and reference set for Promptsmith: the best **code, agent, prompt-engineering and video** prompts from [prompts.chat](https://prompts.chat) (`f/prompts.chat`, `prompts.csv`). That data is **CC0 1.0, public domain**, so it can be reused freely.

## How they were picked
1. Started from all 2,169 prompts in `prompts.csv`.
2. Kept only code, dev tools, agents, prompt engineering and video (scripts, storyboards, motion). Dropped still-image and photo prompts, plus anything under 40 or over 900 words. That left **743 prompts**.
3. Claude rated every one of them from **1.0 to 10.0** with a strict rubric: clear role and goal, testable requirements, defined output format, handles ambiguity, no fluff or jailbreak framing, reusable.
4. Kept every prompt scoring **8.5 or higher** in scope and removed duplicates, leaving **21 prompts**.

| File | Contents |
|---|---|
| `prompts-chat-top.jsonl` | The 21 kept prompts: full text, score, kind, one-line reason, source and license |
| `prompts-chat-ratings.csv` | All 743 ratings (score, kind, length, title, reason), no prompt text |

**Score distribution:** mean 5.7. Only 4 reached 9.0 (OpenAI Create Plan Skill, PostHog + Next.js 15, Claude Code Statusline, Web Typography). The video category was thin: only one video prompt reached 8.5 (a YouTube retention script).

## What Promptsmith learned from them
The patterns shared by the top prompts are now in the command's **Craft patterns** section:
- named input slots
- an exact output template with counts
- a few MUST/NEVER rules
- scope and non-goals
- a stop-or-ask gate
- evidence and verification steps
- numbers instead of adjectives

The prompts themselves aren't pasted into the command, which would bloat every call. They're a reference set.
