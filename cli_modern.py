"""
Interface CLI moderne et interactive pour la gestion des comptes Starlink.
Utilise Rich pour un design moderne avec couleurs, tableaux et menus interactifs.
"""
import sys
import io
import os
from typing import Optional, List
from datetime import datetime

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich import box
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich n'est pas installé. Installation en cours...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "inquirer"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich import box
    from rich.align import Align
    RICH_AVAILABLE = True

try:
    import inquirer
    INQUIRER_AVAILABLE = True
except ImportError:
    INQUIRER_AVAILABLE = False

from account_manager import AccountManager

console = Console()

class ModernCLI:
    """Interface CLI moderne avec Rich."""
    
    def __init__(self):
        self.manager = AccountManager()
        self._show_banner()
    
    def _show_banner(self):
        """Affiche le bandeau d'accueil."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🌍 Geo-Agile Starlink Automation                    ║
║              Gestionnaire Multi-Comptes                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
    
    def _show_menu(self) -> str:
        """Affiche le menu principal interactif."""
        menu = Table.grid(padding=1)
        menu.add_column(style="cyan", justify="right")
        menu.add_column(style="magenta")
        
        menu.add_row("1", "➕ Ajouter un compte")
        menu.add_row("2", "📋 Lister les comptes")
        menu.add_row("3", "✏️  Modifier un compte")
        menu.add_row("4", "🗑️  Supprimer un compte")
        menu.add_row("5", "📊 Statistiques")
        menu.add_row("6", "🔧 Activer/Désactiver un compte")
        menu.add_row("7", "🧪 Mode Test")
        menu.add_row("0", "❌ Quitter")
        
        console.print("\n[bold yellow]━━━ Menu Principal ━━━[/bold yellow]")
        console.print(menu)
        
        choice = Prompt.ask(
            "\n[bold cyan]Choisissez une option[/bold cyan]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7"],
            default="0"
        )
        return choice
    
    def add_account_interactive(self):
        """Ajoute un compte avec une interface moderne."""
        console.print("\n[bold cyan]━━━ Ajout d'un nouveau compte ━━━[/bold cyan]\n")
        
        # Email
        email = Prompt.ask("[bold]Email du compte Starlink[/bold]", default="")
        if not email:
            console.print("[red]❌ Email requis[/red]")
            return False
        
        if email in self.manager.list_accounts():
            if not Confirm.ask(f"[yellow]⚠️  Le compte {email} existe déjà. Remplacer?[/yellow]"):
                console.print("[red]❌ Opération annulée[/red]")
                return False
        
        # Mot de passe (masqué)
        password = Prompt.ask("[bold]Mot de passe[/bold]", password=True)
        if not password:
            console.print("[red]❌ Mot de passe requis[/red]")
            return False
        
        # Mode test
        console.print("\n[yellow]━━━ Configuration du Mode Test ━━━[/yellow]")
        test_mode = Confirm.ask(
            "[bold]Activer le mode test?[/bold] (pour tester sans accès au Dish)",
            default=False
        )
        
        test_coords = None
        if test_mode:
            console.print("\n[dim]Entrez des coordonnées GPS de test[/dim]")
            lat_input = Prompt.ask(
                "[bold]Latitude[/bold]",
                default="48.8584"
            )
            lon_input = Prompt.ask(
                "[bold]Longitude[/bold]",
                default="2.2945"
            )
            
            try:
                lat = float(lat_input)
                lon = float(lon_input)
                test_coords = [lat, lon]
                console.print(f"[green]✅ Coordonnées de test: {lat}, {lon}[/green]")
            except ValueError:
                console.print("[yellow]⚠️  Coordonnées invalides, utilisation des valeurs par défaut[/yellow]")
                test_coords = [48.8584, 2.2945]
        
        # Configuration automatique
        config = {
            'update_threshold_km': 50.0,
            'headless': True,
            'max_retries': 3,
            'initial_retry_delay': 5.0,
            'max_retry_delay': 60.0,
            'enabled': True,
            'test_mode': test_mode,
            'test_coordinates': test_coords
        }
        
        # Afficher le résumé
        summary = Table(title="Configuration", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        summary.add_column("Paramètre", style="cyan", no_wrap=True)
        summary.add_column("Valeur", style="green")
        
        summary.add_row("Seuil de distance", f"{config['update_threshold_km']} km")
        summary.add_row("Mode headless", "Activé" if config['headless'] else "Désactivé")
        summary.add_row("Tentatives max", str(config['max_retries']))
        summary.add_row("Mode test", "✅ Activé" if test_mode else "❌ Désactivé")
        if test_coords:
            summary.add_row("Coordonnées test", f"{test_coords[0]}, {test_coords[1]}")
        
        console.print("\n")
        console.print(summary)
        
        if not Confirm.ask("\n[bold]Confirmer l'ajout?[/bold]", default=True):
            console.print("[red]❌ Opération annulée[/red]")
            return False
        
        # Ajouter avec animation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Ajout du compte...", total=None)
            success = self.manager.add_account(email, password, config)
            progress.update(task, completed=True)
        
        if success:
            console.print(f"\n[bold green]✅ Compte {email} ajouté avec succès![/bold green]")
            return True
        else:
            console.print(f"\n[bold red]❌ Erreur lors de l'ajout du compte {email}[/bold red]")
            return False
    
    def list_accounts(self, detailed: bool = False):
        """Liste les comptes avec un tableau moderne."""
        accounts = self.manager.get_all_accounts()
        
        if not accounts:
            console.print("\n[bold yellow]📭 Aucun compte enregistré[/bold yellow]\n")
            return
        
        # Tableau principal
        table = Table(
            title=f"📋 Comptes enregistrés ({len(accounts)})",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            border_style="cyan"
        )
        
        table.add_column("Email", style="cyan", no_wrap=True)
        table.add_column("Statut", justify="center")
        if detailed:
            table.add_column("Exécutions", justify="right", style="yellow")
            table.add_column("Succès", justify="right", style="green")
            table.add_column("Échecs", justify="right", style="red")
            table.add_column("Dernière exécution", style="dim")
        
        for email, account in accounts.items():
            status = "[green]✅ Actif[/green]" if account.get('enabled', True) else "[yellow]⏸️  Désactivé[/yellow]"
            
            if detailed:
                stats = account.get('stats', {})
                total_runs = stats.get('total_runs', 0)
                success = stats.get('successful_updates', 0)
                failures = stats.get('failed_updates', 0)
                last_run = account.get('last_run', 'Jamais')
                
                if last_run and last_run != 'Jamais':
                    try:
                        dt = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                        last_run = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                
                table.add_row(
                    email,
                    status,
                    str(total_runs),
                    str(success),
                    str(failures),
                    last_run
                )
            else:
                table.add_row(email, status)
        
        console.print("\n")
        console.print(table)
        console.print()
    
    def show_stats(self, email: Optional[str] = None):
        """Affiche les statistiques avec des graphiques visuels."""
        if email:
            account = self.manager.get_account(email)
            if not account:
                console.print(f"[red]❌ Compte {email} non trouvé[/red]")
                return
            
            stats = account.get('stats', {})
            total_runs = stats.get('total_runs', 0)
            success = stats.get('successful_updates', 0)
            failures = stats.get('failed_updates', 0)
            
            # Panel de statistiques
            stats_panel = Panel.fit(
                f"""
