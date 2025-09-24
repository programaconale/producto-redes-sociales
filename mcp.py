import requests
from datetime import datetime, date
from typing import Dict, Optional, List, Any
from urllib.parse import urlencode, quote

class MetricoolAPIClient:
    """Cliente optimizado para interactuar con la API de Metricool con autenticación"""
    
    def __init__(self, user_id: int = None, blog_id: int = None, user_token: str = None):
        """
        Inicializa el cliente con los IDs desde secrets o por defecto
        
        Args:
            user_id: ID del usuario de Metricool
            blog_id: ID del blog/marca en Metricool
            user_token: Token de usuario para autenticación
        """
        import streamlit as st
        
        self.base_url = "https://app.metricool.com/api"
        
        # Configuración con valores por defecto si no están en secrets
        try:
            self.user_id = user_id or st.secrets["api_keys"]["metricool_user_id"]
            self.blog_id = blog_id or st.secrets["projects"]["default_blog_id"]
            self.user_token = user_token or st.secrets["api_keys"]["metricool_user_token"]
        except KeyError:
            # Valores por defecto si no están configurados en secrets
            self.user_id = user_id or 3752757
            self.blog_id = blog_id or 4827857
            self.user_token = user_token or "AFILXUDKQGBHUMVPOXHFWVJEXWLVPSTTXSSVSJLPKIUZHXSHCBCRHFGLMQUYDFIA"
        
        self.session = requests.Session()
        self.auth_configured = True
        
    def set_user_token(self, user_token: str):
        """
        Configura el token de usuario para autenticación
        
        Args:
            user_token: Token de usuario de Metricool
        """
        self.user_token = user_token
        self.auth_configured = True
        print("✅ User Token configurado")
        """
        Configura el token Bearer para autenticación
        
        Args:
            token: Token de autenticación Bearer
        """
        self.session.headers.update({
            'Authorization': f'Bearer {self.user_token}'
        })
        self.auth_configured = True
        print("✅ Token Bearer configurado")
    
    def set_api_key(self, api_key: str):
        """
        Configura la API Key para autenticación
        
        Args:
            api_key: API Key de Metricool
        """
        self.session.headers.update({
            'X-API-Key': api_key
        })
        self.auth_configured = True
        print("✅ API Key configurada")
    
    def set_cookies(self, cookies: Dict[str, str]):
        """
        Configura las cookies de sesión
        
        Args:
            cookies: Diccionario con las cookies de sesión
        """
        for key, value in cookies.items():
            self.session.cookies.set(key, value)
        self.auth_configured = True
        print("✅ Cookies configuradas")
    
    def set_raw_cookie_string(self, cookie_string: str):
        """
        Configura las cookies desde un string copiado del navegador
        
        Args:
            cookie_string: String de cookies copiado del navegador
        """
        self.session.headers.update({
            'Cookie': cookie_string
        })
        self.auth_configured = True
        print("✅ Cookies configuradas desde string")
    
    def set_headers(self, headers: Dict[str, str]):
        """
        Configura headers personalizados (útil para copiar todos los headers del navegador)
        
        Args:
            headers: Diccionario con headers personalizados
        """
        self.session.headers.update(headers)
        self.auth_configured = True
        print("✅ Headers personalizados configurados")
        
    def _format_datetime(self, dt: datetime, include_timezone: bool = True) -> str:
        """
        Formatea datetime según el formato requerido
        
        Args:
            dt: Objeto datetime
            include_timezone: Si incluir información de timezone
        """
        if include_timezone:
            # Formato con timezone URL-encoded: 2025-06-30T00:00:00+02:00
            return dt.strftime("%Y-%m-%dT%H:%M:%S+02:00")
        else:
            # Formato sin timezone: 2025-06-30T00:00:00
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
    
    def _format_date_simple(self, dt: datetime) -> str:
        """Formatea fecha en formato simple YYYYMMDD"""
        return dt.strftime("%Y%m%d")
    
    def _build_url(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Construye la URL completa con parámetros
        
        Args:
            endpoint: Endpoint de la API
            params: Parámetros de la query
        """
        # Agregar parámetros comunes
        params['userId'] = self.user_id
        params['blogId'] = self.blog_id
        
        # Agregar userToken si está configurado
        if self.user_token:
            params['userToken'] = self.user_token
        
        # Construir URL
        url = f"{self.base_url}/{endpoint}"
        if params:
            # Codificar parámetros especiales
            encoded_params = []
            for key, value in params.items():
                if key in ['from', 'to'] and '+' in str(value):
                    # Manejar timezone encoding especial
                    encoded_params.append(f"{key}={quote(str(value), safe='')}")
                else:
                    encoded_params.append(f"{key}={value}")
            
            url += "?" + "&".join(encoded_params)
        
        return url
    
    def _make_request(self, url: str) -> Dict:
        """
        Realiza la petición HTTP con manejo de errores
        
        Args:
            url: URL completa para la petición
        """
        if not self.auth_configured and not self.user_token:
            print("⚠️  ADVERTENCIA: No se ha configurado autenticación (userToken). Es probable que recibas error 401.")
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 401:
                error_msg = "❌ Error 401: No autorizado. Necesitas configurar el userToken."
                print(error_msg)
                return {
                    'url': url, 
                    'status': response.status_code, 
                    'error': error_msg,
                    'data': None
                }
            elif response.status_code == 403:
                error_msg = "❌ Error 403: Prohibido. Verifica que tienes permisos para este recurso."
                print(error_msg)
                return {
                    'url': url,
                    'status': response.status_code,
                    'error': error_msg,
                    'data': None
                }
            elif response.ok:
                return {
                    'url': url,
                    'status': response.status_code,
                    'data': response.json()
                }
            else:
                return {
                    'url': url,
                    'status': response.status_code,
                    'error': f"Error {response.status_code}: {response.text[:200]}",
                    'data': None
                }
                
        except Exception as e:
            return {
                'url': url,
                'status': 0,
                'error': f"Error en la petición: {str(e)}",
                'data': None
            }
    
    def get_timeline_analytics(
        self,
        from_date: datetime,
        to_date: datetime,
        metric: str = "delta_followers",
        network: str = "instagram",
        timezone: str = "Europe/Madrid",
        subject: str = "account"
    ) -> Dict:
        """
        Obtiene analytics de timeline
        
        Ejemplo: delta_followers de Instagram
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True),
            'metric': metric,
            'network': network,
            'timezone': timezone,
            'subject': subject
        }
        
        url = self._build_url("v2/analytics/timelines", params)
        return self._make_request(url)
    
    def get_aggregation_analytics(
        self,
        from_date: datetime,
        to_date: datetime,
        metric: str = "reach",
        network: str = "instagram",
        timezone: str = "Europe/Madrid",
        subject: str = "reels"
    ) -> Dict:
        """
        Obtiene analytics agregados
        
        Ejemplo: reach de Reels de Instagram
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True),
            'metric': metric,
            'network': network,
            'timezone': timezone,
            'subject': subject
        }
        
        url = self._build_url("v2/analytics/aggregation", params)
        return self._make_request(url)
    
    def get_country_distribution(
        self,
        start_date: datetime,
        end_date: datetime,
        encode: bool = True
    ) -> Dict:
        """
        Obtiene distribución por país (formato de fecha simple)
        """
        params = {
            'start': self._format_date_simple(start_date),
            'end': self._format_date_simple(end_date),
            'encode': str(encode).lower()
        }
        
        url = self._build_url("stats/distribution/country", params)
        return self._make_request(url)
    
    def get_distribution_analytics(
        self,
        from_date: datetime,
        to_date: datetime,
        metric: str,  # age, city, country, gender
        network: str = "instagram",
        subject: str = "account"
    ) -> Dict:
        """
        Obtiene analytics de distribución (edad, ciudad, país, género)
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=False),
            'to': self._format_datetime(to_date, include_timezone=False),
            'metric': metric,
            'network': network,
            'subject': subject
        }
        
        url = self._build_url("v2/analytics/distribution", params)
        return self._make_request(url)
    
    def get_instagram_hashtags(
        self,
        from_date: datetime,
        to_date: datetime
    ) -> Dict:
        """
        Obtiene analytics de hashtags de Instagram
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True)
        }
        
        url = self._build_url("v2/analytics/posts/instagram/hashtags", params)
        return self._make_request(url)
    
    def get_instagram_posts(
        self,
        from_date: datetime,
        to_date: datetime
    ) -> Dict:
        """
        Obtiene analytics de posts de Instagram
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True)
        }
        
        url = self._build_url("v2/analytics/posts/instagram", params)
        return self._make_request(url)
    
    def get_instagram_reels(
        self,
        from_date: datetime,
        to_date: datetime
    ) -> Dict:
        """
        Obtiene analytics de Reels de Instagram
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True)
        }
        
        url = self._build_url("v2/analytics/reels/instagram", params)
        return self._make_request(url)
    
    def execute_all_requests(self, period1_from: datetime, period1_to: datetime,
                           period2_from: datetime, period2_to: datetime) -> Dict[str, Any]:
        """
        Ejecuta todas las requests con los períodos especificados
        
        Args:
            period1_from: Fecha inicio período 1 (mayo-junio)
            period1_to: Fecha fin período 1
            period2_from: Fecha inicio período 2 (junio-julio)
            period2_to: Fecha fin período 2
        """
        results = {}
        
        # Request 1: Timeline analytics (período 1)
        results['timeline_delta_followers'] = self.get_timeline_analytics(
            period1_from, period1_to
        )
        
        # Request 2: Aggregation analytics - Reach de Reels (período 2)
        results['reels_reach'] = self.get_aggregation_analytics(
            period2_from, period2_to
        )
        
        # Request 3: Country distribution con formato simple (período 2)
        results['country_distribution_stats'] = self.get_country_distribution(
            period2_from, period2_to
        )
        
        # Requests 4-7: Distribution analytics (período 2)
        for metric in ['age', 'city', 'country', 'gender']:
            results[f'distribution_{metric}'] = self.get_distribution_analytics(
                period2_from, period2_to, metric
            )
        
        # Request 8: Instagram hashtags (período 2)
        results['instagram_hashtags'] = self.get_instagram_hashtags(
            period2_from, period2_to
        )
        
        # Request 9: Instagram posts (período 2)
        results['instagram_posts'] = self.get_instagram_posts(
            period2_from, period2_to
        )
        
        # Request 10: Instagram reels (período 2)
        results['instagram_reels'] = self.get_instagram_reels(
            period2_from, period2_to
        )
        
        return results
    
    def get_facebook_timeline(
        self,
        from_date: datetime,
        to_date: datetime,
        metric: str
    ) -> Dict:
        """
        Obtiene métricas de timeline de Facebook
        
        Args:
            from_date: Fecha de inicio
            to_date: Fecha de fin
            metric: Métrica a obtener (pageFollows, likes, pageImpressions, pageViews, postsCount)
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True),
            'metric': metric,
            'network': 'facebook',
            'timezone': 'Europe/Madrid',
            'subject': 'account',
            'userId': '4031061',
            'blogId': '4827857'  # Cambiado para usar el mismo que Instagram de Widu Legal
        }
        
        url = self._build_url("v2/analytics/timelines", params)
        return self._make_request(url)
    
    def get_facebook_posts(
        self,
        from_date: datetime,
        to_date: datetime
    ) -> Dict:
        """
        Obtiene analytics de posts de Facebook
        
        Args:
            from_date: Fecha de inicio
            to_date: Fecha de fin
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True),
            'timezone': 'Europe/Madrid',
            'userId': '4031061',
            'blogId': '4827857'  # Cambiado para usar el mismo que Instagram de Widu Legal
        }
        
        url = self._build_url("v2/analytics/posts/facebook", params)
        return self._make_request(url)
    
    def get_facebook_distribution(
        self,
        from_date: datetime,
        to_date: datetime,
        metric: str
    ) -> Dict:
        """
        Obtiene distribución de métricas de Facebook
        
        Args:
            from_date: Fecha de inicio
            to_date: Fecha de fin
            metric: Métrica a obtener (followersByCountry, followersByCity)
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=False),
            'to': self._format_datetime(to_date, include_timezone=False),
            'metric': metric,
            'network': 'facebook',
            'subject': 'account',
            'userId': '4031061',
            'blogId': '4827857'  # Cambiado para usar el mismo que Instagram de Widu Legal
        }
        
        url = self._build_url("v2/analytics/distribution", params)
        return self._make_request(url)
    
    def get_youtube_timeline(
        self,
        from_date: datetime,
        to_date: datetime,
        metric: str
    ) -> Dict:
        """
        Obtiene métricas de timeline de YouTube
        
        Args:
            from_date: Fecha de inicio
            to_date: Fecha de fin
            metric: Métrica a obtener (views, likes, dislikes, comments, shares)
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True),
            'metric': metric,
            'network': 'youtube',
            'postsType': 'publishedInRange',
            'timezone': 'Europe/Madrid',
            'userId': '4031061',
            'blogId': '4827857'
        }
        
        url = self._build_url("v2/analytics/timelines", params)
        return self._make_request(url)
    
    def get_youtube_videos_count(
        self,
        from_date: date,
        to_date: date
    ) -> Dict:
        """
        Obtiene el conteo de videos de YouTube
        
        Args:
            from_date: Fecha de inicio
            to_date: Fecha de fin
        """
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'postsType': 'publishedInRange',
            'timezone': 'Europe/Madrid',
            'userId': '4031061',
            'blogId': '4827857'
        }
        
        url = self._build_url("stats/timeline/ytVideos", params)
        return self._make_request(url)
    
    def get_youtube_posts(
        self,
        from_date: datetime,
        to_date: datetime
    ) -> Dict:
        """
        Obtiene analytics de videos de YouTube
        
        Args:
            from_date: Fecha de inicio
            to_date: Fecha de fin
        """
        params = {
            'from': self._format_datetime(from_date, include_timezone=True),
            'to': self._format_datetime(to_date, include_timezone=True),
            'timezone': 'Europe/Madrid',
            'postsType': 'publishedInRange',
            'userId': '4031061',
            'blogId': '4827857'
        }
        
        url = self._build_url("v2/analytics/posts/youtube", params)
        return self._make_request(url)

    # Google Analytics / Web Analytics Methods
    def get_page_views(self, from_date: date, to_date: date):
        """Obtiene datos de vistas de página"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'timezone': 'Europe/Madrid',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/timeline/PageViews", params)
        return self._make_request(url)

    def get_sessions_count(self, from_date: date, to_date: date):
        """Obtiene datos de sesiones"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'timezone': 'Europe/Madrid',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/timeline/SessionsCount", params)
        return self._make_request(url)

    def get_visitors(self, from_date: date, to_date: date):
        """Obtiene datos de visitantes"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'timezone': 'Europe/Madrid',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/timeline/Visitors", params)
        return self._make_request(url)

    def get_daily_posts(self, from_date: date, to_date: date):
        """Obtiene datos de publicaciones diarias"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'timezone': 'Europe/Madrid',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/timeline/DailyPosts", params)
        return self._make_request(url)

    def get_daily_comments(self, from_date: date, to_date: date):
        """Obtiene datos de comentarios diarios"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'timezone': 'Europe/Madrid',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/timeline/DailyComments", params)
        return self._make_request(url)

    def get_visits_by_country(self, from_date: date, to_date: date):
        """Obtiene datos de visitas por país"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'encode': 'true',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/distribution/country", params)
        return self._make_request(url)

    def get_referers(self, from_date: date, to_date: date):
        """Obtiene datos de referencias/páginas visitadas"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'encode': 'true',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/distribution/referers", params)
        return self._make_request(url)

    def get_web_posts(self, from_date: date, to_date: date):
        """Obtiene datos de posts del sitio web"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/posts", params)
        return self._make_request(url)

    def get_traffic_sources(self, from_date: date, to_date: date):
        """Obtiene datos de fuentes de tráfico"""
        params = {
            'start': from_date.strftime('%Y%m%d'),
            'end': to_date.strftime('%Y%m%d'),
            'encode': 'true',
            'userId': str(self.user_id),
            'blogId': str(self.blog_id)
        }
        
        url = self._build_url("stats/distribution/sources", params)
        return self._make_request(url)


# ========================================
# INSTRUCCIONES PARA OBTENER AUTENTICACIÓN
# ========================================
"""
Para obtener el userToken de Metricool:

