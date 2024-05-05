from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models
from app.depends import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def dashboard_get(request: Request, db: Session = Depends(get_db)):
    user_id: str | None = request.cookies.get("user_id")

    if not user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id==user_id).one()

    print(user.leaflets)

    return templates.TemplateResponse(request, "dashboard.html", {"user": user })

@router.get("/leaflet/{leaflet_id}")
def dashboard_leaflet_get(leaflet_id: int, request: Request, db: Session = Depends(get_db)):
    user_id: str | None = request.cookies.get("user_id")

    if not user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id==user_id).one()
    leaflet = db.query(models.Leaflet).filter_by(id=leaflet_id).one()

    return templates.TemplateResponse(request, "leaflet.html", {"user": user, "leaflet": leaflet })

@router.get("/recipe/{recipe_id}")
def dashboard_recipe_get(recipe_id: int, request: Request, db: Session = Depends(get_db)):
    user_id: str | None = request.cookies.get("user_id")

    if not user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id==user_id).one()
    recipe = db.query(models.Recipe).filter_by(id=recipe_id).one()

    return templates.TemplateResponse(request, "recipe.html", {"user": user, "recipe": recipe })


@router.get("/logout")
def dashboard_logout(request: Request):
    request.cookies.pop("user_id")
    return RedirectResponse("/")