[bold cyan]Compte:[/bold cyan] {email}

[bold yellow]📊 Statistiques:[/bold yellow]
  • Total d'exécutions: [bold]{total_runs}[/bold]
  • Succès: [bold green]{success}[/bold green]
  • Échecs: [bold red]{failures}[/bold red]
  
[bold yellow]📈 Taux de succès:[/bold yellow]
  {self._create_progress_bar(success, total_runs) if total_runs > 0 else '[dim]Aucune donnée[/dim]'}
                """,
                title="[bold magenta]Statistiques du Compte[/bold magenta]",
                border_style="cyan"
            )
            console.print("\n")
            console.print(stats_panel)
        else:
            # Statistiques globales
            accounts = self.manager.get_all_accounts()
            if not accounts:
                console.print("\n[bold yellow]📭 Aucun compte enregistré[/bold yellow]\n")
                return
            
            total_runs = 0
            total_success = 0
            total_failures = 0
            
            for acc in accounts.values():
                stats = acc.get('stats', {})
                total_runs += stats.get('total_runs', 0)
                total_success += stats.get('successful_updates', 0)
                total_failures += stats.get('failed_updates', 0)
            
            stats_panel = Panel.fit(
                f"""
[bold yellow]📊 Statistiques Globales:[/bold yellow]

  • Total d'exécutions: [bold]{total_runs}[/bold]
  • Succès: [bold green]{total_success}[/bold green]
  • Échecs: [bold red]{total_failures}[/bold red]
  
