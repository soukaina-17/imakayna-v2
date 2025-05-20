# Import des modules nécessaires de Flask, des modèles, des formulaires et des fonctions personnalisées
from flask import Blueprint, render_template, url_for, flash, redirect, request, session, abort, current_app
from projet.models import Recette, Plat, Comment
from projet.recettes.forms import NewRecetteForm, RecetteUpdateForm, CommentForm
from projet.plats.forms import NewPlatForm
from projet import db
from flask_modals import render_template_modal
from flask_login import login_required, current_user
from projet.helpers import save_picture
from projet.recettes.helpers import get_precedent_suivant_recette, delete_picture
from projet.utils.email_utils import envoyer_mail_nouvelle_recette

# Création du Blueprint pour les routes liées aux recettes
recettes = Blueprint("recettes", __name__)

# ================================
# Création d'une recette ou d’un plat
# ================================
@recettes.route("/dashboard/new_recette", methods=["GET", "POST"])
@login_required  # Nécessite que l'utilisateur soit connecté
def new_recette():
    new_recette_form = NewRecetteForm()  # Formulaire pour ajouter une recette
    new_plat_form = NewPlatForm()        # Formulaire pour ajouter un plat
    form = ""
    flag = session.pop("flag", False)    # Indique si un plat a été ajouté pour ne pas rouvrir le modal

    # Détermine quel formulaire a été soumis
    if "content" in request.form:
        form = "new_recette_form"
    elif "description" in request.form:
        form = "new_plat_form"

    # Formulaire recette
    if form == "new_recette_form" and new_recette_form.validate_on_submit():
        picture_file = save_picture(new_recette_form.thumbnail.data, "static/recette_thumbnails") if new_recette_form.thumbnail.data else None
        recette_slug = str(new_recette_form.slug.data).replace(" ", "-")
        plat = new_recette_form.plat.data

        recette = Recette(
            title=new_recette_form.title.data,
            content=new_recette_form.content.data,
            slug=recette_slug,
            author=current_user,
            plat_name=plat,
            thumbnail=picture_file,
            is_approved=False,  # ➤ Pas encore validée
        )

        db.session.add(recette)
        db.session.commit()

        # Envoi email de notification (admin)
        envoyer_mail_nouvelle_recette(recette, current_app.config["MAIL_USERNAME"])

        flash("Votre recette a bien été créée ! Elle sera publiée après validation.", "success")
        return redirect(url_for("recettes.new_recette"))

    #  Formulaire plat
    elif form == "new_plat_form" and new_plat_form.validate_on_submit():
        picture_file = save_picture(new_plat_form.icon.data, "static/plat_icons", output_size=(150, 150)) if new_plat_form.icon.data else None
        plat = Plat(
            title=new_plat_form.title.data,
            description=new_plat_form.description.data,
            icon=picture_file,
        )
        db.session.add(plat)
        db.session.commit()

        session["flag"] = True  # ➤ évite de rouvrir le modal
        flash("Ce nouveau plat a bien été créé !", "success")
        return redirect(url_for("users.dashboard"))

    # Modal affiché automatiquement si flag est désactivé
    modal = None if flag else "newPlat"
    return render_template_modal(
        "new_recette.html",
        title="New Recette",
        new_recette_form=new_recette_form,
        new_plat_form=new_plat_form,
        active_tab="new_recette",
        modal=modal,
    )

# ================================
# Affichage d’une recette + commentaires
# ================================
@recettes.route("/<string:plat>/<string:recette_slug>", methods=["GET", "POST"])
def recette(plat, recette_slug):
    recette = Recette.query.filter_by(slug=recette_slug).first_or_404()

    # Empêche l'accès si la recette n'est pas encore approuvée (sauf admin)
    if not recette.is_approved and (not current_user.is_authenticated or not current_user.is_admin):
        abort(403)

    precedent_recette, suivant_recette = get_precedent_suivant_recette(recette)
    form = CommentForm()

    if form.validate_on_submit():
        commentaire = Comment(
            content=form.content.data,
            user_id=current_user.id,
            recette_id=recette.id
        )
        db.session.add(commentaire)
        db.session.commit()
        flash("Votre commentaire a été publié avec succès.", "success")
        return redirect(url_for("recettes.recette", plat=plat, recette_slug=recette.slug))

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

