# Deep dive 06: Právne AI nad CZ/SK legislatívou a judikatúrou

*Stav k 15. 10. 2026. Autor: research pre CZ/SK AI startup. Údaje, ktoré som neoveril webom, sú označené „(neoverené)“.*

---

## 1. Čo to je a prečo teraz

**Produkt:** AI asistent pre právnikov, ktorý (a) vyhľadáva v CZ/SK predpisoch v znení účinnom k zvolenému dátumu a v judikatúre, (b) odpovedá s povinnými, overiteľnými citáciami (§, odsek, spisová značka, ECLI), (c) analyzuje zmluvy (riziká, odchýlky od štandardu, extrakcia povinností) a (d) pripravuje drafty (podania, zmluvy, výzvy). Cieľovky: advokáti, firemní právnici, notári, exekútori, verejná správa.

**Prečo teraz:**
- **Dáta sa otvorili.** CZ e-Sbírka (od 2024) poskytuje strojovo čitateľné konsolidované znenia vrátane histórie verzií. rozhodnuti.justice.cz má verejné REST API s anonymizovanými rozhodnutiami okresných, krajských a vrchných súdov (od 1. 1. 2023 to vyžaduje vyhláška č. 403/2022 Sb.).
- **Trh je pripravený, ale nie je obsadený.** Interný prieskum SAK hovorí, že generatívnu AI používa „takmer polovica“ advokátov. SAK prijala záväzné pravidlá k AI (marec 2025, doplnené v novembri 2025). ČAK pripravuje nové stanovisko a AI stratégiu (predloženie predstavenstvu v septembri 2026).
- **Incumbenti sa už hýbu:** ASPI AI a Libra (Wolters Kluwer), CODEXIS AI Agent (Atlas), Beck-Noxtua (C.H.Beck v DE). Okno na diferenciáciu sa preto zatvára. Vyhrať sa dá kvalitou citácií, pokrytím nižších súdov, workflowmi a lokálnym (on-prem) nasadením.

### Čo zaznelo na AI Engineer World's Fair 2026 (SF)

- **„How to Connect AI to Billions of Legal Documents“ (Simon Eskildsen, turbopuffer + Jacob Lauritzen, Legora):** Legora pripája frontier LLM k miliardám právnych dokumentov s tromi cieľmi naraz:
  - striktná izolácia dát naprieč miliónmi prípadov,
  - latencia <100 ms p90,
  - recall@10 95 %+ pri menšom počte agentových slučiek.

  Dve predchádzajúce architektúry neuspeli. Kľúčové rozhodnutie je **per-tenant vs. zdieľaný index** pri striktnej izolácii a maximalizácia relevancie na vstupný token pri obmedzenom inference rozpočte. *Pre nás:* verejný korpus (zákony, judikatúra) má byť jeden zdieľaný index, klientske dokumenty samostatné namespaces per kancelária.
- **„If we want them to do Knowledge Work, we need to design Knowledge Agents“ (Benjamin Clavié, Mixedbread):** Agentov pre znalostnú prácu nemáme kopírovať z coding agentov. Treba ich navrhnúť podľa existujúcich workflowov, napr. **právneho clerkingu** (zber informácií a uvažovanie pre seniorného právnika podľa vlastných pravidiel). *Pre nás:* modelovať prácu koncipienta, teda rešerš → memo → zdroje → otvorené otázky, nie chat.
- **„Stop Chunking Like It's 2022“ (Yuval Belfer, Niv Granot, AI21):** Neexistuje jedna správna veľkosť chunku. Optimum sa medzi dotazmi líši až o 40 p. b. Riešenie je **indexovať vo viacerých veľkostiach a fúzovať cez Reciprocal Rank Fusion**, čo dáva +1–37 % recall bez pretrénovania. *Pre nás:* indexovať súčasne odsek, paragraf a celú časť zákona, pri rozhodnutí právnu vetu, odôvodnenie a celý dokument.
- **„The unreasonable effectiveness of BM25 for agentic search“ (Jo Kristian Bergum):** Agenti (GPT-5 trajektórie z BrowseComp-Plus) píšu dotazy, ktoré hrajú do karát BM25. Defaultné parametre a evaly lexikálny retrieval podhodnocujú. BM25 sa stáva „grepom“ agentového vyhľadávania. *Pre nás:* v práve sú presné reťazce (§ 2910 OZ, 21 Cdo 1234/2020, „bezdôvodné obohatenie“) kritické, BM25 s českou/slovenskou lematizáciou je preto základ.
- **„Your Agreements Are a Database You Can't Query“ (Hiral Shah, Sean Sodha, Docusign + NVIDIA):** Najcennejšie dáta v zmluvách (cenníky, SLA, sadzby) sú v tabuľkách, ktoré klasická extrakcia zničí. Docusign testoval **NVIDIA Nemotron Parse** na reálnych zmluvách (nie syntetických benchmarkoch) a servíruje ho cez **vLLM**. Napája ho na NeMo Retriever embeddingy a reranking.
- **„Building the Document Context Layer for AI Agents“ (Jerry Liu, LlamaIndex):** Približne 90 % firemného kontextu je v dokumentoch (PDF, Word, PPTX). Každý agentový produkt potrebuje „document context layer“: parsing, retrieval, workflowy, a ďalej verziovanie, editácia, oprávnenia a dlhobežiaci agenti.
- **„Citation Needed: Provenance for LLM-Built Knowledge Graphs“ (Daniel Chalef, Zep):**
  - Väzby episode → fact ako štrukturálne vlastnosti grafu.
  - Provenance, ktorá prežije entity resolution.
  - Metadata projection: zdroj sa otaguje raz a tag sa prenesie na všetky odvodené uzly.
  - Filtrovanie faktov podľa pôvodu.
  - GDPR výmaz, ktorý sa šíri po derivačných hranách.
