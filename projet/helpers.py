import secrets
import os 
from PIL import Image
from flask import current_app

def save_picture(form_picture, path, output_size=None): #path : sous-dossier où l’image sera enregistrée.
    random_hex = secrets.token_hex(8) # form_picture : l’image envoyée via le formulaire.
    _, f_ext = os.path.splitext(form_picture.filename) #output_size : dimensions cibles pour redimensionner l’image.
    picture_name = random_hex + f_ext # Crée un nom de fichier unique et Conserve l’extension originale de l’image.
    picture_path = os.path.join(current_app.root_path, path, picture_name) # Crée le chemin complet pour enregistrer l’image.
    i = Image.open(form_picture)
    if output_size: # Si une taille est fournie, l’image est redimensionnée (proportionnellement) à output_size.
        i.thumbnail(output_size)
    i.save(picture_path) # Enregistre l’image dans le chemin spécifié.
    return picture_name # Renvoie le nom de fichier de l’image enregistrée.



import os

def delete_picture(filename, path):
    """
    Supprime une image du disque si elle existe.

    :param filename: nom du fichier à supprimer (ex: "image.jpg")
    :param path: dossier relatif dans lequel se trouve le fichier (ex: "static/recette_thumbnails")
    """
    if filename:
        full_path = os.path.join(current_app.root_path, path, filename)
        if os.path.exists(full_path):
            os.remove(full_path)
