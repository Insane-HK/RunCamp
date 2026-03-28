import requests
from backend.config import NEYNAR_API_KEY, SIGNER_UUID

BASE_URL = "https://api.neynar.com/v2/farcaster/cast"

headers = {
    "accept": "application/json",
    "api_key": NEYNAR_API_KEY,
    "content-type": "application/json"
}


def post_campaign(goal: str, token_name: str, budget: float, strategy_name: str):
    """
    Post the campaign bounty on Farcaster with dynamic details.
    Bot announces the campaign and says it'll check back in 30 mins.
    """
    text = (
        f"🎯 NEW CAMPAIGN LIVE!\n\n"
        f"📋 Goal: {goal}\n"
        f"🏆 Strategy: {strategy_name}\n"
        f"💰 Budget: {budget} {token_name}\n\n"
        f"Complete the tasks below and drop your wallet address in the replies.\n"
        f"🤖 Checking back in 30 mins to evaluate & pay winners!\n\n"
        f"#Monad #Campaign #{token_name.replace('$', '')}"
    )

    data = {
        "text": text,
        "signer_uuid": SIGNER_UUID
    }

    try:
        res = requests.post(BASE_URL, json=data, headers=headers)
        result = res.json()
        print("📢 Campaign posted to Farcaster:", result)
        return result
    except Exception as e:
        print(f"⚠️ Farcaster post failed: {e}")
        return {"error": str(e)}


def reply_to_cast(parent_hash: str, text: str):
    """Reply to a specific Farcaster cast."""
    data = {
        "text": text,
        "parent": parent_hash,
        "signer_uuid": SIGNER_UUID
    }

    try:
        res = requests.post(BASE_URL, json=data, headers=headers)
        print("💬 Replied:", res.json())
    except Exception as e:
        print(f"⚠️ Reply failed: {e}")