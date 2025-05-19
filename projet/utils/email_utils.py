from flask_mail import Message
from flask import current_app
from projet import mail

def envoyer_mail_nouvelle_recette(recette, destinataire):
    sujet = "Nouvelle recette en attente de validation"
    corps = f"""
Bonjour Admin,

Une nouvelle recette intitulée "{recette.title}" a été ajoutée par {recette.author.username}.
Elle est en attente de validation.

Vous pouvez la valider depuis l'administration du site.

Lien : http://localhost:5000/recettes_en_attente

Merci,
L'équipe Imakaina
"""
    msg = Message(subject=sujet, recipients=[destinataire], body=corps)
    mail.send(msg)