- **„How Kepler Built Verifiable AI for Financial Services“ (Vinoo Ganesh, Kepler):** Claude na reasoning a k nemu **deterministická verifikačná infraštruktúra**. Systém indexuje 26M+ SEC filingov a každé číslo validuje až na konkrétny dokument, stranu a riadok. *Pre nás:* rovnaký princíp pre citácie, kde každá citácia sa deterministicky overí proti zdrojovému textu v danom znení.

---

## 2. Dátové zdroje CZ a SK

| Zdroj | Obsah | Prístup | Formát | Poznámky |
|---|---|---|---|---|
| **e-Sbírka** (CZ, MV ČR), e-sbirka.cz | Právne záväzná Sbírka zákonů a mezinárodních smluv, konsolidované znenia a ich verzie | Web zdarma. **Open data:** bulk súbory (opendata.eselpoint.cz, registrované v NKOD). **REST API:** len po registrácii a schválení cez dátovú schránku | JSON a JSON-LD, najväčší súbor ~1 GB komprimovaný / 27+ GB rozbalený | Kritika (Lupa.cz, 2024): chýba dokumentácia, súbory sa musia načítať celé do pamäte, blokovanie IP mimo EÚ. MV odporúčalo produkčné napojenie až po 15. 1. 2026, katalóg NKOD uvádza, že identifikátory fragmentov sa môžu meniť do 15. 1. **2027**. Licencia nie je výslovne uvedená. Predpisy sú úradné dielo bez autorskej ochrany (§ 3 zák. 121/2000 Sb.) (neoverené webom). |
| **e-Legislativa** (CZ) | Legislatívny proces (návrhy, pripomienky) | Spúšťa sa postupne spolu s e-Sbírkou | – | Užitočné na sledovanie pripravovaných zmien (neoverené detailne) |
| **Slov-Lex** (SK), slov-lex.sk | e-Zbierka (právne záväzná elektronická Zbierka zákonov SR), historické znenia, archív Zbierky od 1918 v ZIP | Web zdarma | HTML/PDF, ZIP archív | Verejne zdokumentované API ani bulk open data som **nenašiel** (neoverené, treba sa spýtať MS SR). Väzba N-Lex na SK databázu je podľa EÚ portálu nefunkčná. |
| **rozhodnuti.justice.cz** (CZ, MS ČR) | Anonymizované rozhodnutia okresných, krajských a vrchných súdov (od 2023), vyhľadávač zahŕňa aj NS, NSS a ÚS | **Verejné REST API** `https://rozhodnuti.justice.cz/api/opendata/{rok}/{mesiac}/{deň}`, stránkovanie 100 položiek | Strojovo čitateľný (formát na stránke neuvedený) | Licencia neuvedená. Anonymizáciu robí aplikácia MS (adresy, dátumy narodenia, IČO, účty). Nezverejňujú sa všetky rozhodnutia. |
| **NSS** (CZ) | Judikatúra NSS | Vyhľadávač na nssoud.cz | – | Open data/API som neoveril (neoverené) |
| **NS ČR** | Judikatúra NS | Vyhľadávač na nsoud.cz, časť aj cez rozhodnuti.justice.cz | – | Existuje komunitný „czech-legal-mcp“, ktorý cez open data MS sťahuje NS a NSS |
| **NALUS** (Ústavní soud) | Rozhodnutia ÚS | Fulltext a filtrovanie podľa predpisov | Web | ÚS výslovne odmieta vytvárať nové datasety na žiadosť (InfoZákon). API/bulk nenájdené, prakticky scraping (neoverené). |
| **SK súdy** (MS SR, obcan.justice.sk / Slov-Lex) | Povinné zverejňovanie podľa § 82a zák. 757/2004 Z. z. do 15 prac. dní od právoplatnosti, anonymizácia | Web s vyhľadávaním (dátum, súd, sp. zn., sudca, fulltext) | Všeobecné súdy HTML, NS SR PDF | Bulk/API **nenájdené**. Nezverejňujú sa neverejné konania. |
| **EUR-Lex / Cellar / Úradný vestník EÚ** | Právo EÚ a judikatúra SDEÚ v CS aj SK | SPARQL endpoint a REST nad Cellarom, data dump platných aktov (EU Login), SOAP webservice (registrácia) | Formex XML, HTML, PDF | Opätovné použitie bezplatné podľa rozhodnutia Komisie 2011/833/EÚ. Najlepšie zdokumentovaný zo všetkých zdrojov. |

**Čo chýba:**
1. **Komentáre a odborná literatúra** sú autorsky chránené a patria vydavateľom (Wolters Kluwer, C.H.Beck, Leges, Atlas). Bez licencie ich nemáme, a to je hlavná moat incumbentov.
2. **Neúplnosť judikatúry:** nižšie súdy pred 2023 (CZ) a nie všetky rozhodnutia sa zverejňujú. Pri SK chýba bulk prístup.
3. **Právne vety a anotácie** (Sbírka soudních rozhodnutí a stanovisek a pod.) sú čiastočne redakčné.
4. **Metadáta väzieb** rozhodnutie → aplikovaný § bude treba extrahovať samostatne. CZ e-Sbírka má väzby medzi predpismi, pre judikatúru ich nemá.

