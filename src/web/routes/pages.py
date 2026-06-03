from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()


def _templates(request: Request):
    return request.app.state.templates


@router.get("/login")
def login_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("login.html", {"request": request})


@router.get("/register")
def register_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("register.html", {"request": request})


@router.get("/dashboard")
def dashboard_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("dashboard.html", {"request": request})


@router.get("/expenses")
def expenses_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("expenses.html", {"request": request})


@router.get("/staff")
def staff_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("staff.html", {"request": request})


@router.get("/categories")
def categories_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("categories.html", {"request": request})


@router.get("/recurring")
def recurring_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("recurring.html", {"request": request})


@router.get("/gamification")
def gamification_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("gamification.html", {"request": request})


@router.get("/analytics")
def analytics_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("analytics.html", {"request": request})


@router.get("/settings")
def settings_page(request: Request):
    t = _templates(request)
    return t.TemplateResponse("settings.html", {"request": request})


@router.get("/")
def index(request: Request):
    return RedirectResponse(url="/login")
