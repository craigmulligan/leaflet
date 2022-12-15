from flask import (
    Blueprint,
    render_template,
    abort,
    flash,
    redirect,
    url_for,
    request,
)
from app import database
from app import leaflet_manager
from app.api.utils import authenticated_resource

blueprint = Blueprint("user", __name__)


@blueprint.route("/<int:user_id>", methods=["GET"])
@authenticated_resource
def user_get(user_id):
    db = database.get()
    user = db.user_get_by_id(user_id)

    if not user:
        abort(404)

    if not user.can_view():
        abort(403)

    leaflet_ids = db.leaflet_get_all_by_user(user_id)
    recipe_count = db.recipe_count()

    return render_template("user.html", user=user, leaflet_ids=leaflet_ids, recipe_count=recipe_count)


@blueprint.route("/<int:user_id>", methods=["POST"])
@authenticated_resource
def user_post(user_id):
    """
    TODO: Might want to add CRSF protection, but feels like
    an overkill RN.
    """
    db = database.get()
    user = db.user_get_by_id(user_id)

    if not user:
        abort(404)

    if not user.can_view():
        abort(403)

    recipes_per_week = request.form.get("recipes_per_week")
    serving = request.form.get("serving")
    errors = {}

    if not recipes_per_week:
        errors.update({"recipes_per_week": "Recipes per week is required."})

    if not serving:
        errors.update({"serving": "Servings is required."})

    if errors:
        flash("Error updating settings", "error")
        return render_template("user.html", user=user, errors=errors)

    assert recipes_per_week
    assert serving

    db.user_update(user.id, int(recipes_per_week), int(serving))
    flash("Settings updated", "info")

    return redirect(url_for("user.user_get", user_id=user_id))


@blueprint.route("/<int:user_id>/leaflet", methods=["POST"])
@authenticated_resource
def leaflet_post(user_id):
    db = database.get()
    lm = leaflet_manager.get()
    user = db.user_get_by_id(user_id)

    if not user:
        abort(404)

    if not user.can_view():
        abort(403)

    leaflet = lm.generate(user)
    leaflet_id = lm.save(leaflet)
    lm.send(leaflet)
    flash("We sent you a new leaflet", "info")

    return redirect(url_for("user.leaflet_get", user_id=user_id, leaflet_id=leaflet_id))


@blueprint.route("/<int:user_id>/leaflet/<leaflet_id>", methods=["get"])
@authenticated_resource
def leaflet_get(user_id, leaflet_id):
    db = database.get()
    lm = leaflet_manager.get()
    user = db.user_get_by_id(user_id)

    if not user:
        abort(404)

    if not user.can_view():
        abort(403)

    leaflet = lm.get(user, leaflet_id)

    return render_template("leaflet.html", leaflet=leaflet)
