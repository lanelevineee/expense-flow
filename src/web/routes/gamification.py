from fastapi import APIRouter, Header, Request
from typing import Optional

from src.auth.middleware import verify_token
from src.database import GamificationRepository, ExpenseRepository
from src.services.gamification_service import GamificationService

router = APIRouter()


def _require_auth(authorization: Optional[str]):
    if not authorization:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/stats/{staff_id}")
def get_stats(staff_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = GamificationRepository(db)
    service = GamificationService(repo)
    stats = service.get_stats(staff_id)
    if stats is None:
        return {"xp": 0, "level": 1, "current_streak": 0, "longest_streak": 0,
                "total_expenses": 0, "days_active": 0, "total_achievements": 0}
    earned = repo.get_user_achievements(staff_id)
    return {
        "xp": stats.xp, "level": stats.level,
        "current_streak": stats.current_streak,
        "longest_streak": stats.longest_streak,
        "total_expenses": stats.total_expenses,
        "days_active": stats.days_active,
        "total_achievements": len(earned),
    }


@router.get("/achievements")
def list_achievements(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = GamificationRepository(db)
    service = GamificationService(repo)
    return service.get_achievements()


@router.get("/achievements/{staff_id}")
def get_earned(staff_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = GamificationRepository(db)
    earned = repo.get_user_achievements(staff_id)
    all_ach = repo.get_achievements()
    ach_map = {a.id: a for a in all_ach}
    result = []
    for ua in earned:
        ach = ach_map.get(ua.achievement_id)
        result.append({
            "id": ua.id, "achievement_id": ua.achievement_id,
            "earned_at": ua.earned_at,
            "name": ach.name if ach else "",
            "description": ach.description if ach else "",
            "icon": ach.icon if ach else "",
        })
    return result


@router.get("/leaderboard")
def leaderboard(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = GamificationRepository(db)
    service = GamificationService(repo)
    return service.get_leaderboard()


@router.get("/challenges")
def list_challenges(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = GamificationRepository(db)
    service = GamificationService(repo)
    challenges = service.get_active_challenges()
    return [
        {"id": c.id, "title": c.title, "description": c.description,
         "goal_type": c.goal_type, "goal_value": c.goal_value,
         "xp_reward": c.xp_reward, "ends_at": c.ends_at}
        for c in challenges
    ]


@router.get("/challenges/{challenge_id}/{staff_id}")
def get_progress(challenge_id: int, staff_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = GamificationRepository(db)
    cp = repo.get_challenge_progress(challenge_id, staff_id)
    if cp is None:
        return {"progress": 0, "completed": False}
    return {"progress": cp.progress, "completed": cp.completed}
