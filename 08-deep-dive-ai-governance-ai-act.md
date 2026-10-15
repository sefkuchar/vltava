# Deep dive 08: Riadenie AI a AI Act compliance pre CZ/SK firmy

*Stav k 15. 10. 2026. Právne termíny sú overené webovým vyhľadávaním (zdroje na konci). Čo overené nie je, má značku „(neoverené)“.*

---

## 1. Čo to je a prečo práve teraz

**AI governance** je súbor procesov a technických kontrol, ktorými firma vie povedať: *aké AI systémy a agentov používame (aj tie neschválené, teda „shadow AI“), kto a s akými právami ich používa, k akým dátam a nástrojom (MCP servery, skills) majú prístup, čo urobili (audit log), kde musí rozhodnúť človek (HITL) a do akej rizikovej kategórie AI Act spadajú.* Okrem toho firma potrebuje dokumentáciu a dôkaz o AI literacy školeniach.

**Prečo teraz:**
- Firmy prechádzajú od chatu k **agentom, ktorí vykonávajú akcie** (Claude Code, Copilot, Cursor, MCP servery). Riziko sa tým presúva z „čo model napíše“ na „čo agent urobí“.
- AI Act už platí: zákazy a čl. 4 (AI literacy) od 2. 2. 2025, GPAI od 2. 8. 2025, transparentnosť podľa čl. 50 od 2. 8. 2026. NIS2 v CZ aj SK už platí a núti firmy riadiť riziká dodávateľov vrátane AI SaaS.
- Digital Omnibus posunul high-risk povinnosti na 12/2027. Firmy tak majú **okno na prípravu**, no dopyt bude skôr „pokojný a plánovaný“ než panický.

**Čo zaznelo na AI Engineer World's Fair 2026 (SF):**
- **„Who Approved That MCP Server? Governing the Tool Layer“ (Jim Clark, Docker):** vývojári inštalujú MCP servery rýchlejšie, než ich security stihne skontrolovať, a každý neskontrolovaný server je priama cesta k dátam. Riešením je organizačný katalóg schválených a podpísaných serverov s pravidlom *default-deny* pre všetko ostatné. Politiku vynucuje ten istý engine, ktorý riadi sieť a filesystem.
- **„It's 10pm. Do You Know Where Your Agents Are?“ (Kim Maida, Keycard):** agenti majú dlhožijúce API kľúče a sú preprivilegovaní aj vtedy, keď nič nerobia. Riešením je „správny prístup v správnom čase“, teda krátkodobé tokeny viazané na konkrétnu úlohu, a to pre CLI agentov, MCP servery aj volania API tretích strán.
- **„Governance Is the Real Bottleneck to AI ROI“ (David Hsu, Retool):** limitujúcim faktorom nie je kvalita modelu, ale governance: viditeľnosť, guardrails, schvaľovanie a možnosť rollbacku.
- **„We Vetted 2,000 AI Skills Before They Reached Developers“ (Lucas Palma, Nubank):** skills a pluginy patria do software supply chain. Nubank automaticky reviewuje nebezpečné inštrukcie, deštruktívne príkazy, únik citlivých dát, prácu s credentials, externé volania a postupný drift správania agenta. Review beží lokálne aj v CI a pred interným marketplace. Prednášajúci otvorene priznal, že časť kontrol generovala len šum.
- **„IT Admin for the AI Workforce“ (Sarthak Aggarwal, Decawork):** firmy budú mať dve pracovné sily, ľudskú a AI. Agenti potrebujú rovnaké IT procesy ako ľudia: životný cyklus identity, access governance, riešenie incidentov a audit. Decawork stavia architektúru, v ktorej agent, ktorý rozmýšľa, nemôže konať, a agent, ktorý koná, nemôže improvizovať.
- **„Give the Agent a Budget, Not a Token“ (Sachin Malhotra, Anthropic):** namiesto RBAC navrhuje štyri primitíva:
  - asymetrické slovesá (agent smie `quarantine`, ale nie `delete`),
  - regenerujúce sa rozpočty deštruktívnych akcií,
  - „undo test“: čo agent nevie vrátiť, nesmie urobiť bez druhého kľúča,
  - tripwires namiesto allow-listov.

  Celé to pokryje približne 200 riadkov policy vrstvy a zostáva asi 95 % autonómie s pevným stropom na rozsah škôd.
