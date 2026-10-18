# Porovnání auditů – $shop

| | Před | Po |
|---|---|---|
| Verze | $old_label | $new_label |
| Datum | $old_date | $new_date |
| Otisk feedu | `$old_sha` | `$new_sha` |

## Shrnutí

| Ukazatel | Před | Po | Změna |
|---|---|---|---|
| Kvalita dat pro AI | $old_score / 100 | **$new_score / 100** | $score_delta |
| Vyhledávací AI roboti mají přístup | $old_bots | $new_bots | |
| Stránky se schema.org Product | $old_schema | $new_schema | |
| Obchod zmíněn v AI odpovědích | $old_vis | $new_vis | |

## Problémy v datech (počet produktů)

$issues_table

## Produkty

$products_table

## AI roboti (jen změny)

$bots_table

## Viditelnost v AI odpovědích

$prompts_note
Viditelnost je jediná nedeterministická část – změna může být způsobena i změnou AI modelu, ne jen úpravami obchodu.

$probes_table

---
_Vygenerováno ze šablony `templates/compare.md` z dvou souborů `audit.json`. Stejné vstupy dají vždy stejný výsledek._