[bold yellow]📈 Taux de succès global:[/bold yellow]
  {self._create_progress_bar(total_success, total_runs) if total_runs > 0 else '[dim]Aucune donnée[/dim]'}
                """,
                title="[bold magenta]Statistiques Globales[/bold magenta]",
                border_style="cyan"
            )
            console.print("\n")
            console.print(stats_panel)
    
    def _create_progress_bar(self, value: int, total: int, width: int = 30) -> str:
        """Crée une barre de progression visuelle."""
        if total == 0:
            return "[dim]Aucune donnée[/dim]"
        
        percentage = (value / total) * 100
        filled = int((value / total) * width)
        empty = width - filled
        
        bar = "[green]" + "█" * filled + "[/green]" + "[dim]" + "░" * empty + "[/dim]"
        return f"{bar} {percentage:.1f}%"
    
    def remove_account(self, email: Optional[str] = None):
        """Supprime un compte avec confirmation."""
        if not email:
            email = Prompt.ask("[bold]Email du compte à supprimer[/bold]")
        
        if email not in self.manager.list_accounts():
            console.print(f"[red]❌ Compte {email} non trouvé[/red]")
            return False
        
        # Afficher les infos du compte
        account = self.manager.get_account(email)
        if account:
            stats = account.get('stats', {})
            warning_panel = Panel(
                f"""
[bold yellow]⚠️  Attention![/bold yellow]

Vous êtes sur le point de supprimer le compte:
[bold cyan]{email}[/bold cyan]

