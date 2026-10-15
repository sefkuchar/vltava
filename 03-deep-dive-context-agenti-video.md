# Deep dive: context engines, decentralizovaní agenti, HTML → video

## 1. Video z čistého HTML – HeyGen HyperFrames

**Talk:** „HTML Is All Agents Need“ – James Russo (HeyGen), 3. deň (Session Day 3), 11:10, Track 1

**Príbeh z talku:**
- Najprv veľké prompty → priemerný výstup.
- Potom Remotion → deterministické video, ale React agentov obmedzoval; viac guardrails = nudnejšie výstupy.
- Čisté HTML/CSS/JS → agentom sa vrátila kreativita.
- Framework navrhnutý tak, aby video napísal aj malý model (Gemini Flash). „Ak framework potrebuje najväčší model, bojuje proti agentovi.“
- Hlavný inžiniersky problém: determinizmus v prehliadači (async dekódery obrázkov, fonty, animačné hodiny).
- Agentické loopy + self-improving evals; skills dávajú agentom „taste namiesto guardrails“.

**Technicky (HyperFrames):**
- Headless Chromium načíta HTML kompozíciu → deterministicky posúva čas → screenshot každého snímku → FFmpeg zloží MP4.
- Open source, Apache-2.0, npm balík `hyperframes`.
- ~21 skills pre Claude Code / Cursor / Gemini CLI.
- Prepojenie mena speakera s HyperFrames je odvodené z obsahu talku, v zdrojoch nepotvrdené.

**Využitie CZ/SK:**
- Produktové videá automaticky z feedu Shoptetu / Heureky
- Reels pre realitky z inzerátov
- Tréningové / onboarding videá pre firmy v CZ/SK
- \+ lokálne TTS = lacná masová produkcia → rýchly SaaS

## 2. Context engines

**Spoločná téza:** RAG nestačí. Agent potrebuje vrstvu, ktorá spája entity, vzťahy, oprávnenia, históriu rozhodnutí a aktuálne dáta – a vyberie len to, čo treba. Viac kontextu = často horšie odpovede.

| Talk | Kto | O čom |
|---|---|---|
| Beyond RAG: Build a Relational Context Engine from Scratch (workshop, 1. deň 12:10, Track 7) | Peter Werry, Unblocked | NL → validované DB dotazy nad GitHub PR/issues, schema-aware prompting, identity resolution, retry pri chybe. Open-source simulátor context enginu. |
| How to generate mergeable code with a context engine | Peter Werry, Unblocked | Context engine pre coding agentov – menej tokenov, lepší kód |
| WTF Is the Context Layer? | Prukalpa Sankar, Atlan | Verziované „context repos“ (testovateľné, prenosné), simulácie pred nasadením, traces sa vracajú do kontextu, otvorenosť (MCP, Iceberg) |
| Why your company needs a context graph | Gil Feig, Merge | Context graph ako control plane: tiering čerstvosti dát, provenance, oprávnenia, < 300 ms latencia |
| From Systems of Record to Systems of Context | Omri Bruchim, monday.com | „Decision traces“ – kto čo schválil, aké výnimky platia. To je skutočný moat. |
| The Data Context Layer (workshop) | typedef | Lineage, sémantika metrík, runtime signály, property graph |
| Building the Document Context Layer | Jerry Liu, LlamaIndex | Context layer pre dokumenty (PDF, Word, PPTX → agent-native formáty) |
| Context graphs / GraphRAG / CrabRAG | Neo4j (viac talkov) | Grafová pamäť namiesto čistých vektorov |
| Context Engineering in 2026: Compaction, Memory & Cost (workshop) | Towards AI | Compaction, pamäť, cena; porovnanie open/local modelov |

**Využitie CZ/SK:** context engine nad ERP (Money, Pohoda, Helios, SAP), dokumentmi a e-mailom firmy, s oprávneniami, on-prem kvôli GDPR. Na tom konkrétni agenti (obchod, podpora, účtovníctvo). Moat = znalosť lokálnych systémov a dát.

## 3. Decentralizovaní agenti / flow nezávislý od enginu

### Band.ai – Vlad Luzin (CTO)
- **„Every Agent, Everywhere, All at Once“** (1. deň, Expo Stage 1) – live demo: Claude Code na jednom notebooku, Codex na druhom, lokálny LangGraph agent a OpenClaw doma spolupracujú na jednom cieli, full-duplex.
- **„Is Orchestration the Future?“** (2. deň, Leadership 2) – namiesto orchestrátora collaboration layer, kde agenti rôznych vendorov zdieľajú jednu konverzáciu ako stateful peers.
- Firma: Izrael + SF, založená 2025, seed 17 M $ (apríl 2026, Sierra Ventures, Hetz, Team8). Produkt „Agentic Mesh“ (routing správ, doručovanie, crash recovery) + Control Plane (audit, delegácia). SDK Python/TS, MCP server.

### Ďalšie súvisiace talky
- **Warp (Zach Lloyd)** – Oz: message passing medzi harnessmi (claude, codex), lokálne aj v cloud sandboxoch, model-agnostic.
- **Block – Agent Client Protocol (Alex Hancock)** – štandardný `/acp` endpoint (HTTP + WebSocket), zladený s MCP → agent nezávislý od toho, kde beží.
- **Town (Jean-Denis Greze)** – agent-to-agent správy, HITL pri citlivých dátach.
- **DSPy (Maxime Rivest, Isaac Miller)** – „Separating the Task from the Model“: definuješ signature (vstupy/výstupy), model a prompt sa vymieňajú pod tým; preview DSPy 4.0.
- **Inngest (Dan Farrelly)** – „Your agent architecture has a half-life of 6 months“: stavať tak, aby zmena trendu nevyžadovala prepis.
- **Kimchi** – routing medzi frontier a open-weight modelmi (Kimi, MiniMax), ~2,5× lacnejšie.
- **Tailscale (Remy Guercio)** – „An AI Future Without the Lock-In“: identity-aware AI gateway (Aperture).
- **.txt (Rémi Louf)** – „Agent Frameworks Considered Harmful“.

**Využitie CZ/SK:** firmy sa boja vendor lock-inu a US cloudu →
- model-agnostic flow (Claude / GPT / lokálny GLM podľa citlivosti dát),
- audit + human-in-the-loop (pomáha s AI Act).

Vlastný mesh protokol nestavať – použiť Band / open štandardy (ACP, A2A, MCP) ako základ.

## Zdroje

- [HeyGen open-sources HyperFrames (themenonlab)](https://themenonlab.blog/blog/heygen-hyperframes-video-as-code)
- [HyperFrames: Claude Code can write and render videos](https://themenonlab.blog/blog/hyperframes-claude-code-writes-renders-videos)
- [HyperFrames – open-source HTML video rendering (silenceper)](https://silenceper.com/en/article/2026-05-02-hyperframes-html-video-rendering/)
- [HyperFrames guide (vidmuse)](https://vidmuse.ai/blog/hyperframes-guide)
- [HyperFrames – landscape.jimmysong.io](https://landscape.jimmysong.io/projects/hyperframes/)
- [BAND launches interaction layer, raises $17M seed](https://letsdatascience.com/news/band-launches-interaction-layer-raises-17m-seed-1842660e)
- [BAND exits stealth (CXO Digital Pulse)](https://www.cxodigitalpulse.com/band-exits-stealth-with-17m-to-build-the-communication-and-interaction-layers-for-the-internet-of-agents/)
- [Band Agentic Mesh (lablab.ai)](https://lablab.ai/tech/band-ai/band-agentic-mesh)
