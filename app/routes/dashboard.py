from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from app import models
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def current_user_id(request: Request):
    user_id: str | None = request.cookies.get("user_id")
    return user_id


@router.get("/")
def dashboard_get(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: str | None = Depends(current_user_id),
):
    if not current_user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()

    return templates.TemplateResponse(request, "dashboard.html", {"user": user})


@router.get("/leaflet/{leaflet_id}")
def dashboard_leaflet_get(
    leaflet_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: str | None = Depends(current_user_id),
):
    if not current_user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()
    leaflet = db.query(models.Leaflet).filter_by(id=leaflet_id).one()

    return templates.TemplateResponse(
        request, "leaflet.html", {"user": user, "leaflet": leaflet}
    )


@router.get("/recipe/{recipe_id}")
def dashboard_recipe_get(
    recipe_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: str | None = Depends(current_user_id),
):
    if not current_user_id:
        # Not logged in.
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()
    recipe = db.query(models.Recipe).filter_by(id=recipe_id).one()

    return templates.TemplateResponse(
        request, "recipe.html", {"user": user, "recipe": recipe}
    )


@router.get("/logout")
def dashboard_logout_get():
    response = RedirectResponse("/")
    response.delete_cookie("user_id")

    return response
