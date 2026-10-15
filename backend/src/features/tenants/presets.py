RUBRO_PRESETS: dict[str, dict] = {
    "barberia": {
        "default_sections": ["hero", "services", "team", "location"],
        "sample_services": [
            {"name": "Corte", "duration_minutes": 30, "price_cents": 800000},
            {"name": "Barba", "duration_minutes": 20, "price_cents": 500000},
        ],
    },
    "peluqueria": {
        "default_sections": ["hero", "services", "team", "reviews"],
        "sample_services": [
            {"name": "Corte mujer", "duration_minutes": 45, "price_cents": 1200000},
        ],
    },
}
