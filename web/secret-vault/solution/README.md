# Secret Vault

## Write-up

Ce challenge met en scène une **vulnérabilité classique sur les JWT** : l’acceptation de l’algorithme `"none"` sans vérification de signature.

### Étapes de résolution

1. **Exploration**  
   - Aller sur `/login`, se connecter avec n’importe quel identifiant/mot de passe.  
   - Le serveur renvoie un **token JWT** (champ `token` dans la réponse JSON).

2. **Comprendre le flux**  
   - L’endpoint `/admin` exige un en-tête `Authorization: Bearer <token>`.  
   - Si on envoie le token reçu après login, la réponse indique que l’accès est réservé aux administrateurs : le JWT contient `role: "user"`.

3. **Vulnérabilité**  
   - Le serveur décode le JWT et, si l’en-tête indique l’algorithme `"none"`, il **ne vérifie pas la signature** et accepte le payload tel quel.  
   - Il suffit de forger un JWT avec :
     - **Header** : `{"alg": "none", "typ": "JWT"}`  
     - **Payload** : `{"user": "admin", "role": "admin"}`  
     - **Signature** : vide (ou une chaîne vide, selon la librairie).

4. **Construction du token**  
   - Encoder en base64url (sans padding) :
     - `header` = `eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0`
     - `payload` = `eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ`
   - Token complet (3 parties séparées par `.` ; la signature peut être vide) :  
     `eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4ifQ.`

5. **Exploitation**  
   - Envoyer une requête à `/admin` avec :  
     `Authorization: Bearer <token_forgé>`  
   - Le serveur accepte le payload et voit `role: "admin"`, puis renvoie le flag dans la réponse JSON.

### Concept mis en avant

Ne **jamais** faire confiance à l’algorithme indiqué dans le JWT pour décider de vérifier ou non la signature. Toujours imposer une liste d’algorithmes autorisés (par ex. uniquement `HS256`) et vérifier la signature avec la clé prévue. Sinon, un attaquant peut forger un token avec `alg: "none"` et un payload arbitraire.

## Flag

`shellmates{jwt_n0n3_4lg_1s_d4ng3r0us}`
