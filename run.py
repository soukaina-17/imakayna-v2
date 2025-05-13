from projet import create_app, db
from projet.models import Plat

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

#db.init_app(app)


with app.app_context():
    db.create_all()  # Crée les tables définies par les modèles
    print("Tables créées avec succès")


    plats = Plat.query.all()  # Récupère tous les plats et les affiche
    for plat in plats:
        print(plat.nom, plat.categorie)

    