# Guide de Démarrage Rapide - Geo-Agile Multi-Comptes

## Installation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Installer Playwright
playwright install chromium
```

## Première Utilisation

### Étape 1 : Ajouter votre premier compte

```bash
python cli.py add
```

Suivez les instructions pour :
- Entrer votre email Starlink
- Entrer votre mot de passe (sera chiffré automatiquement)
- Configurer les paramètres (ou utiliser les valeurs par défaut)

### Étape 2 : Vérifier que le compte est bien ajouté

```bash
python cli.py list
```

### Étape 3 : Exécuter pour la première fois

```bash
python main_multi.py
```

Le script va :
- Récupérer la position GPS de votre Dish
- Calculer la distance depuis la dernière position
- Mettre à jour l'adresse si nécessaire
- Générer des logs dans `logs/`

## Commandes Essentielles

```bash
# Ajouter un compte
python cli.py add

# Lister tous les comptes
python cli.py list

# Voir les statistiques
python cli.py stats

# Exécuter pour tous les comptes actifs
python main_multi.py
```

## Migration depuis l'Ancien Système

Si vous utilisiez l'ancien système avec `.env` :

```bash
python migrate_to_multi.py
```

Ce script va migrer automatiquement votre compte depuis `.env` vers le nouveau système.

## Structure des Fichiers Créés

Après la première utilisation, vous aurez :

```
geo_agile/
├── accounts.json          # Vos comptes (chiffrés)
├── .key                   # Clé de chiffrement (NE PAS PARTAGER!)
├── states/                # États par compte
│   └── user_at_example_com.json
└── logs/                  # Logs par compte
    └── user_at_example_com.log
```

## Sécurité

⚠️ **IMPORTANT** :
- Le fichier `.key` contient la clé de déchiffrement
- Ne partagez **JAMAIS** ce fichier
- Ne commitez **JAMAIS** `accounts.json` ou `.key` dans Git
- Ces fichiers sont déjà dans `.gitignore`

## Automatisation

Pour exécuter automatiquement tous les jours à 2h du matin :

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne :
0 2 * * * cd /path/to/geo_agile && /usr/bin/python3 main_multi.py >> /var/log/geo_agile.log 2>&1
```

## Aide

Pour voir toutes les commandes disponibles :

```bash
python cli.py --help
```

Pour chaque commande :

```bash
python cli.py <commande> --help
```

## Dépannage

### "Aucun compte actif trouvé"

→ Ajoutez un compte avec `python cli.py add`

### "Erreur lors du déchiffrement"

→ Vérifiez que `.key` existe et n'a pas été modifié

### "Permission denied"

→ Vérifiez les permissions : `chmod 600 .key accounts.json`

### Problèmes de connexion au Dish

→ Vérifiez que :
- Le Dish est allumé et accessible sur `192.168.100.1`
- L'accès réseau local est activé dans l'app Starlink

## Support

Pour plus de détails, consultez :
- `README.md` : Documentation complète
- `MULTI_ACCOUNTS.md` : Guide détaillé multi-comptes
