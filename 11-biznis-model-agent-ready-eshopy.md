# Biznis model: E-shopy pripravené pre AI agentov (#3)

Nadväzuje na [05-deep-dive-agent-ready-eshopy.md](05-deep-dive-agent-ready-eshopy.md) a demo [demo-agent-ready-eshop/](demo-agent-ready-eshop/README.md).

**Princíp:** audit je len vstupná brána. Jednorazové audity s odovzdaním súborov by boli malý konzultačný biznis. Peniaze sú v mesačnom predplatnom.

## Prečo jednorazový audit nestačí

- **Dáta sa menia denne.** Pribúdajú produkty, menia sa ceny a dostupnosť. Súbory z auditu sú o mesiac zastarané.
- **AI modely sa menia každý mesiac.** Obchod, ktorý je dnes viditeľný, môže o dva mesiace zmiznúť a majiteľ to nezistí.
- **Majitelia súbory sami nenasadia.** Väčšina malých e-shopov nevie, kam vložiť JSON-LD ani ako nahrať doplnkový feed do Google Merchant.
- **Viditeľnosť nevieme garantovať.** Predávame meranie a zlepšovanie, nie zaručený výsledok.

## Lievik

```
1. Mini-audit zdarma      →  2. Nasadenie              →  3. Mesačné predplatné
   (demo audit.py)             (jednorazovo / zdarma)       (tu sú peniaze)
   „91 % e-shopov je            napojíme feed,               denne obohacujeme feed,
    pre AI neviditeľných,       doplnok to vloží             týždenne meriame viditeľnosť,
    tu je váš report“           do šablóny automaticky       porovnanie s konkurenciou, alerty
```

## Ponuka a ceny (odhad z deep dive, treba overiť v rozhovoroch)

| Krok | Čo zákazník dostane | Cena |
|---|---|---|
| **Mini-audit** | report ako z dema (5 produktov, 5 dopytov) | zdarma, náklad ~1 $ |
| **Nasadenie** | napojenie feedu, vloženie JSON-LD, Google Merchant | zdarma alebo jednorazovo ~5 000 Kč |
| **Starter** | týždenné meranie viditeľnosti, skóre, upozornenia | 490–990 Kč/mes. |
| **Pro** | + automatické obohacovanie celého feedu, porovnanie s konkurentmi | 2 490–4 990 Kč/mes. |
| **Agentúry** | white-label pre viac klientov | od 15 000 Kč/mes. |

## Čo je kľúčové

1. **Automatizácia namiesto odovzdávania súborov.** Cieľom je Shoptet doplnok, ktorý obohatený feed a JSON-LD nasadí sám a zákazník už nič nerieši. Kým doplnok nie je, prvým pilotom nasadzujeme ručne.
2. **Meranie pred a po.** Pri pilotoch zmeriame viditeľnosť, nasadíme zmeny a o 4 týždne meriame znova. Výsledná case study s číslami predáva ďalej.
3. **Agentúry ako kanál.** PPC a SEO agentúry majú desiatky e-shopov a hľadajú novú službu („GEO“). Jedna agentúra = až 20 klientov naraz.

## Hlavné riziko

Je ťažké dokázať, že zlepšenie viditeľnosti spôsobili naše zmeny, lebo AI odpovede sú nestále. Treba merať opakovane a štatisticky. Ak to nevieme presvedčivo ukázať, zákazníci po pár mesiacoch odídu (churn pri produktoch typu „meriame, ale výsledok nevidno“).

## Ďalšie kroky

- [ ] Otestovať AI časti dema so živým API kľúčom
- [ ] Urobiť audity 10–20 reálnych CZ/SK e-shopov
- [ ] Poslať reporty majiteľom a agentúram a zistiť ochotu platiť za mesačné sledovanie
- [ ] 2–3 pilotní zákazníci s meraním pred a po (case study)
- [ ] Podať žiadosť o Shoptet partnerstvo (schvaľovanie trvá)
