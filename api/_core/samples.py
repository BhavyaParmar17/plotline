"""Sample briefs."""

SAMPLES = [
    {
        "id": "cafe",
        "label": "Neighbourhood café",
        "brief": {
            "business_name": "Brew & Bloom",
            "industry": "café and coffee",
            "month": "2026-11",
            "goal": {"type": "engagement", "statement": "Get regulars talking about us online and fill weekday afternoons."},
            "audience": {
                "description": "Young professionals and students in Ahmedabad, 20 to 35",
                "pains": "crowded weekend cafés, overpriced coffee, nowhere quiet to work",
                "interests": "specialty coffee, weekend brunch, working from cafés, local events",
            },
            "platforms": {"instagram": 4, "facebook": 2, "youtube_shorts": 1},
            "services": [
                {"name": "Signature cold brews", "description": "Slow-steeped cold brews in six flavours"},
                {"name": "Weekend brunch", "description": "All-day brunch menu on Saturdays and Sundays"},
                {"name": "Private events", "description": "Book the upstairs space for up to 30 guests"},
                {"name": "Coffee workshops", "description": "Monthly brewing workshops for beginners"},
            ],
            "campaigns": [
                {"name": "Winter menu launch", "start": "2026-11-10", "end": "2026-11-24", "service": "Signature cold brews",
                 "message": "Four new winter drinks, made with local jaggery and spices.", "cta": "Try the winter menu this week"},
            ],
            "assets": {"photos": 20, "videos": 6, "product_shots": 12, "team_photos": 5, "testimonials": 4, "case_studies": 0, "blog_posts": 0, "ugc": 3},
            "key_dates": [{"date": "2026-11-21", "name": "Our third anniversary"}],
            "include_observances": True,
        },
    },
    {
        "id": "b2b",
        "label": "B2B software company",
        "brief": {
            "business_name": "Northbeam Analytics",
            "industry": "data analytics",
            "month": "2026-12",
            "goal": {"type": "leads", "statement": "Book 25 discovery calls with finance teams before the new financial quarter."},
            "audience": {
                "description": "Finance and operations heads at mid-sized Indian companies",
                "pains": "spreadsheets that break every month-end, numbers nobody trusts, slow forecasts",
                "interests": "forecasting, automation, board reporting, cost control",
            },
            "platforms": {"linkedin": 4, "x": 3, "instagram": 2},
            "services": [
                {"name": "Revenue dashboards", "description": "Live dashboards built on your existing data"},
                {"name": "Data audits", "description": "A two-week audit of reporting accuracy"},
                {"name": "Forecasting", "description": "Rolling 12-month forecasts"},
            ],
            "campaigns": [
                {"name": "Year-end data audit", "start": "2026-12-01", "end": "2026-12-15", "service": "Data audits",
                 "message": "Start the new year with numbers you can trust: a free audit for the first 20 teams.", "cta": "Book your free audit"},
            ],
            "assets": {"photos": 6, "videos": 3, "product_shots": 5, "team_photos": 4, "testimonials": 3, "case_studies": 2, "blog_posts": 4, "ugc": 0},
            "key_dates": [],
            "include_observances": True,
        },
    },
]
