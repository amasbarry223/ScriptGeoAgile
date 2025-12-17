"""
Geo-Agile Starlink Automation - Version Multi-Comptes
Gère plusieurs comptes Starlink simultanément avec logs séparés et statistiques.
"""
import os
import sys
import time
import json
import logging
import io
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from monitor import StarlinkMonitor
from geocoder import LocationService
from updater import StarlinkPortalClient
from account_manager import AccountManager

# Configuration globale
STATE_DIR = "states"
LOGS_DIR = "logs"
ACCOUNTS_FILE = "accounts.json"

# Créer les répertoires nécessaires
Path(STATE_DIR).mkdir(exist_ok=True)
Path(LOGS_DIR).mkdir(exist_ok=True)

def setup_logger(account_email: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure un logger spécifique pour un compte.
    
    Args:
        account_email: Email du compte
        log_level: Niveau de log
    
    Returns:
        Logger configuré pour ce compte
    """
    # Nettoyer l'email pour le nom de fichier
    safe_email = account_email.replace('@', '_at_').replace('.', '_')
    log_file = os.path.join(LOGS_DIR, f"{safe_email}.log")
    
    logger = logging.getLogger(f"GeoAgile.{safe_email}")
    logger.setLevel(log_level)
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Format de log
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)
    
    # Handler fichier
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler console (seulement pour INFO et plus)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def load_account_state(account_email: str) -> Dict:
    """Charge l'état d'un compte spécifique."""
    safe_email = account_email.replace('@', '_at_').replace('.', '_')
    state_file = os.path.join(STATE_DIR, f"{safe_email}.json")
    
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de l'état pour {account_email}: {e}")
            return {}
    return {}

def save_account_state(account_email: str, state: Dict):
    """Sauvegarde l'état d'un compte spécifique."""
    safe_email = account_email.replace('@', '_at_').replace('.', '_')
    state_file = os.path.join(STATE_DIR, f"{safe_email}.json")
    
    try:
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de l'état pour {account_email}: {e}")

def exponential_backoff(attempt: int, initial_delay: float, max_delay: float) -> float:
    """Calcule le délai d'attente pour un retry avec backoff exponentiel."""
    return min(initial_delay * (2 ** attempt), max_delay)

def retry_with_backoff(func, max_retries: int, operation_name: str, 
                      initial_delay: float = 5.0, max_delay: float = 60.0):
    """Exécute une fonction avec retry et exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            result = func()
            if attempt > 0:
                print(f"✅ {operation_name} réussie après {attempt} tentative(s) de retry")
            return result
        except Exception as e:
            if attempt < max_retries:
                delay = exponential_backoff(attempt, initial_delay, max_delay)
                print(f"⚠️  {operation_name} échouée (tentative {attempt + 1}/{max_retries + 1}): {e}")
                print(f"   Nouvelle tentative dans {delay:.1f}s...")
                time.sleep(delay)
            else:
                print(f"❌ {operation_name} échouée après {max_retries + 1} tentatives: {e}")
    
    return None

def process_account(account_email: str, account_config: Dict, manager: AccountManager) -> bool:
    """
    Traite un compte individuel.
    
    Returns:
        True si succès, False sinon
    """
    logger = setup_logger(account_email)
    
    logger.info("=" * 60)
    logger.info(f"Démarrage du traitement pour le compte: {account_email}")
    logger.info("=" * 60)
    
    try:
        # Configuration du compte
        password = account_config.get('password')
        update_threshold = account_config.get('update_threshold_km', 50.0)
        headless = account_config.get('headless', True)
        max_retries = account_config.get('max_retries', 3)
        initial_retry_delay = account_config.get('initial_retry_delay', 5.0)
        max_retry_delay = account_config.get('max_retry_delay', 60.0)
        
        # Initialisation des composants
        logger.info("Initialisation des composants...")
        monitor = StarlinkMonitor()
        geocoder = LocationService()
        updater = StarlinkPortalClient(account_email, password, headless=headless)
        
        # 1. Récupération de la position GPS
        logger.info("Étape 1: Acquisition de la position GPS du Dish...")
        
        # Mode test : utiliser des coordonnées de test si configurées
        test_mode = account_config.get('test_mode', False)
        test_coords = account_config.get('test_coordinates', None)
        
        if test_mode and test_coords:
            logger.info(f"🧪 MODE TEST ACTIVÉ - Utilisation de coordonnées de test")
            logger.info(f"   Coordonnées test: {test_coords}")
            current_pos = (float(test_coords[0]), float(test_coords[1]))
        else:
            def _get_position():
                pos = monitor.get_gps_position()
                if not pos:
                    raise ValueError("Position GPS non disponible")
                return pos
            
            current_pos = retry_with_backoff(
                _get_position, 
                max_retries, 
                "Acquisition GPS",
                initial_retry_delay,
                max_retry_delay
            )
            
            if not current_pos:
                logger.error("Impossible d'obtenir la position GPS du Dish. Arrêt.")
                manager.update_account_stats(account_email, False)
                return False
        
        logger.info(f"Position GPS: Latitude={current_pos[0]:.6f}, Longitude={current_pos[1]:.6f}")
        
        # 2. Vérification de la distance
        state = load_account_state(account_email)
        last_pos = state.get("last_pos")
        
        should_update = False
        distance = None
        
        if last_pos:
            last_pos_tuple = (last_pos[0], last_pos[1])
            distance = geocoder.calculate_distance_km(current_pos, last_pos_tuple)
            logger.info(f"Distance depuis dernière mise à jour: {distance:.2f} km (seuil: {update_threshold} km)")
            
            if distance > update_threshold:
                logger.info(f"Distance dépasse le seuil ({update_threshold} km). Initiation de la mise à jour.")
                should_update = True
            else:
                logger.info("Distance dans le seuil. Aucune mise à jour nécessaire.")
        else:
            logger.info("Aucun état précédent trouvé. Traitement comme première exécution.")
            should_update = True
        
        # 3. Mise à jour de l'adresse si nécessaire
        new_address = None
        update_success = False
        
        if should_update:
            logger.info("Étape 2: Résolution de l'adresse depuis les coordonnées GPS...")
            
            def _resolve():
                addr = geocoder.get_address_from_coords(current_pos[0], current_pos[1])
                if not addr:
                    raise ValueError("Impossible de résoudre l'adresse")
                return addr
            
            new_address = retry_with_backoff(
                _resolve,
                max_retries,
                "Résolution d'adresse",
                initial_retry_delay,
                max_retry_delay
            )
            
            if not new_address:
                logger.error("Impossible de résoudre l'adresse. Arrêt de la mise à jour.")
                manager.update_account_stats(account_email, False)
                return False
            
            logger.info(f"Adresse résolue: {new_address}")
            
            # En mode test, simuler la mise à jour au lieu de se connecter réellement
            if test_mode:
                logger.info("🧪 MODE TEST - Simulation de la mise à jour sur le portail...")
                logger.info("   (En mode test, la connexion au portail réel est simulée)")
                time.sleep(1)  # Simuler un délai
                update_success = True
                logger.info("✅ Mise à jour simulée avec succès (mode test)")
            else:
                logger.info("Étape 3: Mise à jour de l'adresse de service sur le portail...")
                
                def _update():
                    success = updater.update_service_address(new_address)
                    if not success:
                        raise ValueError("Échec de la mise à jour de l'adresse")
                    return success
                
                update_success = retry_with_backoff(
                    _update,
                    min(max_retries, 2),  # Moins de retries pour la mise à jour
                    "Mise à jour d'adresse",
                    initial_retry_delay,
                    max_retry_delay
                )
            
            if update_success:
                logger.info("Mise à jour d'adresse réussie.")
                # Mise à jour de l'état
                state["last_pos"] = current_pos
                state["last_address"] = new_address
                state["last_updated"] = time.time()
                state["last_updated_iso"] = datetime.now().isoformat()
                save_account_state(account_email, state)
                manager.update_account_stats(account_email, True)
            else:
                logger.error("Échec de la mise à jour d'adresse.")
                manager.update_account_stats(account_email, False)
                return False
        else:
            logger.info("Aucune mise à jour nécessaire - distance dans le seuil.")
            update_success = True
            manager.update_account_stats(account_email, True)
        
        # Journalisation des détails
        execution_log = {
            "timestamp": datetime.now().isoformat(),
            "gps_coordinates": {
                "latitude": current_pos[0],
                "longitude": current_pos[1]
            },
            "resolved_address": new_address,
            "distance_km": distance,
            "update_threshold_km": update_threshold,
            "update_triggered": should_update,
            "update_successful": update_success
        }
        
        logger.info("=== Détails de l'exécution ===")
        logger.info(f"Timestamp: {execution_log['timestamp']}")
        logger.info(f"Coordonnées GPS: {execution_log['gps_coordinates']}")
        if new_address:
            logger.info(f"Adresse résolue: {new_address}")
        if distance is not None:
            logger.info(f"Distance: {distance:.2f} km (seuil: {update_threshold} km)")
        logger.info(f"Mise à jour déclenchée: {should_update}")
        logger.info(f"Mise à jour réussie: {update_success}")
        logger.info("==============================")
        
        # Sauvegarder dans l'historique
        if "execution_history" not in state:
            state["execution_history"] = []
        
        state["execution_history"].append(execution_log)
        if len(state["execution_history"]) > 100:
            state["execution_history"] = state["execution_history"][-100:]
        
        save_account_state(account_email, state)
        
        logger.info("=" * 60)
        logger.info(f"Traitement terminé pour {account_email}")
        logger.info("=" * 60)
        
        return update_success
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du compte {account_email}: {e}", exc_info=True)
        manager.update_account_stats(account_email, False)
        return False

def main():
    """Point d'entrée principal - traite tous les comptes actifs."""
    print("=" * 60)
    print("Geo-Agile Starlink Automation - Version Multi-Comptes")
    print("=" * 60)
    
    manager = AccountManager()
    accounts = manager.get_all_accounts(enabled_only=True)
    
    if not accounts:
        print("\n❌ Aucun compte actif trouvé.")
        print("   Utilisez 'python cli.py add' pour ajouter un compte.")
        return
    
    print(f"\n📋 {len(accounts)} compte(s) actif(s) à traiter\n")
    
    results = {}
    
    for email, account_config in accounts.items():
        print(f"\n🔄 Traitement du compte: {email}")
        print("-" * 60)
        
        try:
            success = process_account(email, account_config, manager)
            results[email] = success
            
            if success:
                print(f"✅ {email}: Succès")
            else:
                print(f"❌ {email}: Échec")
        except Exception as e:
            print(f"❌ {email}: Erreur - {e}")
            results[email] = False
    
    # Résumé final
    print("\n" + "=" * 60)
    print("Résumé de l'exécution")
    print("=" * 60)
    
    successful = sum(1 for success in results.values() if success)
    failed = len(results) - successful
    
    print(f"✅ Succès: {successful}")
    print(f"❌ Échecs: {failed}")
    print(f"📊 Total: {len(results)}")
    
    if failed > 0:
        print("\nComptes en échec:")
        for email, success in results.items():
            if not success:
                print(f"  - {email}")

if __name__ == "__main__":
    main()
