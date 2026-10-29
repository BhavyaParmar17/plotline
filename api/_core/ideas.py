"""
Idea templates. Each template belongs to a pillar and is filled from the
brief (service, audience, pains, interests, campaign, occasion). Having
several per pillar, plus rotation, keeps the month from repeating itself.
"""
from __future__ import annotations

TEMPLATES = {
    "educate": [
        ("ed-mistakes", "3 mistakes people make with {service_lower}", "Walk through the most common mistakes {audience} make with {service_lower} and how to avoid each one."),
        ("ed-howto", "How to get more from {service_lower}", "A practical step-by-step that helps {audience} get better results, with one tip they can use today."),
        ("ed-myth", "Myth vs fact: {service_lower}", "Pick one belief about {service_lower} that holds people back and correct it with a clear example."),
        ("ed-checklist", "A quick checklist before you choose {service_lower}", "Give {audience} a short checklist for choosing well, written so it can be saved and reused."),
        ("ed-pain", "Why {pain} happens, and what helps", "Explain the real cause of {pain} in plain words, then show how {service_lower} addresses it."),
        ("ed-glossary", "A jargon-free guide to {service_lower}", "Define three terms {audience} hear often but rarely get explained, with an everyday example for each."),
        ("ed-interest", "What {interest} has to do with {service_lower}", "Connect something {audience} already care about ({interest}) to a practical lesson about {service_lower}."),
    ],
    "showcase": [
        ("sh-inaction", "{service} in action", "Show {service_lower} from start to finish so people see exactly what they get."),
        ("sh-before-after", "Before and after: {service_lower}", "A clear before and after, with one line on what changed and why it matters."),
        ("sh-detail", "The detail most people miss in {service_lower}", "Zoom in on one detail of {service_lower} that shows the care behind it."),
        ("sh-for-who", "Is {service_lower} right for you?", "Describe the person {service_lower} suits best, and who it doesn’t, so the right {audience} recognise themselves."),
        ("sh-day", "A day with {service_lower}", "Follow one real job or order from first message to finished result."),
        ("sh-compare", "Choosing the right {service_lower} option", "Lay out how {service_lower} compares with the alternatives so people can pick with confidence."),
    ],
    "proof": [
        ("pr-testimonial", "In their words: a customer on {service_lower}", "Share one customer’s review with their photo or a quote card, and the result they got."),
        ("pr-case", "Case study: solving {pain}", "Problem, what we did, the result. Use real numbers from a customer story about {service_lower}."),
        ("pr-numbers", "{service}: the numbers this month", "Share a few real figures from recent work with {service_lower} that show results, not just activity."),
        ("pr-ugc", "Repost: a customer on {service_lower}", "Reshare a customer’s post (with permission) and thank them by name."),
        ("pr-faq-proof", "What customers ask before choosing {service_lower}", "Answer the question new customers ask most, backed by a review or result."),
    ],
    "bts": [
        ("bt-team", "Meet the person behind {service_lower}", "Introduce one team member: what they do, what they enjoy, a small personal detail."),
        ("bt-process", "How we prepare for {service_lower}", "Show the preparation people never see, in quick clips or a short sequence."),
        ("bt-workspace", "Where {service_lower} happens", "A short tour of where the work happens, with one story about the space."),
        ("bt-why", "Why we do {service_lower} the way we do", "Tell the origin story in a few lines: the problem we noticed and why we cared."),
        ("bt-tools", "The tools we rely on for {service_lower}", "Show the tools, kit or ingredients behind the work, and why we chose them."),
        ("bt-week", "A week of {service_lower}, in 30 seconds", "A fast montage of the week: wins, small moments, one lesson learned."),
    ],
    "engage": [
        ("en-poll", "Quick poll: what matters most in {service_lower}?", "Ask {audience} to pick what matters most when choosing {service_lower}. Use the answers in a later post."),
        ("en-question", "What’s your biggest challenge with {pain}?", "Invite replies about {pain} and answer every comment."),
        ("en-thisorthat", "This or that: {interest} edition", "Two options related to {interest}; ask people to vote and say why."),
        ("en-tip-swap", "Your best tip for {interest}?", "Ask {audience} for their best tip on {interest}, then feature a few in a follow-up."),
        ("en-ama", "Ask us anything about {service_lower}", "Open the floor for questions and answer them in replies or a follow-up video."),
        ("en-fill", "Finish the sentence: {interest} is…", "Post a sentence starter about {interest} and ask people to complete it."),
    ],
    "promote": [
        ("po-offer", "{service}: book your slot this month", "A clear offer for {service_lower} with what’s included, the price or starting point, and how to book."),
        ("po-urgency", "Limited spots for {service_lower}", "Explain honestly why availability is limited and when it closes."),
        ("po-bundle", "Pair {service_lower} with something extra", "Suggest a combination that gives better value, with one reason it works well together."),
        ("po-faq", "Before you book {service_lower}: your questions answered", "Answer price, timing and process questions in one place, then the booking link."),
        ("po-reminder", "Last call for {service_lower}", "A friendly reminder of the offer with the deadline and a single clear action."),
    ],
    "moments": [
        ("mo-occasion", "{occasion}", "Mark {occasion} in a way that fits {business}: a short message, a relevant tip or a small gesture linked to {service_lower}."),
        ("mo-season", "{service}: why it suits this season", "Tie the time of year to a practical point about {service_lower}."),
        ("mo-thanks", "A thank-you from the {service_lower} team", "A simple thank-you post with a photo from the month."),
    ],
}

CAMPAIGN_TEMPLATES = [
    ("ca-announce", "{campaign}: it’s here", "Announce {campaign}. Lead with the key message: {message}"),
    ("ca-why", "Why we’re running {campaign}", "Explain the idea behind {campaign} and who it helps. Key message: {message}"),
    ("ca-how", "How {campaign} works", "Walk through how to take part or what’s included in {campaign}, step by step."),
    ("ca-proof", "{campaign}: early results", "Share early reactions or results from {campaign} with a real quote or number."),
    ("ca-faq", "{campaign}: your questions answered", "Answer the three most likely questions about {campaign}."),
    ("ca-bts", "Behind the scenes of {campaign}", "Show the people and the work that went into {campaign}, in a few quick shots."),
    ("ca-question", "What would you want from {campaign}?", "Ask your audience a simple question about {campaign} and reply to every answer."),
    ("ca-last", "{campaign} ends soon", "Remind people {campaign} closes soon, with one clear action."),
]

HOW_TO = {
    "reel": "Hook in the first second, 3–4 quick cuts, end on the call to action. 15–30 seconds, captions on.",
    "carousel": "Cover slide with the hook, one point per slide, final slide is the call to action. 6–8 slides.",
    "image": "One strong photo with a short overlay line and a caption of three or four sentences.",
    "story": "3–5 frames with a poll, quiz or question sticker on the second frame.",
    "text": "Open with a one-line hook, three to five short paragraphs, end with a question.",
    "document": "PDF carousel of 6–10 pages, one idea per page, large type.",
    "poll": "One question with 3–4 options. Reply to comments within the first hour.",
    "video": "60–90 seconds, presenter or screen recording, captions on.",
    "link": "Share the article with a two-line summary of why it matters now.",
    "post": "A single post under 280 characters.",
    "thread": "5–7 posts: hook, one point per post, recap with the call to action.",
    "short": "Vertical, 20–40 seconds, hook in the first two seconds, captions on.",
}