- **„Auth for Agents“ (Michael Grinich, WorkOS):** otvorený protokol `auth.md` pre registráciu a autentifikáciu agentov bez formulárov. Adoptujú ho Cloudflare, Firecrawl a monday.com.
- **„Trust, But Verify: Human-in-the-Loop“ (Michael Liendo, Auth0):** HITL je spektrum od inline potvrdenia cez out-of-band schválenie až po agenta s vlastnou peňaženkou. Vzor sa volí podľa závažnosti dôsledkov a s vedomím kompromisov v latencii a UX.
- **„The Lethal Trifecta Is Already on Your Developers' Laptops“ (Michael Patterson, Coder):** prístup k privátnym dátam, nedôveryhodný obsah a možnosť komunikovať von spolu dávajú exfiltráciu, na ktorú neexistuje oprava na úrovni promptu. Navrhuje štyri kroky: riadený compute, centralizované credentials, *default-deny egress* a audit viazaný na identitu.
- **„An AI Future Without the Lock-In“ (Remy Guercio, Tailscale Aperture):** namiesto výberu jedného „walled garden“ odporúča vybudovať vlastnú spojovaciu vrstvu, teda identity-aware AI gateway nezávislú od dodávateľa modelov.
- **„Operate agents safely at scale with enterprise governance“ (Ashu Joshi, Microsoft):** identita, compliance a životný cyklus agentov v enterprise. Ide o pozicionovanie Agent 365 a Entra Agent ID.
- **„Guardians of the State: Air-Gapped AI Fortress“ (Rachna Srivastava):** air-gapped open-weight modely a dvojfázová sanitizácia PII (deterministické pravidlá plus lokálny LLM). K tomu validácia, že PII neuniká do kontextu modelu ani do logov.
- **„AI agents don't read your policy docs. They hit your APIs.“:** skutočná politika je to, čo sa stane v milisekunde volania. Gateway preto potrebuje identitu pre každého agenta, krátkodobé credentials, odstraňovanie PII a tajomstiev z promptov, rate limity podľa tokenov a sémantickú cache. Heslo talku: *„Policy states intent. Infrastructure enforces it.“*
- **Dopĺňa sa s:** „Dual-Surface Architecture“ (Carlyle: jeden governovaný MCP/API server, fázový prechod od čítania k zápisom) a „We Gave an Agent Production Code Access…“ (scoped permissions, approval gates, audit trail).

**Pointa pre nás:** svetová špička už nerieši, či governance potrebujeme, ale *runtime vynucovanie* (gateway, identita, rozpočty). Tým sa líši od papierového compliance, ktoré dnes v CZ/SK predáva Big4.

---

## 2. AI Act: stav k októbru 2026

### Časová os (po Digital Omnibus)

| Termín | Čo platí | Stav |
|---|---|---|
| 1. 8. 2024 | Nariadenie (EÚ) 2024/1689 nadobudlo účinnosť | overené |
| **2. 2. 2025** | Zákazy (čl. 5) + **AI literacy (čl. 4)** | platí |
| **2. 8. 2025** | GPAI modely, governance, sankčné ustanovenia | platí |
| **2. 8. 2026** | Transparentnosť čl. 50 (informovať, že ide o AI, deepfakes) | platí |
| 2. 12. 2026 | Čl. 50(2) strojovo čitateľné označovanie generovaného obsahu pre systémy uvedené na trh pred 2. 8. 2026; nové zákazy („nudifiers“, CSAM) | podľa Omnibusu |
| 2. 8. 2027 | Termín pre členské štáty na zriadenie regulačných sandboxov (posunutý o rok) | podľa Omnibusu |
| **2. 12. 2027** | **High-risk Annex III** (HR/nábor, credit scoring, vzdelávanie, kritická infraštruktúra…), pôvodne 2. 8. 2026 | podľa Omnibusu |
| 2. 8. 2028 | High-risk Annex I (AI v regulovaných produktoch, napr. zdravotnícke pomôcky) | podľa Omnibusu |
| 2. 8. 2030 | AI systémy pre orgány verejnej moci (legacy) | podľa Omnibusu |

**Digital Omnibus on AI:** Komisia ho navrhla 19. 11. 2025. Pôvodný návrh viazal posun na dostupnosť noriem, výsledná dohoda stanovila **pevné dátumy**.
- 7. 5. 2026: politická dohoda.
- 16. 6. 2026: schválenie v EP.
- 29. 6. 2026: finálne prijatie v Rade.
- Publikácia ako **nariadenie (EÚ) 2026/1744**. Do platnosti vstúpilo 27. 7. 2026. Dátum uvádzajú viaceré sekundárne zdroje, priamo v Úradnom vestníku som ho neoveril.

Ďalšie zmeny:
- **Čl. 4 bol zmäkčený, nie zrušený.** Povinnosť „zabezpečiť dostatočnú úroveň“ AI gramotnosti sa zmenila na povinnosť „prijať opatrenia podporujúce“ AI gramotnosť. Konkrétna úroveň u jednotlivca sa už negarantuje.
- **Úľavy pre „small mid-caps“** (menej ako 750 zamestnancov, obrat do 150 mil. €).
- **Posilnené právomoci AI Office** voči GPAI.

### Pokuty (čl. 99 AI Act, Omnibus výšky nemenil)

- **Zakázané praktiky:** do 35 mil. € alebo 7 % celosvetového obratu.
- **Ostatné povinnosti operátorov** (provider, deployer, čl. 50): do 15 mil. € alebo 3 %.
- **Nepravdivé informácie orgánom:** do 7,5 mil. € alebo 1 %.
- **MSP:** platí nižšia z oboch hodnôt.
- **Čl. 4 (literacy)** nie je v čl. 99 uvedený samostatne. Sankcie za neho závisia od národných zákonov (neoverené, ako to riešia CZ/SK zákony).

### Provider vs. deployer: čo musí bežná firma

- **Provider** vyvíja AI systém a uvádza ho na trh pod svojím menom (OpenAI, Microsoft, ale aj firma, ktorá si postaví vlastný HR scoring).
- **Deployer** AI systém používa v rámci svojej činnosti. Typická CZ/SK firma, ktorá používa ChatGPT Enterprise, Microsoft Copilot alebo agentov, je **deployer**.

