# One-shot UI bench: findings

Six throwaway one-shot UI requests were run through Hermes (Claude Sonnet) with `evals/oneshot_bench.py`. Each result was rendered in Chrome, screenshotted and rated from the screenshots (1–10: polish, originality, whether it looks finished).

Variants: **off** = raw gist, **auto** = raw gist + auto-mode hook, **forge** = gist → `/promptsmith` prompt → build.

| Gist | off | auto | forge v1 | forge v2 | forge v3 |
|---|---|---|---|---|---|
| make me an isolated button | 3 | 3 | 2 | **8** | – |
| design a fashion website | 6 | 6.5 | 2 | 7 | **8** |
| design a portfolio website | 5 | 5 | 4 | **8** | – |
| make a pricing card section | 6 | 6 | 6.5 | **7** | – |
| make a login page | 5 | 6 | 5.5 | **7.5** | – |
| make a cool loading animation | 5 | 5.5 | 5 | 3 | **7.5** |
| **average** | 5.0 | 5.3 | 4.2 | 6.8 | **≈7.7** |

## What we learned
1. **v1 forge was worse than doing nothing on design gists.** "Design a fashion website" became a prompt for a *design spec document*, and the build step produced a style guide page instead of a site. The portfolio came out full of `[My Name]` placeholders, and the button was a lone button on a white page.
2. **Rules that fixed it (v2):** for visual build requests, the prompt must ask for the working thing, not a plan ("design" means design and build). It must invent realistic sample content instead of placeholders, pick one named visual direction (hex palette, font pairing, a signature detail) and avoid the default dark/indigo gradient look. A single component should get a small showcase page with its variants and states.
3. **Two failure modes appeared in v2, and v3 fixed both:** random stock-photo URLs showed unrelated subjects (a notebook on a fashion hero), so the prompt now asks for CSS/SVG art or clearly labeled image slots instead. An orbit animation flew outside its card and over a button, so animations now have to stay inside their container and respect `prefers-reduced-motion`.
4. **Auto mode barely moved the needle** (5.0 → 5.3). The hook did fire (its context is in the saved API messages), but a short one-line nudge doesn't change what gets built. The full forged prompt does.
5. **Every one of the 30 renders had zero JS errors.** The differences were all design and intent, not broken code.

Caveats: this is one run per cell, the ratings are one model's judgment from screenshots, and the build model was Claude Sonnet via Hermes. Treat the numbers as directional.
