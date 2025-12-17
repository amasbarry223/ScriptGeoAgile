"""
Script pour activer/désactiver le mode test sur un compte existant.
"""
import sys
import io
import os

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from account_manager import AccountManager

def main():
    if len(sys.argv) < 2:
        print("Usage: python enable_test_mode.py <email> [lat] [lon]")
        print("\nExemples:")
        print("  python enable_test_mode.py user@email.com")
        print("  python enable_test_mode.py user@email.com 48.8584 2.2945")
        print("\nPour désactiver le mode test:")
        print("  python enable_test_mode.py user@email.com disable")
        return
    
    email = sys.argv[1]
    manager = AccountManager()
    
    account = manager.get_account(email)
    if not account:
        print(f"❌ Compte {email} non trouvé")
        return
    
    if len(sys.argv) >= 3 and sys.argv[2].lower() == 'disable':
        # Désactiver le mode test
        config_updates = {
            'test_mode': False,
            'test_coordinates': None
        }
        if manager.update_account_config(email, config_updates):
            print(f"✅ Mode test désactivé pour {email}")
        else:
            print(f"❌ Erreur lors de la désactivation")
        return
    
    # Activer le mode test
    if len(sys.argv) >= 4:
        try:
            lat = float(sys.argv[2])
            lon = float(sys.argv[3])
            test_coords = [lat, lon]
        except ValueError:
            print("❌ Coordonnées invalides. Utilisation des coordonnées par défaut.")
            test_coords = [48.8584, 2.2945]  # Tour Eiffel
    else:
        # Coordonnées par défaut (Tour Eiffel)
        test_coords = [48.8584, 2.2945]
        print(f"Utilisation des coordonnées par défaut: {test_coords}")
    
    config_updates = {
        'test_mode': True,
        'test_coordinates': test_coords
    }
    
    if manager.update_account_config(email, config_updates):
        print(f"✅ Mode test activé pour {email}")
        print(f"   Coordonnées de test: {test_coords}")
        print(f"\n💡 Le script utilisera ces coordonnées au lieu de se connecter au Dish")
    else:
        print(f"❌ Erreur lors de l'activation du mode test")

if __name__ == "__main__":
    main()