**Povinnosti deployera už dnes:**
1. **AI literacy (čl. 4):** zdokumentované opatrenia, teda školenia podľa rolí.
2. **Kontrola zákazov (čl. 5):** napr. žiadne rozpoznávanie emócií na pracovisku.
3. **Transparentnosť (čl. 50):** chatbot musí oznámiť, že je AI, a deepfakes treba označiť.

**Od 12/2027, ak firma používa high-risk systém** (napr. AI na triedenie životopisov alebo credit scoring), čl. 26 vyžaduje:
- používať systém podľa návodu,
- zabezpečiť ľudský dohľad,
- monitorovať systém,
- uchovávať logy minimálne 6 mesiacov,
- informovať zamestnancov.

Banky a verejná správa navyše robia **FRIA** (posúdenie vplyvu na základné práva).

**Pozor na prechod z deployera na providera:** ak firma substantívne upraví systém alebo ho nasadí na high-risk účel, stáva sa providerom (čl. 25).

**Praktický záver:** bežná firma nepotrebuje 200-stranovú dokumentáciu. Potrebuje **inventár AI, klasifikáciu rizika, AI politiku, školenia a logy**. Na všetko z toho sa dá postaviť produkt.

### Národné orgány a implementačné zákony

- **CZ:** MPO pripravilo adaptačný zákon (10 strán, 26 paragrafov) a koncom roka 2025 ho predložilo vláde.
  - **ČTÚ:** hlavný orgán dozoru nad trhom a jednotné kontaktné miesto.
  - **ČNB:** finančný sektor.
  - **ÚOOÚ:** biometria a osobné údaje.
  - **ÚNMZ:** notifikujúci orgán.
  - **Stav v Snemovni:** schválenie som k 10/2026 nenašiel (neoverené, overiť na psp.cz).
- **SK:** vládny návrh zákona o umelej inteligencii (LP/2026/17, tlač 1447) určuje **MIRRI** ako všeobecný orgán dozoru nad trhom a jednotné kontaktné miesto. MIRRI bude prevádzkovať aj sandbox.
  - **Ďalšie orgány:** NBÚ, ÚOOÚ SR, Inšpekcia práce a MS SR.
  - **Stav:** v septembri 2026 NR SR posunula návrh do 2. čítania. Navrhovaná účinnosť je **1. 1. 2027**. Finálne schválenie je neoverené.

### Prepojenie s ďalšími reguláciami

- **NIS2, CZ:** zákon č. **264/2025 Sb.** o kybernetickej bezpečnosti platí od **1. 11. 2025**. NÚKIB eviduje 5 768 subjektov (1 516 vo vyšších povinnostiach). Riadenie rizík dodávateľov a aktív sa týka aj AI SaaS a agentov.
- **NIS2, SK:** novela zákona **69/2018 Z. z.** (zákon 366/2024 Z. z.) platí od **1. 1. 2025**. Vyhlášky NBÚ 226/2025 a 227/2025 platia od 1. 9. 2025.
- **DORA** (od 17. 1. 2025): banky, poisťovne a investičné firmy. Riadenie ICT rizík a register ICT dodávateľov, kam patria aj LLM API. Banky v CZ/SK teda už *musia* evidovať AI dodávateľov.
- **GDPR:** DPIA pri spracúvaní osobných údajov v AI, právny základ pri prenose údajov do USA a čl. 22 (automatizované rozhodovanie). Omnibus doplnil právny základ pre detekciu biasu.

**Predajný argument:** jeden AI inventár a jeden audit log pokryjú AI Act, NIS2 (aktíva a dodávatelia), DORA (ICT register) aj GDPR (záznamy o spracovaní).

---

## 3. Trh CZ/SK

**Kto to musí riešiť (podľa naliehavosti):**
1. **Banky a poisťovne:** DORA a ČNB/NBS už platia, credit scoring je high-risk podľa Annex III. Majú rozpočty, ale často siahajú po Big4.
2. **Energetika, utility, telco, doprava:** NIS2 (vyššie povinnosti), AI v kritickej infraštruktúre.
3. **Zdravotníctvo:** AI v zdravotníckych pomôckach (Annex I, 2028), GDPR citlivé dáta. Typicky chcú on-prem riešenie.
4. **Verejná správa:** FRIA, MIRRI/DIA (neoverené), citlivosť na suverenitu dát. On-prem/air-gapped je výhoda.
5. **Firmy s 250 a viac zamestnancami:** HR AI (nábor je high-risk), Copilot rollouty, vývojári s coding agentmi.
6. **IT/software firmy:** shadow AI a MCP na laptopoch vývojárov. To je presne „lethal trifecta“ z talku Coder.

**Adopcia AI:**
- **CZ (ČSÚ, 2025):** AI používa **18 %** podnikov s 10 a viac zamestnancami (2024: 11 %, EÚ 2025: 20 %). Generatívnu AI na text a kód používa **13 %** (EÚ: 9 %). Z veľkých podnikov AI používa **54 %**.
- **SK:** oficiálne číslo ŠÚ SR za rok 2025 som nenašiel (neoverené). OECD uvádza, že SK zaostáva približne na polovici priemeru EÚ v jednom z ukazovateľov za rok 2024. Prieskum EIBIS 2025 uvádza, že GenAI používa približne 35 % slovenských firiem, ide však o inú metodiku.
- **Interpretácia:** shadow AI je výrazne vyššia než oficiálna adopcia, lebo zamestnanci používajú ChatGPT bez vedomia IT. Presné CZ/SK čísla sú neoverené.

