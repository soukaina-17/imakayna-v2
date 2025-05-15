from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
)

class NewPlatForm(FlaskForm):
    title = StringField("Le nom du Plat", validators=[DataRequired(), Length(max=50)])
    description = TextAreaField(
        "Description du Plat", validators=[DataRequired(), Length(max=150)]
    )
    icon = FileField("Icon", validators=[DataRequired(), FileAllowed(["jpg", "png"])])
    submit = SubmitField("Create")

    # ✅ Vérification personnalisée du titre, avec import local pour éviter un import circulaire
    def validate_title(self, title):
        from projet.models import Plat  # ✅ Import placé ici pour casser la boucle circulaire
        course = Plat.query.filter_by(title=title.data).first()
        if course:
            raise ValidationError(
                "Ce nom de plat existe déjà ! Veuillez en choisir un autre."
            )
