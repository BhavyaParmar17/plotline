"""
Planning rules: content pillars, goal mixes, platform formats, posting days,
asset needs and fixed-date observances. Everything the planner decides from
lives here, so it can be read and tuned in one place.
"""

THEMES = {
    "educate": {"label": "Educate", "funnel": "Awareness", "color": "#2F6FB0",
                "about": "Teach something useful that your audience can act on."},
    "showcase": {"label": "Showcase", "funnel": "Consideration", "color": "#7A4FB5",
                 "about": "Show a service or product doing its job."},
    "proof": {"label": "Proof", "funnel": "Consideration", "color": "#1F8A5B",
              "about": "Testimonials, results and case studies from real customers."},
    "bts": {"label": "Behind the scenes", "funnel": "Awareness", "color": "#B7741A",
            "about": "People, process and the work nobody usually sees."},
    "engage": {"label": "Conversation", "funnel": "Awareness", "color": "#B83B5E",
               "about": "Questions, polls and prompts that invite replies."},
    "promote": {"label": "Offer", "funnel": "Decision", "color": "#0E7C86",
                "about": "A direct ask: book, buy, enquire or sign up."},
    "moments": {"label": "Moments", "funnel": "Awareness", "color": "#7D6A45",
                "about": "Dates, seasons and occasions your audience already cares about."},
}

GOALS = {
    "awareness": {"label": "Grow awareness", "mix": {"educate": 30, "showcase": 15, "proof": 10, "bts": 17, "engage": 18, "promote": 5, "moments": 5}},
    "leads": {"label": "Generate leads", "mix": {"educate": 25, "showcase": 20, "proof": 20, "bts": 7, "engage": 8, "promote": 15, "moments": 5}},
    "sales": {"label": "Drive sales", "mix": {"educate": 15, "showcase": 25, "proof": 20, "bts": 5, "engage": 5, "promote": 25, "moments": 5}},
    "engagement": {"label": "Build engagement", "mix": {"educate": 15, "showcase": 10, "proof": 10, "bts": 22, "engage": 33, "promote": 5, "moments": 5}},
    "launch": {"label": "Launch something new", "mix": {"educate": 20, "showcase": 30, "proof": 10, "bts": 15, "engage": 8, "promote": 12, "moments": 5}},
    "retention": {"label": "Keep customers coming back", "mix": {"educate": 25, "showcase": 10, "proof": 15, "bts": 15, "engage": 20, "promote": 10, "moments": 5}},
}

PLATFORMS = {
    "instagram": {"label": "Instagram", "short": "IG", "days": [1, 3, 5, 0, 2, 4, 6],
                  "formats": {"reel": 40, "carousel": 35, "image": 15, "story": 10}},
    "linkedin": {"label": "LinkedIn", "short": "in", "days": [1, 2, 3, 0, 4, 5, 6],
                 "formats": {"text": 30, "document": 25, "image": 20, "poll": 10, "video": 15}},
    "facebook": {"label": "Facebook", "short": "FB", "days": [2, 4, 0, 3, 1, 5, 6],
                 "formats": {"image": 40, "video": 25, "link": 20, "text": 15}},
    "x": {"label": "X", "short": "X", "days": [0, 1, 2, 3, 4, 5, 6],
          "formats": {"post": 50, "thread": 30, "image": 20}},
    "youtube_shorts": {"label": "YouTube Shorts", "short": "YT", "days": [4, 5, 2, 6, 0, 1, 3],
                       "formats": {"short": 100}},
}

FORMATS = {
    "reel": {"label": "Reel", "asset": "videos", "time": "18:30"},
    "carousel": {"label": "Carousel", "asset": None, "time": "12:30"},
    "image": {"label": "Single image", "asset": "photos", "time": "12:30"},
    "story": {"label": "Story sequence", "asset": None, "time": "20:00"},
    "text": {"label": "Text post", "asset": None, "time": "09:00"},
    "document": {"label": "Document carousel", "asset": None, "time": "09:30"},
    "poll": {"label": "Poll", "asset": None, "time": "10:00"},
    "video": {"label": "Video", "asset": "videos", "time": "17:30"},
    "link": {"label": "Link post", "asset": "blog_posts", "time": "13:00"},
    "post": {"label": "Post", "asset": None, "time": "11:00"},
    "thread": {"label": "Thread", "asset": None, "time": "11:30"},
    "short": {"label": "Short", "asset": "videos", "time": "17:00"},
}

# how well a format suits a theme (1 = neutral)
AFFINITY = {
    "educate": {"carousel": 1.8, "document": 1.9, "thread": 1.8, "reel": 1.2, "text": 1.3, "short": 1.2, "link": 1.4},
    "showcase": {"reel": 1.8, "carousel": 1.4, "image": 1.5, "video": 1.6, "short": 1.6},
    "proof": {"image": 1.5, "carousel": 1.4, "document": 1.4, "video": 1.4, "text": 1.2, "reel": 1.2},
    "bts": {"reel": 1.8, "story": 1.8, "video": 1.5, "image": 1.3, "short": 1.6},
    "engage": {"poll": 2.4, "story": 2.0, "post": 1.6, "text": 1.4, "thread": 0.8, "document": 0.6, "link": 0.4},
    "promote": {"reel": 1.5, "image": 1.6, "story": 1.4, "link": 1.4, "short": 1.3, "poll": 0.3},
    "moments": {"image": 1.8, "post": 1.5, "story": 1.4, "reel": 1.2, "poll": 0.5, "document": 0.4},
}

# assets that a theme prefers, used before generic photos/videos
THEME_ASSETS = {
    "proof": ["testimonials", "case_studies"],
    "bts": ["team_photos", "videos"],
    "showcase": ["product_shots", "photos"],
    "educate": ["blog_posts"],
}

ASSET_TYPES = {
    "photos": "Photos",
    "videos": "Video clips",
    "product_shots": "Product or service shots",
    "team_photos": "Team photos",
    "testimonials": "Testimonials or reviews",
    "case_studies": "Case studies",
    "blog_posts": "Blog posts or articles",
    "ugc": "Customer posts (UGC)",
}

CTA_BY_FUNNEL = {
    "Awareness": ["Follow for more like this", "Save this for later", "Share it with someone who needs it"],
    "Consideration": ["Ask us anything in the comments", "Send us a message to learn more", "See more on our page"],
    "Decision": ["Book now through the link in bio", "Message us to get started", "Enquire today"],
}

# fixed-date observances that work for most Indian audiences (month, day, name)
OBSERVANCES = [
    (1, 1, "New Year’s Day"), (1, 12, "National Youth Day"), (1, 26, "Republic Day"),
    (2, 14, "Valentine’s Day"), (3, 8, "International Women’s Day"), (3, 15, "World Consumer Rights Day"),
    (4, 7, "World Health Day"), (4, 22, "Earth Day"), (5, 1, "Labour Day"),
    (6, 5, "World Environment Day"), (6, 21, "International Yoga Day"), (6, 30, "Social Media Day"),
    (7, 1, "National Doctors’ Day"), (8, 15, "Independence Day"), (9, 5, "Teachers’ Day"),
    (10, 2, "Gandhi Jayanti"), (10, 10, "World Mental Health Day"), (11, 14, "Children’s Day"),
    (12, 25, "Christmas"), (12, 31, "New Year’s Eve"),
]

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
