from fastapi import APIRouter, Query, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session
from app import models
from app.db import get_db
from app.llm import LLM, get_llm

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
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()
    leaflet = db.query(models.Leaflet).filter_by(id=leaflet_id).one()

    return templates.TemplateResponse(
        request, "leaflet.html", {"user": user, "leaflet": leaflet}
    )


@router.get("/recipe")
def dashboard_recipes_get(
    request: Request,
    db: Session = Depends(get_db),
    llm: LLM = Depends(get_llm),
    search: Optional[str] = Query(default=None),
    current_user_id: str | None = Depends(current_user_id),
):
    if not current_user_id:
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()

    query = (
        db.query(models.Recipe)
        .join(models.Leaflet)
        .join(models.User)
        .join(models.RecipeEmbedding)
        .filter(models.User.id == current_user_id)
        .order_by(models.Recipe.created_at)
    )

    if search:
        print(f"search query: {search}")
        embeddings = llm.generate_embeddings(search)
        query = query.order_by(
            models.RecipeEmbedding.embedding.cosine_distance(embeddings)
        )

    recipes = query.limit(10)

    return templates.TemplateResponse(
        request, "recipes.html", {"user": user, "recipes": recipes}
    )


@router.get("/recipe/{recipe_id}")
def dashboard_recipe_get(
    recipe_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: str | None = Depends(current_user_id),
):
    if not current_user_id:
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()
    recipe = db.query(models.Recipe).filter_by(id=recipe_id).one()

    return templates.TemplateResponse(
        request, "recipe.html", {"user": user, "recipe": recipe}
    )


@router.get("/settings")
def dashboard_settings_get(
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: str | None = Depends(current_user_id),
):
    if not current_user_id:
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()

    return templates.TemplateResponse(request, "settings.html", {"user": user})


@router.post("/settings")
def dashboard_settings_post(
    request: Request,
    prompt: Annotated[str, Form()],
    db: Session = Depends(get_db),
    current_user_id: str | None = Depends(current_user_id),
):
    if not current_user_id:
        return RedirectResponse("/signin")

    user = db.query(models.User).filter(models.User.id == current_user_id).one()
    user.prompt = prompt
    db.add(user)
    db.commit()

    return templates.TemplateResponse(request, "settings.html", {"user": user})


@router.get("/logout")
def dashboard_logout_get():
    response = RedirectResponse("/")
    response.delete_cookie("user_id")

    return response
