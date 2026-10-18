# Postup: opakovateľný AI readiness audit a porovnanie pred / po

Tento postup zaručí, že audit toho istého obchodu dá **vždy ten istý výsledok** a že sa dajú porovnať dva behy:
pred úpravami (v1) a po úpravách (v2), alebo mesiac po mesiaci.

## Čo je deterministické a čo nie

| Časť | Deterministická? | Prečo |
|---|---|---|
| Skóre dát z feedu | ✅ áno | čistý kód nad XML, pevné pravidlá v `eshop/score.py` |
| robots.txt a schema.org | ✅ áno, ak sa web nezmenil | čistý kód nad HTML |
| AI obohatenie | ✅ áno, ak sa použije uložený súbor | výstup AI sa uloží do `enrichments.json` a ďalej sa len načítava |
| Viditeľnosť v AI | ❌ nie | živý web a AI modely sa menia. Riešenie: **pevná sada dopytov** (`prompts.json`) a výsledky uložené v `probes.json` |
| Report `report.md` / porovnanie | ✅ áno | vyplnené zo šablón `templates/*.md` iba zo snímky `audit.json` |

Každý beh uloží **snímku `audit.json`**: zoradené kľúče, žiadne časové značky, dátum sa zadáva ručne cez `--date`.
Otisk feedu (SHA-256) v reporte ukazuje, či sa audit robil na tých istých dátach.

## Pravidlá (dodržať pri každom audite)

1. **Pevný dátum:** vždy `--date YYYY-MM-DD` (deň auditu), nie automatický.
2. **Pevné označenie:** `--label`, napr. `v1`, `v2`, `2026-11`.
3. **Uložiť vstupy:** feed (`heureka.xml`), `enrichments.json`, `probes.json` a `prompts.json` do priečinka obchodu,
   napr. `audits/<obchod>/<label>/`. Bez nich sa beh nedá zopakovať.
4. **Rovnaká sada dopytov** pre všetky behy jedného obchodu. Kto zmení `prompts.json`, začína novú sériu meraní.
5. **Rovnaké parametre kontroly webu:** rovnaké `--pages`, ideálne všetky (`--pages 100`).
6. **AI obohatenie len raz na verziu dát:** ak sa feed nezmenil (rovnaký otisk), znovu použiť uložený `enrichments.json`.

## Krok za krokom

### A) Nový obchod – prvý audit (v1)

```bash
cd demo-agent-ready-eshop
SHOP=obchod-cz; DIR=audits/$SHOP/v1; mkdir -p $DIR
curl -o $DIR/heureka.xml "https://www.obchod.cz/<url-feedu>"
cp sample/prompts.json $DIR/prompts.json          # upraviť dopyty podľa kategórií obchodu, potom už nemeniť

.venv/bin/python audit.py --feed $DIR/heureka.xml --site --pages 100 \
  --label v1 --date 2026-10-18 --out out/$SHOP/v1
```

**AI kroky – variant 1, automaticky cez API** (treba `ANTHROPIC_API_KEY`):
```bash
.venv/bin/python audit.py --feed $DIR/heureka.xml --site --pages 100 --enrich 5 \
  --visibility 5 --prompts $DIR/prompts.json --label v1 --date 2026-10-18 --out out/$SHOP/v1
```
Potom uložiť výsledky AI do `$DIR/enrichments.json` a `$DIR/probes.json`, aby sa beh dal zopakovať bez API.

**AI kroky – variant 2, ručne v Claude Code** (bez API):
1. Požiadať Claude Code: _„Obohať 5 najslabších produktov z `out/<obchod>/v1/audit.json` podľa pravidiel v
   AUDIT-POSTUP.md a ulož do `audits/<obchod>/v1/enrichments.json`.“_
   - Formát zodpovedá triede `Enrichment` v `eshop/enrich.py`. Vzor: `sample/v1/enrichments.json`.
   - **Každý parameter musí mať `source_quote`, teda doslovný úryvok z feedu.** Nič nevymýšľať. Čo chýba, patrí do `missing_info`.
2. Požiadať Claude Code: _„Polož každý dopyt z `prompts.json` webovému vyhľadávaniu a ulož citované domény do
   `probes.json` (formát `sample/v1/probes.json`). `mentioned` = true iba vtedy, ak odpoveď spomenie doménu obchodu.“_
3. Spustiť audit s uloženými výsledkami:
```bash
.venv/bin/python audit.py --feed $DIR/heureka.xml --site --pages 100 \
  --enrichments $DIR/enrichments.json --probes $DIR/probes.json \
  --label v1 --date 2026-10-18 --out out/$SHOP/v1
```

### B) Po úpravách obchodu (v2) a porovnanie

```bash
DIR2=audits/$SHOP/v2; mkdir -p $DIR2
curl -o $DIR2/heureka.xml "https://www.obchod.cz/<url-feedu>"
cp audits/$SHOP/v1/prompts.json $DIR2/            # TÁ ISTÁ sada dopytov
# (voliteľne) zmerať viditeľnosť znova, ideálne ~4 týždne po úpravách → $DIR2/probes.json

.venv/bin/python audit.py --feed $DIR2/heureka.xml --site --pages 100 [--probes $DIR2/probes.json] \
  --label v2 --date 2026-11-15 --out out/$SHOP/v2
.venv/bin/python compare.py out/$SHOP/v1/audit.json out/$SHOP/v2/audit.json -o out/$SHOP/compare-v1-v2.md
```

### C) Overenie, že beh je opakovateľný

Spustiť ten istý príkaz dvakrát do rôznych priečinkov a porovnať:
```bash
diff -r out/$SHOP/v1 out/$SHOP/v1-kontrola && echo "identické"
```
Ak sa výsledky líšia a vstupy sú rovnaké, zmenil sa web obchodu, nie audit (robots.txt, schema.org).

## Výstupy každého behu

| Súbor | Na čo |
|---|---|
| `audit.json` | snímka – zdroj pravdy pre reporty a porovnania |
| `report.md` | report zo šablóny `templates/report.md` (do e-mailu, Notion, PDF) |
| `report.html` | vizuálny report pre majiteľa obchodu |
| `heureka-enriched.xml`, `merchant-supplemental.tsv`, `jsonld/` | súbory na nasadenie (iba ak bolo obohatenie) |
| `compare-*.md` | porovnanie dvoch behov zo šablóny `templates/compare.md` |

## Úprava šablón

`templates/report.md` a `templates/compare.md` používajú premenné `$nazov` (Python `string.Template`).
Text a poradie sekcií sa dá meniť voľne. Zoznam premenných je vo funkciách `render_report` a `render_compare`
v `eshop/snapshot.py`. Pri zmene štruktúry `audit.json` zvýšiť `SCHEMA_VERSION`. `compare.py` potom odmietne
porovnať nekompatibilné snímky.

## Ukážka na fiktívnom obchode

```bash
./run_compare_demo.sh        # postaví weby v1/v2, spustí ich lokálne, urobí oba audity a porovnanie
open out/compare-v1-v2.md
```
Výsledok: kvalita dát 57 → 100, AI boty odblokované (OAI-SearchBot, PerplexityBot), schema.org 0/12 → 12/12.
Viditeľnosť po úpravách nie je zmeraná, lebo fiktívny obchod nie je na internete.
