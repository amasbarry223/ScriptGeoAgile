"""
Interface CLI pour la gestion des comptes Starlink.
"""
import sys
import argparse
import json
import os
from datetime import datetime
from typing import Optional
from account_manager import AccountManager

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class CLI:
    """Interface en ligne de commande pour gérer les comptes."""
    
    def __init__(self):
        self.manager = AccountManager()
    
    def add_account_interactive(self):
        """Ajoute un compte de manière interactive - seulement email et mot de passe."""
        print("\n=== Ajout d'un nouveau compte Starlink ===")
        print("(Configuration automatique avec valeurs optimales)")
        
        email = input("Email du compte Starlink: ").strip()
        if not email:
            print("❌ Email requis")
            return False
        
        if email in self.manager.list_accounts():
            overwrite = input(f"⚠️  Le compte {email} existe déjà. Remplacer? (o/N): ").strip().lower()
            if overwrite != 'o':
                print("❌ Opération annulée")
                return False
        
        password = None
        while not password:
            password = input("Mot de passe: ").strip()
            if not password:
                print("❌ Mot de passe requis")
        
        # Demander si mode test
        print("\n--- Mode Test (pour tester sans accès au Dish) ---")
        test_mode_input = input("Activer le mode test? (o/N): ").strip().lower()
        test_mode = test_mode_input == 'o'
        test_coords = None
        
        if test_mode:
            print("\nEntrez des coordonnées GPS de test (ou appuyez sur Entrée pour coordonnées par défaut)")
            lat_input = input("Latitude [48.8584 (Tour Eiffel)]: ").strip()
            lon_input = input("Longitude [2.2945 (Tour Eiffel)]: ").strip()
            
            try:
                lat = float(lat_input) if lat_input else 48.8584
                lon = float(lon_input) if lon_input else 2.2945
                test_coords = [lat, lon]
                print(f"✅ Coordonnées de test: {lat}, {lon}")
            except ValueError:
                print("⚠️  Coordonnées invalides, utilisation des valeurs par défaut")
                test_coords = [48.8584, 2.2945]
        
        # Configuration automatique avec valeurs optimales
        config = {
            'update_threshold_km': 50.0,  # Seuil optimal pour éviter les mises à jour trop fréquentes
            'headless': True,              # Mode headless par défaut pour serveur
            'max_retries': 3,              # Nombre optimal de tentatives
            'initial_retry_delay': 5.0,    # Délai initial raisonnable
            'max_retry_delay': 60.0,       # Délai maximum pour éviter les attentes trop longues
            'enabled': True,               # Compte activé par défaut
            'test_mode': test_mode,        # Mode test
            'test_coordinates': test_coords # Coordonnées de test
        }
        
        print(f"\nConfiguration automatique appliquée:")
        print(f"  - Seuil de distance: {config['update_threshold_km']} km")
        print(f"  - Mode headless: Activé")
        print(f"  - Tentatives max: {config['max_retries']}")
        if test_mode:
            print(f"  - 🧪 MODE TEST: Activé avec coordonnées {test_coords}")
        else:
            print(f"  - Mode production: Connexion au Dish requise")
        
        if self.manager.add_account(email, password, config):
            print(f"\n✅ Compte {email} ajouté avec succès!")
            return True
        else:
            print(f"❌ Erreur lors de l'ajout du compte {email}")
            return False
    
    def list_accounts(self, detailed: bool = False):
        """Liste tous les comptes."""
        accounts = self.manager.get_all_accounts()
        
        if not accounts:
            print("\n📭 Aucun compte enregistré")
            return
        
        print(f"\n=== Comptes enregistrés ({len(accounts)}) ===")
        
        for email, account in accounts.items():
            status = "✅ Actif" if account.get('enabled', True) else "⏸️  Désactivé"
            print(f"\n📧 {email} - {status}")
            
            if detailed:
                stats = account.get('stats', {})
                if stats:
                    print(f"   Exécutions: {stats.get('total_runs', 0)}")
                    print(f"   Succès: {stats.get('successful_updates', 0)}")
                    print(f"   Échecs: {stats.get('failed_updates', 0)}")
                    if stats.get('last_success'):
                        print(f"   Dernier succès: {stats['last_success']}")
    
    def remove_account(self, email: Optional[str] = None):
        """Supprime un compte."""
        if not email:
            email = input("Email du compte à supprimer: ").strip()
        
        if not email:
            print("❌ Email requis")
            return False
        
        if email not in self.manager.list_accounts():
            print(f"❌ Compte {email} non trouvé")
            return False
        
        confirm = input(f"⚠️  Êtes-vous sûr de vouloir supprimer le compte {email}? (o/N): ").strip().lower()
        if confirm != 'o':
            print("❌ Opération annulée")
            return False
        
        if self.manager.remove_account(email):
            print(f"✅ Compte {email} supprimé")
            return True
        else:
            print(f"❌ Erreur lors de la suppression du compte {email}")
            return False
    
    def show_stats(self, email: Optional[str] = None):
        """Affiche les statistiques d'un compte ou de tous les comptes."""
        if email:
            account = self.manager.get_account(email)
            if not account:
                print(f"❌ Compte {email} non trouvé")
                return
            
            stats = account.get('stats', {})
            print(f"\n=== Statistiques pour {email} ===")
            print(f"Total d'exécutions: {stats.get('total_runs', 0)}")
            print(f"Succès: {stats.get('successful_updates', 0)}")
            print(f"Échecs: {stats.get('failed_updates', 0)}")
            
            if stats.get('total_runs', 0) > 0:
                success_rate = (stats.get('successful_updates', 0) / stats.get('total_runs', 1)) * 100
                print(f"Taux de succès: {success_rate:.1f}%")
            
            if stats.get('last_success'):
                print(f"Dernier succès: {stats['last_success']}")
            if stats.get('last_failure'):
                print(f"Dernier échec: {stats['last_failure']}")
        else:
            accounts = self.manager.get_all_accounts()
            if not accounts:
                print("\n📭 Aucun compte enregistré")
                return
            
            print("\n=== Statistiques globales ===")
            total_runs = 0
            total_success = 0
            total_failures = 0
            
            for email, account in accounts.items():
                stats = account.get('stats', {})
                total_runs += stats.get('total_runs', 0)
                total_success += stats.get('successful_updates', 0)
                total_failures += stats.get('failed_updates', 0)
            
            print(f"Total d'exécutions: {total_runs}")
            print(f"Succès: {total_success}")
            print(f"Échecs: {total_failures}")
            
            if total_runs > 0:
                success_rate = (total_success / total_runs) * 100
                print(f"Taux de succès global: {success_rate:.1f}%")
    
    def enable_account(self, email: Optional[str] = None):
        """Active un compte."""
        if not email:
            email = input("Email du compte à activer: ").strip()
        
        if self.manager.enable_account(email):
            print(f"✅ Compte {email} activé")
            return True
        else:
            print(f"❌ Erreur lors de l'activation du compte {email}")
            return False
    
    def disable_account(self, email: Optional[str] = None):
        """Désactive un compte."""
        if not email:
            email = input("Email du compte à désactiver: ").strip()
        
        if self.manager.disable_account(email):
            print(f"✅ Compte {email} désactivé")
            return True
        else:
            print(f"❌ Erreur lors de la désactivation du compte {email}")
            return False
    
    def update_account(self, email: Optional[str] = None):
        """Met à jour l'email et/ou le mot de passe d'un compte."""
        if not email:
            email = input("Email du compte à modifier: ").strip()
        
        account = self.manager.get_account(email)
        if not account:
            print(f"❌ Compte {email} non trouvé")
            return False
        
        print(f"\n=== Modification du compte {email} ===")
        print("(Laissez vide pour conserver la valeur actuelle)")
        
        # Nouvel email
        new_email = input(f"Nouvel email [{email}]: ").strip()
        if not new_email:
            new_email = email
        
        # Nouveau mot de passe
        new_password = input("Nouveau mot de passe (laissez vide pour conserver): ").strip()
        
        # Si changement d'email, créer nouveau compte et supprimer l'ancien
        if new_email != email:
            if new_email in self.manager.list_accounts():
                print(f"❌ Le compte {new_email} existe déjà")
                return False
            
            # Récupérer la configuration actuelle
            config = account.copy()
            if 'password' in config:
                del config['password']
            if 'password_encrypted' in config:
                del config['password_encrypted']
            
            # Utiliser le nouveau mot de passe ou l'ancien
            password_to_use = new_password if new_password else account.get('password')
            if not password_to_use:
                print("❌ Mot de passe requis")
                return False
            
            # Créer le nouveau compte
            if self.manager.add_account(new_email, password_to_use, config):
                # Supprimer l'ancien compte
                self.manager.remove_account(email)
                print(f"✅ Compte modifié: {email} -> {new_email}")
                return True
            else:
                print(f"❌ Erreur lors de la modification")
                return False
        else:
            # Juste changer le mot de passe
            if new_password:
                config = account.copy()
                if 'password' in config:
                    del config['password']
                if 'password_encrypted' in config:
                    del config['password_encrypted']
                
                if self.manager.add_account(email, new_password, config):
                    print(f"✅ Mot de passe mis à jour pour {email}")
                    return True
                else:
                    print(f"❌ Erreur lors de la mise à jour")
                    return False
            else:
                print("❌ Aucune modification effectuée")
                return False