---

## 3. Konkurencia

### Globálni hráči

- **Legora** (SE): 1 500 kancelárií a in-house tímov (FT/Dealroom, 2026), rokovania o valuácii ≥ 10 mld. USD. **V CZ ju nasadila kancelária KŠB** (okt. 2025, „prvá veľká nezávislá CZ kancelária“). Cena sa stanovuje na ponuku, tretie strany uvádzajú ~3 000 USD/user/rok a minimum ~10 seats (neoverené oficiálne).
- **Harvey** (US): v roku 2026 zdvojnásobuje headcount v Európe. Odhady tretích strán sú 1 200–2 000+ USD/user/mesiac, s menším tierom ~399 USD (neoverené oficiálne). CZ/SK klienta som nenašiel (neoverené).
- **CoCounsel (Thomson Reuters), Lexis+ AI:** zamerané na US/UK obsah, CZ/SK pokrytie nenájdené. CoCounsel ~225–400 USD/user/mesiac podľa tretích strán (neoverené).
- **OpenAI „Astra for Law“** (sept. 2026): stránku sa nepodarilo načítať (403), podľa výsledkov vyhľadávania je zameraná na US judikatúru (neoverené).

Záver: globálni hráči sú drahí a CZ/SK obsah nemajú v jadre. Legora sa k nemu dostáva cez dokumenty klienta, nie cez kurátorovaný korpus.

### Lokálni hráči

| Hráč | Čo má | Cena |
|---|---|---|
| **Wolters Kluwer – ASPI, ASPI AI, Libra** (CZ aj SK) | ASPI AI (2025) odpovedá s odkazmi na predpisy, novšie aj s judikatúrou. **Libra** (WK kúpil Libra Technology GmbH) je AI pracovný priestor s obsahom ASPI, v CZ aj SK. Praetor AI (Word/Outlook add-in, anonymizér). | ASPI balíky „od 27 990 Kč“ (obdobie neuvedené), staršie verejné zmluvy uvádzajú ~33,6 tis. Kč/rok za 1 používateľa bez DPH (2016) a ~62,7 tis. Kč/rok za 5 používateľov (2018). Libra má 14-dňový trial. |
| **CODEXIS AI / AI Agent** (Atlas consulting, CZ) | Rešerše, práca s vlastnými dokumentmi, návrhy zmlúv, citácia § a judikátov, obsah zahŕňa komentáre, literatúru, vzory, sněmovní tisky, vyhlášky obcí a EÚ. Private cloud alebo on-prem. **Partnerstvo s ČAK:** noví advokáti dostávajú ročnú licenciu a 1M AI kreditov zdarma (8/2026). | Neuvedená |
| **C.H.Beck – Beck-online** | V DE Beck-Noxtua (11/2025), C.H.Beck získal väčšinu v Noxtua (Series C > 114 M€, 9/2026). CZ/SK AI verziu som nenašiel (neoverené). | – |
| **Lawrence AI** (CZ startup, UK Praha) | Agent „juniorov“ na rešerš, analýzu dokumentov a drafting | ~590 Kč/mesiac podľa staršieho newslettera, študenti 190 Kč (neoverené aktuálne) |
| **Advomate** (CZ, Brno) | Rešerš a revízia zmlúv, uvádza 300+ klientov (Škoda Auto, Skanska), seed > 6 mil. Kč (2024). Investícia od Google podľa titulku Forbes je neoverená. | – |
| **Roboprávník** (Brno, 2025) | Kontrola zmlúv, Word, chat s dokumentmi, CZ judikatúra a legislatíva | – |
| **Praktik.AI** (SK) | AI platforma pre advokátov, podľa tímu 100+ platiacich, 2 000+ registrovaných, ~10 k€ MRR (LinkedIn, neoverené) | – |
| **Legito** (CZ) | Automatizácia dokumentov a zmlúv (neoverené aktuálne AI funkcie) | – |
| **Judikaty.info** (SK) | Agregácia judikatúry z bezplatných zdrojov (NS SR, JASPI) | – |
| **EPI** (SK), **Lexforum** (SK) | Právne informačné systémy, AI funkcie som neoveril | – |

**Medzera:**
1. **Nezávislý, cross-border CZ+SK** produkt (SK trh je pre CZ hráčov sekundárny).
2. **Ostrá verifikácia citácií v čase**, teda či § platil v znení k dátumu skutku. Marketing incumbentov to tvrdí, ale nemerajú to verejne.
3. **Hlboké pokrytie nižších súdov** z rozhodnuti.justice.cz, ktoré redakčné databázy pokrývajú výberovo.
4. **Workflowy pre niky** (exekútori, notári, obce) a **on-prem** pre menšie kancelárie za dostupnú cenu.

Najväčšie riziko: ASPI a CODEXIS majú komentáre a distribúciu (CODEXIS cez ČAK).

---

## 4. Veľkosť trhu

- **Advokáti ČR:** 13 319 ku koncu 2025, plus 2 601 koncipientov (ČAK).
- **Advokáti SR:** 5 600+ advokátov a ~2 500 koncipientov (profil SAK, 2/2025). Staršie údaje uvádzajú 5 296–5 386, oficiálnu štatistiku 2026 som nenašiel.
- **Notári ČR:** 439 notárskych úradov (2023, numerus clausus), od 1. 1. 2026 o jeden menej. **Notári SR:** neoverené (rádovo stovky).
- **Exekútori:** CZ ~150–160 (neoverené, posledný overený údaj 114 je zo staršieho obdobia), SK neoverené.
- **Firemní právnici:** CZ/SK štatistika neexistuje. Odhad niekoľko tisíc (neoverené).
- **Verejná správa:** 6 000+ obcí v CZ a ~2 900 v SR (neoverené webom). Ministerstvá a úrady dnes kupujú ASPI/CODEXIS cez verejné zákazky.

