from flask import Blueprint, render_template, abort, flash
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

    return render_template("user.html", user=user)


@blueprint.route("/<int:user_id>/digest", methods=["POST"])
@authenticated_resource
def new_digest(user_id):
    db = database.get()
    rm = recipe_manager.get()
    user = db.user_get_by_id(user_id)

    if not user:
        abort(404)

    if not user.can_view():
        abort(403)

    digest = rm.get_digest(user)
    rm.save_digest(digest)

    flash("Sent you a new digest")
    return render_template("user.html", user=user)
