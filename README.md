# Geo-Agile Starlink Automation - Multi-Comptes

**Geo-Agile** est un outil d'automatisation sophistiqué conçu pour maintenir votre adresse de service Starlink synchronisée avec votre position physique. Idéal pour les utilisateurs "Roam" ou mobiles qui souhaitent éviter les restrictions "loin de chez soi" à long terme.

## 🆕 Nouveautés Version Multi-Comptes

✅ **Gestion de plusieurs comptes Starlink simultanément**  
🔒 **Chiffrement sécurisé des mots de passe**  
🎯 **Configuration personnalisée par compte**  
📊 **Logs séparés et traçabilité complète**  
🛠️ **Interface CLI intuitive pour gérer les comptes**  
📈 **Statistiques d'exécution par compte**

## Features

-   **Auto-Detection**: Interroge votre terminal Starlink via gRPC pour obtenir les coordonnées GPS en temps réel.
-   **Smart Geocoding**: Convertit les coordonnées GPS en adresse postale valide via OpenStreetMap (Nominatim).
-   **Threshold Logic**: Met à jour l'adresse uniquement si vous avez déplacé de plus de `UPDATE_THRESHOLD_KM` (par défaut: 50km).
-   **Portal Automation**: Se connecte automatiquement à starlink.com et met à jour l'adresse de service.
-   **Robust Error Handling**: Logique de retry automatique avec backoff exponentiel pour les erreurs réseau et API.
-   **Security Detection**: Détecte les CAPTCHAs, 2FA et erreurs d'authentification nécessitant une intervention manuelle.
-   **Post-Update Verification**: Vérifie que les mises à jour d'adresse ont réussi.
-   **Enhanced Logging**: Logs détaillés avec coordonnées GPS et adresses résolues pour débogage et audit.

## Prerequisites

-   Python 3.8+
-   Starlink Dish powered on and reachable on local network (`192.168.100.1`).
-   **"Allow access on local network"** enabled in your Starlink App (Settings > Advanced > Debug Data).

## Installation

1.  **Install System Dependencies:**
    You may need gRPC tools or compilers if `starlink-grpc-core` requires them.

2.  **Install Python Packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright Browsers:**
    ```bash
    playwright install chromium
    ```

## Configuration

### Gestion des Comptes

La version multi-comptes utilise un système de gestion de comptes sécurisé. Les mots de passe sont chiffrés et stockés dans `accounts.json`.

#### Ajouter un compte

```bash
python cli.py add
```

Cette commande vous guidera interactivement pour :
- Entrer l'email du compte Starlink
- Entrer le mot de passe (sera chiffré automatiquement)
- Configurer le seuil de distance (par défaut: 50 km)
- Configurer le mode headless
- Configurer le nombre de tentatives

#### Lister les comptes

```bash
# Liste simple
python cli.py list

# Liste détaillée avec statistiques
python cli.py list --detailed
```

#### Gérer les comptes

```bash
# Activer un compte
python cli.py enable user@email.com

# Désactiver un compte
python cli.py disable user@email.com

# Supprimer un compte
python cli.py remove user@email.com

# Modifier la configuration d'un compte
python cli.py config user@email.com

# Afficher les statistiques
python cli.py stats                    # Statistiques globales
python cli.py stats user@email.com     # Statistiques d'un compte
```

### Structure des Fichiers

```
geo_agile/
├── accounts.json          # Comptes avec mots de passe chiffrés
├── .key                   # Clé de chiffrement (ne pas partager!)
├── states/                # États par compte
│   ├── user1_at_example_com.json
│   └── user2_at_example_com.json
└── logs/                  # Logs séparés par compte
    ├── user1_at_example_com.log
    └── user2_at_example_com.log
```

## Usage

### Exécution Multi-Comptes

Exécutez le script principal pour traiter tous les comptes actifs :

```bash
python main_multi.py
```

Le script va :
1. Charger tous les comptes actifs
2. Traiter chaque compte séquentiellement
3. Générer des logs séparés pour chaque compte
4. Mettre à jour les statistiques par compte
5. Afficher un résumé final

### Automation (Cron)

Configurez un cron job pour exécuter automatiquement :

```bash
# Tous les jours à 2h du matin
0 2 * * * cd /path/to/geo_agile && /usr/bin/python3 main_multi.py >> /var/log/geo_agile.log 2>&1
```


## Technical Improvements

The script has been enhanced with the following technical improvements:

### 1. Robust Web Automation (updater.py)
- **Resilient Selectors**: Uses text-based selectors (`get_by_text`, `get_by_role`) instead of fragile CSS classes
- **Error Detection**: Automatically detects CAPTCHAs, 2FA, and authentication errors
- **Post-Update Verification**: Verifies that address updates were successful before completing

### 2. Reliable Position Acquisition (monitor.py)
- **API Verification**: Checks gRPC API availability and version before attempting connections
- **Connectivity Checks**: Verifies network connectivity to the Dishy before gRPC calls
- **Timeout Management**: Configurable timeouts prevent indefinite blocking
- **Multiple Retrieval Methods**: Tries multiple API methods to retrieve GPS coordinates

### 3. Enhanced Orchestration (main_multi.py)
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Enhanced Logging**: Detailed logs include GPS coordinates, resolved addresses, and execution history
- **Execution History**: Maintains a history of the last 100 executions per account

## Important Notes

-   **Terms of Service**: Automating the Starlink portal may violate ToS. Use at your own risk.
-   **Selectors**: The `updater.py` uses resilient text-based selectors, but you should still verify behavior in non-headless mode initially.
-   **Manual Intervention**: If CAPTCHA or 2FA is detected, the script will stop and require manual intervention.
-   **Log Files**: Execution details are logged to both console and the log file specified in `LOG_FILE`.