**Ochota platiť:** Kancelárie dnes platia za ASPI/CODEXIS desiatky tisíc Kč ročne za kanceláriu. Benchmark je ~30–35 tis. Kč/rok za prvého používateľa (staršie zákazky). **Hrubý TAM (len advokáti CZ+SK):** ~19 000 advokátov + ~5 000 koncipientov. Pri 100 €/seat/mesiac (cieľ, neoverená ochota) to dáva ~29 M€ ročne. Realistický SAM pre startup (malé a stredné kancelárie, 10 % penetrácia) je ~2–3 M€ ARR. Na veľký biznis treba expanziu (PL, AT, HU) alebo upsell workflowov.

---

## 5. Ako to postaviť

### Architektúra

```
          ┌───────────── INGESTION (denne) ─────────────┐
 e-Sbírka JSON ─┐                                         │
 Slov-Lex HTML ─┤→ parser → normalizácia → verzie (valid_from/valid_to)
 rozhodnuti API ┤        ↓                       ↓
 NALUS/NSS/SK ──┤   segmentácia podľa § / odst. / písm.; rozhodnutia: hlavička,
 EUR-Lex Cellar ┘   výrok, odôvodnenie, právna veta  → extrakcia odkazov (regex+LLM)
                         ↓                       ↓
      ┌──────────────────┴──────┐   ┌────────────┴───────────┐
      │ Multi-granular index     │   │ Citačný graf (Postgres/ │
      │ BM25 (lematizácia CS/SK) │   │ Neo4j): predpis↔§↔novela│
      │ + dense (BGE-M3/Qwen3-E) │   │ ↔rozhodnutie↔ECLI       │
      │ zdieľaný verejný namespace│  └────────────┬───────────┘
      │ + per-tenant namespaces  │                │
      └──────────┬───────────────┘                │
                 ↓                                ↓
   AGENT (plánovač rešerše → nástroje: search_law(as_of), search_cases,
          get_section(id,date), follow_citations, read_client_doc)
                 ↓
   Reranker (cross-encoder multilingual) → RRF fúzia → kontext
                 ↓
   LLM generovanie s POVINNÝMI citáciami [doc_id#fragment@verzia]
                 ↓
   DETERMINISTICKÝ VERIFIKÁTOR: existuje fragment? platil k dátumu?
   citovaný text ⊂ zdroj (fuzzy match)? rozhodnutie nebolo zrušené?
                 ↓
   Odpoveď + zdroje + varovania („§ zmenený novelou č. X od …“)
```

### Kľúčové rozhodnutia

1. **Verzie v čase:** Každý fragment (§, odsek) dostane `valid_from`/`valid_to` a odkaz na novelu. Nástroj `search_law(query, as_of=date)` filtruje na znenie účinné k dátumu. e-Sbírka má verzie fragmentov priamo. Pri Slov-Lexe treba diffovať historické znenia (pracné).
2. **Chunking podľa štruktúry, nie tokenov:** paragraf ako primárna jednotka, plus odsek a celá hlava ako ďalšie granularity a RRF fúzia (AI21). Každý chunk nesie hierarchiu (zákon › časť › hlava › §) ako prefix.
3. **Hybrid search:** BM25 s lematizáciou je nutnosť, lebo čeština a slovenčina sú flektívne. Na lematizáciu MorphoDiTa/UDPipe (ÚFAL MFF UK), pri SK napr. stemmer alebo morfologický slovník (neoverené). Dense embeddingy: multilingválne BGE-M3, multilingual-e5-large alebo Qwen3-Embedding (CZ/SK výkon treba zmerať, neoverené). Seznam má malé české modely (15–20M parametrov, 256 dim, väčšinou max 128 tokenov, licencie CC-BY / CC-BY-NC), vhodné skôr na rýchly prvý stupeň. Reranker: bge-reranker-v2-m3 alebo Cohere Rerank multilingual (neoverené na CZ/SK).
4. **Citačný graf:** Regexy na „§ 123 odst. 2 zákona č. 89/2012 Sb.“, „sp. zn. 21 Cdo 1234/2020“ a ECLI, plus LLM fallback. Hrany nesú provenance podľa Zepu (z ktorého dokumentu a verzie väzba vznikla). Graf slúži na „ktoré rozhodnutia aplikujú § X“ a na varovanie pri zrušenom alebo prekonanom judikáte.
5. **Agentic search:** agent v štýle clerkingu (Clavié), ktorý naplánuje rešerš, iteruje dotazy (BM25 je pre agentov silný, Bergum), a vráti memo so zdrojmi a otvorenými otázkami.
6. **Verifikácia (Kepler pattern):** LLM smie citovať len ID fragmentov z kontextu. Verifikátor deterministicky skontroluje existenciu, platnosť k dátumu a zhodu citovaného textu. Neoverená citácia sa nezobrazí ako fakt.
7. **Izolácia klientskych dát (Legora pattern):** verejný korpus je jeden index, klientske dokumenty majú per-tenant namespace (turbopuffer, Qdrant alebo pgvector s RLS).

