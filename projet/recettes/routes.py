from flask import Blueprint
from projet.models import Recette, Plat, Comment
from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    session,
    abort,
)
from projet.recettes.forms import (
    NewRecetteForm,
    RecetteUpdateForm,
    CommentForm,
)
from projet.plats.forms import NewPlatForm
from projet import db
from flask_modals import render_template_modal
from flask_login import (
    login_required,
    current_user,
)
from projet.helpers import save_picture
from projet.recettes.helpers import get_precedent_suivant_recette, delete_picture

recettes = Blueprint("recettes", __name__)

# Route pour créer une nouvelle recette ou un nouveau plat
@recettes.route("/dashboard/new_recette", methods=["GET", "POST"])
@login_required
def new_recette():
    new_recette_form = NewRecetteForm()
    new_plat_form = NewPlatForm()
    form = ""
    flag = session.pop("flag", False)
    if "content" in request.form:
        form = "new_recette_form"
    elif "description" in request.form:
        form = "new_plat_form"

    if form == "new_recette_form" and new_recette_form.validate_on_submit():
        if new_recette_form.thumbnail.data:
            picture_file = save_picture(
                new_recette_form.thumbnail.data, "static/recette_thumbnails"
            )
        else:
            picture_file = None
        recette_slug = str(new_recette_form.slug.data).replace(" ", "-")
        plat = new_recette_form.plat.data
        recette = Recette(
            title=new_recette_form.title.data,
            content=new_recette_form.content.data,
            slug=recette_slug,
            author=current_user,
            plat_name=plat,
            thumbnail=picture_file,
            is_approved=False,  # Recette en attente de validation
        )
        db.session.add(recette)
        db.session.commit()
        flash("Votre recette a bien été créee!", "success")
        return redirect(url_for("recettes.new_recette"))

    elif form == "new_plat_form" and new_plat_form.validate_on_submit():
        if new_plat_form.icon.data:
            picture_file = save_picture(
                new_plat_form.icon.data, "static/plat_icons", output_size=(150, 150)
            )
        else:
            picture_file = None
        plat_title = str(new_plat_form.title.data).replace(" ", "-")
        plat = Plat(
            title=new_plat_form.title.data,
            description=new_plat_form.description.data,
            icon=picture_file,
        )
        db.session.add(plat)
        db.session.commit()
        session["flag"] = True
        flash("Ce nouveau plat a bien été crée!", "success")
        return redirect(url_for("users.dashboard"))

    modal = None if flag else "newPlat"
    return render_template_modal(
        "new_recette.html",
        title="New Recette",
        new_recette_form=new_recette_form,
        new_plat_form=new_plat_form,
        active_tab="new_recette",
        modal=modal,
    )

# Route pour afficher les détails d'une recette avec ses commentaires
@recettes.route("/<string:plat>/<string:recette_slug>", methods=["GET", "POST"])
def recette(plat, recette_slug):
    recette = Recette.query.filter_by(slug=recette_slug).first()
    if recette:
        precedent_recette, suivant_recette = get_precedent_suivant_recette(recette)
    else:
        recette_id = None
    recette = Recette.query.get_or_404(recette.id if recette else recette_id)

    form = CommentForm()

    # Traitement de l'envoi de commentaire
    if form.validate_on_submit():
        commentaire = Comment(
            content=form.content.data,
             user_id=current_user.id,
            recette_id=recette.id
        )
        db.session.add(commentaire)
        db.session.commit()
        flash("Votre commentaire a été publié avec succès.", "success")
        return redirect(url_for("recettes.recette", plat=plat, recette_slug=recette_slug))
    else:
        if request.method == "POST":
            flash("Erreur lors de la publication du commentaire.", "danger")
            print("form.errors:", form.errors)

    commentaires = Comment.query.filter_by(recette_id=recette.id).order_by(Comment.date_posted.desc()).all()

    return render_template(
        "recette_view.html",
        title=recette.title,
        recette=recette,
        precedent_recette=precedent_recette,
        suivant_recette=suivant_recette,
        form=form,
        commentaires=commentaires
    )

# Route pour afficher les recettes de l'utilisateur connecté
@recettes.route("/dashboard/user_recettes", methods=["GET", "POST"])
@login_required
def user_recettes():
    recettes_user = current_user.recettes
    return render_template(
        "user_recettes.html",
        title="Vos Recettes",
        active_tab="user_recettes",
        recettes=recettes_user,
    )

# Route pour mettre à jour une recette
@recettes.route("/<string:plat>/<string:recette_slug>/update", methods=["GET", "POST"])
@login_required
def update_recette(recette_slug, plat):
    recette = Recette.query.filter_by(slug=recette_slug).first()
    if recette:
        precedent_recette, suivant_recette = get_precedent_suivant_recette(recette)
    recette_id = recette.id if recette else None
    recette = Recette.query.get_or_404(recette_id)
    if recette.author != current_user:
        abort(403)
    form = RecetteUpdateForm()
    if form.validate_on_submit():
        recette.plat_name = form.plat.data
        recette.title = form.title.data
        recette.slug = str(form.slug.data).replace(" ", "-")
        recette.content = form.content.data
        if form.thumbnail.data:
            delete_picture(recette.thumbnail, "static/recette_thumbnails")
            new_picture = save_picture(form.thumbnail.data, "static/recette_thumbnails")
            recette.thumbnail = new_picture
        db.session.commit()
        flash("Votre recette a bien été modifiée!", "success")
        return redirect(
            url_for("recettes.recette", recette_slug=recette.slug, plat=recette.plat_name.title)
        )
    elif request.method == "GET":
        form.plat.data = recette.plat_name.title
        form.title.data = recette.title
        form.slug.data = recette.slug
        form.content.data = recette.content
    return render_template(
        "update_recette.html",
        title="Update | " + recette.title,
        recette=recette,
        precedent_recette=precedent_recette,
        suivant_recette=suivant_recette,
        form=form,
    )

# Route pour supprimer une recette
@recettes.route("/recette/<recette_id>/delete", methods=["POST"])
@login_required
def delete_recette(recette_id):
    recette = Recette.query.get_or_404(recette_id)
    if recette.author != current_user:
        abort(403)
    db.session.delete(recette)
    db.session.commit()
    flash("Votre recette a bien été supprimé!", "success")
    return redirect(url_for("recettes.user_recettes"))

# Route pour afficher toutes les recettes approuvées
@recettes.route('/recettes')
def all_recettes():
    recettes = Recette.query.filter_by(is_approved=True).all()
    return render_template('recettes.html', recettes=recettes)
