from flask import Blueprint, redirect, url_for, flash, render_template, abort
from projet import admin, db
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_admin import AdminIndexView
from functools import wraps

adminbp = Blueprint("adminbp", __name__)

# -------------------------
# Classe personnalisée pour sécuriser l'accès à l'interface Admin
# -------------------------
class MyModelView(ModelView):
    def is_accessible(self):
        # Seul l'utilisateur avec l'ID 1 peut accéder à l'admin
        return current_user.is_authenticated and current_user.id == 1

# -------------------------
# Classe personnalisée pour désactiver l'accès à l'index de l'admin
# -------------------------
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return False

# -------------------------
# Import des modèles déplacé ici pour éviter les imports circulaires
# -------------------------
from projet.models import User, Recette, Plat

# Ajout des vues admin pour les modèles User, Recette et Plat
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Recette, db.session))
admin.add_view(MyModelView(Plat, db.session))

# -------------------------
# Décorateur : Autorise uniquement les administrateurs à accéder aux routes protégées
# -------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Refus d'accès
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
# Route : Liste des recettes en attente de validation
# -------------------------
@adminbp.route('/admin/recettes_en_attente')
@admin_required
def recettes_en_attente():
    from projet.models import Recette  # import local pour éviter les boucles
    recettes = Recette.query.filter_by(is_approved=False).all()
    return render_template('admin/recettes_en_attente.html', recettes=recettes)

# -------------------------
# Route : Valider une recette spécifique
# -------------------------
@adminbp.route('/admin/approve_recette/<int:recette_id>')
@admin_required
def approve_recette(recette_id):
    from projet.models import Recette  # import local ici aussi
    recette = Recette.query.get_or_404(recette_id)
    recette.is_approved = True
    db.session.commit()
    flash("Recette approuvée avec succès.", "success")
    return redirect(url_for('recettes_en_attente'))
