from flask import Blueprint
import secrets
import os
from projet.models import Recette, Plat
from flask_ckeditor import upload_success, upload_fail
from flask import (
    render_template,
    url_for,
    request,
    send_from_directory,
)
from flask import current_app
from sqlalchemy import or_




main = Blueprint("main", __name__)


@main.route("/files/<path:filename>")
def uploaded_files(filename):
    path = os.path.join(current_app.root_path, "static/media")
    return send_from_directory(path, filename)


@main.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("upload")
    extension = f.filename.split(".")[-1].lower()
    if extension not in ["jpg", "gif", "png", "jpeg"]:
        return upload_fail(message="Cette extension de fichier non autorisée!")
    random_hex = secrets.token_hex(8)
    image_name = random_hex + extension
    f.save(os.path.join(current_app.root_path, "static/media", image_name))
    url = url_for("main.uploaded_files", filename=image_name)
    return upload_success(url, filename=image_name)

@main.route("/", methods=["GET"])
@main.route("/home", methods=["GET"])
def home():
    page = request.args.get("page", 1, type=int)
    recherche = request.args.get("recherche", "").strip()

    if recherche:
        recettes = Recette.query.filter(
            Recette.is_approved == True,
            or_(
                Recette.title.ilike(f"%{recherche}%"),
                Recette.content.ilike(f"%{recherche}%")
            )
        ).order_by(Recette.date_posted.desc()).paginate(page=page, per_page=6)
    else:
        recettes = Recette.query.filter_by(
            is_approved=True
        ).order_by(Recette.date_posted.desc()).paginate(page=page, per_page=6)

    plats = Plat.query.paginate(page=1, per_page=6)
    return render_template("home.html", recettes=recettes, plats=plats, recherche=recherche)





@main.route("/about")
def about():
    return render_template("about.html", title="About")
