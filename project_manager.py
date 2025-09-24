"""
Gestor de proyectos/clientes para el dashboard de Analytics
"""

import streamlit as st
from mcp import MetricoolAPIClient
from datetime import datetime
import json

# Configuración dinámica - se obtiene de la API

USER_ID = st.secrets["api_keys"]["metricool_user_id"]
USER_TOKEN = st.secrets["api_keys"]["metricool_user_token"]

@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_all_projects():
    """Obtiene todos los proyectos disponibles del usuario"""
    try:
        # Crear cliente temporal para obtener proyectos
        temp_client = MetricoolAPIClient(
            user_id=USER_ID,
            blog_id=4827857,  # Blog ID temporal para la consulta
            user_token=USER_TOKEN
        )
        
        # Construir URL del endpoint de proyectos
        params = {
            'userId': str(USER_ID)
        }
        
        url = temp_client._build_url("admin/simpleProfiles", params)
        response = temp_client._make_request(url)
        
        if response and response.get('status') == 200:
            profiles_data = response.get('data', [])
            
            # Convertir a formato de proyectos
            projects = {}
            for i, profile in enumerate(profiles_data):
                try:
                    if isinstance(profile, dict):
                        blog_id = profile.get('id')
                        label = profile.get('label', f'Proyecto {blog_id}')
                        url_site = profile.get('url', '')
                        
                        # Validar que blog_id existe y es válido
                        if blog_id is None:
                            st.warning(f"⚠️ Proyecto {i} sin blog_id, saltando...")
                            continue
                        
                        # Asegurar que todos los valores son strings válidos
                        clean_label = str(label) if label is not None else f'Proyecto {blog_id}'
                        clean_url = str(url_site) if url_site is not None else ''
                        clean_blog_id = int(blog_id) if str(blog_id).isdigit() else blog_id
                        
                        # Crear clave única para el proyecto
                        project_key = f"project_{clean_blog_id}"
                        
                        projects[project_key] = {
                            'name': clean_label,
                            'blog_id': clean_blog_id,
                            'description': f'Sitio web: {clean_url}' if clean_url else f'Blog ID: {clean_blog_id}',
                            'url': clean_url,
                            'raw_data': profile  # Guardar datos completos para debug
                        }
                    else:
                        st.warning(f"⚠️ Proyecto {i} no es un diccionario: {type(profile)}")
                except Exception as e:
                    st.error(f"❌ Error procesando proyecto {i}: {str(e)}")
                    continue
            
            return projects
        else:
            st.error(f"Error obteniendo proyectos: Status {response.get('status') if response else 'Sin respuesta'}")
            return {}
            
    except Exception as e:
        st.error(f"Error obteniendo proyectos: {str(e)}")
        return {}

