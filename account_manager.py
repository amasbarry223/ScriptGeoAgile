"""
Gestionnaire de comptes Starlink avec chiffrement sécurisé des mots de passe.
"""
import os
import json
import base64
import logging
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from getpass import getpass

logger = logging.getLogger("GeoAgile.AccountManager")

class AccountManager:
    """Gestionnaire de comptes avec chiffrement sécurisé."""
    
    ACCOUNTS_FILE = "accounts.json"
    KEY_FILE = ".key"
    
    def __init__(self):
        self.accounts_file = self.ACCOUNTS_FILE
        self.key_file = self.KEY_FILE
        self.cipher_suite = None
        self._load_or_create_key()
    
    def _load_or_create_key(self):
        """Charge la clé de chiffrement ou en crée une nouvelle."""
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                self.cipher_suite = Fernet(key)
            except Exception as e:
                logger.error(f"Erreur lors du chargement de la clé: {e}")
                self._create_new_key()
        else:
            self._create_new_key()
    
    def _create_new_key(self):
        """Crée une nouvelle clé de chiffrement."""
        try:
            # Générer une clé depuis un mot de passe maître ou aléatoirement
            # Pour la sécurité, on génère une clé aléatoire
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)  # Permissions restrictives
            self.cipher_suite = Fernet(key)
            logger.info("Nouvelle clé de chiffrement créée")
        except Exception as e:
            logger.error(f"Erreur lors de la création de la clé: {e}")
            raise
    
    def _encrypt_password(self, password: str) -> str:
        """Chiffre un mot de passe."""
        if not self.cipher_suite:
            raise ValueError("Cipher suite non initialisée")
        encrypted = self.cipher_suite.encrypt(password.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Déchiffre un mot de passe."""
        if not self.cipher_suite:
            raise ValueError("Cipher suite non initialisée")
        try:
            encrypted_bytes = base64.b64decode(encrypted_password.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement: {e}")
            raise
    
    def load_accounts(self) -> Dict:
        """Charge tous les comptes depuis le fichier."""
        if not os.path.exists(self.accounts_file):
            return {}
        
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
            
            # Déchiffrer les mots de passe
            decrypted_accounts = {}
            for email, account_info in accounts_data.items():
                decrypted_accounts[email] = account_info.copy()
                if 'password_encrypted' in account_info:
                    try:
                        decrypted_accounts[email]['password'] = self._decrypt_password(
                            account_info['password_encrypted']
                        )
                        # Ne pas garder la version chiffrée en mémoire
                        del decrypted_accounts[email]['password_encrypted']
                    except Exception as e:
                        logger.error(f"Erreur lors du déchiffrement du mot de passe pour {email}: {e}")
                        continue
            
            return decrypted_accounts
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erreur lors du chargement des comptes: {e}")
            return {}
    
    def save_accounts(self, accounts: Dict):
        """Sauvegarde tous les comptes dans le fichier avec chiffrement."""
        try:
            # Préparer les données avec mots de passe chiffrés
            encrypted_accounts = {}
            for email, account_info in accounts.items():
                encrypted_accounts[email] = account_info.copy()
                # Chiffrer le mot de passe si présent
                if 'password' in encrypted_accounts[email]:
                    encrypted_accounts[email]['password_encrypted'] = self._encrypt_password(
                        encrypted_accounts[email]['password']
                    )
                    # Ne pas sauvegarder le mot de passe en clair
                    del encrypted_accounts[email]['password']
            
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(encrypted_accounts, f, indent=4, ensure_ascii=False)
            
            # Permissions restrictives
            os.chmod(self.accounts_file, 0o600)
            logger.info(f"Comptes sauvegardés: {len(accounts)} compte(s)")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des comptes: {e}")
            return False
    
    def add_account(self, email: str, password: str, config: Optional[Dict] = None) -> bool:
        """
        Ajoute ou met à jour un compte.
        Les valeurs par défaut sont appliquées automatiquement si non spécifiées.
        
        Args:
            email: Email du compte Starlink
            password: Mot de passe (sera chiffré)
            config: Configuration optionnelle du compte (valeurs par défaut si None)
        """
        accounts = self.load_accounts()
        
        # Configuration par défaut optimale
        default_config = {
            'enabled': True,
            'update_threshold_km': 50.0,
            'headless': True,
            'max_retries': 3,
            'initial_retry_delay': 5.0,
            'max_retry_delay': 60.0,
            'test_mode': False,  # Mode test désactivé par défaut
            'test_coordinates': None  # Coordonnées de test (lat, lon)
        }
        
        # Si le compte existe déjà, préserver certaines données
        if email in accounts:
            existing = accounts[email]
            # Préserver les stats et l'historique
            default_config['stats'] = existing.get('stats', {
                'total_runs': 0,
                'successful_updates': 0,
                'failed_updates': 0,
                'last_success': None,
                'last_failure': None
            })
            default_config['created_at'] = existing.get('created_at')
            default_config['last_run'] = existing.get('last_run')
        else:
            # Nouveau compte
            from datetime import datetime
            default_config['stats'] = {
                'total_runs': 0,
                'successful_updates': 0,
                'failed_updates': 0,
                'last_success': None,
                'last_failure': None
            }
            default_config['created_at'] = datetime.now().isoformat()
        
        # Fusionner avec la config fournie (si présente)
        if config:
            default_config.update(config)
        
        account_config = {
            'email': email,
            'password': password,
            **default_config
        }
        
        accounts[email] = account_config
        return self.save_accounts(accounts)
    
    def remove_account(self, email: str) -> bool:
        """Supprime un compte."""
        accounts = self.load_accounts()
        if email in accounts:
            del accounts[email]
            return self.save_accounts(accounts)
        return False
    
    def get_account(self, email: str) -> Optional[Dict]:
        """Récupère un compte spécifique."""
        accounts = self.load_accounts()
        return accounts.get(email)
    
    def get_all_accounts(self, enabled_only: bool = False) -> Dict:
        """Récupère tous les comptes."""
        accounts = self.load_accounts()
        if enabled_only:
            return {email: acc for email, acc in accounts.items() if acc.get('enabled', True)}
        return accounts
    
    def list_accounts(self) -> List[str]:
        """Liste les emails de tous les comptes."""
        return list(self.load_accounts().keys())
    
    def update_account_config(self, email: str, config_updates: Dict) -> bool:
        """Met à jour la configuration d'un compte."""
        accounts = self.load_accounts()
        if email not in accounts:
            return False
        
        accounts[email].update(config_updates)
        return self.save_accounts(accounts)
    
    def update_account_stats(self, email: str, success: bool):
        """Met à jour les statistiques d'un compte."""
        accounts = self.load_accounts()
        if email not in accounts:
            return False
        
        if 'stats' not in accounts[email]:
            accounts[email]['stats'] = {
                'total_runs': 0,
                'successful_updates': 0,
                'failed_updates': 0,
                'last_success': None,
                'last_failure': None
            }
        
        stats = accounts[email]['stats']
        stats['total_runs'] = stats.get('total_runs', 0) + 1
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        if success:
            stats['successful_updates'] = stats.get('successful_updates', 0) + 1
            stats['last_success'] = timestamp
        else:
            stats['failed_updates'] = stats.get('failed_updates', 0) + 1
            stats['last_failure'] = timestamp
        
        accounts[email]['last_run'] = timestamp
        return self.save_accounts(accounts)
    
    def enable_account(self, email: str) -> bool:
        """Active un compte."""
        return self.update_account_config(email, {'enabled': True})
    
    def disable_account(self, email: str) -> bool:
        """Désactive un compte."""
        return self.update_account_config(email, {'enabled': False})
