from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
# ❌ On supprime l'import direct de Plat pour éviter les imports circulaires
# from projet.models import Plat

from wtforms import StringField, SubmitField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, Length

# ✅ Import local de Plat à l'intérieur de la fonction
# Cela évite que models.py et forms.py s'importent mutuellement au démarrage
def choice_query():
    from projet.models import Plat
    return Plat.query

class NewRecetteForm(FlaskForm):
    # Utilise la fonction choice_query() qui importe Plat au bon moment
    plat = QuerySelectField("Plat", query_factory=choice_query, get_label="title")
    title = StringField("Titre de la Recette", validators=[DataRequired(), Length(max=100)])
    slug = StringField(
        "Slug",
        validators=[DataRequired(), Length(max=32)],
        render_kw={
            "placeholder": "Version courte et descriptive de notre titre. Optimisé pour le référencement"
        },
    )
    content = CKEditorField(
        "Contenu de la Recette", validators=[DataRequired()], render_kw={"rows": "20"}
    )
    thumbnail = FileField(
        "Thumbnail", validators=[DataRequired(), FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Post")

class RecetteUpdateForm(NewRecetteForm):
    # Rend le thumbnail optionnel à la mise à jour
    thumbnail = FileField("Thumbnail", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField("Update")

# Formulaire pour les commentaires des utilisateurs
class CommentForm(FlaskForm):
    content = TextAreaField("Votre commentaire", validators=[DataRequired()])
    submit = SubmitField("Publier")
