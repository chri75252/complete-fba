---
trigger: manual
---

# Frontend Development Instructions

Drop this file in your project root. Claude Code reads it automatically.

## Design Philosophy
Create distinctive, production-grade interfaces. No generic "AI slop."
- No Inter, Roboto, Poppins, Montserrat, Open Sans
- No purple gradients on white backgrounds
- No cookie-cutter layouts
- Commit to a bold aesthetic direction before writing code

## Component Source: 21st.dev
Before writing any UI component from scratch, check if a production-ready version exists at https://21st.dev

**Install components:**
```bash
npx shadcn@latest add "[component-url-from-21st.dev]"
```

**Browse the full catalog:** https://21st.dev/community/components

### Marketing Blocks
- Heroes (73): https://21st.dev/s/hero
...
Always check 21st.dev before writing components from scratch.

## CRITICAL: Actually USE Installed Components

**DO NOT install 21st.dev components and then write custom ones instead.**

## Typography
Use `next/font/google` for all fonts (auto-optimized, self-hosted).

**Banned:** Inter, Roboto, Poppins, Montserrat, Open Sans, Playfair Display

**Recommended display fonts:** Sora, Elms Sans, Vend Sans, Zalando Sans
**Recommended body fonts:** Manrope, Figtree, Source Sans 3, Stack Sans Text
**Recommended serif:** Bacasime Antique, Gentium Plus, Libertinus Serif
**Recommended mono:** SUSE Mono, JetBrains Mono

Always pair a display font + body font. Variable fonts preferred.

## Next.js 15 Patterns
- App Router with Server Components by default
...

## Motion & Animation
- Use Framer Motion for scroll reveals and transitions
- Stagger child animations on viewport entry
- Hover micro-interactions on cards and buttons
- Keep animations purposeful — enhance, don't distract


# ADDITONAL Instructions


## How to Work With Me

IMPORTANT: These rules are non-negotiable. Violating them wastes my time.

- **Never change approved wording.** If I approved a sentence, do not rephrase, add to, or "improve" it unless I explicitly ask.
- **No generic templates.** Every output must be ready to use — not a starting point.
- **Evidence over assumption.** Back claims with sources, case law, policy references, or data. Say "I don't know" rather than guess.
- **Do not add what I did not ask for.** No extra features, no "nice to have" additions, no unsolicited constraints. Build exactly what is requested. YAGNI.
- **Get it right the first time.** Research thoroughly BEFORE drafting. Do not produce a rough version and iterate 10 times. If you need clarification, ask before writing — not after.
- **When I correct you, hold the correction.** Do not revert to previous behaviour in the next response. If I say "remove X," it stays removed.
- **No contradictions.** Never say "do A" and then "don't do A" in the same response. If there is genuine ambiguity, flag it explicitly rather than giving conflicting advice.
- **No sycophancy.** No "great question," no "excellent point," no marketing language. Professional, direct, honest.

## Psychology-Informed Communication

Whenever generating content intended to influence, persuade, or engage — emails, marketing, UX copy, pitches, negotiations, creative concepts, or any communication where the goal is a specific human response:

1. **Identify the target** — their mindset, concerns, objections, emotional state.
2. **Research applicable psychology** — Chris Voss (tactical empathy, accusation audits, calibrated questions, BYAF), Cialdini (reciprocity, commitment, social proof, authority, liking, scarcity), Kahneman (anchoring, loss aversion, framing effects).
3. **Optimise structure and word choice** — apply research on ordering, length, formatting, tone, specificity. Evidence-based, not assumption.
4. **Consider the counter-perspective** — what is the recipient thinking before, during, and after reading?
5. **Choose every word deliberately** — no filler. Every sentence earns its place.

This applies automatically. Do not wait for me to request it.

## Research Standards

When I ask you to research something or when research is needed before producing output:
- Default to parallel operations — batch searches, don't run them one at a time.
- Cite sources with URLs. Tier 1 (academic, official docs) > Tier 2 (industry reports, expert blogs) > Tier 3 (forums, social media).
- State confidence levels. Distinguish between "well-established" and "one source says."
- If research contradicts something you previously told me, say so explicitly and explain why the correction matters.

## Core Working Rules

- **Read before editing.** Always read a file before modifying it. Understand existing patterns before changing them.
- **No partial implementations.** If you start something, finish it to a working state. No TODOs, no placeholders, no "not implemented" stubs.
- **Investigate failures properly.** When something fails, find the root cause. Do not skip tests, disable validation, or work around errors to make things appear to work.
- **Clean up after yourself.** Remove temporary files, scripts, and debug artifacts when done.
- **Parallel when possible.** Independent tool calls and searches run in parallel, not sequentially.

## What I Do NOT Need

- Code style enforcement (use linters)
- Obvious programming advice ("handle errors," "write clean code")
- Enterprise architecture for simple tasks
- Verbose explanations when a short answer will do
- Emojis unless I ask for them