### Stack

- **Úložisko:** Postgres (metadáta, verzie, graf cez rekurzívne CTE), na začiatok bez Neo4j.
- **Vyhľadávanie:** OpenSearch alebo Tantivy na BM25, Qdrant alebo turbopuffer na vektory.
- **Parsing:** Docling alebo LlamaParse na klientske PDF. Na tabuľky v zmluvách otestovať Nemotron Parse cez vLLM.
- **LLM:** Claude (Sonnet/Opus) cez EU región (AWS Bedrock Frankfurt / GCP Vertex EU) na reasoning. **Lokálny režim** pre dôverné dáta: open-weight model (Qwen3, Mistral Small/Medium, Llama) na vLLM v CZ/SK DC alebo on-prem (kvalita v CZ/SK je neoverená a treba ju zmerať na eval sete).
- **Eval set:** 300–500 otázok od praktizujúcich advokátov (CZ a SK zvlášť) so zlatými odpoveďami a zlatými citáciami. Metriky:
  - recall@10 retrievalu,
  - citation precision (každá citácia existuje a podporuje tvrdenie),
  - temporal accuracy (správne znenie k dátumu),
  - podiel odpovedí „neviem“, ktoré sú správne.

  Spúšťať pri každej zmene a mesačne revidovať s 2–3 advokátmi.

### Čo je ťažké

- Temporálna konsolidácia SK predpisov bez API.
- Kvalita anonymizácie a OCR v rozhodnutiach.
- Prepojenie rozhodnutí na správne znenie § (súd aplikoval znenie účinné k dátumu skutku).
- Chýbajúce komentáre, keďže advokáti ich považujú za kľúčové.
- Morfológia CZ/SK pri BM25 a nedostatok kvalitných CZ/SK rerankerov.
- Zabrániť, aby model „vedel“ právo z pretrénovania a citoval mimo kontextu.

---

## 6. Regulácia a etika

- **ČAK:** Platí stanovisko z roku 2023. Nové stanovisko a **AI stratégia ČAK** sú v príprave (štruktúra schválená, predloženie predstavenstvu 9/2026). Ide aj o minimálne IT štandardy pre advokátov **a vývojárov legal tech**, povinné AI vzdelávanie a 10 odporúčaní (Maisner, 2024).
  - ČAK výslovne odmieta marketing „AI právnik“. Názov a komunikácia preto nesmú tvrdiť, že nahrádzajú advokáta.
  - Advokát zodpovedá za výstup (§ 24 ZoA) a musí zachovať mlčanlivosť (§ 21 ZoA).
- **SAK:** Záväzné pravidlá k AI z marca 2025, doplnené v novembri 2025 o ochranu mlčanlivosti a dát klientov, plus metodické usmernenie s minimálnymi požiadavkami. Text usmernenia (súhlas klienta, umiestnenie serverov) som neoveril a treba ho prečítať pred MVP.
- **GDPR:** Rozhodnutia sú anonymizované, ale nie dokonale, preto treba vlastnú detekciu PII a proces výmazu. Klientske dokumenty spracúvame ako **sprostredkovateľ** (DPA), s EU hostingom a zero-retention u LLM providera. Výmaz má propagovať aj do odvodených dát (embeddingy, graf), čo je Zep pattern.
- **AI Act (nariadenie 2024/1689):** Annex III bod 8(a) pokrýva systémy určené na pomoc **justičným orgánom** (alebo ADR) pri skúmaní a výklade faktov a práva. Príklady Komisie sa týkajú sudcov (drafting rozhodnutí, vyhľadávanie podobných prípadov).
  - **Nástroj pre advokátov podľa textu do bodu 8 nespadá.** Ide skôr o general-purpose použitie s povinnosťami transparentnosti (čl. 50) a AI gramotnosti (čl. 4).
  - **Pozor:** predaj súdom alebo verejnej správe na rozhodovanie môže produkt dostať do high-risk režimu. Výnimka čl. 6 ods. 3 platí pre úzke procedurálne a prípravné úlohy.
  - Termíny pre high-risk povinnosti mohli posunúť návrhy „digital omnibus“ (neoverené).
  - Odporúčanie: verejnú správu a súdy v MVP vynechať.
- **Zodpovednosť:** V zmluve treba jasne uviesť, že ide o nástroj na podporu, výstup overuje advokát, a dohodnúť obmedzenie náhrady škody. UX má vynútiť kontrolu zdrojov (klikateľné citácie, varovania pri neistote) a auditný log.

---

## 7. MVP za 6–8 týždňov

**Scope:** **ČR, občianske a obchodné právo** (OZ 89/2012 Sb., ZOK 90/2012 Sb., OSŘ, ZP), rozhodnutia NS a NSS, plus nižšie súdy z rozhodnuti.justice.cz od 2023. Dôvod: CZ má najlepšie dáta (e-Sbírka verzie a API rozhodnutí) a 2,5× väčší trh. SK pridať ako druhý krok.

| Týždeň | Výstup |
|---|---|
| 1–2 | Ingestion e-Sbírky (verzie fragmentov) a rozhodnuti.justice.cz API, parser §, regex citácií, eval set v1 (100 otázok s 3 advokátmi) |
| 3–4 | Hybrid search (BM25 + dense + reranker, multi-granular RRF), `as_of` filter, citačný graf v Postgres |
| 5–6 | Agent rešerše a memo s citáciami, deterministický verifikátor, UI s panelom zdrojov, upload zmluvy a checklist rizík (len NDA, nájom, SPA lite) |
| 7–8 | Pilot u 5–10 kancelárií, meranie (čas rešerše, citation precision), eval v2, DPA a bezpečnostná dokumentácia |