@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_project_profile(blog_id: int):
    """Obtiene el perfil de un proyecto/cliente específico"""
    try:
        client = MetricoolAPIClient(
            user_id=USER_ID,
            blog_id=blog_id,
            user_token=USER_TOKEN
        )
        
        # Construir URL del endpoint de perfil
        params = {
            'refreshBrandCache': 'false',
            'userId': str(USER_ID),
            'blogId': str(blog_id)
        }
        
        url = client._build_url("admin/profile", params)
        response = client._make_request(url)
        
        if response and response.get('status') == 200:
            return response.get('data', {})
        else:
            return None
            
    except Exception as e:
        st.error(f"Error obteniendo perfil del proyecto: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def check_network_data_availability(_client, blog_id, network):
    """Verifica si hay datos disponibles para una red social específica"""
    from datetime import datetime, date
    
    try:
        # Calcular fechas del último mes
        today = date.today()
        if today.month == 1:
            last_month = 12
            year = today.year - 1
        else:
            last_month = today.month - 1
            year = today.year
        
        from_date = datetime(year, last_month, 1)
        to_date = datetime(year, last_month + 1, 1) - datetime.resolution
        
        # Mapeo de redes sociales a sus métricas principales
        network_metrics = {
            'instagram': 'followers',
            'linkedin': 'Followers', 
            'facebook': 'pageFollows',
            'youtube': 'views'
        }
        
        if network not in network_metrics:
            return False
        
        metric = network_metrics[network]
        
        # Hacer una consulta de prueba para ver si hay datos
        if network == 'facebook':
            response = _client.get_facebook_timeline(from_date, to_date, metric)
        elif network == 'youtube':
            response = _client.get_youtube_timeline(from_date, to_date, metric)
        else:
            response = _client.get_timeline_analytics(
                from_date=from_date,
                to_date=to_date,
                metric=metric,
                network=network,
                subject="account"
            )
        
        # Verificar si la respuesta tiene datos válidos
        if response and response.get('status') == 200:
            data = response.get('data', {}).get('data', [])
            return len(data) > 0 and any(item.get('value', 0) >= 0 for item in data)
        
        return False
        
    except Exception as e:
        return False

def get_available_networks(profile_data, client=None, blog_id=None):
    """Extrae las redes sociales disponibles del perfil y verifica si tienen datos"""
    if not profile_data:
        return {}
    
    networks = {}
    
    # Instagram
    if profile_data.get('instagram'):
        has_data = False
        if client and blog_id:
            has_data = check_network_data_availability(client, blog_id, 'instagram')
        
        networks['instagram'] = {
            'name': 'Instagram',
            'handle': profile_data.get('instagram'),
            'picture': profile_data.get('instagramPicture'),
            'icon': '📸',
            'available': True,
            'has_data': has_data
        }
    
    # LinkedIn
    if profile_data.get('linkedinCompany'):
        has_data = False
        if client and blog_id:
            has_data = check_network_data_availability(client, blog_id, 'linkedin')
        
        networks['linkedin'] = {
            'name': 'LinkedIn',
            'company_name': profile_data.get('linkedInCompanyName'),
            'picture': profile_data.get('linkedInPicture'),
            'icon': '💼',
            'available': True,
            'has_data': has_data
        }
    
    # Facebook
    if profile_data.get('facebook'):
        has_data = False
        if client and blog_id:
            has_data = check_network_data_availability(client, blog_id, 'facebook')
        
        networks['facebook'] = {
            'name': 'Facebook',
            'page_name': profile_data.get('facebook'),
            'page_id': profile_data.get('facebookPageId'),
            'picture': profile_data.get('facebookPicture'),
            'icon': '📘',
            'available': True,
            'has_data': has_data
        }
    
    # YouTube
    if profile_data.get('youtube'):
        has_data = False
        if client and blog_id:
            has_data = check_network_data_availability(client, blog_id, 'youtube')
        
        networks['youtube'] = {
            'name': 'YouTube',
            'channel_id': profile_data.get('youtube'),
            'channel_name': profile_data.get('youtubeChannelName'),
            'picture': profile_data.get('youtubeChannelPicture'),
            'icon': '📺',
            'available': True,
            'has_data': has_data
        }
    
    # Twitter/X
    if profile_data.get('twitter'):
        networks['twitter'] = {
            'name': 'Twitter',
            'handle': profile_data.get('twitter'),
            'picture': profile_data.get('twitterPicture'),
            'icon': '🐦',
            'available': True,
            'has_data': False  # No implementado aún
        }
    
    # TikTok
    if profile_data.get('tiktok'):
        networks['tiktok'] = {
            'name': 'TikTok',
            'handle': profile_data.get('tiktok'),
            'picture': profile_data.get('tiktokPicture'),
            'icon': '📱',
            'available': True,
            'has_data': False  # No implementado aún
        }
    
    return networks

def create_project_selector():
    """Crea el selector de proyectos en el sidebar"""
    st.sidebar.header("🏢 Selector de Proyecto")
    
    # Obtener proyectos dinámicamente
    with st.spinner("🔍 Cargando proyectos..."):
        available_projects = get_all_projects()
    
    if not available_projects:
        st.sidebar.error("❌ No se pudieron cargar los proyectos")
        return None, None, {}
    
    
    # Validar y limpiar datos de proyectos
    clean_projects = {}
    for key, value in available_projects.items():
        try:
            # Asegurar que key es string
            clean_key = str(key) if key is not None else f"project_unknown_{len(clean_projects)}"
            
            # Asegurar que name es string
            project_name = value.get("name", f"Proyecto {value.get('blog_id', 'Unknown')}")
            clean_name = str(project_name) if project_name is not None else f"Proyecto {clean_key}"
            
            clean_projects[clean_key] = {
                **value,
                "name": clean_name
            }
        except Exception as e:
            st.sidebar.warning(f"⚠️ Error procesando proyecto {key}: {str(e)}")
            continue
    
    if len(clean_projects) == 0:
        st.sidebar.error("❌ No hay proyectos válidos disponibles")
        return None, None, {}
    
    # Crear opciones para el selectbox
    project_options = {key: value["name"] for key, value in clean_projects.items()}
    
    
    try:
        selected_project_key = st.sidebar.selectbox(
            "Selecciona el proyecto:",
            options=list(project_options.keys()),
            format_func=lambda x: project_options.get(x, str(x)),
            key="selected_project"
        )
    except Exception as e:
        st.sidebar.error(f"❌ Error en selector: {str(e)}")
        st.sidebar.write("**Debug info:**")
        st.sidebar.write(f"- Total opciones: {len(project_options)}")
        st.sidebar.write(f"- Claves: {list(project_options.keys())}")
        st.sidebar.write(f"- Valores: {list(project_options.values())}")
        return None, None, {}
    
    selected_project = clean_projects[selected_project_key]
    
    # Mostrar información del proyecto seleccionado
    st.sidebar.info(f"""
    **📋 Proyecto Seleccionado:**
    {selected_project['name']}
    
    **📝 Descripción:**
    {selected_project['description']}
    
    **🔢 Blog ID:**
    {selected_project['blog_id']}
    """)
    
    # Obtener perfil del proyecto
    with st.spinner("🔍 Verificando redes disponibles..."):
        profile_data = get_project_profile(selected_project['blog_id'])
    
    if profile_data:
        # Crear cliente para verificar datos
        client = create_client_for_current_project()
        
        # Obtener redes disponibles y verificar datos
        with st.spinner("📊 Verificando disponibilidad de datos..."):
            available_networks = get_available_networks(profile_data, client, selected_project['blog_id'])
        
        # Mostrar redes disponibles
        st.sidebar.success("✅ Proyecto cargado correctamente")
        st.sidebar.markdown("**🌐 Redes Sociales Activas:**")
        
        if available_networks:
            for network_key, network_info in available_networks.items():
                icon = network_info['icon']
                name = network_info['name']
                has_data = network_info.get('has_data', False)
                
                # Información adicional según la red
                extra_info = ""
                if network_key == 'instagram':
                    extra_info = f"@{network_info['handle']}"
                elif network_key == 'linkedin':
                    extra_info = network_info['company_name']
                elif network_key == 'facebook':
                    extra_info = network_info['page_name']
                elif network_key == 'youtube':
                    extra_info = network_info['channel_name']
                elif network_key == 'twitter':
                    extra_info = f"@{network_info['handle']}"
                elif network_key == 'tiktok':
                    extra_info = f"@{network_info['handle']}"
                
                # Indicador de datos
                data_indicator = "✅" if has_data else "⚠️"
                data_text = "con datos" if has_data else "sin datos"
                
                st.sidebar.markdown(f"- {icon} **{name}** {extra_info} {data_indicator} *({data_text})*")
        else:
            st.sidebar.warning("⚠️ No hay redes sociales configuradas")
        
        # Guardar en session state
        st.session_state['current_project'] = selected_project
        st.session_state['current_profile'] = profile_data
        st.session_state['available_networks'] = available_networks
        
        return selected_project, profile_data, available_networks
    else:
        st.sidebar.error("❌ Error al cargar el proyecto")
        st.session_state['current_project'] = None
        st.session_state['current_profile'] = None
        st.session_state['available_networks'] = {}
        
        return None, None, {}

def get_current_blog_id():
    """Obtiene el blog_id del proyecto actualmente seleccionado"""
    current_project = st.session_state.get('current_project')
    if current_project:
        return current_project['blog_id']
    return 4827857  # Default a Widu Legal

def is_network_available(network_name):
    """Verifica si una red social está disponible para el proyecto actual"""
    available_networks = st.session_state.get('available_networks', {})
    return network_name.lower() in available_networks

def show_network_not_available(network_name, icon="📱"):
    """Muestra mensaje cuando una red no está disponible"""
    st.error(f"""
    ## {icon} {network_name} No Disponible
    
    **⚠️ Esta red social no está configurada para el proyecto actual.**
    
    **Proyecto:** {st.session_state.get('current_project', {}).get('name', 'Desconocido')}
    
    **💡 Posibles soluciones:**
    - Verifica que {network_name} esté conectado en Metricool
    - Selecciona un proyecto diferente que tenga {network_name} activo
    - Contacta al administrador para configurar {network_name}
    """)
    
    # Mostrar redes disponibles
    available_networks = st.session_state.get('available_networks', {})
    if available_networks:
        st.info("**🌐 Redes disponibles para este proyecto:**")
        cols = st.columns(len(available_networks))
        for i, (network_key, network_info) in enumerate(available_networks.items()):
            with cols[i]:
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 8px; margin: 5px;'>
                    <div style='font-size: 2rem;'>{network_info['icon']}</div>
                    <div style='font-weight: bold;'>{network_info['name']}</div>
                </div>
                """, unsafe_allow_html=True)

def create_client_for_current_project():
    """Crea un cliente de Metricool para el proyecto actual"""
    blog_id = get_current_blog_id()
    return MetricoolAPIClient(
        user_id=USER_ID,
        blog_id=blog_id,
        user_token=USER_TOKEN
    )

def should_show_network_page(network_name):
    """
    Determina si se debe mostrar una página de red social específica
    Basado en las redes disponibles del proyecto actual
    """
    available_networks = st.session_state.get('available_networks', {})
    
    # Mapeo de nombres de páginas a claves de redes
    network_mapping = {
        'instagram': 'instagram',
        'linkedin': 'linkedin', 
        'facebook': 'facebook',
        'youtube': 'youtube',
        'twitter': 'twitter',
        'tiktok': 'tiktok'
    }
    
    network_key = network_mapping.get(network_name.lower())
    if not network_key:
        return False
    
    # Solo mostrar si la red está disponible Y tiene datos relevantes
    is_available = network_key in available_networks
    
    
    return is_available

def get_network_filter_info():
    """Obtiene información sobre qué redes están disponibles para filtrado"""
    available_networks = st.session_state.get('available_networks', {})
    current_project = st.session_state.get('current_project', {})
    
    return {
        'available_networks': available_networks,
        'project_name': current_project.get('name', 'Desconocido'),
        'blog_id': current_project.get('blog_id', 0),
        'total_networks': len(available_networks)
    }

def show_project_info_header():
    """Muestra información del proyecto en el header"""
    current_project = st.session_state.get('current_project')
    if current_project:
        available_networks = st.session_state.get('available_networks', {})
        networks_count = len(available_networks)
        networks_list = ', '.join([net['name'] for net in available_networks.values()])
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 15px; border-radius: 10px; border-left: 4px solid #000000; margin-bottom: 20px;'>
            <h4 style='margin: 0; color: #000000;'>🏢 {current_project['name']}</h4>
            <p style='margin: 5px 0 0 0; color: #6c757d; font-size: 0.9rem;'>{current_project['description']}</p>
            <p style='margin: 5px 0 0 0; color: #F8E964; font-size: 0.8rem;'>
                🌐 {networks_count} redes activas: {networks_list}
            </p>
        </div>
        """, unsafe_allow_html=True)
