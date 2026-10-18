# Demo: AI readiness audit pre e-shop

Prvé demo k príležitosti #3 „E-shopy pripravené pre AI agentov“ (viď [`../05-deep-dive-agent-ready-eshopy.md`](../05-deep-dive-agent-ready-eshopy.md)).

Vstup je **Heureka XML feed**, ktorý má takmer každý CZ/SK e-shop. Výstup je **HTML report pre majiteľa obchodu**
a súbory, ktoré vie hneď nasadiť. Toto je nástroj na „zdarma mini-audit“, ktorým získame prvých zákazníkov.

## Čo audit robí

| Krok | Čo kontroluje / robí | Treba API kľúč? |
|---|---|---|
| 1. Kvalita dát | názov so značkou a modelom, dĺžka popisu, počet parametrov, platný EAN (kontrolný súčet), výrobca, obrázok, Heureka kategória, dodacia lehota → skóre 0–100 | nie |
| 2. Web a AI boty | robots.txt pre vyhľadávacie AI boty (OAI-SearchBot, PerplexityBot, Claude-SearchBot…) a tréningové boty; schema.org `Product` JSON-LD na produktových stránkach (cena, dostupnosť, GTIN, značka, hodnotenia) | nie |
| 3. AI obohatenie | Claude vyťaží parametre, use-cases a FAQ z existujúcich popisov. **Každý parameter musí mať doslovný citát zo zdroja.** Deterministická kontrola zahodí vymyslené hodnoty | áno |
| 4. Viditeľnosť v AI | Claude vygeneruje typické otázky zákazníkov, položí ich Claude s webovým vyhľadávaním (lokalita CZ) a zistí, či odpoveď spomenie obchod a koho cituje namiesto neho | áno |

**Výstupy** (v `out/`):
- `report.html` – report v češtine pre majiteľa
- `heureka-enriched.xml` – pôvodný feed + overené parametre doplnené ako `PARAM`
- `merchant-supplemental.tsv` – doplnkový feed do Google Merchant Center (ovplyvňuje Google AI Mode, funguje v CZ)
- `jsonld/*.json` – schema.org Product na vloženie do šablóny
- `audit.json` – surové skóre

## Spustenie

```bash
cd demo-agent-ready-eshop
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# bez AI – na ukážkovom feede (fiktívny obchod so zámernými chybami)
.venv/bin/python audit.py --feed sample/heureka-sample.xml --open

# reálny obchod – URL jeho Heureka feedu (nájdeš v administrácii e-shopu v sekcii exportov / feedov)
.venv/bin/python audit.py --feed https://www.obchod.cz/heureka.xml --site --open

# s AI (obohatenie 5 najslabších produktov + 5 dopytov na viditeľnosť)
export ANTHROPIC_API_KEY=sk-ant-...
.venv/bin/python audit.py --feed sample/heureka-sample.xml --enrich 5 --visibility 5 --open
```

Model sa dá zmeniť cez `CLAUDE_MODEL` (predvolený `claude-opus-5-5`).

## Overené pri vývoji

- Parsovanie feedu, skóre a výstupy: na ukážkovom feede.
- robots.txt: datart.cz sa načíta. alza.cz a mall.cz vracajú automatickým nástrojom 403 → report ukáže „nepodarilo sa overiť“ (nie falošné „povolené“).
- schema.org: na produktových stránkach datart.cz správne nájde `Product` so všetkými poľami.
- Kontrola halucinácií: vymyslená „hlučnosť 45 dB“ aj nesediaci „príkon 1600 W“ boli zamietnuté.
- **AI časti (kroky 3–4) zatiaľ nie sú otestované so živým API** – chýbal API kľúč. Bez kľúča skript skončí jasnou hláškou.

## Náklady (odhad, neoverené)

- Obohatenie: ~$0,01–0,03 za produkt.
- Viditeľnosť: ~$0,05–0,15 za dopyt (web search + model).
- Mini-audit (5 produktov + 5 dopytov): rádovo **$0,5–1** na obchod.

## Obmedzenia dema

- Viditeľnosť sa meria len cez Claude, nie cez ChatGPT, Gemini ani Perplexity. Odpovede AI sú nedeterministické, v produkcii treba opakované meranie.
- Shoptet API (doplnok) chýba, demo pracuje len s XML feedom.
- Bez checkoutu a ACP/UCP. Podľa deep dive v EÚ zatiaľ nefungujú.
- Formát `product_detail` v Merchant TSV treba pred nasadením overiť v Merchant Center.
- Kontrola webu prechádza len prvých N produktových URL z feedu.

## Ďalšie kroky

1. Spustiť audit na 10–20 reálnych CZ e-shopoch (verejné feedy alebo od známych) a doladiť skóre.
2. Pridať meranie v ChatGPT (OpenAI API s web search) a Perplexity (Sonar API).
3. Poslať mini-audity majiteľom a agentúram a zistiť, či by platili 1–5 tis. Kč mesačne.
4. Podať žiadosť o Shoptet partnerstvo (schvaľovanie trvá).
