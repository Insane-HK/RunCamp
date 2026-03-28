from backend.payment import pay_user


def process_campaign_submission(wallet: str, task_reward: float, token_name: str, max_winners: int = 10):
    """
    Process a predefined submission payout.
    The admin clicked "Evaluate & Pay" on a specific predefined submission.
    Pays a fixed portion of the task budget to the given wallet.
    """
    print("🤖 Processing Campaign Payout...")
    print(f"💰 Task Budget: {task_reward} {token_name} | Max Winners: {max_winners}")

    if not wallet or not wallet.startswith("0x"):
        return {"status": "error", "message": "Invalid wallet address provided."}

    # Fixed payout: task budget split evenly among max winners
    individual_payout = round(task_reward / max_winners, 2)
    print(f"💸 Paying {individual_payout} {token_name} to {wallet}")

    try:
        tx_hash = pay_user(wallet, str(individual_payout), token_name)
        return {
            "status": "success",
            "message": f"Paid {individual_payout} {token_name} to winner!",
            "tx": tx_hash,
            "wallet": wallet,
            "amount_paid": f"{individual_payout} {token_name}"
        }
    except Exception as e:
        print("❌ Payment error:", str(e))
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    res = process_campaign_submission(
        "0xA7c835A0e0Db1F976443732585FB3Cfe3D6ab38B",
        8000, "$TKL"
    )
    print("Result:", res)