**Dopyt po AI Act službách:**
- Všetky Big4 v CZ majú AI Act stránky: EY ponúka mapovanie AI systémov a posúdenie rizík, PwC má „Trust over AI“ a akadémiu (2-hodinové školenie pre zamestnancov, program pre vedenie, 2-dňový kurz).
- Businessinfo.cz upozorňuje, že veľké firmy a zahraniční odberatelia začínajú **vyžadovať AI compliance v dodávateľských dotazníkoch**. To je dopyt v supply chain aj pre MSP.
- Kvantifikáciu trhu CZ/SK som nenašiel (neoverené).

---

## 4. Konkurencia

### Globálne platformy

| Kategória | Hráči | Poznámka / cena |
|---|---|---|
| GRC / AI governance (papier, registre, riziká) | **Credo AI**, **Holistic AI**, **OneTrust AI Governance**, **IBM watsonx.governance** | Credo, Holistic a OneTrust nemajú verejné ceny (enterprise, 12-mesačné zmluvy). IBM watsonx.governance od približne **3 500 $/mes.** (Basic, podľa porovnávača) |
| Microsoft ekosystém | **Agent 365** (GA 1. 5. 2026), **Entra Agent ID**, Purview DSPM for AI | **15 $/používateľ/mes.** samostatne alebo v **M365 E7 za 99 $/používateľ/mes.**. Najväčšia hrozba. |
| MCP / tool governance | **Docker MCP Gateway** (open source), MintMCP, Permit.io, Aembit | Katalóg, default-deny, filtrovanie nástrojov |
| Identita agentov | **Keycard**, WorkOS (auth.md), Auth0 for AI Agents | Krátkodobé tokeny viazané na úlohu, audit pre každého agenta |
| Runtime AI security / guardrails | **Lakera** (kúpil Check Point, približne 300 mil. $), **Prompt Security** (kúpil SentinelOne, približne 250 mil. $), **Zenity** | Konsolidácia do veľkých security vendorov |
| AI gateway | Tailscale Aperture, Portkey, Kong AI Gateway, Cloudflare AI Gateway | Infra vrstva, nie compliance |
| EU registre AI | Daiki (Viedeň), SimpleAct | Lacnejšie AI registre (neoverené ceny) |

### Lokálne (CZ/SK)

- **Big4 (Deloitte, PwC, EY, KPMG):** AI Act gap analýzy, AI governance frameworky, školenia. Ceny nie sú verejné. Typické projekty pre veľké banky stoja odhadom desiatky tisíc € a viac (neoverené).
- **Advokátske kancelárie** (napr. LeitnerLaw, Prosman Pavlović a ďalšie): právne analýzy, AI politiky, zmluvy s dodávateľmi. Technickú implementáciu nerobia.
- **Menšie consultingy a školitelia:** ČAS/qcom (ISO 42001), TÜV SÜD e-learning, regulation-ai.eu (certifikácia 299 €).
- **CZ/SK startupy:** žiadny dominantný CZ/SK produkt na AI governance alebo AI gateway som nenašiel (neoverené). To je príležitosť.

### Medzera

1. **Stredné firmy (250 až 2 000 zamestnancov),** ktoré si Big4 nedovolia a nechcú enterprise GRC za desaťtisíce dolárov ročne.
2. **Technická implementácia namiesto papierov:** Big4 a advokáti dodajú politiku, ale nie gateway, discovery a audit log. Talky z konferencie jasne ukazujú, že governance sa vynucuje v runtime.
3. **On-prem a suverenita:** banky, zdravotníctvo a verejná správa v CZ/SK chcú riešenie, ktoré neposiela prompty do US SaaS. Credo, Holistic aj Microsoft sú cloudové.
4. **Multi-vendor:** firmy s ChatGPT, Claude, Gemini, lokálnymi modelmi a MCP. Microsoft governuje najmä svoj ekosystém.
5. **Lokálny jazyk a právo:** dokumentácia v češtine a slovenčine, mapovanie na ČTÚ/MIRRI, NIS2 vyhlášky a ČNB/NBS.

---

## 5. Ako to postaviť technicky

```
              ┌──────────────────────── Discovery (shadow AI) ────────────────────────┐
              │ DNS/proxy logy (Zscaler, FortiGate, Squid) → klasifikácia AI domén     │
              │ SaaS discovery (M365/Google OAuth granty, Entra sign-ins)              │
              │ Endpoint skener: ~/.cursor, ~/.claude, mcp.json, VS Code ext., skills  │
              │ (voliteľne) browser extension – detekcia vkladania dát do AI webov    │
              └───────────────┬────────────────────────────────────────────────────────┘
                              ▼
 Používatelia / agenti ──► ┌───────────────── AI + MCP GATEWAY (on-prem/K8s) ─────────────────┐
 (Copilot, Claude Code,    │ Identita: OIDC (Entra/Keycloak), per-agent SPIFFE/krátke tokeny   │
  interné aplikácie)       │ Policy: OPA/Rego – kto, aký model, aké MCP nástroje, verbs        │
                           │ DLP: Presidio + CZ/SK rozpoznávače (rodné číslo, IBAN, IČO)        │
                           │ Rozpočty: tokeny/€ per user/agent, „disruptive action budget"     │
                           │ MCP katalóg: Docker MCP Gateway, default-deny, podpísané image    │
                           │ HITL hook: nevratné akcie → schválenie (Slack/Teams/e-mail)       │
                           └──────┬──────────────────────┬──────────────────────┬──────────────┘
                                  ▼                      ▼                      ▼
                    LLM providery (OpenAI,     Audit log (append-only:   Register AI systémov
                    Anthropic, Azure, lokálne  OpenTelemetry → Langfuse  + klasifikácia rizika
                    vLLM/Ollama)               + ClickHouse/S3 WORM)     + LLM generátor dokumentácie
                                                                          (AI politika, čl. 26, FRIA, DPIA)
```

