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
from app import recipe_manager
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

    digest_times = db.digest_get_all_by_user(user_id)

    return render_template("user.html", user=user, digests=digest_times)


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

    flash("Settings updated", "info")

    return redirect(url_for("user.user_get", user_id=user_id))


@blueprint.route("/<int:user_id>/digest", methods=["POST"])
@authenticated_resource
def digest_new(user_id):
    db = database.get()
    rm = recipe_manager.get()
    user = db.user_get_by_id(user_id)

    if not user:
        abort(404)

    if not user.can_view():
        abort(403)

    digest = rm.get_digest(user)
    rm.save_digest(digest)

    flash("We sent you a new digest", "info")

    return render_template("digest.html", digest=digest)
