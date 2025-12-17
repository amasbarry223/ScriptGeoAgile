# Rendre le Dépôt GitHub Public

## Méthode 1 : Via l'Interface Web GitHub (Recommandé)

1. **Accédez à votre dépôt :**
   - Allez sur : https://github.com/amasbarry223/ScriptGeoAgile

2. **Accédez aux paramètres :**
   - Cliquez sur l'onglet **"Settings"** (en haut du dépôt)

3. **Changez la visibilité :**
   - Faites défiler jusqu'à la section **"Danger Zone"** (en bas de la page)
   - Cliquez sur **"Change visibility"**
   - Sélectionnez **"Make public"**
   - Confirmez en tapant le nom du dépôt : `amasbarry223/ScriptGeoAgile`

4. **Confirmez :**
   - Cliquez sur **"I understand, change repository visibility"**

## Méthode 2 : Via GitHub CLI (si installé)

```bash
gh repo edit amasbarry223/ScriptGeoAgile --visibility public
```

## Vérification

Une fois fait, votre dépôt sera accessible publiquement à :
**https://github.com/amasbarry223/ScriptGeoAgile**

## ⚠️ Important - Sécurité

Avant de rendre le dépôt public, assurez-vous que :

✅ **Fichiers sensibles exclus** (vérifié dans `.gitignore`) :
- `accounts.json` - Mots de passe chiffrés
- `.key` - Clé de chiffrement
- `states/` - États par compte
- `logs/` - Logs par compte
- `.env` - Variables d'environnement

✅ **Aucune information sensible dans le code** :
- Pas de mots de passe en dur
- Pas de clés API exposées
- Pas de données personnelles

Le projet est **sécurisé** pour être rendu public car tous les fichiers sensibles sont dans `.gitignore`.
