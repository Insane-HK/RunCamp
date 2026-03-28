import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from backend.campaign_generator import generate_campaign_strategies
from backend.campaign_agent import process_campaign_submission
from backend.farcaster import post_campaign
from backend.config import CONTRACT_ADDRESS

app = FastAPI(title="AI Campaign Manager — Monad")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# In-memory state
db_state = {
    "strategies": [],
    "active_strategy": None,
    "campaign_launched": False,
    "checked": False,
    "current_submissions": [],
    "winners_paid": 0,
    "max_winners": 10,
    "goal": "",
    "token_name": "MON",
    "budget": 0,
    "deposited": False,
    "farcaster_posted": False,
    "payment_log": [],
    "contract_address": CONTRACT_ADDRESS,
}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": db_state
    })


@app.get("/reset", response_class=HTMLResponse)
async def reset_dashboard(request: Request):
    db_state["strategies"] = []
    db_state["active_strategy"] = None
    db_state["campaign_launched"] = False
    db_state["checked"] = False
    db_state["current_submissions"] = []
    db_state["winners_paid"] = 0
    db_state["goal"] = ""
    db_state["budget"] = 0
    db_state["deposited"] = False
    db_state["farcaster_posted"] = False
    db_state["payment_log"] = []
    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": db_state
    })


@app.post("/generate", response_class=HTMLResponse)
async def generate_plans(
    request: Request,
    goal: str = Form(...),
    days: int = Form(...),
    mon_budget: float = Form(...)
):
    """Step 1: Campaign maker sets budget in native MON → Generate AI strategies."""
    
    # Native token payout
    token_str = "MON"

    strats = generate_campaign_strategies(goal, days, mon_budget, token_str)

    db_state["strategies"] = strats
    db_state["active_strategy"] = None
    db_state["goal"] = goal
    db_state["token_name"] = token_str
    db_state["budget"] = mon_budget
    db_state["deposited"] = True

    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": db_state
    })


@app.post("/select", response_class=HTMLResponse)
async def select_strategy(request: Request, strat_id: str = Form(...)):
    """Step 2: Select one of the AI-generated strategies."""
    for strat in db_state["strategies"]:
        if strat["id"] == strat_id:
            db_state["active_strategy"] = strat
            db_state["campaign_launched"] = False
            db_state["checked"] = False
            db_state["current_submissions"] = []
            db_state["winners_paid"] = 0
            db_state["payment_log"] = []
            break

    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": db_state
    })


@app.post("/launch", response_class=HTMLResponse)
async def launch_campaign(request: Request):
    """Step 3: Launch campaign — bot posts on Farcaster. Shows waiting state."""
    db_state["campaign_launched"] = True
    db_state["checked"] = False
    db_state["current_submissions"] = []

    # Post campaign to Farcaster
    if db_state["active_strategy"]:
        try:
            post_campaign(
                goal=db_state["goal"],
                token_name=db_state["token_name"],
                budget=db_state["budget"],
                strategy_name=db_state["active_strategy"]["name"]
            )
            db_state["farcaster_posted"] = True
        except Exception as e:
            print(f"⚠️ Farcaster posting failed: {e}")
            db_state["farcaster_posted"] = False

    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": db_state
    })


@app.post("/check", response_class=HTMLResponse)
async def check_submissions(request: Request):
    """
    Step 4: User clicks 'Check Now' after waiting.
    Reveals 2 fake submissions from the first task that has remaining submissions.
    """
    db_state["checked"] = True
    db_state["current_submissions"] = []

    if db_state["active_strategy"]:
        # Collect 2 unpaid submissions from across all tasks
        revealed = []
        for task in db_state["active_strategy"]["tasks"]:
            for sub in task.get("submissions", []):
                if not sub.get("paid", False) and len(revealed) < 2:
                    revealed.append({
                        "task_id": task["id"],
                        "task_title": task["title"],
                        "task_reward": task["reward"],
                        "task_token": task["token"],
                        "username": sub["username"],
                        "wallet": sub["wallet"],
                        "text": sub["text"],
                        "timestamp": sub["timestamp"],
                    })
            if len(revealed) >= 2:
                break

        db_state["current_submissions"] = revealed

    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": db_state
    })


@app.post("/pay_all", response_class=HTMLResponse)
async def pay_all_submissions(request: Request):
    """
    Step 5: User clicks 'Evaluate & Pay All'.
    Automatically pays ALL currently revealed submissions at once.
    Updates counter (e.g. 0/10 → 2/10).
    """
    results = []

    for sub in db_state["current_submissions"]:
        if sub.get("already_paid"):
            continue

        task_reward = sub["task_reward"]
        token_name = sub["task_token"]
        wallet = sub["wallet"]

        res = process_campaign_submission(
            wallet=wallet,
            task_reward=task_reward,
            token_name=token_name,
            max_winners=db_state["max_winners"]
        )

        if res.get("status") == "success":
            db_state["winners_paid"] += 1
            sub["already_paid"] = True

            # Mark as paid in the strategy task submissions too
            if db_state["active_strategy"]:
                for task in db_state["active_strategy"]["tasks"]:
                    if task["id"] == sub["task_id"]:
                        for s in task["submissions"]:
                            if s["wallet"] == wallet:
                                s["paid"] = True
                                s["evaluated"] = True

        results.append({
            "wallet": wallet,
            "username": sub["username"],
            "task": sub["task_title"],
            **res
        })

    db_state["payment_log"].extend(results)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": db_state,
        "pay_results": results
    })


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
