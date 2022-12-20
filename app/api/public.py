from flask import (
    session,
    redirect,
    url_for,
    Blueprint,
    render_template,
)

blueprint = Blueprint("public", __name__)

@blueprint.route("/faq", methods=["GET"])
def faq_get():

    faqs = [(
        "What is this?", "Leaflet is a simple tool to help you eat more plant based meals week on week. You give it a few details about how many recipes you'd like to receive per week and the serving size of each meal. It will then send you a weekly \"leaflet\", a randomly selected set of simple recipes along with a combined shopping list."
    ), (
        "Why did you make this?", "I grew up in South Africa, a country like many others, whose cuisine is dominated by meat. As I was transitioning to a plant based diet I didn't have any vegetarian recipes to fallback on. I found learning a totally new set of \"go-to\" recipes daunting. I'm hoping this helps others in a similar spot."
    ), (
        "Where do the recipes come from?", "Most of them are directly taken or adapted from <a href=\"https://www.bbcgoodfood.com\" target=\"_blank\">BBC goodfood</a>(), but you can send me more that you like leaflet@craigmulligan.com"
    )]

    return render_template("faq.html", faqs=faqs)

@blueprint.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("user.user_get", user_id=session["user_id"]))

    return redirect(url_for("auth.signin_get"))