**(a) Discovery shadow AI**
- Import DNS a proxy logov a ich porovnanie so zoznamom približne 500 AI domén.
- Microsoft Graph pre OAuth aplikácie a Copilot používanie.
- Ľahký endpoint skener (osquery alebo vlastný Go binár), ktorý nájde nainštalované MCP servery, skills a AI rozšírenia v IDE. To je presne problém, ktorý opisovali Docker a Nubank.
- Výstup: zoznam „AI aktív“ s vlastníkom.

**(b) Gateway**
- **LLM proxy:** **LiteLLM** (MIT, virtual keys, rozpočty, logovanie, 100+ providerov) alebo **Portkey** (OSS gateway), prípadne **Envoy AI Gateway** pre K8s-native nasadenia.
- **MCP vrstva:** **Docker MCP Gateway** (katalóg, filtrovanie nástrojov).
- **Policy:** **OPA** (rozhodnutie pre každé volanie: identita × model × nástroj × citlivosť dát).
- **PII:** **Microsoft Presidio** doplnený o lokálny malý model, teda dvojfázový prístup z talku Air-Gapped Fortress.
- **Trace a audit:** **Langfuse** (self-host) a OpenTelemetry.
- **Identita:** Keycloak alebo Entra ID, krátkodobé tokeny pre každého agenta (koncept Keycard a WorkOS).
- **Rozpočty a verbs:** podľa talku Anthropic. Agent dostane N deštruktívnych akcií za okno a nevratné akcie idú cez HITL.

**(c) Register a klasifikácia rizika**
- Formulár a dotazník (účel, dáta, používatelia, rozhodovanie o ľuďoch?) vedú cez rozhodovací strom AI Act (čl. 5, potom Annex III, potom čl. 50) ku kategórii zakázané / high-risk / transparentnosť / minimálne.
- LLM (môže bežať lokálne) z registra vygeneruje AI politiku, záznam podľa čl. 26, šablónu FRIA, DPIA prílohu a NIS2/DORA prepojenia, a to v CZ/SK.
- **Výsledok vždy reviewuje človek.** Klasifikácia je návrh, nie právny posudok.

**(d) HITL**
- Gateway zadrží volanie nevratného nástroja (zápis do DB, odoslanie e-mailu von, platbu) a pošle požiadavku na schválenie do Teams alebo Slacku. Schválenie sa zapíše do audit logu.
- Vzor HITL sa volí podľa závažnosti dôsledkov (Auth0 talk).

**On-prem varianta:** Helm chart alebo docker-compose, lokálne modely cez vLLM (napr. Qwen alebo Llama na klasifikáciu a PII), žiadna telemetria von, WORM úložisko logov (MinIO s object lock).

**Čo je ťažké:**
- **Pokrytie:** agenti na laptopoch obchádzajú proxy (priame API kľúče, lokálne MCP). Treba egress kontrolu (default-deny) a MDM, a to je politicky citlivé.
- **Kvalita DLP v CZ/SK:** false positives otravujú používateľov, false negatives znamenajú únik.
- **Latencia a spoľahlivosť:** gateway je single point of failure pre všetku AI vo firme.
- **Rýchlosť ekosystému:** MCP spec, auth.md a A2A sa menia každý kvartál.
- **Zodpovednosť:** klasifikácia rizika z LLM nesmie pôsobiť ako právna rada. Treba partnera advokáta.
- **Logy obsahujú osobné údaje:** treba retenciu, prístupové práva a GDPR k samotnému audit logu.

---

## 6. MVP za 6–8 týždňov

**Odporúčanie: začať službou s vlastným nástrojom („service-led, product-backed“).** Dôvody:
- trh CZ/SK je malý,
- termíny sa posunuli,
- kupujúci chcú človeka, ktorý im to vysvetlí,
- z každého projektu ale vznikne reusable kód.

**Balík „AI Act & Agent Readiness“ (pilotný scope):**
1. **Týždeň 1–2:** shadow AI discovery (DNS/proxy logy, M365, endpoint skener) a workshop. Výstup: AI inventár.
2. **Týždeň 2–3:** register a klasifikácia rizika, AI politika, mapovanie na NIS2/DORA/GDPR. Výstupy generuje vlastný nástroj, review robí partner advokát.
3. **Týždeň 3–4:** AI literacy školenie (rolové: všetci / vývojári / manažment), atestácia a evidencia účasti.
4. **Týždeň 4–8:** nasadenie gateway (LiteLLM + OPA + Presidio + Langfuse + MCP katalóg) pre jeden pilotný tím. Obvykle sú to vývojári s Claude Code alebo Cursor, kde je riziko „lethal trifecta“ najviditeľnejšie.

