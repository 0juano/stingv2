"""
Search configuration for agent-specific domains and triggers
"""

AGENT_SEARCH_CONFIG = {
    "bcra": {
        "domains": [
            "bcra.gob.ar",
            "boletinoficial.gob.ar",
            "infoleg.gob.ar"
        ],
        "keywords": ["BCRA", "comunicación A", "banco central argentina", "normativa cambiaria"],
        "triggers": [
            "límite", "cotización", "dólar", "tipo de cambio",
            "cepo", "comunicación a", "pago", "transferencia"
        ],
        "search_suffix": "site:bcra.gob.ar OR site:boletinoficial.gob.ar filetype:pdf"
    },
    "comex": {
        "domains": [
            "afip.gob.ar",
            "tarifar.com",
            "argentina.gob.ar/aduana",
            "boletinoficial.gob.ar",
            "infoleg.gob.ar",
            "argentina.gob.ar/normativa"
        ],
        "keywords": ["NCM", "arancel", "decreto", "resolución general AFIP", "aduana argentina"],
        "triggers": [
            "arancel", "ncm", "posición arancelaria", "simi",
            "licencia", "importación", "tarifa", "impuesto"
        ],
        "search_suffix": "site:afip.gob.ar OR site:boletinoficial.gob.ar decreto resolución"
    },
    "senasa": {
        "domains": [
            "senasa.gob.ar",
            "boletinoficial.gob.ar",
            "argentina.gob.ar/senasa",
            "infoleg.gob.ar"
        ],
        "keywords": ["SENASA", "resolución SENASA", "protocolo fitosanitario", "normativa sanitaria"],
        "triggers": [
            "protocolo", "certificado", "fitosanitario", "requisito",
            "exportación", "sanitario", "roe"
        ],
        "search_suffix": "site:senasa.gob.ar OR site:boletinoficial.gob.ar resolución SENASA"
    }
}

TEMPORAL_TRIGGERS = [
    "actual", "hoy", "vigente", "último", "última",
    "2024", "2025", "ahora", "reciente", "nuevo"
]

# Cache durations in hours
CACHE_DURATIONS = {
    "exchange_rate": 1,  # 1 hour for exchange rates
    "regulation": 24     # 24 hours for regulations
}