def main():
    """Point d'entrée principal du CLI."""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de comptes Geo-Agile Starlink",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python cli.py add                    # Ajouter un compte interactivement
  python cli.py list                   # Lister tous les comptes
  python cli.py list --detailed        # Lister avec détails
  python cli.py remove user@email.com  # Supprimer un compte
  python cli.py stats                  # Statistiques globales
  python cli.py stats user@email.com   # Statistiques d'un compte
  python cli.py enable user@email.com  # Activer un compte
  python cli.py disable user@email.com # Désactiver un compte
  python cli.py update user@email.com # Modifier l'email ou le mot de passe
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande add
    subparsers.add_parser('add', help='Ajouter un nouveau compte')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Lister les comptes')
    list_parser.add_argument('--detailed', '-d', action='store_true', help='Afficher les détails')
    
    # Commande remove
    remove_parser = subparsers.add_parser('remove', help='Supprimer un compte')
    remove_parser.add_argument('email', nargs='?', help='Email du compte à supprimer')
    
    # Commande stats
    stats_parser = subparsers.add_parser('stats', help='Afficher les statistiques')
    stats_parser.add_argument('email', nargs='?', help='Email du compte (optionnel pour stats globales)')
    
    # Commande enable
    enable_parser = subparsers.add_parser('enable', help='Activer un compte')
    enable_parser.add_argument('email', nargs='?', help='Email du compte à activer')
    
    # Commande disable
    disable_parser = subparsers.add_parser('disable', help='Désactiver un compte')
    disable_parser.add_argument('email', nargs='?', help='Email du compte à désactiver')
    
    # Commande update (remplace config)
    update_parser = subparsers.add_parser('update', help='Modifier l\'email ou le mot de passe d\'un compte')
    update_parser.add_argument('email', nargs='?', help='Email du compte à modifier')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CLI()
    
    try:
        if args.command == 'add':
            cli.add_account_interactive()
        elif args.command == 'list':
            cli.list_accounts(detailed=args.detailed)
        elif args.command == 'remove':
            cli.remove_account(args.email)
        elif args.command == 'stats':
            cli.show_stats(args.email)
        elif args.command == 'enable':
            cli.enable_account(args.email)
        elif args.command == 'disable':
            cli.disable_account(args.email)
        elif args.command == 'config':
            cli.update_config(args.email)
    except KeyboardInterrupt:
        print("\n\n❌ Opération annulée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()