**Čo postaviť my (6–8 týždňov, 2 ľudia):**
- endpoint/MCP skener (CLI),
- jednoduchý register a klasifikátor v CZ/SK s generovaním DOCX,
- hardened docker-compose/Helm šablóna gateway s CZ/SK PII rozpoznávačmi,
- dashboard (top používatelia, modely, MCP nástroje, blokované požiadavky).

**Prvých 5–10 zákazníkov:**
- 2–3 **design partneri zadarmo alebo so zľavou** zo siete (IT firmy a softvérové domy s 50–300 vývojármi). Rýchly cyklus, technický kupujúci.
- **Webinár „AI Act po Omnibuse: čo musíte do 2. 12. 2026 a do 12/2027“** s advokátskou kanceláriou.
- **LinkedIn obsah** o shadow AI a MCP (napr. „našli sme X MCP serverov na laptopoch“). Postaviť ho na anonymizovaných dátach z pilotov.
- **NIS2 subjekty:** NÚKIB eviduje približne 5,8 tis. subjektov a slovenské NBÚ ďalšie. AI predávať ako doplnok k ich NIS2 programu.
- **Asociácie:** Česká asociace umělé inteligence, AMSP ČR, slovak.AI, ITAS.

---

## 7. Biznis model a cenotvorba (návrh, neoverené na trhu)

| Položka | Cena (návrh) |
|---|---|
| AI Act Quick Scan (inventár + klasifikácia + report) pre MSP | 3 000–6 000 € |
| Readiness audit + politika + mapovanie NIS2/DORA (stredná firma) | 8 000–20 000 € |
| AI literacy školenie | 40–90 €/osoba e-learning; 1 500–3 000 €/deň workshop |
| Nasadenie gateway (on-prem, pilot) | 10 000–25 000 € jednorazovo |
| SaaS / licencia gateway + register | 5–10 €/používateľ/mes. alebo 20–50 €/agent/mes.; on-prem od ~15 000 €/rok |
| Retainer (správa katalógu MCP, aktualizácie regulácie, reporty) | 1 000–3 000 €/mes. |

Ceny sú zámerne pod úrovňou Big4. Benchmarky: Agent 365 stojí 15 $ za používateľa, IBM od 3 500 $ mesačne.

**Kanály:**
1. **Advokátske kancelárie:** oni robia právo, my techniku. Vzájomné odporúčania, prípadne revenue share 10–20 %.
2. **IT integrátori a MSP/MSSP** (najmä tí, ktorí robia NIS2): white-label gateway a discovery.
3. **Microsoft partneri:** ponúknuť doplnok k Copilot a Agent 365 rolloutom (multi-vendor, MCP, on-prem). Microsoft netreba vytláčať.
4. **Audítori ISO 27001/42001:** predaj „pripravenosti na certifikáciu“.

---

## 8. Riziká a otvorené otázky

- **Posun termínov:** high-risk sa presunul na 12/2027 a čl. 4 bol zmäkčený, takže regulačný tlak je dnes menší. Predaj preto treba postaviť na **bezpečnosti agentov a kontrole nákladov**, nie na strachu z pokút.
- **Microsoft to zabalí:** Agent 365 + Entra Agent ID + Purview v E5/E7 pokryjú „dosť dobre“ firmy, ktoré sú čisto na Microsofte. Obrana: multi-vendor, MCP, on-prem, CZ/SK jazyk a lokálne právo.
- **Big4 a advokáti:** majú dôveru bánk. Skôr s nimi spolupracovať ako implementačný partner než súťažiť.
- **Konsolidácia security vendorov:** Check Point, SentinelOne a pravdepodobne Palo Alto, Zscaler a Cloudflare pridajú AI governance do existujúcich produktov.
- **Rýchlo meniaci sa stack:** údržba integrácií (MCP, auth.md, A2A) môže zjesť malý tím.
- **Právna zodpovednosť:** potrebujeme poistenie profesijnej zodpovednosti a jasný disclaimer, že klasifikácia nie je právna rada.
- **Otvorené otázky:**
  - Kedy a v akej podobe CZ adaptačný zákon prejde? Aké budú sankcie za čl. 4?
  - Prijme NR SR zákon s účinnosťou od 1. 1. 2027?
  - Koľko CZ/SK stredných firiem reálne zaplatí za technickú governance? Treba overiť 15–20 rozhovormi.

---

## 9. Odporúčanie a 5 ďalších krokov

**Odporúčanie:** ísť do toho ako **služba s vlastným open-source-based nástrojom**. Zamerať sa na **stredné firmy a softvérové firmy s vývojármi používajúcimi agentov**, s výraznou on-prem/suverenitnou kartou pre financie a verejnú správu. Pozicionovanie: *„Big4 vám dodá politiku, my ju vynútime v infraštruktúre.“* Produkt (gateway + register) postupne vytiahnuť z opakujúcich sa projektov.