[dim]Statistiques qui seront perdues:[/dim]
  • Exécutions: {stats.get('total_runs', 0)}
  • Succès: {stats.get('successful_updates', 0)}
  • Échecs: {stats.get('failed_updates', 0)}
                """,
                title="[bold red]Confirmation de suppression[/bold red]",
                border_style="red"
            )
            console.print("\n")
            console.print(warning_panel)
        
        if not Confirm.ask("\n[bold red]Êtes-vous sûr de vouloir supprimer ce compte?[/bold red]", default=False):
            console.print("[yellow]❌ Opération annulée[/yellow]")
            return False
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Suppression du compte...", total=None)
            success = self.manager.remove_account(email)
            progress.update(task, completed=True)
        
        if success:
            console.print(f"\n[bold green]✅ Compte {email} supprimé[/bold green]")
            return True
        else:
            console.print(f"\n[bold red]❌ Erreur lors de la suppression[/bold red]")
            return False
    
    def update_account(self, email: Optional[str] = None):
        """Modifie un compte avec interface moderne."""
        if not email:
            email = Prompt.ask("[bold]Email du compte à modifier[/bold]")
        
        account = self.manager.get_account(email)
        if not account:
            console.print(f"[red]❌ Compte {email} non trouvé[/red]")
            return False
        
        console.print("\n[bold cyan]━━━ Modification du compte ━━━[/bold cyan]\n")
        
        # Nouvel email
        new_email = Prompt.ask(
            f"[bold]Nouvel email[/bold]",
            default=email
        )
        
        # Nouveau mot de passe
        change_password = Confirm.ask("[bold]Changer le mot de passe?[/bold]", default=False)
        new_password = None
        if change_password:
            new_password = Prompt.ask("[bold]Nouveau mot de passe[/bold]", password=True)
        
        # Si changement d'email
        if new_email != email:
            if new_email in self.manager.list_accounts():
                console.print(f"[red]❌ Le compte {new_email} existe déjà[/red]")
                return False
            
            config = account.copy()
            if 'password' in config:
                del config['password']
            if 'password_encrypted' in config:
                del config['password_encrypted']
            
            password_to_use = new_password if new_password else account.get('password')
            if not password_to_use:
                console.print("[red]❌ Mot de passe requis[/red]")
                return False
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Modification du compte...", total=None)
                if self.manager.add_account(new_email, password_to_use, config):
                    self.manager.remove_account(email)
                    progress.update(task, completed=True)
                    console.print(f"\n[bold green]✅ Compte modifié: {email} → {new_email}[/bold green]")
                    return True
                else:
                    console.print(f"\n[bold red]❌ Erreur lors de la modification[/bold red]")
                    return False
        else:
            # Juste changer le mot de passe
            if new_password:
                config = account.copy()
                if 'password' in config:
                    del config['password']
                if 'password_encrypted' in config:
                    del config['password_encrypted']
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("[cyan]Mise à jour du mot de passe...", total=None)
                    if self.manager.add_account(email, new_password, config):
                        progress.update(task, completed=True)
                        console.print(f"\n[bold green]✅ Mot de passe mis à jour pour {email}[/bold green]")
                        return True
                    else:
                        console.print(f"\n[bold red]❌ Erreur lors de la mise à jour[/bold red]")
                        return False
            else:
                console.print("[yellow]❌ Aucune modification effectuée[/yellow]")
                return False
    
    def toggle_account_status(self, email: Optional[str] = None):
        """Active ou désactive un compte."""
        if not email:
            email = Prompt.ask("[bold]Email du compte[/bold]")
        
        account = self.manager.get_account(email)
        if not account:
            console.print(f"[red]❌ Compte {email} non trouvé[/red]")
            return False
        
        is_enabled = account.get('enabled', True)
        action = "désactiver" if is_enabled else "activer"
        
        if not Confirm.ask(f"[bold]Voulez-vous {action} le compte {email}?[/bold]", default=True):
            return False
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]{action.capitalize()} le compte...", total=None)
            if is_enabled:
                success = self.manager.disable_account(email)
            else:
                success = self.manager.enable_account(email)
            progress.update(task, completed=True)
        
        if success:
            status = "désactivé" if is_enabled else "activé"
            console.print(f"\n[bold green]✅ Compte {email} {status}[/bold green]")
            return True
        else:
            console.print(f"\n[bold red]❌ Erreur lors de l'opération[/bold red]")
            return False
    
    def manage_test_mode(self, email: Optional[str] = None):
        """Gère le mode test d'un compte."""
        if not email:
            email = Prompt.ask("[bold]Email du compte[/bold]")
        
        account = self.manager.get_account(email)
        if not account:
            console.print(f"[red]❌ Compte {email} non trouvé[/red]")
            return False
        
        is_test_mode = account.get('test_mode', False)
        action = "désactiver" if is_test_mode else "activer"
        
        console.print(f"\n[yellow]━━━ Mode Test ━━━[/yellow]\n")
        console.print(f"Mode test actuel: [bold]{'✅ Activé' if is_test_mode else '❌ Désactivé'}[/bold]")
        
        if is_test_mode:
            test_coords = account.get('test_coordinates')
            if test_coords:
                console.print(f"Coordonnées test: [cyan]{test_coords[0]}, {test_coords[1]}[/cyan]")
        
        if Confirm.ask(f"\n[bold]Voulez-vous {action} le mode test?[/bold]", default=True):
            if is_test_mode:
                # Désactiver
                self.manager.update_account_config(email, {
                    'test_mode': False,
                    'test_coordinates': None
                })
                console.print(f"\n[bold green]✅ Mode test désactivé pour {email}[/bold green]")
            else:
                # Activer
                console.print("\n[dim]Entrez des coordonnées GPS de test[/dim]")
                lat = Prompt.ask("[bold]Latitude[/bold]", default="48.8584")
                lon = Prompt.ask("[bold]Longitude[/bold]", default="2.2945")
                
                try:
                    test_coords = [float(lat), float(lon)]
                    self.manager.update_account_config(email, {
                        'test_mode': True,
                        'test_coordinates': test_coords
                    })
                    console.print(f"\n[bold green]✅ Mode test activé pour {email}[/bold green]")
                    console.print(f"   Coordonnées: [cyan]{test_coords[0]}, {test_coords[1]}[/cyan]")
                except ValueError:
                    console.print("[red]❌ Coordonnées invalides[/red]")
                    return False
    
    def run(self):
        """Lance l'interface interactive."""
        while True:
            try:
                choice = self._show_menu()
                
                if choice == "0":
                    console.print("\n[bold yellow]👋 Au revoir![/bold yellow]\n")
                    break
                elif choice == "1":
                    self.add_account_interactive()
                elif choice == "2":
                    detailed = Confirm.ask("\n[bold]Afficher les détails?[/bold]", default=False)
                    self.list_accounts(detailed=detailed)
                elif choice == "3":
                    self.update_account()
                elif choice == "4":
                    self.remove_account()
                elif choice == "5":
                    email = Prompt.ask(
                        "\n[bold]Email du compte (laissez vide pour statistiques globales)[/bold]",
                        default=""
                    )
                    self.show_stats(email if email else None)
                elif choice == "6":
                    self.toggle_account_status()
                elif choice == "7":
                    self.manage_test_mode()
                
                if choice != "0":
                    Prompt.ask("\n[dim]Appuyez sur Entrée pour continuer...[/dim]", default="")
                    console.clear()
                    self._show_banner()
                    
            except KeyboardInterrupt:
                console.print("\n\n[bold yellow]👋 Au revoir![/bold yellow]\n")
                break
            except Exception as e:
                console.print(f"\n[bold red]❌ Erreur: {e}[/bold red]\n")
                Prompt.ask("[dim]Appuyez sur Entrée pour continuer...[/dim]", default="")

def main():
    """Point d'entrée principal."""
    cli = ModernCLI()
    cli.run()

if __name__ == "__main__":
    main()
