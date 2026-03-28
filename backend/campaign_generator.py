import random

# Predefined pool of fake Farcaster user wallets for simulation
PREDEFINED_WALLETS = [
    "0xA7c835A0e0Db1F976443732585FB3Cfe3D6ab38B",
    "0x82af1BdcE0c5D36A896B202720dBEbD2B4A102d8",
    "0x111111125434b319222cdbbf8c261bfa2de7a01a",
    "0x222222222228b319222cdbbf8c261bfa2de7a01a",
    "0x3333333333333333333333333333333333333333",
    "0x4444444444444444444444444444444444444444",
    "0x5555555555555555555555555555555555555555",
    "0x6666666666666666666666666666666666666666",
    "0x7777777777777777777777777777777777777777",
    "0x8888888888888888888888888888888888888888",
]

# Dynamic submission text templates
SUBMISSION_TEMPLATES = [
    "🔥 Just created an insane meme for {goal}! My community loved it. Here's proof: farcaster.link/cast/{hash}",
    "Built a full explainer thread about {goal} — 8 casts deep with infographics. Link: farcaster.link/thread/{hash}",
    "Retweeted and quote-tweeted the official {goal} launch post. Massive engagement! Link: farcaster.link/rt/{hash}",
    "Recorded a 3-minute walkthrough video on {goal}. Posted on Farcaster + YouTube. Link: farcaster.link/vid/{hash}",
    "Wrote a technical deep-dive on {goal} architecture. Got 50+ likes organically. Link: farcaster.link/post/{hash}",
    "Created a comparison chart: {goal} vs competitors. Going viral rn 🚀 Link: farcaster.link/chart/{hash}",
    "Hosted a Twitter Space about {goal} with 200+ listeners. Recording: farcaster.link/space/{hash}",
    "Made an animated explainer GIF showing how {goal} works. Link: farcaster.link/gif/{hash}",
    "Posted a before/after case study using {goal}. Super engaged comments. Link: farcaster.link/case/{hash}",
    "Launched a community poll about {goal} features — 500+ votes. Link: farcaster.link/poll/{hash}",
]

# Fake Farcaster usernames
FARCASTER_USERNAMES = [
    "@cryptowizard", "@defi_sarah", "@monad_maxi", "@web3_builder",
    "@based_dev", "@nft_queen", "@chain_explorer", "@pixel_artist",
    "@solidity_sam", "@token_hunter", "@meme_lord", "@alpha_seeker",
]


def _generate_fake_hash():
    return "0x" + "".join(random.choices("abcdef0123456789", k=8))


def _generate_submissions_for_task(task, goal, count=3):
    """Generate dynamic fake Farcaster submissions for a task."""
    submissions = []
    used_wallets = set()
    used_usernames = set()

    for _ in range(count):
        # Pick a unique wallet
        wallet = random.choice([w for w in PREDEFINED_WALLETS if w not in used_wallets])
        used_wallets.add(wallet)

        # Pick a unique username
        username = random.choice([u for u in FARCASTER_USERNAMES if u not in used_usernames])
        used_usernames.add(username)

        text = random.choice(SUBMISSION_TEMPLATES).format(
            goal=goal,
            hash=_generate_fake_hash()
        )

        submissions.append({
            "username": username,
            "wallet": wallet,
            "text": text,
            "timestamp": f"{random.randint(1, 59)}m ago",
            "evaluated": False,
            "paid": False
        })

    return submissions


def generate_campaign_strategies(goal: str, days: int, budget: float, token_name: str):
    """
    Generates 3 distinct campaign strategies with dynamically created 
    fake Farcaster submissions per task. Predefined wallet addresses are
    assigned to each submission. Strategy base is designed to be expanded
    to 15+ strategies in the future (auto-pick 3-5 based on days).
    """

    # ──── Strategy 1: Aggressive Virality ────
    strat1 = {
        "id": "strat_viral",
        "name": "🔥 Aggressive Virality",
        "description": f"Maximum reach through meme warfare & retweets over {days} days. Best for fast token awareness.",
        "tasks": [
            {
                "id": "t1",
                "title": f"Create a Viral Meme about {goal}",
                "requirement": "Verifiable Farcaster Post Link containing image/meme.",
                "reward": int(budget * 0.70),
                "token": token_name,
                "submissions": _generate_submissions_for_task(None, goal, count=3)
            },
            {
                "id": "t2",
                "title": "Retweet the official launch announcement",
                "requirement": "Verifiable Retweet/Quote-cast Link.",
                "reward": int(budget * 0.30),
                "token": token_name,
                "submissions": _generate_submissions_for_task(None, goal, count=2)
            }
        ]
    }

    # ──── Strategy 2: Deep Technical Content ────
    strat2 = {
        "id": "strat_deep",
        "name": "🧠 Deep Technical Content",
        "description": "Rewards high-effort developers and researchers. Quality over quantity.",
        "tasks": [
            {
                "id": "t3",
                "title": f"Write a technical thread on {goal}",
                "requirement": "Verifiable Farcaster Thread Link (>3 casts).",
                "reward": int(budget * 0.80),
                "token": token_name,
                "submissions": _generate_submissions_for_task(None, goal, count=3)
            },
            {
                "id": "t4",
                "title": "Record a 2-minute video tutorial",
                "requirement": "Youtube/Loom Tracking Link.",
                "reward": int(budget * 0.20),
                "token": token_name,
                "submissions": _generate_submissions_for_task(None, goal, count=2)
            }
        ]
    }

    # ──── Strategy 3: Balanced Community Growth ────
    strat3 = {
        "id": "strat_balanced",
        "name": "⚖️ Balanced Community Growth",
        "description": "Steadily builds community engagement across memes, threads, and replies.",
        "tasks": [
            {
                "id": "t5",
                "title": "Post an insightful meme",
                "requirement": "Farcaster Post Link with image.",
                "reward": int(budget * 0.40),
                "token": token_name,
                "submissions": _generate_submissions_for_task(None, goal, count=2)
            },
            {
                "id": "t6",
                "title": f"Summary thread on {goal}",
                "requirement": "Farcaster Thread Link (>2 casts).",
                "reward": int(budget * 0.40),
                "token": token_name,
                "submissions": _generate_submissions_for_task(None, goal, count=2)
            },
            {
                "id": "t7",
                "title": "Engage via constructive replies",
                "requirement": "Link to quality reply/discussion.",
                "reward": int(budget * 0.20),
                "token": token_name,
                "submissions": _generate_submissions_for_task(None, goal, count=2)
            }
        ]
    }

    # ──────────────────────────────────────────────────────────────
    # TODO (Future): Expand to 15 strategies total.
    #   Auto-pick 3-5 based on campaign duration (days).
    #   Examples to add:
    #     - "🎯 Influencer Outreach"
    #     - "🎨 Creative Contest"
    #     - "📊 Data-Driven Analytics"
    #     - "🤝 Partnership Cross-Promo"
    #     - "🛠️ Build-to-Earn"
    #     - "📱 Social Raid"
    #     - "🏆 Leaderboard Gamification"
    #     - "🎙️ Podcast/Spaces Campaign"
    #     - "📝 Blog/Article Writing"
    #     - "🧪 Testnet Participation"
    #     - "📣 Ambassador Program"
    #     - "🎮 Gamified Quests"
    #   Selection logic:
    #     if days <= 3: pick 3 fast-execution strategies
    #     if days <= 7: pick 4 mixed strategies
    #     if days > 7:  pick 5 long-term strategies
    # ──────────────────────────────────────────────────────────────

    return [strat1, strat2, strat3]
