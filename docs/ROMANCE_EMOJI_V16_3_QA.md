# MEOWNURI SOL v16.3 · Emoji-only fish gift QA

Scope: Day 1 Samsaeki × Kkami fish-to-wood courtship scene only. No changes to ASTRA or public main.

- Slow 65-second ten-shot scene inherited from SOL v16.2
- 8 short emoji reactions: 🐟 → ❔ → 🐟💛 → ✨ → ☺️ → 🪵💛 → 😳 → 💛
- One bubble maximum, beside each character rather than covering eyes
- New balloons contain no words or language-dependent dialogue
- Minimal gentle sound accompanies the gift and return-gift balloon
- Speech, captions and the old bond-choice dialogue remain disabled within this scene

## Local verification

Chromium, 390×844 mobile 2D safe mode: ten sampled timestamps including both blank-emotion pauses and all eight emoji reactions PASS. Scene completes (story phase 1, friendToken=true), balloon is removed. No JavaScript page errors in tested path. All screenshots are local test artifacts.

## Online deployment verification

Vercel SOL preview project is READY. GitHub Actions independently fetched the production alias via HTTPS and verified the exact SHA-256:
`ef7eb4cd1a1250b704a8f7d420dd57d82adf7da371b5d1d5c5c8bc1e8c12dc5c`.

Review: https://meownuri-sol-v16-story-preview.vercel.app/?scene=gift

## Still unverified

Normal hardware-accelerated 3D WebGL view, Galaxy Z Flip physical device, speaker sound level, and uninterrupted 65-second natural playback in a headless browser. Those are distinct from the 2D timing-jump tests.