# ================================
# Recettes de l’utilisateur connecté
# ================================
@recettes.route("/dashboard/user_recettes")
@login_required
def user_recettes():
    if current_user.is_admin:
        # Affiche les recettes créées par l’admin
        recettes = Recette.query.filter_by(author=current_user).order_by(Recette.date_posted.desc()).all()
    else:
        # Affiche les recettes de l’utilisateur, même refusées, avec leur statut
        recettes = Recette.query.filter_by(author=current_user).order_by(Recette.date_posted.desc()).all()
        
    return render_template("user_recettes.html", title="Mes recettes", recettes=recettes, active_tab="user_recettes")

# ================================
# Suppression d'une recette
# ================================
@recettes.route("/recette/delete/<int:recette_id>", methods=["POST"])
@login_required
def delete_recette(recette_id):
    recette = Recette.query.get_or_404(recette_id)

    # Seul l'auteur ou un admin peut supprimer
    if recette.author != current_user and not current_user.is_admin:
        abort(403)

    # Supprimer l’image associée si présente
    if recette.thumbnail:
        delete_picture("static/recette_thumbnails/" + recette.thumbnail)

    db.session.delete(recette)
    db.session.commit()
    flash("Recette supprimée avec succès.", "success")
    return redirect(url_for("recettes.user_recettes"))

# voir les recettes en attente

@recettes.route("/admin/recettes_a_valider")
@login_required
def recettes_a_valider():
    # Vérifie que l'utilisateur est un administrateur
    if not current_user.is_admin:
        abort(403)

    # Récupère les recettes non validées
    recettes = Recette.query.filter_by(is_approved=False).order_by(Recette.date_posted.desc()).all()
    return render_template("admin/recettes_a_valider.html", recettes=recettes, title="Recettes à valider")

# Route pour valider une recette
@recettes.route("/admin/valider_recette/<int:recette_id>", methods=["POST"])
@login_required
def valider_recette(recette_id):
    if not current_user.is_admin:
        abort(403)

    recette = Recette.query.get_or_404(recette_id)
    recette.is_approved = True
    recette.motif_refus = None
    db.session.commit()
    flash("Recette validée avec succès.", "success")
    return redirect(url_for("recettes.recettes_a_valider"))

# ================================
# Modification d'une recette
# ================================
@recettes.route("/recette/update/<string:recette_slug>/<string:plat>", methods=["GET", "POST"])
@login_required
def update_recette(recette_slug, plat):
    recette = Recette.query.filter_by(slug=recette_slug).first_or_404()

    # Seul l'auteur ou un admin peut modifier
    if recette.author != current_user and not current_user.is_admin:
        abort(403)

    form = RecetteUpdateForm(obj=recette)

    if form.validate_on_submit():
        recette.title = form.title.data
        recette.content = form.content.data

        # Met à jour l'image si une nouvelle a été envoyée
        if form.thumbnail.data:
            if recette.thumbnail:
                delete_picture("static/recette_thumbnails/" + recette.thumbnail)
            recette.thumbnail = save_picture(form.thumbnail.data, "static/recette_thumbnails")

        db.session.commit()
        flash("Recette mise à jour avec succès.", "success")
        return redirect(url_for("recettes.user_recettes"))

    return render_template("edit_recette.html", title="Modifier recette", form=form, recette=recette)

@recettes.route("/admin/refuser_recette/<int:recette_id>", methods=["POST"])
@login_required
def refuser_recette(recette_id):
    if not current_user.is_admin:
        abort(403)

    recette = Recette.query.get_or_404(recette_id)
    motif = request.form.get("motif")

    if not motif:
        flash("Veuillez fournir un motif de refus.", "danger")
        return redirect(url_for("recettes.recettes_a_valider"))

    recette.is_approved = False  # La recette reste non approuvée
    recette.motif_refus = motif
    db.session.commit()

    flash("Recette refusée avec motif. Elle reste cachée.", "warning")
    return redirect(url_for("recettes.recettes_a_valider"))