**Ako získať prvých 10 kancelárií:**
1. Vlastná sieť: 3–5 malých a stredných kancelárií (2–20 advokátov) ako design partneri zadarmo na 3 mesiace výmenou za eval otázky a týždenný feedback.
2. Koncipienti ako šampióni, keďže sú hlavnými používateľmi (podľa ČAK). Treba ich osloviť cez sekcie ČAK a akcie, napr. Future Legal (UP Olomouc), Advokátní deník a epravo semináre.
3. Verejne publikovaný benchmark „citation accuracy CZ legal AI“ (náš eval vs. ChatGPT / ASPI AI / CODEXIS AI) ako obsahový marketing. Pozor na podmienky použitia konkurenčných produktov.
4. LinkedIn demá na konkrétnych prípadoch (napr. „zmena § k dátumu skutku“).

---

## 8. Biznis model a cenotvorba

- **Per seat SaaS:**
  - *Solo:* 49–79 €/mesiac (cieľ pod cenou ASPI, aby sa dal kúpiť popri ňom).
  - *Kancelária:* 89–129 €/seat/mesiac.
  - *Enterprise / on-prem:* ročná licencia od ~15–30 k€ plus implementácia.

  Ceny sú hypotézy na validáciu v pilote.
- **Usage add-ony:** hromadná revízia zmlúv (due diligence) za kredity, podobne ako Legora agentic tier.
- **Kanály:**
  - priamy predaj malým a stredným kanceláriám,
  - partnerstvá so softvérom pre správu kancelárie (napr. Singularity, Advokátní software, neoverené),
  - komory (vzdelávanie, CODEXIS už má s ČAK program pre nových advokátov),
  - in-house tímy veľkých firiem (Advomate ukazuje dopyt: Škoda, Skanska),
  - neskôr reselling cez vydavateľa alebo licencia obsahu (komentáre) výmenou za distribúciu.
- **Moat:** kvalita citácií a temporálna presnosť, eval dáta od praktikov, CZ+SK pokrytie, on-prem.

---

## 9. Riziká a otvorené otázky

1. **Incumbenti s obsahom a distribúciou** (WK ASPI/Libra, CODEXIS + ČAK, Beck-Noxtua). Riziko „good enough“ bundlu je vysoké.
2. **Globálni hráči:** Legora už v CZ je a Harvey expanduje v EÚ. Pri veľkých kanceláriách sa nedá súťažiť.
3. **Dáta:** e-Sbírka mení identifikátory fragmentov (do 2027?), SK nemá API, licencie open dát nie sú výslovné, hrozí blokovanie scrapingu.
4. **Komentáre** bez licencie znamenajú nižšiu vnímanú hodnotu u seniorných advokátov.
5. **Halucinácie:** jedna zlá citácia v podaní môže zničiť reputáciu na malom trhu.
6. **Regulácia:** nové stanovisko ČAK a IT štandardy pre vývojárov môžu priniesť nové požiadavky. Ak by sme išli do justície, hrozí high-risk.
7. **Malý trh:** CZ+SK samo nestačí na venture škálu, treba expanzný plán (PL, HU, AT, RO).
8. **Otvorené:**
   - Za čo presne kancelárie zaplatia navyše k ASPI/CODEXIS?
   - Akú kvalitu dosahujú lokálne open modely v CZ/SK práve?
   - Je možná licencia komentárov od menšieho vydavateľa (Leges, Wolters SK)?

---

## 10. Odporúčanie a ďalšie kroky

**Odporúčanie: Ísť do toho podmienečne.** Cieliť na malé a stredné CZ kancelárie a in-house s produktom „rešerš a memo s overenými citáciami k dátumu“ a revíziou zmlúv. Diferencovať sa merateľnou presnosťou citácií, pokrytím nižších súdov, CZ+SK a on-prem. Nesúťažiť šírkou obsahu s ASPI/CODEXIS. Go/no-go po pilote: ≥5 z 10 kancelárií ochotných platiť ≥ 79 €/seat.

**5 konkrétnych krokov (najbližšie 2 týždne):**
1. **Dáta:**
   - stiahnuť e-Sbírka open data a podať žiadosť o REST API cez dátovú schránku,
   - spustiť crawler rozhodnuti.justice.cz API,
   - písomne sa spýtať MS SR a Slov-Lexu na bulk a API a podmienky použitia.
2. **Eval set:** s 3 advokátmi (CZ) napísať 100 rešeršných otázok so zlatými citáciami a zmerať ChatGPT, ASPI AI (trial), Libra (14-dňový trial) a CODEXIS AI. Výsledok poslúži ako baseline aj ako marketing.
3. **Regulácia:** získať a preštudovať text metodického usmernenia SAK k AI, stanovisko ČAK 2023 a pripravované IT štandardy. Konzultovať s advokátom zmluvné podmienky a DPA.
4. **Discovery:** 15 rozhovorov (10 advokátov z malých a stredných kancelárií, 3 in-house, 2 notári) o tom, čo dnes platia, čo im chýba a koľko by zaplatili.
5. **Technický spike (1 týždeň):** prototyp `search_law(as_of)` nad OZ a ZOK s BM25 (lematizácia) + BGE-M3 + rerankerom a deterministickým verifikátorom citácií, meraný na eval sete.

---

## 11. Zdroje

