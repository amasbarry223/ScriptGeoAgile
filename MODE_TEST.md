# Mode Test - Geo-Agile

## 🧪 Qu'est-ce que le mode test ?

Le mode test permet de tester le script **localement** sans avoir accès au Dish Starlink. Il utilise des **coordonnées GPS de test** au lieu de se connecter au Dish.

## ✅ Ce qui fonctionne en mode test

1. **Récupération GPS** : Utilise des coordonnées de test (pas besoin du Dish)
2. **Résolution d'adresse** : Convertit les coordonnées en adresse postale
3. **Calcul de distance** : Compare avec la dernière position enregistrée
4. **Logique de mise à jour** : Détermine si une mise à jour est nécessaire

## ⚠️ Ce qui nécessite une connexion réelle

- **Connexion au portail Starlink** : Nécessite une connexion Internet et des identifiants valides
- **Mise à jour de l'adresse** : Nécessite de se connecter au vrai portail Starlink

## 📋 Comment utiliser le mode test

### Option 1 : Activer lors de l'ajout d'un compte

```bash
python cli.py add
```

Lors de l'ajout, choisissez "o" pour activer le mode test et entrez des coordonnées (ou utilisez les valeurs par défaut).

### Option 2 : Activer sur un compte existant

```bash
# Activer avec coordonnées par défaut (Tour Eiffel)
python enable_test_mode.py votre@email.com

# Activer avec coordonnées personnalisées
python enable_test_mode.py votre@email.com 48.8584 2.2945

# Désactiver le mode test
python enable_test_mode.py votre@email.com disable
```

## 🎯 Coordonnées de test par défaut

- **Latitude** : 48.8584
- **Longitude** : 2.2945
- **Lieu** : Tour Eiffel, Paris, France

## 📊 Résultat du test

Lors du test, vous verrez :

```
🧪 MODE TEST ACTIVÉ - Utilisation de coordonnées de test
   Coordonnées test: [48.8584, 2.2945]
Position GPS: Latitude=48.858400, Longitude=2.294500
Adresse résolue: Avenue Gustave Eiffel, Quartier du Gros-Caillou...
```

## 🔄 Workflow complet testé

1. ✅ **Acquisition GPS** : Coordonnées de test utilisées
2. ✅ **Résolution d'adresse** : Adresse résolue depuis les coordonnées
3. ✅ **Calcul de distance** : Comparaison avec dernière position
4. ⚠️ **Connexion portail** : Nécessite une connexion réelle (peut échouer en test)

## 💡 Pour tester complètement

Pour tester **complètement** le script (y compris la mise à jour sur le portail), vous avez deux options :

### Option A : Tester avec un vrai compte (recommandé avant déploiement)

1. Désactivez le mode test : `python enable_test_mode.py votre@email.com disable`
2. Assurez-vous que le Dish est accessible
3. Lancez : `python main_multi.py`

### Option B : Tester seulement la logique (sans mise à jour portail)

Le mode test permet de vérifier que :
- ✅ Les coordonnées sont bien utilisées
- ✅ L'adresse est correctement résolue
- ✅ La logique de distance fonctionne
- ✅ Les logs sont générés correctement

La connexion au portail nécessitera toujours une connexion Internet réelle et des identifiants valides.

## 📝 Notes importantes

- Le mode test **ne modifie pas** le portail Starlink réel
- Les coordonnées de test sont **simulées** uniquement
- Les logs et statistiques sont **réels** et enregistrés
- Pour le déploiement en production, **désactivez le mode test**

## 🚀 Déploiement en production

Avant de déployer sur un serveur :

1. Désactivez le mode test pour tous les comptes :
   ```bash
   python enable_test_mode.py votre@email.com disable
   ```

2. Vérifiez que le serveur peut accéder au Dish (même réseau ou VPN)

3. Testez une dernière fois avec un compte réel

4. Déployez et configurez le cron job
