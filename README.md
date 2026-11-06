# mon projet API Bibliothèque (FastAPI + SQLite)

API REST qui gère des livres (titre, auteur, année, genre) 
ajouter, lister, lire, modifier, supprimer

## pour l'Installation j'ai utlisé
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt


# j'ai lancé avec 
fastapi dev main.py

le Serveur : http://127.0.0.1:8000

la base `biblio.db` j'ai fais que en sorte que ça soit créée automatiquement au démarrage.

Erreurs : 404 signifie (livre introuvable), 422 signifie (données invalides).

## Choix de conception

- Deux modèles Pydantic : `LivreIn` (entrée, sans id) et `Livre` (sortie, avec id).
- Requêtes SQL paramétrées (`?`).
- Connexion SQLite fournie par une dépendance `get_db`, toujours fermée (`finally`).
- j'ai fais la Création de la table au démarrage grâce à lifespan.
- Fonction lire_ou_404 réutilisée par GET, PUT et DELETE.
