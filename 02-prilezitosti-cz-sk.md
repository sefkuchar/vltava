# Príležitosti pre CZ/SK trh

Zoradené podľa kombinácie: rýchlosť k peniazom × lokálna ochrana pred konkurenciou (jazyk, regulácia, lokálny ekosystém).

| # | Príležitosť | Prečo tu | Inšpirácia z konferencie |
|---|---|---|---|
| 1 | **AI enablement / FDE agentúra pre stredné firmy a korporáty** | Firmy majú Copilot licencie, ale nič nenasadené. Rýchle peniaze, z projektov vzniknú produkty. | Forward Deployed Engineering track, Uber, Coinbase, Automattic |
| 2 | **Voice agenti v CZ/SK** (call centrá, energetika, zdravotníctvo, poisťovne) | Malé jazyky globálni hráči riešia slabo. Lokalizácia (výslovnosť, mená, adresy) = reálna ochrana. | Hippocratic, Plivo „5 failure modes“, Gradium, EliseAI |
| 3 | **E-shopy pripravené pre AI agentov** (katalógy pre agentov, viditeľnosť v ChatGPT/Gemini, ACP) | Tisíce e-shopov na Shoptete / Heureke / Allegre na to nie sú pripravené. Plugin / SaaS. | PayPal „Agent-Readable Catalogs“, Best Buy, Inth „LLMs recommend us“ |
| 4 | **Lokálne / on-prem AI pre banky, verejný sektor, zdravotníctvo** | GDPR, AI Act, nedôvera k US cloudu. Open-weight modely sú už dosť dobré. | Local AI track, „Air-gapped AI Fortress“, Akamai |
| 5 | **Právne AI nad CZ/SK legislatívou a judikatúrou** | Slov-Lex, Sbírka zákonů, súdne rozhodnutia sú verejné. Legora sem lokálne nejde. | Legora + turbopuffer, Mixedbread |
| 6 | **GTM engineering na CEE dátach** (ARES, ORSR, Finstat + enrichment agentmi) | „Clay pre CEE“ neexistuje, registre sú verejné. | Clay, Ramp, Exa |
| 7 | **Riadenie AI a AI Act compliance** (inventár agentov, oprávnenia, audit) | Regulácia prichádza, korporáty nevedia, čo im beží. | Docker MCP Gateway, Keycard, Retool, Snyk |
| 8 | **Ambient scribe pre lekárov v CZ/SK** | Obrovská medzera, ale pomalý predaj a regulácia. | Abridge, Hinge Health, Ufonia |
| 9 | **Video ako kód pre e-commerce a marketing** | Lacná masová produkcia videí v CZ/SK (HyperFrames + lokálne TTS). | HeyGen HyperFrames – viď `03-deep-dive-…` |
| 10 | **Context engine nad lokálnymi ERP** (Money, Pohoda, Helios, SAP) | Znalosť lokálnych systémov a dát = moat. On-prem kvôli GDPR. | Unblocked, Atlan, Merge, monday.com – viď `03-deep-dive-…` |

## Odporúčaná stratégia

1. Začať s **#1 (enablement / FDE)** – cash flow + poznanie trhu a reálnych problémov.
2. Z projektov vytiahnuť produkt, kde nás chráni jazyk alebo lokálny ekosystém: **#2 (voice)**, **#3 (agent-ready e-shopy)** alebo **#10 (context engine nad ERP)**.
3. **Nerobiť** infra / dev tools (evals, sandboxy, inference) – tam sa konkuruje globálne a s veľkým kapitálom.

### Spoločná téza

Context engine nad dátami firmy + agenti nezávislí od modelu (Claude / GPT / lokálny GLM podľa citlivosti dát) + audit a schvaľovanie človekom (AI Act) + generovaný obsah (napr. HyperFrames videá).

> Pozn.: tvrdenia o CZ/SK trhu sú zatiaľ hypotézy – treba overiť researchom konkurencie (viď `04-dalsie-kroky.md`).
