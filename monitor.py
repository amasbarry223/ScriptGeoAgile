import logging
import sys
import socket
import time

# Try importing the starlink grpc tools
try:
    import starlink_grpc
except ImportError:
    # If the package is not installed or named differently
    starlink_grpc = None

# Try importing grpc directly for low-level access
try:
    import grpc
    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    grpc = None

logger = logging.getLogger("GeoAgile.Monitor")

class StarlinkMonitor:
    def __init__(self, ip="192.168.100.1", port=9200, timeout=10):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def _check_connectivity(self):
        """
        Vérifie si le Dishy est accessible sur le réseau avant d'essayer gRPC.
        Retourne True si accessible, False sinon.
        """
        try:
            logger.debug(f"Vérification de la connectivité vers {self.ip}:{self.port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.ip, self.port))
            sock.close()
            
            if result == 0:
                logger.debug("Dishy est accessible sur le réseau")
                return True
            else:
                logger.warning(f"Dishy non accessible sur {self.ip}:{self.port} (code: {result})")
                return False
        except socket.timeout:
            logger.warning(f"Timeout lors de la vérification de connectivité vers {self.ip}:{self.port}")
            return False
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification de connectivité: {e}")
            return False

    def _verify_grpc_api(self):
        """
        Vérifie la disponibilité et la version de l'API gRPC.
        Retourne un tuple (is_available, api_info).
        """
        if not starlink_grpc:
            logger.error("Bibliothèque starlink-grpc-core non trouvée. Veuillez l'installer.")
            return (False, None)
        
        try:
            # Vérifier les attributs disponibles dans la bibliothèque
            api_info = {
                "has_get_location": hasattr(starlink_grpc, 'get_location'),
                "has_get_status": hasattr(starlink_grpc, 'get_status'),
                "has_get_history": hasattr(starlink_grpc, 'get_history'),
                "module_version": getattr(starlink_grpc, '__version__', 'unknown')
            }
            
            logger.info(f"Informations API gRPC: {api_info}")
            
            if not any([api_info["has_get_location"], api_info["has_get_status"]]):
                logger.warning("Aucune méthode de récupération de position trouvée dans l'API")
                return (False, api_info)
            
            return (True, api_info)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'API gRPC: {e}")
            return (False, None)

    def _get_location_via_status(self, context=None):
        """
        Tente de récupérer la position via get_status si disponible.
        """
        try:
            if hasattr(starlink_grpc, 'get_status'):
                logger.debug("Tentative de récupération via get_status...")
                if context:
                    status = starlink_grpc.get_status(context)
                else:
                    status = starlink_grpc.get_status(self.ip, self.port)
                
                # Essayer d'extraire les coordonnées GPS du statut
                # La structure exacte dépend de la version de l'API
                if isinstance(status, dict):
                    # Formats possibles selon les versions
                    if 'location' in status:
                        loc = status['location']
                        if 'latitude' in loc and 'longitude' in loc:
                            return (loc['latitude'], loc['longitude'])
                    if 'latitude' in status and 'longitude' in status:
                        return (status['latitude'], status['longitude'])
                    if 'gps' in status:
                        gps = status['gps']
                        if 'latitude' in gps and 'longitude' in gps:
                            return (gps['latitude'], gps['longitude'])
                
                logger.debug(f"Structure de status reçue: {type(status)}")
        except Exception as e:
            logger.debug(f"Erreur lors de la récupération via get_status: {e}")
        
        return None

    def _get_location_direct(self):
        """
        Tente de récupérer la position via get_location si disponible.
        """
        try:
            if hasattr(starlink_grpc, 'get_location'):
                logger.debug("Tentative de récupération via get_location...")
                # Essayer différentes signatures de fonction possibles
                location = None
                try:
                    location = starlink_grpc.get_location(self.ip, self.port)
                except TypeError:
                    # Peut-être que la fonction nécessite un contexte
                    try:
                        location = starlink_grpc.get_location()
                    except:
                        pass
                
                if location:
                    if isinstance(location, tuple) and len(location) == 2:
                        return location
                    elif isinstance(location, dict):
                        if 'latitude' in location and 'longitude' in location:
                            return (location['latitude'], location['longitude'])
        except Exception as e:
            logger.debug(f"Erreur lors de la récupération via get_location: {e}")
        
        return None

    def get_gps_position(self):
        """
        Se connecte au Dishy Starlink et récupère les données de localisation.
        Inclut la vérification de connectivité, la vérification de l'API, et la gestion des timeouts.
        Retourne: tuple (latitude, longitude) ou None si échec.
        """
        if not starlink_grpc:
            logger.error("Bibliothèque starlink-grpc-core non trouvée. Veuillez l'installer.")
            return None

        # Vérifier la connectivité réseau d'abord
        if not self._check_connectivity():
            logger.error(f"Dishy non accessible sur {self.ip}:{self.port}. Vérifiez la connexion réseau.")
            return None

        # Vérifier l'API gRPC
        is_available, api_info = self._verify_grpc_api()
        if not is_available:
            logger.error("API gRPC non disponible ou incompatible")
            return None

        try:
            logger.info(f"Interrogation du Dishy à {self.ip}:{self.port}...")
            
            # Créer un contexte avec timeout si l'API le supporte
            context = None
            if GRPC_AVAILABLE and hasattr(grpc, 'insecure_channel'):
                try:
                    channel = grpc.insecure_channel(f"{self.ip}:{self.port}")
                    # Configurer le timeout
                    grpc.channel_ready_future(channel).result(timeout=self.timeout)
                    context = channel
                except Exception as e:
                    logger.debug(f"Impossible de créer un contexte gRPC direct: {e}")
            
            # Essayer différentes méthodes pour récupérer la position
            position = None
            
            # Méthode 1: get_location direct
            position = self._get_location_direct()
            if position:
                logger.info(f"Position récupérée via get_location: {position}")
                return position
            
            # Méthode 2: get_status puis extraction
            position = self._get_location_via_status(context)
            if position:
                logger.info(f"Position récupérée via get_status: {position}")
                return position
            
            # Si aucune méthode n'a fonctionné
            logger.warning("Aucune méthode de récupération de position n'a fonctionné. "
                          "Vérifiez la version de l'API starlink-grpc-core et la documentation.")
            return None

        except socket.timeout:
            logger.error(f"Timeout lors de la connexion au Dishy (timeout: {self.timeout}s)")
            return None
        except grpc.RpcError as e:
            logger.error(f"Erreur gRPC lors de la récupération des données GPS: {e}")
            return None
        except Exception as e:
            logger.error(f"Échec de la récupération des données GPS: {e}")
            return None

# Simple manual test block
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = StarlinkMonitor()
    pos = monitor.get_gps_position()
    print(f"Position: {pos}")