**Konferencia:** `conference/sessions.json` (AI Engineer World's Fair 2026): talky Legora/turbopuffer, Mixedbread, AI21, Bergum, Docusign/NVIDIA, LlamaIndex, Zep, Kepler.

**Dáta CZ/SK/EÚ**
- [Lupa.cz – e-Sbírka ukazuje, jak neotevírat data](https://www.lupa.cz/clanky/e-sbirka-ukazuje-jak-neotevirat-data/)
- [MV ČR – Omezení e-Sbírky / e-Legislativa](https://mv.gov.cz/bsmv/clanek/omezeni-e-sbirky-spojene-s-postupnym-spoustenim-e-legislativy-do-ostreho-provozu.aspx)
- [MV ČR – spuštění e-Sbírky](https://mv.gov.cz/bsmv/clanek/ministerstvo-vnitra-spustilo-elektronickou-sbirku-zakonu-a-mezinarodnich-smluv.aspx)
- [Portál veřejné správy – e-Sbírka](https://portal.gov.cz/sluzby-vs/esbirka-S66167)
- [NKOD – katalog datových sad](https://data.gov.cz/datasets?page=215)
- [Dostupný advokát – e-Sbírka](https://dostupnyadvokat.cz/blog/e-sbirka)
- [rozhodnuti.justice.cz](https://rozhodnuti.justice.cz/)
- [rozhodnuti.justice.cz – Open data](https://rozhodnuti.justice.cz/opendata/)
- [Právní prostor – aplikace pro anonymizaci rozhodnutí](https://www.pravniprostor.cz/aktuality/soudy-ziskaly-novou-aplikaci-pro-anonymizovani-svych-rozhodnuti)
- [justice.cz – info o vyhlášce 403/2022 Sb.](https://justice.cz/documents/40329/1262031/30+Si+4_2023/27654882-cb4b-4dd3-8e5c-ca886e2a1acb)
- [czech-legal-mcp (Smithery)](https://smithery.ai/server/janmacher02-xl8y/czech-legal-mcp)
- [Ústavní soud – odpověď k NALUS](https://www.usoud.cz/fileadmin/user_upload/SPR._US_271-25_INF_.pdf)
- [N-Lex – Slov-Lex](https://n-lex.europa.eu/n-lex/legis_sk/jaspi.predpisy_form?lang=sk)
- [N-Lex – informácie o národnej databáze](https://n-lex.europa.eu/n-lex/info/info-sk/index?lang=sk)
- [e-Justice – národná judikatúra SK](https://e-justice.europa.eu/topics/legislation-and-case-law/national-case-law/sk_sk)
- [Najprávo – Súdne rozhodnutia prístupné verejnosti](https://www.najpravo.sk/clanky/sudne-rozhodnutia-pristupne-verejnosti.html)
- [Judikaty.info – pomocník](https://www.judikaty.info/judikatura-rozsudok-judikat)
- [EUR-Lex – opätovné použitie obsahu](https://eur-lex.europa.eu/content/help/data-reuse/reuse-contents-eurlex-details.html)
- [EUR-Lex – webservice](https://eur-lex.europa.eu/content/help/data-reuse/webservice.html?locale=sk)
- [Rozhodnutie Komisie 2011/833/EÚ](https://eur-lex.europa.eu/eli/dec/2011/833/oj)

**Konkurencia**
- [KŠB nasazuje Legoru](https://www.ksb.cz/en/clanky/ksb-jako-prvni-velka-nezavisla-advokatni-kancelar-na-ceskem-trhu-prinasi-do-sve-praxe-ai-platformu-legora-jako-symbolicke-spojeni-ceskeho-prava-a-svetove-umele-inteligence)
- [Dealroom – Legora valuation talks](https://dealroom.co/news/144827-legora-reportedly-in-talks-to-raise-at-a-10b-valuation/)
- [Realtid – Harvey v Európe](https://www.realtid.se/juridik/svenska-legora-utmanas-av-amerikanska-jatten-pa-hemmaplan/)
- [Vaquill – Harvey/Legora/CoCounsel pricing](https://www.vaquill.ai/blog/harvey-legora-cocounsel-pricing-reality)
- [Vaquill – Harvey price per seat 2026](https://www.vaquill.ai/blog/harvey-ai-price-increase-per-seat-2026)
- [Bind – Legora pricing 2026](https://bindlegal.com/resources/comparisons/legora-pricing-2026/)
- [OpenAI – Astra for Law](https://openai.com/cs-CZ/index/astra-for-law/)
- [epravo – ASPI AI asistent](https://www.epravo.cz/top/aktualne/vyuzijte-noveho-ai-asistenta-pro-pravni-reserse-119439.html)
- [epravo – Libra na českom trhu](https://www.epravo.cz/top/aktualne/wolters-kluwer-uvadi-na-cesky-trh-ai-pravni-pracovni-prostor-libra-s-integrovanym-obsahem-aspi-120997.html?pdf=1)
- [epravo.sk – AI nástroje pre právne profesie v SK a CZ](https://www.epravo.sk/top/aktualne/oblubene-ai-nastroje-pre-pravne-profesie-dostupne-na-slovensku-a-v-cesku-6481.html)
- [Wolters Kluwer – ASPI predplatné](https://www.wolterskluwer.com/cs-cz/solutions/aspi/predplatne)
- [MPSV – cenová príloha ASPI](https://admin-miniweby.mpsv.cz/documents/35829/66899/d__priloha.pdf/fd735d58-f219-8111-7854-a1e4c608a62e)
- [MENDELU – zmluva ASPI](https://zakazky.mendelu.cz/document_18654/19375bfcbda09edc9-smlouva-o-poskytnuti-uzivacich-prav-ke-sluzbe-aspi-pdf)
- [Právní prostor – CODEXIS AI](https://pravniprostor.cz/clanky/pravo-it/codexis-ai-prvni-pravni-ai-nad-overenymi-relevantnimi-zdroji-v-CR)
- [Právní prostor – CODEXIS AI Agent a zodpovedná práca](https://pravniprostor.cz/clanky/pravo-it/od-odpovedi-k-odpovedne-pravni-praci-proc-se-v-ceske-advokacii-meni-standard-vyuziti-ai)
- [Advokátní deník – CODEXIS AI zdarma pre nových advokátov](https://advokatnidenik.cz/2026/08/18/zacinajici-advokati-ziskaji-zdarma-pristup-ke-codexis-ai-a-onepost/)
- [Beck-Noxtua launch](https://www.noxtua.com/news/press-releases/launch-beck-noxtua)
- [C.H.Beck – väčšinový podiel v Noxtua](https://www.leadersleague.com/en/news/germany-c-h-beck-takes-majority-stake-in-noxtua-in-eur114m-plus-series-c)
- [Lawrence AI – advokatnidenik](https://advokatnidenik.cz/2025/04/02/lawrence-predstavuje-prulomoveho-ai-asistenta-pro-pravni-profesionaly/)
- [Lawrence AI newsletter](https://lawrenceai.substack.com/p/51-promptu-ktere-vas-presvedci-lawrence)
- [Forbes.cz – Advomate](https://forbes.cz/pravnik-do-kapsy-cesky-ai-startup-ziskal-investici-od-googlu-a-miri-do-zahranici/)
- [CC.cz – Advomate](https://cc.cz/partak-pro-pravo-cesky-startup-vyuziva-skoda-auto-ci-skanska-nyni-nabira-novou-investici/)
- [Stanford CodeX – Roboprávník](https://techindex.law.stanford.edu/companies/robopr-vn-k)
- [LinkedIn – Praktik.AI (Fast Forward)](https://sk.linkedin.com/in/zuzana-hackenberg-89236970)
- [Future Legal 2026](https://www.businessinfo.cz/akce/future-legal-2/)
- [UK – RAG nad judikatúrou NS ČR (diplomová práca)](https://dspace.cuni.cz/handle/20.500.11956/203298)

**Trh a regulácia**
- [Advokátní deník – štatistiky ČAK 2025](https://advokatnidenik.cz/2026/08/20/statistiky-cak-pocty-advokatnich-koncipientu-rostou-ale-jenom-v-praze/)
- [DevelopmentAid – SAK profil](https://www.developmentaid.org/donors/view/442066/slovak-bar-association-slovenska-advokatska-komora)
- [Právne noviny – SAK 415 sťažností](https://pravnenoviny.sk/advokatska-komora-presetrila-vlani-415-staznosti-na-svojich-advokatov/)
- [Právní prostor – Notári (Foukal a Neubauer)](https://pravniprostor.cz/clanky/ostatni-pravo/foukal-a-neubauer-notar-ma-byt-charakterni-clovek)
- [MSp – zrušenie notárskeho úradu Trutnov](https://msp.gov.cz/documents/d/msp/rozhodnuti-o-zruseni-notarskeho-uradu-pdf)
- [Právní prostor – Strategie ČAK pro AI](https://pravniprostor.cz/clanky/ostatni-pravo/strategie-ceske-advokatni-komory-pro-umelou-inteligenci)
- [Advokátní deník – Flash news ČAK 6/2023](https://advokatnidenik.cz/2023/06/21/flash-news-z-jednani-predstavenstva-cak-cerven-2023/)
- [Advokátní deník – ČAK a zahraničné komory (10 odporúčaní)](https://advokatnidenik.cz/2024/05/23/v-kankove-palaci-se-sesli-zastupci-cak-a-zahranicnich-advokatnich-komor/)
- [Najprávo – SAK metodické usmernenie k AI](https://www.najpravo.sk/kratke-spravy/sak-na-svojom-webe-zverejnila-metodicke-usmernenie-k-pouzivaniu-ai-v-advokatskej-praxi.html?print=1)
- [TASR – justícia a AI](https://www.teraz.sk/slovensko/predstavitelia-justicie-sa-zhodli-ze/858032-clanok.html)
- [AI Act Service Desk – Annex III bod 8](https://ai-act-service-desk.ec.europa.eu/fr/node/468)
- [Bundesnetzagentur – High-risk AI systems](https://www.bundesnetzagentur.de/EN/Areas/Digitalisation/AI/09_HighRisk/start.html)
- [CCBE – odpoveď ku konzultácii high-risk](https://www.ccbe.eu/fileadmin/speciality_distribution/public/documents/IT_LAW/ITL_Position_papers/EN_ITL_20250920_CCBE-response-to-the-targeted-stakeholder-consultation-on-the-implementation-of-the-AI-Act-s-rules-for-high-risk-AI-systems_1.pdf)

**Technika**
- [Seznam – Czech semantic embedding models (GitHub)](https://github.com/seznam/czech-semantic-embedding-models)
- [Some Like It Small (arXiv)](https://arxiv.org/pdf/2311.13921)
- [DaReCzech / Small-E-Czech (arXiv)](https://arxiv.org/pdf/2112.01810)
