# Guide Multi-Comptes Geo-Agile

## Vue d'ensemble

La version multi-comptes de Geo-Agile permet de gérer plusieurs comptes Starlink simultanément avec :
- Chiffrement sécurisé des mots de passe
- Configuration personnalisée par compte
- Logs séparés par compte
- Statistiques détaillées par compte

## Sécurité

### Chiffrement des Mots de Passe

Les mots de passe sont chiffrés avec **Fernet** (symmetric encryption) :
- Une clé de chiffrement est générée automatiquement au premier lancement
- La clé est stockée dans `.key` avec des permissions restrictives (600)
- Les mots de passe chiffrés sont stockés dans `accounts.json`

⚠️ **IMPORTANT** :
- Ne partagez **JAMAIS** le fichier `.key`
- Ne commitez **JAMAIS** `accounts.json` ou `.key` dans Git
- Ces fichiers sont déjà dans `.gitignore`

### Permissions des Fichiers

Les fichiers sensibles ont des permissions restrictives :
- `.key` : 600 (lecture/écriture propriétaire uniquement)
- `accounts.json` : 600 (lecture/écriture propriétaire uniquement)

## Gestion des Comptes

### Ajouter un Compte

```bash
python cli.py add
```

Exemple d'interaction :
```
=== Ajout d'un nouveau compte Starlink ===
Email du compte Starlink: user@example.com
Mot de passe: ********

--- Configuration optionnelle ---
Seuil de distance pour mise à jour (km) [50]: 75
Mode headless (o/N) [O]: o
Nombre max de tentatives [3]: 5

✅ Compte user@example.com ajouté avec succès!
```

### Configuration par Compte

Chaque compte peut avoir sa propre configuration :

- **update_threshold_km** : Distance minimale pour déclencher une mise à jour (défaut: 50.0 km)
- **headless** : Mode navigateur headless (défaut: True)
- **max_retries** : Nombre maximum de tentatives (défaut: 3)
- **initial_retry_delay** : Délai initial avant retry (défaut: 5.0s)
- **max_retry_delay** : Délai maximum entre retries (défaut: 60.0s)
- **enabled** : Activer/désactiver le compte (défaut: True)

### Activer/Désactiver un Compte

```bash
# Désactiver temporairement un compte
python cli.py disable user@example.com

# Réactiver un compte
python cli.py enable user@example.com
```

Les comptes désactivés sont ignorés lors de l'exécution de `main_multi.py`.

## Logs et Traçabilité

### Logs Séparés

Chaque compte a son propre fichier de log dans `logs/` :
- Format : `{email_safe}.log`
- Exemple : `user_at_example_com.log`

Les logs contiennent :
- Toutes les opérations pour ce compte
- Coordonnées GPS exactes
- Adresses résolues
- Erreurs et warnings
- Historique des exécutions

### États par Compte

Chaque compte a son propre fichier d'état dans `states/` :
- Format : `{email_safe}.json`
- Contient : dernière position, dernière adresse, historique des exécutions

## Statistiques

### Statistiques par Compte

Chaque compte maintient ses propres statistiques :

```bash
python cli.py stats user@example.com
```

Affiche :
- Total d'exécutions
- Nombre de succès
- Nombre d'échecs
- Taux de succès
- Dernier succès/échec

### Statistiques Globales

```bash
python cli.py stats
```

Affiche les statistiques agrégées de tous les comptes.

## Exécution

### Traitement de Tous les Comptes

```bash
python main_multi.py
```

Le script :
1. Charge tous les comptes actifs depuis `accounts.json`
2. Traite chaque compte séquentiellement
3. Génère des logs séparés
4. Met à jour les statistiques
5. Affiche un résumé final

### Résumé d'Exécution

À la fin de chaque exécution, un résumé est affiché :

```
============================================================
Résumé de l'exécution
============================================================
✅ Succès: 2
❌ Échecs: 1
📊 Total: 3

Comptes en échec:
  - user3@example.com
```

## Structure des Données

### accounts.json

```json
{
  "user@example.com": {
    "email": "user@example.com",
    "password_encrypted": "gAAAAABh...",
    "enabled": true,
    "update_threshold_km": 50.0,
    "headless": true,
    "max_retries": 3,
    "created_at": "2024-01-01T00:00:00",
    "last_run": "2024-01-15T10:30:00",
    "stats": {
      "total_runs": 15,
      "successful_updates": 12,
      "failed_updates": 3,
      "last_success": "2024-01-15T10:30:00",
      "last_failure": "2024-01-10T08:15:00"
    }
  }
}
```

### État d'un Compte (states/{email}.json)

```json
{
  "last_pos": [48.8584, 2.2945],
  "last_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France",
  "last_updated": 1705312200.0,
  "last_updated_iso": "2024-01-15T10:30:00",
  "execution_history": [...]
}
```

## Bonnes Pratiques

1. **Sauvegarde régulière** : Sauvegardez `accounts.json` et `.key` dans un endroit sécurisé
2. **Rotation des logs** : Les logs peuvent devenir volumineux, envisagez une rotation
3. **Monitoring** : Surveillez les statistiques pour détecter les problèmes
4. **Tests** : Testez avec un compte en mode non-headless avant de passer en production
5. **Sécurité** : Ne partagez jamais les fichiers de clés ou de comptes

## Dépannage

### Problème : "Aucun compte actif trouvé"

Solution : Vérifiez que vous avez ajouté des comptes avec `python cli.py add`

### Problème : "Erreur lors du déchiffrement"

Solution : Vérifiez que le fichier `.key` existe et n'a pas été modifié

### Problème : "Permission denied" sur `.key` ou `accounts.json`

Solution : Vérifiez les permissions (devrait être 600) :
```bash
chmod 600 .key accounts.json
```

### Problème : Logs non générés

Solution : Vérifiez que le répertoire `logs/` existe et est accessible en écriture
