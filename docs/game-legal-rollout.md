# Browsergame legal notices rollout

Prepared 2026-10-26. These changes are a reviewable implementation, not a certification of legal compliance.

## Scope

The standalone static page /spiele-rechtliches/ covers eight GitHub Pages games: genesis, dungeon, ai-idle, idle, dungeon-keeper, dispatch, particle and dc-idle, each under future-pulse.de. It does not load Hugo's analytics/comment templates, scripts, fonts, or tracking pixels. Operator details are reused from the existing public imprint.

197 game JS/TS/TSX/CSS files and the HTML entry points were inspected for storage/network use. AI-Idle's optional model saving uses IndexedDB as well as LocalStorage. Dungeon Runner and DC-Idle currently have no persistent game saves in the inspected code.

## Deployment order

1. Review operator details and legal wording, then merge this central page PR.
2. Verify the three anchors on https://future-pulse.de/spiele-rechtliches/.
3. Merge the legal-notice PRs in agent-genesis, Dungeon-Runner, AI-Idle and dc-idle. Links open a new tab so the active game is retained.
4. Archived repositories Idle-Game-v2, Dungeon-Keeper, Emergency-Dispatch-Idle and particle-universe cannot accept pushes/PRs. Their complete patches are in docs/game-legal-patches/. After unarchiving, apply with git apply --check followed by git apply, review, and open a PR in that repository. Archives were not changed.
5. crows-federation has a separate draft. Its README describes a VPS/Docker/nginx deployment, not GitHub Pages. Confirm that it is live and provide current hosting provider and server-log retention before adding its privacy scope and merging its draft. Do not describe it as GitHub Pages.
6. Quantum Forge points to quantum.future-pulse.tech, outside the requested .de scope. browser-rl-showcase is a separate RL demo, not a game; it is not silently included.

## License findings

Agent Genesis, Particle Universe and DC-Idle contain MIT LICENSE files. Dungeon Runner, AI-Idle, Idle-Game-v2 and Emergency-Dispatch-Idle already declare MIT in README/package.json; the missing full LICENSE files are restored from the standard MIT text. Dungeon-Keeper contains no explicit general license declaration; no license is assigned to it by these changes. The operator needs to choose one before general reuse rights can be described.

DC-Idle runtime dependency license notices are copied from the locked npm packages; @pixi/colord's omitted LICENSE is supplied from its upstream LICENSE.md. TensorFlow.js 4.17.0's copyright header and upstream Apache-2.0 text are retained separately. This inventory does not prove that every asset in every repository is free of third-party claims.

## Privacy changes

External Google Fonts requests are removed from the prepared game versions; existing CSS fallback font stacks remain. AI-Idle asks before requesting TensorFlow.js from jsDelivr, keeps the consent only for the current page, and permits the base game to continue on refusal. Model training remains local.

The generic blog privacy text is not certified by this change. Only its scope link is added. The obsolete EU ODR link is removed from the imprint (platform discontinued 2025-07-20).

## Verification limits

The repository source configuration was inspected. The web retrieval service could not open the game subdomains, so current DNS, hosting deployment, and live accessibility must be verified after merging. Crow Federation hosting is specifically unresolved. No missing provider details or fixed provider retention periods are invented.
