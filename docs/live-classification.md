# FR — Classification de colonnes avec plan exact

`scan` reste local par défaut. `estimate` ou `scan --dry-run` construit les requêtes sans connexion réseau. La prévisualisation **contient les échantillons**, même avec `--mask` : celui-ci conserve notamment les domaines email et ne garantit aucune anonymisation. Le résultat des appels ne conserve pas les échantillons. Les noms de colonnes restent visibles. Les nouvelles sorties `--out` sont créées avec permissions `600`, sans écrasement.

```sh
jev-pii scan local-data/columns.json --dry-run --lang fr --out local-data/preview.json
# Lire et examiner chaque payload puis son plan_sha256.
jev-pii scan local-data/columns.json --live --lang fr --approve-plan <plan_sha256> --max-calls 10 --out local-data/inventory.json
python -m examples.transport_demo --lang fr
```

Le SHA256 doit correspondre aux octets de toutes les requêtes ordonnées par colonne : une modification d’échantillon, de langue, de masquage ou de question impose une nouvelle prévisualisation. Il exprime un accord local, pas une authentification ni un accord de traitement. Configurez `TYPESAFE_API_KEY` uniquement dans l’environnement du processus. Une requête payante par colonne, au maximum 10 par défaut ; le budget est contrôlé avant tout envoi. Une erreur interrompt le lot : des requêtes antérieures peuvent déjà avoir été facturées. Le transport n’effectue ni relance ni redirection, ignore les proxies d’environnement et cible uniquement l’API officielle. Son délai d’inactivité réseau est de 15 secondes ; réponses limitées à 1 Mo, requêtes à 200 ko, 1–100 échantillons par colonne. Aucun corps d’erreur fournisseur n’est affiché.

La bibliothèque expose `preview_plan` et `TypeSafeTransport`. Le paramètre `allow_loopback=True` autorise exclusivement HTTP local pour les tests ; le CLI ne l’expose pas. Les cinq questions sont explicites, les choix sont des tables d’options, et les réponses Noul/Choice, probabilités, modèle et compteurs sont validés avant inclusion. Les valeurs et textes utilisateur ne sont jamais traduits. La probabilité Noul `personal` n’est pas une mesure de précision ou une certification ; le champ historique `confidence` reprend cette probabilité en mode sémantique. Les détecteurs locaux et échantillons peuvent manquer des données : aucune conclusion juridique ni certification DLP.

Validation : tests HTTP et CLI synthétiques en FR/EN/ES, démonstration locale, Python 3.11/3.13 en CI. Un appel payant sur un texte fictif a validé les cinq réponses de l’API officielle (587 jetons d’entrée, 151 de sortie). Aucun benchmark de détection réel. Contrat vérifié dans la [documentation officielle TypeSafe](https://docs.typesafe.ai/api) et les [primitives](https://docs.typesafe.ai/primitives).

# EN — Column classification with an exact plan

`scan` stays local by default. `estimate` or `scan --dry-run` constructs requests without network access. The preview **contains samples**, even with `--mask`: email domains survive and masking is not anonymization. Call results omit samples; column names remain visible. New `--out` files have mode `600` and never overwrite.

```sh
jev-pii scan local-data/columns.json --dry-run --lang en --out local-data/preview.json
# Read and review every payload, then its plan_sha256.
jev-pii scan local-data/columns.json --live --lang en --approve-plan <plan_sha256> --max-calls 10 --out local-data/inventory.json
python -m examples.transport_demo --lang en
```

SHA256 must match the bytes of all requests sorted by column: changes to samples, language, masking or questions require a fresh preview. It is local acknowledgement, not authentication or a processing agreement. Set `TYPESAFE_API_KEY` only in the process environment. One paid request per column, at most 10 by default; the budget is checked before any send. Errors stop the batch: earlier requests may already have been billed. The transport has no retries or redirects, ignores environment proxies and targets only the official API. Network inactivity timeout is 15 seconds; responses are limited to 1 MB, requests to 200 KB, with 1–100 samples per column. Provider error bodies are never displayed.

The library exposes `preview_plan` and `TypeSafeTransport`. `allow_loopback=True` allows only local HTTP for tests; the CLI does not expose it. Five explicit questions use option maps, and Noul/Choice responses, probabilities, model and token counters are validated before inclusion. User values and text are never translated. The `personal` Noul is not measured accuracy or certification; the legacy `confidence` field repeats it in semantic mode. Local detectors and samples can miss data: this provides no legal conclusion or DLP certification.

Validation: synthetic FR/EN/ES HTTP and CLI tests, local demo, Python 3.11/3.13 in CI. One paid call on fictional text validated all five answers against the official API (587 input tokens, 151 output tokens). No real detection benchmark was performed. Contract checked against the [official TypeSafe API](https://docs.typesafe.ai/api) and [primitives](https://docs.typesafe.ai/primitives).

# ES — Clasificación de columnas con un plan exacto

`scan` sigue siendo local por defecto. `estimate` o `scan --dry-run` prepara las peticiones sin red. La vista previa **contiene muestras**, incluso con `--mask`: conserva dominios de correo y no garantiza anonimización. Los resultados omiten las muestras; los nombres de columnas siguen visibles. Los nuevos archivos `--out` tienen permisos `600` y nunca sobrescriben.

```sh
jev-pii scan local-data/columns.json --dry-run --lang es --out local-data/preview.json
# Leer y revisar cada payload y después su plan_sha256.
jev-pii scan local-data/columns.json --live --lang es --approve-plan <plan_sha256> --max-calls 10 --out local-data/inventory.json
python -m examples.transport_demo --lang es
```

El SHA256 debe corresponder a los bytes de todas las peticiones ordenadas por columna: cambiar muestras, idioma, enmascaramiento o preguntas exige otra vista previa. Es una aceptación local, no autenticación ni acuerdo de tratamiento. Defina `TYPESAFE_API_KEY` solo en el entorno del proceso. Una petición de pago por columna, máximo 10 por defecto; el presupuesto se verifica antes de enviar. Un error detiene el lote: las peticiones anteriores pueden estar facturadas. El transporte no reintenta ni redirige, ignora los proxies del entorno y solo utiliza la API oficial. El plazo de inactividad de red es de 15 segundos; respuestas limitadas a 1 MB, peticiones a 200 KB y 1–100 muestras por columna. Nunca se muestran cuerpos de error del proveedor.

La biblioteca expone `preview_plan` y `TypeSafeTransport`. `allow_loopback=True` solo permite HTTP local para pruebas; el CLI no lo expone. Las cinco preguntas son explícitas, los criterios son mapas de opciones, y las respuestas Noul/Choice, probabilidades, modelo y contadores se validan antes de incluirlos. No se traducen datos ni textos del usuario. La probabilidad Noul `personal` no es precisión medida ni certificación; el campo histórico `confidence` la repite en modo semántico. Los detectores y las muestras pueden omitir datos: no constituye conclusión jurídica ni certificación DLP.

Validación: pruebas HTTP y CLI sintéticas en FR/EN/ES, ejemplo local y Python 3.11/3.13 en CI. Una llamada de pago con texto ficticio validó las cinco respuestas de la API oficial (587 tokens de entrada, 151 de salida). Sin benchmark real de detección. Contrato verificado con la [API oficial TypeSafe](https://docs.typesafe.ai/api) y sus [primitivas](https://docs.typesafe.ai/primitives).
