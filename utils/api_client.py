# utils/api_client.py
import requests
import os
import time
import socket
from dotenv import load_dotenv

class SIGAClient:
    def __init__(self):
        load_dotenv()
        
        self.base_urls = [
            "https://siga.talentotech2.com.co/siga_new/web/app.php/api/rest",
            "http://talentotech2prueba.datasae.com/siga_new/web/app.php/api/rest"
        ]
        self.current_base_url = None
        
        self.client_id = "talentotech2_webservice"
        self.secreto = "LcU54XCSqzRU"
        self.access_token = None
        self.auth_token = None
        
        self.siga_username = os.getenv('SIGA_USERNAME', 'api_user')
        self.siga_password = os.getenv('SIGA_PASSWORD', 'Api_user123*')
        
        self.periodos_academicos = [
            '2024090208', '2024091608', '2024100708', 
            '2024101510', '2025011112', '2025012710'
        ]
    
    def authenticate(self):
        """Autenticar en la API de SIGA"""
        if not self._test_endpoints():
            return False
        
        if not self._get_access_token():
            return False
            
        if not self._authenticate_user():
            return False
            
        return True
    
    def _test_endpoints(self):
        """Probar endpoints disponibles"""
        for base_url in self.base_urls:
            hostname = base_url.split('//')[1].split('/')[0]
            try:
                socket.gethostbyname(hostname)
                self.current_base_url = base_url
                return True
            except:
                continue
        return False
    
    def _get_access_token(self):
        """Obtener token de acceso"""
        try:
            session = requests.Session()
            session.trust_env = False
            
            response = session.post(
                f"{self.current_base_url}/obtener_token",
                data={'client_id': self.client_id, 'secreto': self.secreto},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                datos = response.json()
                if datos.get('RESPUESTA') == '1':
                    self.access_token = datos.get('access_token')
                    return True
        except:
            pass
        return False
    
    def _authenticate_user(self):
        """Autenticar usuario"""
        try:
            session = requests.Session()
            session.trust_env = False
            
            response = session.post(
                f"{self.current_base_url}/autenticar",
                data={'username': self.siga_username, 'password': self.siga_password},
                headers={'auth_token': self.access_token},
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                datos = response.json()
                if datos.get('RESPUESTA') == '1':
                    self.auth_token = datos.get('TOKEN')
                    return True
        except:
            pass
        return False
    
    def get_reporte_1003(self):
        """Obtener reporte 1003"""
        try:
            session = requests.Session()
            session.trust_env = False
            
            response = session.post(
                f"{self.current_base_url}/talentotech2/informacion_reporte_1003",
                json={"soloactivos": True},
                headers={
                    'token': self.access_token,
                    'token_autenticacion': self.auth_token,
                    'Content-Type': 'application/json'
                },
                timeout=120,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def get_reporte_992_completo(self):
        """Obtener reporte 992 de todos los periodos"""
        datos_consolidados = []
        
        for periodo in self.periodos_academicos:
            try:
                session = requests.Session()
                session.trust_env = False
                
                payload = {
                    "cod_periodo_academico": int(periodo),
                    "solo_pendientes_matricula": False
                }
                
                response = session.post(
                    f"{self.current_base_url}/talentotech2/informacion_reporte_992",
                    json=payload,
                    headers={
                        'token': self.access_token,
                        'token_autenticacion': self.auth_token,
                        'Content-Type': 'application/json'
                    },
                    timeout=60,
                    verify=False
                )
                
                if response.status_code == 200:
                    datos = response.json()
                    if isinstance(datos, list):
                        for registro in datos:
                            registro['cod_periodo_academico'] = periodo
                        datos_consolidados.extend(datos)
                
                time.sleep(1)  # Pausa entre requests
                
            except:
                continue
        
        return datos_consolidados if datos_consolidados else None