**Ďalšie kroky:**
1. **Do 2 týždňov:** 15 discovery rozhovorov (CISO, CTO, compliance) v CZ/SK. Overiť ochotu platiť za audit, gateway a školenie.
2. **Do 3 týždňov:** postaviť demo: endpoint/MCP skener + LiteLLM/OPA/Presidio/Langfuse gateway s CZ/SK PII rozpoznávačmi + blokovanie neschváleného MCP servera (demo podľa Docker talku).
3. **Do 4 týždňov:** uzavrieť partnerstvo s 1 advokátskou kanceláriou v CZ a 1 v SK a pripraviť spoločný webinár k Omnibusu a termínu 2. 12. 2026.
4. **Do 6 týždňov:** pripraviť AI literacy kurz v CZ/SK (3 rolové moduly + atestácia) ako lacný vstupný produkt.
5. **Do 8 týždňov:** 2–3 platení pilotní zákazníci. Overiť stav CZ adaptačného zákona (psp.cz) a SK zákona (nrsr.sk) a podľa toho aktualizovať ponuku.

---

## 10. Zdroje

**Konferencia:** `conference/sessions.json` (AI Engineer World's Fair 2026; talky citované v sekcii 1).

**AI Act a Digital Omnibus**
- [AI Act – nariadenie (EÚ) 2024/1689, EUR-Lex](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [Orrick – Digital Omnibus Finalizes 8 Compliance Changes (07/2026)](https://www.orrick.com/en/Insights/2026/07/EU-AI-Act-Update-Digital-Omnibus-Finalizes-8-Compliance-Changes)
- [Gibson Dunn – EU AI Act Omnibus Agreement](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/)
- [Jones Walker – Yes, August 2 Still Matters](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html)
- [Cooley – Digital AI Omnibus Delays Key Deadlines](https://cdp.cooley.com/digital-ai-omnibus-delays-key-deadlines-introduces-new-rules/)
- [DLA Piper – The Digital AI Omnibus](https://knowledge.dlapiper.com/dlapiperknowledge/globalemploymentlatestdevelopments/2026/The-Digital-AI-Omnibus-Proposed-deferral-of-high-risk-AI-obligations-under-the-AI-Act)
- [ActuIA – omnibus 2026/1744](https://www.actuia.com/en/news/ai-act-obligations-in-force-and-delays-under-omnibus-2026-1744/)
- [Digital Policy Alert – Omnibus entered into force](https://digitalpolicyalert.org/event/42393-digital-omnibus-on-ai-regulation-20250359-including-organisational-requirement-entered-into-force)
- [Rada EÚ – časová os AI Act](https://www.consilium.europa.eu/sk/policies/artificial-intelligence-act/timeline-artificial-intelligence/)
- [aiactblog.nl – politická dohoda 05/2026](https://www.aiactblog.nl/en/posts/digital-omnibus-ai-act-may-2026-status-political-agreement)
- [KI-Campus – Omnibus recalibrates Article 4](https://ki-campus.org/en/blog/eu-ai-act-ai-omnibus-recalibrates-article-4-ai-literacy-remains-mandatory)
- [IAPP – AI literacy changes](https://iapp.org/news/a/eu-ai-act-literacy-changes-may-complicate-more-than-simplify-compliance)
- [Presencis – Article 4](https://cdn.presencis.com/regulations/eu-ai-act/article-4/)

**CZ/SK implementácia a NIS2**
- [Lupa.cz – český zákon o AI (10 stran, 26 paragrafů)](https://www.lupa.cz/aktuality/finisuje-priprava-ceskeho-zakona-o-umele-inteligenci-navrh-ma-10-stran-a-26-paragrafu/)
- [Právní prostor – Rok 2026: reálný test AI regulace](https://pravniprostor.cz/clanky/pravo-it/rok-2026-realny-test-ai-regulace-od-teorie-k-praxi)
- [Cybrela – AI Act a český zákon](https://cybrela.com/ai-act-vse-o-nove-regulaci-umele-inteligence/)
- [LeitnerLaw – český adaptační zákon](https://www.leitnerlaw.cz/novinky/ai-act-v-praxi-cesky-adaptacni-zakon-vymezuje-kompetence-postupy-a-sankce/)
- [ÚNMZ – implementace AI Act v ČR](https://agenturacas.gov.cz/wp-content/uploads/TZ-UNMZ-Implementace-AI-Act-v-CR.pdf)
- [Zoznam – Dohľad nad AI preberie MIRRI](https://openiazoch.zoznam.sk/technologie/dohlad-nad-umelou-inteligenciou-preberie-mirri-poslanci-posunuli-zakon-dalej/)
- [Info.sk – vláda schválila dohľad nad AI](https://www.info.sk/sprava/281740/vlada-schvalila-dohlad-nad-umelou-inteligenciou-mirri-povedie-kontrolu-ai-a-zriadi-sandbox)
- [AI Priority Map – SK zákon LP/2026/17](https://aiprioritymap.com/sk/insights/slovensky-zakon-o-umelej-inteligencii-lp-2026-17)
- [Prosman Pavlović – nový slovenský zákon o AI](https://www.prosman-pavlovic.sk/novy-slovensky-zakon-o-umelej-inteligencii-co-prinasa-a-ake-otazky-otvara-z-pohladu-praxe/)
- [Lupa.cz – zákon o kyberbezpečnosti začal platit](https://www.lupa.cz/clanky/regulace-podle-nis2-zakon-o-kyberbezpecnosti-zacal-platit-registrovat-se-musite-sami-pozor-na-pokuty/)
- [Právní prostor – ZKB a prováděcí předpisy účinné](https://pravniprostor.cz/zmeny-v-legislative/vyslo-ve-sbirce-zakonu/novy-zakon-o-kyberneticke-bezpecnosti-jeho-provadeci-predpisy-nabyly-ucinnosti)
- [NÚKIB – informace ke kontrolní a sankční praxi 2026](https://nukib.gov.cz/download/uredni_deska/odpovedi_106/2026_10_Informace-ke-kontrolni-a-sankcni-praxi-NUKIB.pdf)
- [Lansky – SK novela zákona o kybernetickej bezpečnosti](https://www.lansky.at/en/newsroom/news/general-news/amendment-to-the-cyber-security-act-as-a-result-of-transposition-of-the-nis-2-directive-into-slovak-law)
- [Lex Mundi – NIS2 Slovakia](https://www.lexmundi.com/guides/status-of-the-nis2-implementation-act-in-the-european-union/jurisdictions/europe/slovak-republic/)

**Trh a adopcia**
- [ČSÚ – V používání AI dohání podniky v Česku průměr EU](https://csu.gov.cz/produkty/v-pouzivani-ai-dohani-podniky-v-cesku-prumer-eu)
- [ČSÚ – ICT v podnicích](https://csu.gov.cz/ict-v-podnicich)
- [Eurostat – Use of AI in enterprises](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises)
- [OECD Economic Survey Slovak Republic 2026 – AI](https://www.oecd.org/en/publications/oecd-economic-surveys-slovak-republic-2026_ada964c8-en/full-report/reaping-the-economic-benefits-from-ai_728bb5d0.html)
- [EIB – EIBIS 2025 Slovakia](https://www.eib.org/en/press/all/2025-516-slovak-firms-invest-trade-and-innovate-but-confidence-weakens-amid-rising-uncertainty?lang=sk)
- [BusinessInfo – EU AI Act a české SME](https://www.businessinfo.cz/clanky/eu-ai-act-a-ceske-sme-co-musite-splnit-a-co-vam-naopak-pomuze/)

**Konkurencia**
- [EY CZ – AI Act](https://www.ey.com/cs_cz/services/cybersecurity/ai-act)
- [PwC CZ – AI Act / Trust over AI](https://www.pwc.com/cz/en/sluzby/umela-inteligence-ai/ai-act.html)
- [PwC CZ – Akademie AI Act](https://www.pwc.com/cz/cs/akademie/ai-act.html)
- [KPMG SK – AI Act regulácia](https://kpmg.com/sk/sk/novinky/2025/10/ai-act-regulacia.html)
- [TÜV SÜD – e-learning AI Act](https://www.tuvsud.com/cs-cz/cinnosti/vzdelavani/e-learning/e-learning-ai-act)
- [regulation-ai.eu – Academy](https://www.regulation-ai.eu/cs/academy/)
- [ePravo – povinnost AI gramotnosti v praxi](https://www.epravo.cz/top/clanky/povinnost-zajisteni-gramotnosti-dle-ai-aktu-a-jeji-naplnovani-v-praxi-120133.html)
- [Licensing School – Agent 365 GA](https://www.licensingschool.co.uk/licensing-blog/2026/03/23/agent-365-ga-announcement/)
- [Rencore – Agent 365 pricing](https://rencore.com/en/blog/understanding-microsoft-agent-365-pricing)
- [Redress Compliance – Agent 365 licensing](https://redresscompliance.com/agent-365-licensing-guide.html)
- [Dupple – AI governance tools 2026 (ceny IBM)](https://dupple.com/learn/best-ai-governance-tools)
- [Kosmoy – Credo AI alternatives](https://kosmoy.com/resources/blog/credo-ai-alternatives/)
- [Capterra – Credo AI](https://www.capterra.com/p/10050777/Credo-AI/)
- [CyberScoop – Check Point kupuje Lakera](https://cyberscoop.com/check-point-lakera-acquistion-ai-security/)
- [Calcalist – Lakera deal](https://www.calcalistech.com/ctechnews/article/rj5bc1vige)
- [Decryption Digest – Lakera, Prompt Security po akvizíciách](https://www.decryptiondigest.com/blog/ai-guardrail-vendors-after-acquisition-lakera-prompt-security-aim-calypsoai)
- [MintMCP – Docker MCP Gateway alternatives](https://www.mintmcp.com/blog/docker-mcp-gateway-alternatives)
- [Keycard docs – Agent access](https://docs.keycard.ai/admin/unified-access-gateway/agent-access/index.md)
- [Permit.io – Six layers of MCP gateway](https://www.permit.io/blog/six-layers-mcp-gateway)
- [Daiki – AI Registry](https://persportaal.anp.nl/artikel/CSN-181224020/-daiki-announces-launch-of-ai-registry-to-streamline-ai-risk-management-and-regulatory-compliance)
- [Česká asociace umělé inteligence – EU AI Act](https://asociace.ai/eu-ai-act/)

**Open-source stavebné bloky (neoverované v tejto rešerši, všeobecne známe projekty)**
- [LiteLLM](https://github.com/BerriAI/litellm) · [Portkey Gateway](https://github.com/Portkey-AI/gateway) · [Envoy AI Gateway](https://github.com/envoyproxy/ai-gateway) · [Docker MCP Gateway](https://github.com/docker/mcp-gateway) · [Open Policy Agent](https://www.openpolicyagent.org/) · [Langfuse](https://github.com/langfuse/langfuse) · [Microsoft Presidio](https://github.com/microsoft/presidio)
