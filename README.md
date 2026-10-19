# jev-pii

**Inventory personal data with local checks first and optional semantic classification at column—not row—granularity.**

This tool can send sampled real values to a third-party API. Review `--dry-run` bytes, prefer `--local-only`, consider `--mask` (which reduces accuracy), and settle your own processing agreement before production use.

[![Tests](https://github.com/gbesse/jev-pii/actions/workflows/test.yml/badge.svg)](https://github.com/gbesse/jev-pii/actions/workflows/test.yml) ![MIT](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![Public alpha](https://img.shields.io/badge/status-public_alpha-orange)

## 30-second offline quick start
`git clone https://github.com/gbesse/jev-pii.git && cd jev-pii && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt && python -m examples.offline_demo`

## Example: detect inventory drift without sharing rows

`python -m examples.inventory_diff` now shows both a synthetic PII increase and a remediation pass that removes the payment column and phone number. It stays local and reports no network payloads. / L'exemple montre aussi la suppression des données sensibles sans envoi réseau. / El ejemplo muestra también la eliminación de datos sensibles sin envío por red.

Run `python -m examples.inventory_diff` to compare two synthetic column inventories locally. It reports added columns and changed detector categories without printing sample values or making network requests. The synthetic card number also triggers the broad phone pattern, illustrating why detector output needs human review. Fill the processing-record fields yourself before acting on a real inventory.

## Classification Jev / Jev classification / Clasificación Jev

FR : Le transport est disponible avec `scan --live --approve-plan <sha256>`. Prévisualisez d’abord avec `scan --dry-run` ; le CLI reste local par défaut. [Guide FR/EN/ES](docs/live-classification.md).

EN: The transport is available through `scan --live --approve-plan <sha256>`. Preview with `scan --dry-run` first; the CLI stays local by default. [FR/EN/ES guide](docs/live-classification.md).

ES: El transporte está disponible con `scan --live --approve-plan <sha256>`. Previsualice con `scan --dry-run`; el CLI es local por defecto. [Guía FR/EN/ES](docs/live-classification.md).

## Library and integration
Use `detect`, `scan_columns`, `payload_for`, `diff`, and `html_report`. CLI commands are `scan`, `estimate`, `report`, and `diff`. Input in this alpha is a JSON map of column names to values.

## How it decides
Local regexes detect emails, phones and UUIDs; Luhn and mod-97 validate cards and IBANs. Optional seeded samples yield one five-question column payload: personal data, category, special category, data subject, and free-text risk. Risk ranking, counts, processing-record blanks, and remediation are code-owned.

## Boundaries
Database/file/log connectors and national-ID data packs are not yet shipped; `assert_read_only` is available to adapters. Masking lowers semantic accuracy. No socket opens in local-only mode. This is an inventory aid, not legal advice; row counts must come from source systems. No live benchmark is claimed.

## Validation
Run `python -m compileall -q src tests && python -m unittest discover -s tests && python -m examples.offline_demo`; CI runs Python 3.11 and 3.13.

## Related projects
[DecisionPacks](https://github.com/gbesse/decisionpacks), [Autonomy Meter](https://github.com/gbesse/autonomy-meter), and [jev-codebook](https://github.com/gbesse/jev-codebook).

Independent project; not affiliated with TypeSafe AI. [API documentation](https://docs.typesafe.ai/api) · [model notes](https://docs.typesafe.ai/model-jaggedness/jev-1.13/)

## Inventory coverage / Couverture de l’inventaire / Cobertura del inventario

EN: Each column now reports provided rows, nonempty rows, matching rows, per-detector row counts and the exact planned semantic sample count. Overlapping detectors count the same row once in `matched_rows`. Supplied population `row_count` remains separate and cannot be smaller than the provided rows. These counters describe inspected data, not prevalence across unprovided data, detector accuracy or legal certainty. Counts contain no sample values; dry-run payloads still contain the approved samples.

FR : Chaque colonne indique désormais les lignes fournies, non vides, détectées, les comptages par détecteur et le nombre exact d’échantillons sémantiques prévus. Les détecteurs qui se recouvrent ne comptent la ligne qu’une fois dans `matched_rows`. Le `row_count` de population reste distinct et ne peut être inférieur aux lignes fournies. Ces compteurs décrivent les données examinées, pas la prévalence dans les données absentes, la précision ni une certitude juridique. Les compteurs ne contiennent aucune valeur ; les requêtes prévisualisées contiennent toujours les échantillons approuvés.

ES: Cada columna informa filas proporcionadas, no vacías, detectadas, recuentos por detector y el número exacto de muestras semánticas previstas. Detectores solapados cuentan una fila una sola vez en `matched_rows`. El `row_count` poblacional sigue separado y no puede ser menor que las filas proporcionadas. Los recuentos describen datos inspeccionados, no prevalencia en datos ausentes, precisión ni certeza jurídica. No contienen valores; las peticiones previsualizadas siguen conteniendo muestras aprobadas.


FR : Le scan fige les colonnes et les comptes de population avant le premier appel de transport. Les constats locaux restent liés aux données du plan prévisualisé, même si un callback modifie les entrées. Chaque réponse de transport est copiée pour préserver les colonnes déjà traitées. Tests sur données fictives ; aucun gain de précision ou conformité réglementaire mesuré.

EN: A scan snapshots columns and population counts before its first transport call. Local findings stay bound to preview-plan data even if a callback mutates inputs. Each transport answer is copied to preserve previously processed columns. Tests use fictional data; no measured accuracy gain or regulatory compliance claim.

ES: El escaneo fija columnas y recuentos de población antes de la primera llamada de transporte. Los hallazgos locales siguen vinculados a los datos del plan previo aunque un callback cambie las entradas. Cada respuesta se copia para preservar columnas ya procesadas. Tests con datos ficticios; sin mejora de precisión medida ni garantía de cumplimiento normativo.

## Régression de couverture / Coverage regressions / Regresiones de cobertura

FR — `diff()` et `coverage_diff()` signalent les changements de couverture et les baisses de proportion de lignes fournies par rapport au total déclaré, même sans changement de détecteur. Métadonnées absentes ou invalides restent `coverage_unchecked`. La comparaison ne contient aucune valeur source. Le total est déclaré par l’appelant, pas vérifié en base ; une couverture complète ne prouve jamais l’absence de données personnelles.

EN — `diff()` and `coverage_diff()` flag coverage changes and declining provided-row fractions against declared totals, even when detectors are unchanged. Missing or invalid metadata remains `coverage_unchecked`. The comparison contains no source values. Population totals are caller-declared, not database-verified; complete coverage never establishes absence of personal data.

ES — `diff()` y `coverage_diff()` señalan cambios de cobertura y descensos de proporción de filas aportadas frente al total declarado, aunque detectores no cambien. Metadatos ausentes o inválidos quedan `coverage_unchecked`. La comparación no contiene valores fuente. Totales son declarados por quien llama, no verificados en base; cobertura completa nunca prueba ausencia de datos personales.
