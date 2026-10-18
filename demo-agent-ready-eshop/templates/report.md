# AI readiness audit – $shop

| | |
|---|---|
| Verze | **$label** |
| Datum auditu | $date |
| Otisk feedu (SHA-256) | `$feed_sha256` |
| Produktů ve feedu | $products |

## Shrnutí

| Ukazatel | Hodnota |
|---|---|
| Kvalita dat pro AI | **$feed_score / 100** |
| Vyhledávací AI roboti mají přístup | $search_bots_ok |
| Stránky se schema.org Product | $schema_share |
| Obchod zmíněn v AI odpovědích | $visibility |

## 1. Kvalita produktových dat

$issues_table

### Skóre produktů

$products_table

## 2. Web a AI roboti

$bots_table

### Strukturovaná data na produktových stránkách

$pages_table

## 3. AI obohacení dat

Každý parametr musí mít doslovnou oporu ve zdrojových datech, jinak ho kontrola zamítne.

$enrich_table

## 4. Viditelnost v AI odpovědích

> Jediná nedeterministická část auditu: odpovědi AI se mění v čase. Porovnávejte jen běhy se stejnou sadou dotazů.

$probes_table

---
_Report vygenerován ze šablony `templates/report.md`. Stejný `audit.json` dá vždy stejný report._
