# CLI Simplifié - Geo-Agile

## 🎯 Objectif

Le CLI a été simplifié pour ne gérer que l'essentiel :
- **Ajouter** des comptes (email + mot de passe)
- **Modifier** des comptes (email ou mot de passe)
- **Supprimer** des comptes

Tout le reste (configuration, seuils, retries, etc.) est **automatique** avec des valeurs optimales.

## 📋 Commandes disponibles

### 1. Ajouter un compte

```bash
python cli.py add
```

**Ce qui est demandé :**
- Email du compte Starlink
- Mot de passe

**Configuration automatique appliquée :**
- ✅ Seuil de distance : 50 km (optimal)
- ✅ Mode headless : Activé (pour serveur)
- ✅ Tentatives max : 3 (optimal)
- ✅ Délais de retry : Optimisés automatiquement

### 2. Modifier un compte

```bash
python cli.py update email@exemple.com
```

Permet de modifier :
- L'email du compte
- Le mot de passe

La configuration reste automatique.

### 3. Supprimer un compte

```bash
python cli.py remove email@exemple.com
```

### 4. Lister les comptes

```bash
# Liste simple
python cli.py list

# Liste avec statistiques
python cli.py list --detailed
```

### 5. Voir les statistiques

```bash
# Tous les comptes
python cli.py stats

# Un compte spécifique
python cli.py stats email@exemple.com
```

### 6. Activer/Désactiver

```bash
python cli.py enable email@exemple.com
python cli.py disable email@exemple.com
```

## 🔧 Configuration automatique

Le système applique automatiquement ces valeurs optimales pour chaque compte :

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| Seuil de distance | 50 km | Évite les mises à jour trop fréquentes |
| Mode headless | Activé | Optimal pour serveur/automatisation |
| Tentatives max | 3 | Équilibre entre fiabilité et rapidité |
| Délai initial retry | 5 secondes | Temps raisonnable pour réessayer |
| Délai max retry | 60 secondes | Évite les attentes trop longues |

**Vous n'avez pas besoin de configurer quoi que ce soit !** Le système décide automatiquement.

## 📝 Exemple d'utilisation

```bash
# 1. Ajouter un compte
python cli.py add
# Entrez : votre@email.com
# Entrez : votre_mot_de_passe

# 2. Vérifier
python cli.py list

# 3. Lancer le traitement
python main_multi.py

# 4. Voir les résultats
python cli.py stats
```

## ✨ Avantages

- ✅ **Simple** : Seulement email et mot de passe à saisir
- ✅ **Automatique** : Configuration optimale appliquée automatiquement
- ✅ **Rapide** : Pas de questions sur la configuration
- ✅ **Fiable** : Valeurs testées et optimisées
