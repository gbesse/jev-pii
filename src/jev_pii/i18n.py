"""User-facing strings and atomic questions; user samples are never translated."""

TEXT = {
    "en": {
        "description": "Local PII inventory; preview exact samples before explicit paid classification.",
        "input": "JSON column map or inventory; paths and user data retain their language.",
        "out": "New private output file; never overwrite.",
        "local": "Local detectors only; no network.",
        "dry": "Preview exact request bytes; output contains sampled values.",
        "mask": "Mask digits and parts of email addresses; this is not anonymization.",
        "live": "Send the approved samples to TypeSafe; one paid request per column.",
        "approve": "SHA256 plan from the exact preview, required with --live.",
        "budget": "Maximum requests, checked before any call (default 10).",
        "size": "Samples per column (1–100, default 20).",
        "seed": "Deterministic sampling seed (default 7).",
        "help": "Show this help.",
        "usage": "usage",
        "options": "options",
        "positional": "arguments",
        "error": "Operation failed; check input, options and output destination.",
        "plan": "Preview again and provide its plan SHA256 with --approve-plan.",
        "budget_error": "The plan exceeds the request budget; no requests sent.",
        "input_error": "Expected a JSON map of column names to lists of scalar values.",
        "response": "Invalid TypeSafe response; no raw response is logged.",
        "network": "TypeSafe request failed; no automatic retry or redirect.",
        "key": "Set TYPESAFE_API_KEY in the process environment; never in a command argument.",
        "bounds": "Invalid sampling, timeout, model, endpoint or payload size.",
        "title": "PII inventory",
        "remediation": [
            "Confirm purpose and retention",
            "Restrict access",
            "Review high-risk columns",
        ],
        "questions": [
            "Do `samples` in `column` contain data relating to an identifiable person?",
            "Which personal-data category best describes `samples` in `column`?",
            "Do `samples` in `column` reveal health, racial or ethnic origin, political or religious views, union membership, biometric or genetic data, or sex life?",
            "Whose personal data is represented in `samples` in `column`?",
            "Do `samples` in `column` contain free text that may include personal data?",
        ],
        "category": [
            "Identity or personal identifiers",
            "Contact details",
            "Financial information",
            "Health information",
            "Other or insufficient evidence",
        ],
        "subject": [
            "Employee",
            "Customer",
            "Prospect",
            "Patient",
            "Other or insufficient evidence",
        ],
    },
    "fr": {
        "description": "Inventaire local des données personnelles ; prévisualisez les échantillons avant toute classification payante explicite.",
        "input": "Colonnes JSON ou inventaire ; les chemins et données gardent leur langue.",
        "out": "Nouveau fichier privé ; aucun écrasement.",
        "local": "Détecteurs locaux uniquement ; aucun réseau.",
        "dry": "Prévisualiser les octets exacts ; la sortie contient des valeurs échantillonnées.",
        "mask": "Masquer les chiffres et une partie des adresses email ; ce n’est pas une anonymisation.",
        "live": "Envoyer les échantillons approuvés à TypeSafe ; une requête payante par colonne.",
        "approve": "SHA256 du plan prévisualisé, requis avec --live.",
        "budget": "Maximum de requêtes, vérifié avant tout appel (10 par défaut).",
        "size": "Échantillons par colonne (1–100, 20 par défaut).",
        "seed": "Graine déterministe (7 par défaut).",
        "help": "Afficher cette aide.",
        "usage": "utilisation",
        "options": "options",
        "positional": "arguments",
        "error": "Échec ; vérifiez les données, options et la destination de sortie.",
        "plan": "Prévisualisez de nouveau et fournissez le SHA256 du plan avec --approve-plan.",
        "budget_error": "Le plan dépasse le budget de requêtes ; aucun envoi.",
        "input_error": "Une table JSON de noms de colonnes vers des listes de valeurs simples est requise.",
        "response": "Réponse TypeSafe invalide ; aucune réponse brute n’est journalisée.",
        "network": "Échec de la requête TypeSafe ; aucune relance ni redirection automatique.",
        "key": "Définissez TYPESAFE_API_KEY dans l’environnement du processus, jamais comme argument.",
        "bounds": "Échantillonnage, délai, modèle, destination ou taille de requête invalide.",
        "title": "Inventaire des données personnelles",
        "remediation": [
            "Confirmer la finalité et la conservation",
            "Restreindre l’accès",
            "Examiner les colonnes à risque",
        ],
        "questions": [
            "Les `samples` de `column` contiennent-ils des données relatives à une personne identifiable ?",
            "Quelle catégorie de données personnelles décrit le mieux les `samples` de `column` ?",
            "Les `samples` de `column` révèlent-ils la santé, l’origine raciale ou ethnique, les opinions politiques ou religieuses, l’appartenance syndicale, la biométrie, la génétique ou la vie sexuelle ?",
            "À qui appartiennent les données personnelles des `samples` de `column` ?",
            "Les `samples` de `column` contiennent-ils du texte libre pouvant inclure des données personnelles ?",
        ],
        "category": [
            "Identité ou identifiants personnels",
            "Coordonnées",
            "Informations financières",
            "Informations de santé",
            "Autre ou preuves insuffisantes",
        ],
        "subject": [
            "Employé",
            "Client",
            "Prospect",
            "Patient",
            "Autre ou preuves insuffisantes",
        ],
    },
    "es": {
        "description": "Inventario local de datos personales; previsualice las muestras antes de una clasificación de pago explícita.",
        "input": "Columnas JSON o inventario; rutas y datos conservan su idioma.",
        "out": "Nuevo archivo privado; nunca sobrescribir.",
        "local": "Solo detectores locales; sin red.",
        "dry": "Previsualizar los bytes exactos; la salida contiene valores muestreados.",
        "mask": "Ocultar dígitos y parte de los correos; no es anonimización.",
        "live": "Enviar las muestras aprobadas a TypeSafe; una petición de pago por columna.",
        "approve": "SHA256 del plan previsualizado, obligatorio con --live.",
        "budget": "Máximo de peticiones, comprobado antes de cualquier llamada (10 por defecto).",
        "size": "Muestras por columna (1–100, 20 por defecto).",
        "seed": "Semilla determinista (7 por defecto).",
        "help": "Mostrar esta ayuda.",
        "usage": "uso",
        "options": "opciones",
        "positional": "argumentos",
        "error": "Operación fallida; compruebe datos, opciones y destino de salida.",
        "plan": "Previsualice de nuevo y proporcione el SHA256 del plan con --approve-plan.",
        "budget_error": "El plan supera el presupuesto de peticiones; no se envió ninguna.",
        "input_error": "Se requiere un mapa JSON de nombres de columnas a listas de valores simples.",
        "response": "Respuesta TypeSafe inválida; no se registra la respuesta original.",
        "network": "Petición TypeSafe fallida; sin reintento ni redirección automática.",
        "key": "Defina TYPESAFE_API_KEY en el entorno del proceso, nunca como argumento.",
        "bounds": "Muestreo, plazo, modelo, destino o tamaño de petición inválido.",
        "title": "Inventario de datos personales",
        "remediation": [
            "Confirmar finalidad y conservación",
            "Restringir el acceso",
            "Revisar columnas de riesgo",
        ],
        "questions": [
            "¿Los `samples` de `column` contienen datos relativos a una persona identificable?",
            "¿Qué categoría de datos personales describe mejor los `samples` de `column`?",
            "¿Los `samples` de `column` revelan salud, origen racial o étnico, opiniones políticas o religiosas, afiliación sindical, biometría, genética o vida sexual?",
            "¿De quién son los datos personales de los `samples` de `column`?",
            "¿Los `samples` de `column` contienen texto libre que pueda incluir datos personales?",
        ],
        "category": [
            "Identidad o identificadores personales",
            "Datos de contacto",
            "Información financiera",
            "Información sanitaria",
            "Otro o pruebas insuficientes",
        ],
        "subject": [
            "Empleado",
            "Cliente",
            "Prospecto",
            "Paciente",
            "Otro o pruebas insuficientes",
        ],
    },
}
CATEGORY = ("identity", "contact", "financial", "health", "other")
SUBJECT = ("employee", "customer", "prospect", "patient", "other")


class PiiError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(" / ".join(TEXT[lang][code] for lang in ("fr", "en", "es")))


def questions(lang="en"):
    if lang not in TEXT:
        raise PiiError("bounds")
    t = TEXT[lang]
    return {
        name: {
            "type": kind,
            "instructions": instructions,
            **({"criteria": dict(zip(keys, t[name]))} if keys else {}),
        }
        for name, kind, instructions, keys in zip(
            ("personal", "category", "special", "subject", "free_text"),
            ("noul", "choice", "noul", "choice", "noul"),
            t["questions"],
            (None, CATEGORY, None, SUBJECT, None),
        )
    }