OPCIÓN 1: Desde las peticiones del navegador (RECOMENDADO)
-----------------------------------------------------------
1. Abre Chrome/Firefox y ve a https://app.metricool.com
2. Inicia sesión normalmente
3. Abre las DevTools (F12)
4. Ve a la pestaña "Network" (Red)
5. Refresca la página o navega por Metricool
6. Busca cualquier petición a la API (que empiece con /api/)
7. Click en la petición
8. En la URL verás: &userToken=AFILXUDKQGBHUMVPOXHFWVJEXWLVPSTTXSSVSJLPKIUZHXSHCBCRHFGLMQUYDFIA
9. Copia ese token

OPCIÓN 2: Usando las cookies del navegador
-------------------------------------------
1. En las DevTools, pestaña "Network"
2. Click derecho en cualquier petición > Copy > Copy as cURL
3. Busca la línea que empieza con -H 'Cookie: ...'
4. Copia todo el contenido de las cookies

OPCIÓN 3: Usando un Bearer Token (si está disponible)
------------------------------------------------------
1. En las DevTools, pestaña "Network"
2. Click en cualquier petición a la API
3. Ve a "Headers" > "Request Headers"
4. Busca "Authorization: Bearer [token]"
5. Copia el token
"""


if __name__ == "__main__":
    # MÉTODO 1: Inicializar cliente con userToken directamente
    client = MetricoolAPIClient(
        user_id=4031061, 
        blog_id=4827857,
        user_token="AFILXUDKQGBHUMVPOXHFWVJEXWLVPSTTXSSVSJLPKIUZHXSHCBCRHFGLMQUYDFIA"  # Tu token aquí
    )
    
    # MÉTODO 2: Configurar userToken después de inicializar
    # client = MetricoolAPIClient(user_id=4031061, blog_id=4827857)
    # client.set_user_token("AFILXUDKQGBHUMVPOXHFWVJEXWLVPSTTXSSVSJLPKIUZHXSHCBCRHFGLMQUYDFIA")
    
    # Definir períodos de tiempo
    period1_from = datetime(2025, 5, 29, 0, 0, 0)
    period1_to = datetime(2025, 6, 29, 23, 59, 59)
    
    period2_from = datetime(2025, 6, 30, 0, 0, 0)
    period2_to = datetime(2025, 7, 31, 23, 59, 59)
    
    # Ejecutar todas las requests
    all_results = client.execute_all_requests(
        period1_from, period1_to,
        period2_from, period2_to
    )
    
    # Imprimir URLs generadas
    print("URLs generadas:")
    for key, result in all_results.items():
        print(f"\n{key}:")
        print(f"  URL: {result['url']}")
        print(f"  Status: {result['status']}")
        if result.get('data'):
            print(f"  ✅ Datos recibidos correctamente")
    
    # También puedes ejecutar requests individuales
    print("\n--- Ejemplo de request individual ---")
    result = client.get_timeline_analytics(
        from_date=datetime(2025, 5, 29, 0, 0, 0),
        to_date=datetime(2025, 6, 29, 23, 59, 59),
        metric="delta_followers",
        network="instagram"
    )
    print(f"URL: {result['url']}")
    print(f"Status: {result['status']}")
    
    # Ejemplo con diferentes métricas
    print("\n--- Ejemplo con diferentes métricas ---")
    result = client.get_aggregation_analytics(
        from_date=datetime(2025, 6, 30, 0, 0, 0),
        to_date=datetime(2025, 7, 31, 23, 59, 59),
        metric="impressions",  # Cambiar métrica
        network="instagram",
        subject="stories"  # Cambiar subject
    )
    print(f"URL: {result['url']}")
    print(f"Status: {result['status']}")