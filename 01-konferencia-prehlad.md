# AI Engineer World's Fair 2026 – prehľad

- **Kde/kedy:** San Francisco, 29. 6. – 2. 7. 2026
- **Rozsah:** 561 sessions, 552 speakerov, 346 firiem, ~48 trackov
- **Zdroj:** https://ai.engineer/worldsfair/2026/sessions.json (+ `speakers.json`), lokálne v `conference/`

## Kto tam bol

| Kategória | Firmy |
|---|---|
| **Frontier labs** | Anthropic (13 speakerov), OpenAI (10), Google / DeepMind (17), Microsoft (14 + vlastný track M), Meta, Amazon AGI, NVIDIA, Hugging Face |
| **Coding agenti** | Cursor, Cognition, Factory, Warp, Cline, Sourcegraph, Qodo, Greptile, Sonar, GitHub, Conductor, HumanLayer |
| **Infra / inference** | Together AI, Modal, Fireworks, FriendliAI, Baseten, CoreWeave, Cerebras, OpenRouter, Red Hat (vLLM) |
| **Sandboxy / security** | Docker, E2B, Daytona, Browserbase, Snyk, WorkOS, Keycard, Auth0, Better Auth |
| **Evals / observability** | Arize, Braintrust, Langfuse (ClickHouse), W&B, Datadog, Dynatrace |
| **Dáta / RAG / dokumenty** | Neo4j, Reducto, LlamaIndex, Elastic, Pinecone, turbopuffer, Exa, Bright Data, Oxylabs, Firecrawl |
| **Enterprise adopteri** | Uber, Stripe, PayPal, Nubank, Coinbase, DoorDash, Spotify, LinkedIn, Notion, Figma, Ramp, Maersk, Morgan Stanley, Best Buy |

### CEE ľudia – networking

- **Jan Čurn** (Apify, CZ) – 2 talky: „x402 isn't good (yet)“, „MCP doesn't suck – your agent does“
- **Daniel Svoňava** (Superlinked, SK) – „Large clusters for small models“ (inference)
- **Tereza Tížková** (Factory) – „Rise of the Software Factory“
- **Druid AI** (RO) – performance review framework pre enterprise agentov
- **Oxylabs** (LT) – web data infra pre agentov

## 10 hlavných tém

1. **Software factories & koniec code review** – agenti píšu väčšinu kódu (Uber: 70 % PR od AI, 15 % plne autonómne). Bottleneck je verifikácia a review, nie generovanie.
2. **Harness & context engineering** – nezáleží až tak na modeli, ale na harnesse okolo (skills, pamäť, sandbox, kontext). Buzzwordy roka: *Skills* (SKILL.md), *MCP*.
3. **Agent security & governance** – identita agentov, oprávnenia, rozpočty, sandboxy (microVM), kontrola MCP serverov a skills (Nubank vetoval 2 000 skills).
4. **Evals → self-improving loop** – produkčné traces → evals → automatický PR s opravou.
5. **Agentic commerce** – agenti nakupujú a platia (x402, ACP, MCP, wallety pre agentov) – Stripe, PayPal, Circle, AWS.
6. **Voice agenti** – Hippocratic AI (200 M hovorov s pacientmi), Gradium, Plivo, LiveKit, EliseAI; latencia < 200 ms, reálne správanie volajúcich.
7. **Local AI & suverenita** – open-weight modely (GLM 5.2, MiniMax, Kimi) na DGX, air-gapped nasadenia, routing local vs. cloud, vlastné fine-tuned modely („stop renting intelligence“).
8. **Vertikálne AI** – finance (Kepler, Intuit), zdravotníctvo (Abridge, Hinge), právo (Legora – miliardy právnych dokumentov), GTM (Clay, Ramp, Notion).
9. **Document AI / OCR** – parsing dokumentov ako context layer (Reducto, LlamaIndex); Sarvam trénoval vlastný OCR pre 22 indických jazykov.
10. **Forward Deployed Engineering** – samostatný track; Anthropic, Cursor, Cognition, Ramp, Sierra posielajú inžinierov priamo k zákazníkovi.

**Pre nás nerelevantné** (kapitálovo náročné, globálna konkurencia): post-training, RL, kernely, robotika, world models, inference infra.
