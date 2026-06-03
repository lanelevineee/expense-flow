from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional

from src.auth.middleware import verify_token
from src.database import CategoryRepository

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    icon: str = "other"
    description: str = ""
    budget: float = 0.0


class CategoryUpdate(BaseModel):
    icon: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None


def _require_auth(authorization: Optional[str]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/")
def list_categories(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = CategoryRepository(db)
    cats = repo.get_all()
    return [
        {"id": c.id, "name": c.name, "icon": c.icon, "color": c.color, "budget": c.budget}
        for c in cats
    ]


@router.post("/")
def create_category(req: CategoryCreate, request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    db = request.app.state.db
    repo = CategoryRepository(db)
    existing = repo.get_by_name(req.name)
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")
    cat_id = repo.add(req.name, req.icon, req.description, req.budget)
    return {"id": cat_id, "name": req.name}


@router.put("/{cat_id}")
def update_category(cat_id: int, req: CategoryUpdate, request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    db = request.app.state.db
    repo = CategoryRepository(db)
    cats = repo.get_all()
    existing = next((c for c in cats if c.id == cat_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")
    kwargs = {}
    if req.icon is not None:
        kwargs["icon"] = req.icon
    if req.description is not None:
        kwargs["color"] = req.description
    if req.budget is not None:
        kwargs["budget"] = req.budget
    if kwargs:
        repo.update(cat_id, **kwargs)
    return {"success": True}


@router.delete("/{cat_id}")
def delete_category(cat_id: int, request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    db = request.app.state.db
    repo = CategoryRepository(db)
    repo.delete(cat_id)
    return {"success": True}
