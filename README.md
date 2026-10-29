# MiniLien — Python / Django

MiniLien est un petit service de raccourcissement d'URL : on lui donne une adresse longue, il renvoie un lien court
(`http://localhost:8080/r/aZ3k9Q`) qui redirige vers l'adresse d'origine et compte les visites.

Le périmètre est volontairement réduit. L'application fonctionne en local sur votre poste, **et c'est tout** :
pas de conteneur, pas d'automatisation, pas de monitoring. C'est à vous de les ajouter.

## Prérequis

- Python 3.14 (3.12 minimum)

## Lancer l'application

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

(Sous Windows : `.venv\Scripts\activate`)

```bash
pip install -r requirements.txt
```

```bash
python manage.py runserver 8080
```

L'application répond sur http://localhost:8080.

## Lancer les tests

```bash
python manage.py test
```

ou, de façon équivalente :

```bash
pytest
```

## L'API

| Méthode | Route | Rôle | Réponses |
|---|---|---|---|
| `POST` | `/api/liens` | Crée un lien court. Corps : `{"url": "https://..."}` | `201` + lien ; `400` |
| `GET` | `/api/liens` | Liste les liens, du plus récent au plus ancien | `200` |
| `GET` | `/api/liens/{code}` | Détail d'un lien, avec son nombre de visites | `200` ; `404` |
| `DELETE` | `/api/liens/{code}` | Supprime un lien. En-tête `X-Admin-Token` obligatoire | `204` ; `401` ; `404` |
| `GET` | `/r/{code}` | Redirige vers l'URL d'origine et compte la visite | `302` ; `404` |

Les erreurs ont toujours le même format : `{"code": "URL_INVALIDE", "message": "..."}`.
Codes possibles : `REQUETE_INVALIDE`, `URL_INVALIDE`, `LIEN_INTROUVABLE`, `ACCES_REFUSE`.

Les liens sont gardés **en mémoire** : ils disparaissent quand l'application redémarre. Il n'y a pas de base de données.

Cette mémoire est propre à chaque processus : servez l'application avec un seul worker gunicorn (la valeur par défaut). Pour traiter plusieurs requêtes en parallèle, augmentez le nombre de threads (`--threads`), qui partagent la même mémoire.

### Essayer avec curl

```bash
curl -i -X POST http://localhost:8080/api/liens -H "Content-Type: application/json" -d '{"url": "https://openclassrooms.com"}'
```

```bash
curl -i http://localhost:8080/r/<code>
```

```bash
curl http://localhost:8080/api/liens
```

## Configuration

La configuration se trouve dans `minilien/settings.py` : `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, adresse publique des liens courts (`MINILIEN_BASE_URL`) et jeton d'administration (`MINILIEN_ADMIN_TOKEN`).

`runserver` est le serveur de développement de Django : il ne doit pas servir l'application en production.

## Organisation du code

```
manage.py
minilien/          configuration du projet Django (settings, urls, wsgi)
links/
├── views.py       routes /api/liens et /r/{code}
├── store.py       création, recherche, visites (stockage en mémoire)
├── urls.py
└── tests.py       tests de l'API
```
