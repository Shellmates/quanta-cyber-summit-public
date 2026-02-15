"""
Secret Vault - Challenge web CTF (difficulté moyenne).
Application Flask avec authentification JWT volontairement vulnérable
à l'algorithme "none".
"""

import os
import jwt
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Clé utilisée pour signer les JWT (côté serveur)
JWT_SECRET = os.environ.get("JWT_SECRET", "vault-secret-key-2024")

FLAG = os.environ.get("FLAG", "shellmates{jwt_n0n3_4lg_1s_d4ng3r0us}")


def create_token(username: str, role: str) -> str:
    """Crée un JWT signé avec HS256."""
    payload = {"user": username, "role": role}
    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256",
    )


def decode_token_vulnerable(token: str):
    """
    Décode et vérifie le JWT.
    Comportement vulnérable : si alg est "none", la signature n'est pas vérifiée.
    (Simule une mauvaise configuration courante dans des librairies JWT.)
    """
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")

        if alg == "none" or alg == "None":
            # Comportement vulnérable : accepter sans vérifier la signature
            return jwt.decode(
                token,
                options={"verify_signature": False},
            )
        # Comportement normal : vérifier avec la clé
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
        )
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Décorateur : exige un JWT valide dans Authorization: Bearer."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Token manquant. Utilise Authorization: Bearer <token>"}), 401
        token = auth[7:]
        payload = decode_token_vulnerable(token)
        if not payload:
            return jsonify({"error": "Token invalide ou expiré"}), 401
        request.jwt_payload = payload
        return f(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    """Page d'accueil avec lien vers la zone de login."""
    return """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Secret Vault</title></head>
    <body>
    <h1>Secret Vault</h1>
    <p>Seuls les administrateurs peuvent accéder au coffre.</p>
    <p><a href="/login">Se connecter</a></p>
    </body>
    </html>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    """Formulaire de login et génération du JWT (role: user)."""
    if request.method == "GET":
        return """
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Login - Secret Vault</title></head>
        <body>
        <h1>Connexion</h1>
        <form method="POST">
            <label>Utilisateur: <input name="username" type="text" /></label><br/>
            <label>Mot de passe: <input name="password" type="password" /></label><br/>
            <button type="submit">Se connecter</button>
        </form>
        </body>
        </html>
        """
    username = request.form.get("username", "").strip() or "guest"
    # On accepte n'importe quel mot de passe pour simplifier le challenge
    token = create_token(username, "user")
    return jsonify({"token": token, "message": "Connecté en tant qu'utilisateur."})


@app.route("/admin")
@require_auth
def admin():
    """Zone admin : retourne le flag si role == admin."""
    if request.jwt_payload.get("role") != "admin":
        return jsonify({"error": "Accès réservé aux administrateurs."}), 403
    return jsonify({"flag": FLAG, "message": "Bien joué."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
