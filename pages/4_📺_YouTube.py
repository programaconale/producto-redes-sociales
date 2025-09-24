import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import sys
import os
import openai
import json

# Agregar el directorio padre al path para importar mcp
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from mcp import MetricoolAPIClient
from project_manager import (
    create_project_selector, 
    is_network_available, 
    show_network_not_available,
    create_client_for_current_project,
    show_project_info_header
)

# Configuración de la página
st.set_page_config(
    page_title="YouTube Analytics - Widu Legal",
    page_icon="📺",
    layout="wide"
)

# Configurar OpenAI
OPENAI_API_KEY = st.secrets["api_keys"]["openai_api_key"]
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Selector de proyectos
project_info, profile_data, available_networks = create_project_selector()

# Verificar si YouTube está disponible para el proyecto actual
if not is_network_available('youtube'):
    show_network_not_available('YouTube', '📺')
    st.stop()

# Mostrar información del proyecto
show_project_info_header()

# Función para obtener cliente dinámico basado en el proyecto actual
@st.cache_resource
def get_current_client(blog_id):
    """Obtiene el cliente de Metricool para el blog_id especificado"""
    return create_client_for_current_project()

# Obtener proyecto actual y cliente
current_project = st.session_state.get('current_project')
if not current_project:
    st.error("❌ No hay proyecto seleccionado. Ve al dashboard principal para seleccionar un proyecto.")
    st.stop()

current_blog_id = current_project.get('blog_id')
client = get_current_client(current_blog_id)

# CSS personalizado para YouTube
st.markdown("""
<style>
    .metric-card {
        background: #F8E964;
        color: black;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .youtube-header {
        background: #F8E964;
        color: black;
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Logo de Jungle Creative Agency en sidebar
st.sidebar.image("https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png", width=200)
st.sidebar.markdown("---")

# Header principal con logos
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.image("https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png", width=150)

with col2:
    st.markdown("""
    <div class='youtube-header'>
        <h1>📺 YouTube Analytics</h1>
        <p>Dashboard completo de métricas de YouTube</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("<p style='text-align: center; font-size: 12px; color: #666; margin-top: -10px;'>Cliente</p>", unsafe_allow_html=True)

# Selector de fechas
st.sidebar.header("⚙️ Configuración")
col1, col2 = st.sidebar.columns(2)

with col1:
    from_date = st.date_input(
        "📅 Fecha inicio",
        value=date(2025, 7, 1),  # Basado en los endpoints proporcionados
        key="youtube_from_date"
    )

with col2:
    to_date = st.date_input(
        "📅 Fecha fin", 
        value=date(2025, 7, 31),  # Basado en los endpoints proporcionados
        key="youtube_to_date"
    )

# Información sobre períodos de datos disponibles
st.sidebar.info("""
📅 **Períodos de datos disponibles:**
- Views/Likes/Comments/Shares: Jul 2025
- Dislikes: May-Jun 2025
- Videos: Jul 2025
""")

# Fechas alternativas para dislikes
dislikes_from_date = date(2025, 5, 31)
dislikes_to_date = date(2025, 6, 30)

# Botón de test (después de definir el cliente)
if st.sidebar.button("🧪 Test API YouTube"):
    st.sidebar.write("🔍 Probando API...")
    
    # Test 1: Views
    test_response = client.get_youtube_timeline(
        from_date=datetime.combine(from_date, datetime.min.time()),
        to_date=datetime.combine(to_date, datetime.max.time()),
        metric='views'
    )
    
    if test_response:
        st.sidebar.write(f"✅ Views Status: {test_response.get('status')}")
        st.sidebar.write(f"🔗 Views URL: {test_response.get('url', 'No URL')}")
    
    # Test 2: Videos Count (específico)
    st.sidebar.write("🔍 Probando conteo de videos...")
    videos_count_response = client.get_youtube_videos_count(
        from_date=from_date,
        to_date=to_date
    )
    
    if videos_count_response:
        st.sidebar.write(f"✅ Videos Count Status: {videos_count_response.get('status')}")
        st.sidebar.write(f"🔗 Videos Count URL: {videos_count_response.get('url', 'No URL')}")
        st.sidebar.write("📊 Estructura de respuesta:")
        st.sidebar.json(videos_count_response)
    else:
        st.sidebar.write("❌ Sin respuesta del conteo de videos")

# Funciones para obtener datos de YouTube
@st.cache_data(ttl=1800)
def get_youtube_views(_client, from_date, to_date):
    """Obtiene las vistas de YouTube"""
    try:
        from datetime import datetime
        if isinstance(from_date, date):
            from_date_dt = datetime.combine(from_date, datetime.min.time())
        else:
            from_date_dt = from_date
            
        if isinstance(to_date, date):
            to_date_dt = datetime.combine(to_date, datetime.max.time())
        else:
            to_date_dt = to_date
        
        response = _client.get_youtube_timeline(
            from_date=from_date_dt,
            to_date=to_date_dt,
            metric='views'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo vistas de YouTube: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_youtube_likes(_client, from_date, to_date):
    """Obtiene los likes de YouTube"""
    try:
        from datetime import datetime
        if isinstance(from_date, date):
            from_date_dt = datetime.combine(from_date, datetime.min.time())
        else:
            from_date_dt = from_date
            
        if isinstance(to_date, date):
            to_date_dt = datetime.combine(to_date, datetime.max.time())
        else:
            to_date_dt = to_date
        
        response = _client.get_youtube_timeline(
            from_date=from_date_dt,
            to_date=to_date_dt,
            metric='likes'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo likes de YouTube: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_youtube_dislikes(_client, from_date, to_date):
    """Obtiene los dislikes de YouTube"""
    try:
        from datetime import datetime
        if isinstance(from_date, date):
            from_date_dt = datetime.combine(from_date, datetime.min.time())
        else:
            from_date_dt = from_date
            
        if isinstance(to_date, date):
            to_date_dt = datetime.combine(to_date, datetime.max.time())
        else:
            to_date_dt = to_date
        
        response = _client.get_youtube_timeline(
            from_date=from_date_dt,
            to_date=to_date_dt,
            metric='dislikes'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo dislikes de YouTube: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_youtube_comments(_client, from_date, to_date):
    """Obtiene los comentarios de YouTube"""
    try:
        from datetime import datetime
        if isinstance(from_date, date):
            from_date_dt = datetime.combine(from_date, datetime.min.time())
        else:
            from_date_dt = from_date
            
        if isinstance(to_date, date):
            to_date_dt = datetime.combine(to_date, datetime.max.time())
        else:
            to_date_dt = to_date
        
        response = _client.get_youtube_timeline(
            from_date=from_date_dt,
            to_date=to_date_dt,
            metric='comments'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo comentarios de YouTube: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_youtube_shares(_client, from_date, to_date):
    """Obtiene las compartidas de YouTube"""
    try:
        from datetime import datetime
        if isinstance(from_date, date):
            from_date_dt = datetime.combine(from_date, datetime.min.time())
        else:
            from_date_dt = from_date
            
        if isinstance(to_date, date):
            to_date_dt = datetime.combine(to_date, datetime.max.time())
        else:
            to_date_dt = to_date
        
        response = _client.get_youtube_timeline(
            from_date=from_date_dt,
            to_date=to_date_dt,
            metric='shares'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo compartidas de YouTube: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_youtube_videos_count(_client, from_date, to_date):
    """Obtiene el conteo de videos de YouTube"""
    try:
        response = _client.get_youtube_videos_count(
            from_date=from_date,
            to_date=to_date
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo conteo de videos de YouTube: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_youtube_videos(_client, from_date, to_date):
    """Obtiene los videos de YouTube"""
    try:
        from datetime import datetime
        if isinstance(from_date, date):
            from_date_dt = datetime.combine(from_date, datetime.min.time())
        else:
            from_date_dt = from_date
            
        if isinstance(to_date, date):
            to_date_dt = datetime.combine(to_date, datetime.max.time())
        else:
            to_date_dt = to_date
        
        response = _client.get_youtube_posts(
            from_date=from_date_dt,
            to_date=to_date_dt
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo videos de YouTube: {str(e)}")
        return None

# Función para generar reporte completo
@st.cache_data(ttl=1800)
def generate_youtube_report(_client, from_date, to_date, dislikes_from_date, dislikes_to_date):
    """Genera reporte completo de YouTube con fechas específicas por métrica"""
    report = {}
    
    # Métricas con fechas principales (Jul 2025)
    report['views'] = get_youtube_views(_client, from_date, to_date)
    report['likes'] = get_youtube_likes(_client, from_date, to_date)
    report['comments'] = get_youtube_comments(_client, from_date, to_date)
    report['shares'] = get_youtube_shares(_client, from_date, to_date)
    report['videos'] = get_youtube_videos(_client, from_date, to_date)
    
    # Dislikes con fechas específicas (May-Jun 2025)
    report['dislikes'] = get_youtube_dislikes(_client, dislikes_from_date, dislikes_to_date)
    
    # Nota: El conteo de videos se calcula directamente desde report['videos']
    
    return report

# Funciones para crear gráficos
def create_youtube_timeline_chart(data, title, metric_name, color="#F8E964"):
    """Crea gráfico de línea temporal para YouTube"""
    if not data or not isinstance(data, dict) or data.get('status') != 200:
        return go.Figure().add_annotation(text="No hay datos disponibles", showarrow=False)
    
    try:
        api_data = data.get('data', {})
        if isinstance(api_data, dict):
            timeline_data = api_data.get('data', [])
        else:
            timeline_data = api_data if isinstance(api_data, list) else []
        
        if not timeline_data or len(timeline_data) == 0:
            return go.Figure().add_annotation(text="No hay datos disponibles", showarrow=False)
        
        values_data = timeline_data[0].get('values', [])
        
        dates = []
        values = []
        
        for item in values_data:
            if isinstance(item, dict):
                date_str = item.get('dateTime', '')
                value = item.get('value', 0)
                
                if date_str:
                    try:
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        dates.append(date_obj)
                        values.append(value)
                    except:
                        continue
        
        if not dates:
            return go.Figure().add_annotation(text="No hay fechas válidas", showarrow=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=metric_name,
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color),
            hovertemplate=f'<b>{metric_name}</b><br>' +
                         'Fecha: %{x|%d/%m/%Y}<br>' +
                         f'Valor: %{{y:,}}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"📺 {title}",
            xaxis_title="Fecha",
            yaxis_title=metric_name,
            template="plotly_white",
            hovermode='x unified',
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)

def extract_total_value(data):
    """Extrae la suma total de valores de una métrica de timeline"""
    if not data or not isinstance(data, dict) or data.get('status') != 200:
        return 0
    
    try:
        api_data = data.get('data', {})
        if isinstance(api_data, dict):
            timeline_data = api_data.get('data', [])
        else:
            timeline_data = api_data if isinstance(api_data, list) else []
        
        if timeline_data and len(timeline_data) > 0:
            values_data = timeline_data[0].get('values', [])
            total = sum(item.get('value', 0) for item in values_data if isinstance(item, dict))
            return total
        
        return 0
    except:
        return 0

def calculate_percentage_change(current_value, previous_value):
    """Calcula el cambio porcentual"""
    if previous_value == 0:
        return 0 if current_value == 0 else 100
    
    change = ((current_value - previous_value) / previous_value) * 100
    return change

def generate_youtube_analysis(youtube_data):
    """Genera análisis específico para YouTube con formato detallado"""
    try:
        # Extraer métricas del mes actual
        total_views = extract_total_value(youtube_data.get('views', {}))
        total_likes = extract_total_value(youtube_data.get('likes', {}))
        total_dislikes = extract_total_value(youtube_data.get('dislikes', {}))
        total_comments = extract_total_value(youtube_data.get('comments', {}))
        total_shares = extract_total_value(youtube_data.get('shares', {}))
        total_videos = extract_total_value(youtube_data.get('videos_count', {}))
        
        # Extraer métricas del mes anterior
        total_views_prev = extract_total_value(youtube_data.get('views_previous', {}))
        total_likes_prev = extract_total_value(youtube_data.get('likes_previous', {}))
        total_dislikes_prev = extract_total_value(youtube_data.get('dislikes_previous', {}))
        total_comments_prev = extract_total_value(youtube_data.get('comments_previous', {}))
        total_shares_prev = extract_total_value(youtube_data.get('shares_previous', {}))
        total_videos_prev = extract_total_value(youtube_data.get('videos_count_previous', {}))
        
        # Calcular cambios porcentuales
        views_change = calculate_percentage_change(total_views, total_views_prev)
        likes_change = calculate_percentage_change(total_likes, total_likes_prev)
        dislikes_change = calculate_percentage_change(total_dislikes, total_dislikes_prev)
        comments_change = calculate_percentage_change(total_comments, total_comments_prev)
        shares_change = calculate_percentage_change(total_shares, total_shares_prev)
        videos_change = calculate_percentage_change(total_videos, total_videos_prev)
        
        # Calcular engagement rate
        engagement_rate = 0
        if total_views > 0:
            engagement_rate = ((total_likes + total_comments + total_shares) / total_views) * 100
        
        # Crear análisis con formato específico
        analysis = f"""**Crecimiento y Alcance:**
Tuvimos un total de {total_views:,} visualizaciones, esto representa un {'aumento' if views_change >= 0 else 'disminución'} en comparación con el mes anterior en un ({views_change:+.1f}%).
También tuvimos un {'aumento' if likes_change >= 0 else 'disminución'} del ({likes_change:+.1f}%) en los me gusta, con un total de {total_likes:,} likes.

**Interacciones:**
Las interacciones con videos han {'aumentado' if likes_change >= 0 else 'disminuido'} en un {likes_change:+.1f}% en comparación con el mes anterior. Esto indica que el contenido {'está resonando' if likes_change >= 0 else 'no está resonando'} con la audiencia actual.
El engagement rate promedio es del {engagement_rate:.1f}%, con {total_comments:,} comentarios y {total_shares:,} compartidos.

**Contenido:**
Se publicaron {total_videos:,} videos con un {'aumento' if videos_change >= 0 else 'disminución'} del ({videos_change:+.1f}%) respecto al mes anterior.
La consistencia en la publicación de videos es {'buena' if videos_change >= 0 else 'necesita mejora'} para mantener el engagement.

**Rendimiento:**
Los videos generaron {total_views:,} visualizaciones con un {'aumento' if views_change >= 0 else 'disminución'} del ({views_change:+.1f}%) respecto al mes anterior.
El ratio de likes/dislikes es de {total_likes/total_dislikes if total_dislikes > 0 else 'N/A'}, lo que indica una {'buena' if total_likes > total_dislikes else 'necesita mejora'} recepción del contenido."""
        
        return analysis
        
    except Exception as e:
        return f"Error generando análisis de YouTube: {str(e)}"

def extract_videos_count_from_posts(videos_data):
    """Extrae el conteo real de videos desde el endpoint de posts/videos"""
    if not videos_data:
        return 0
    
    # Manejar la estructura de respuesta de Metricool API
    if isinstance(videos_data, dict):
        if videos_data.get('status') != 200:
            return 0
        
        api_data = videos_data.get('data', {})
        if isinstance(api_data, dict):
            data = api_data.get('data', [])
        else:
            data = api_data if isinstance(api_data, list) else []
    elif isinstance(videos_data, list):
        data = videos_data
    else:
        return 0
    
    # El conteo real es simplemente la cantidad de videos en la lista
    video_count = len(data) if data else 0
    st.sidebar.write(f"🔍 Debug videos_count - Conteo real de videos: {video_count}")
    return video_count

def create_youtube_videos_table(videos_data):
    """Crea tabla de videos de YouTube similar a Instagram posts"""
    if not videos_data:
        st.info("No hay datos de videos disponibles para el período seleccionado.")
        return
    
    # Manejar la estructura de respuesta de Metricool API
    if isinstance(videos_data, dict):
        if videos_data.get('status') != 200:
            st.error(f"Error en la API: Status {videos_data.get('status', 'desconocido')}")
            if videos_data.get('error'):
                st.error(f"Mensaje de error: {videos_data['error']}")
            return
        
        api_data = videos_data.get('data', {})
        if isinstance(api_data, dict):
            data = api_data.get('data', [])
        else:
            data = api_data if isinstance(api_data, list) else []
    elif isinstance(videos_data, list):
        data = videos_data
    else:
        st.error(f"Formato de datos inesperado: {type(videos_data)}")
        return
    
    if not data:
        st.info("No se encontraron videos en el período seleccionado.")
        return
    
    st.subheader("📺 Videos de YouTube")
    
    # Estadísticas generales
    total_videos = len(data)
    total_views = sum(video.get('views', 0) for video in data if isinstance(video, dict))
    total_likes = sum(video.get('likes', 0) for video in data if isinstance(video, dict))
    total_comments = sum(video.get('comments', 0) for video in data if isinstance(video, dict))
    total_shares = sum(video.get('shares', 0) for video in data if isinstance(video, dict))
    
    # Mostrar estadísticas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📺 Total Videos", total_videos)
    
    with col2:
        if total_views > 0:
            st.metric("👁️ Total Vistas", f"{total_views:,}")
    
    with col3:
        if total_likes > 0:
            st.metric("👍 Total Likes", f"{total_likes:,}")
    
    with col4:
        if total_comments > 0:
            st.metric("💬 Total Comentarios", f"{total_comments:,}")
    
    with col5:
        if total_shares > 0:
            st.metric("🔄 Total Compartidas", f"{total_shares:,}")
    
    # Paginación
    videos_per_page = 5
    total_pages = (len(data) - 1) // videos_per_page + 1
    
    if 'youtube_current_page' not in st.session_state:
        st.session_state.youtube_current_page = 1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Anterior", key="youtube_prev_page") and st.session_state.youtube_current_page > 1:
            st.session_state.youtube_current_page -= 1
    
    with col2:
        st.write(f"Página {st.session_state.youtube_current_page} de {total_pages}")
    
    with col3:
        if st.button("Siguiente ➡️", key="youtube_next_page") and st.session_state.youtube_current_page < total_pages:
            st.session_state.youtube_current_page += 1
    
    # Mostrar videos de la página actual
    start_idx = (st.session_state.youtube_current_page - 1) * videos_per_page
    end_idx = start_idx + videos_per_page
    current_videos = data[start_idx:end_idx]
    
    for i, video in enumerate(current_videos):
        if not isinstance(video, dict):
            continue
        
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin: 20px 0;'>
            <h4 style='color: #F8E964; margin-bottom: 15px;'>📺 Video {start_idx + i + 1}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Thumbnail del video con manejo de errores
            if video.get('imageUrl'):
                try:
                    image_url = video['imageUrl']
                    image_url_str = str(image_url) if image_url is not None else ""
                    if (image_url and 
                        image_url_str.strip() and 
                        image_url_str != '0' and 
                        image_url != 0 and
                        'http' in image_url_str.lower()):
                        st.image(image_url, width=150, caption="📺")
                    else:
                        st.markdown("""
                        <div style='width: 150px; height: 150px; background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); 
                                    border-radius: 8px; display: flex; align-items: center; justify-content: center;
                                    border: 2px dashed #f39c12;'>
                            <div style='text-align: center; color: #d68910;'>
                                <div style='font-size: 24px; margin-bottom: 5px;'>⚠️</div>
                                <div style='font-size: 11px; font-weight: bold;'>URL inválida</div>
                                <div style='font-size: 9px; margin-top: 2px;'>{} ({})</div>
                            </div>
                        </div>
                        """.format(
                            str(image_url)[:15] + "..." if len(str(image_url)) > 15 else str(image_url),
                            type(image_url).__name__
                        ), unsafe_allow_html=True)
                except Exception as e:
                    st.markdown("""
                    <div style='width: 150px; height: 150px; background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); 
                                border-radius: 8px; display: flex; align-items: center; justify-content: center;
                                border: 2px dashed #000000;'>
                        <div style='text-align: center; color: #721c24;'>
                            <div style='font-size: 24px; margin-bottom: 5px;'>❌</div>
                            <div style='font-size: 11px; font-weight: bold;'>Error de carga</div>
                            <div style='font-size: 9px; margin-top: 2px;'>Imagen rota</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='width: 150px; height: 150px; background: linear-gradient(135deg, #F8E964 0%, #CC0000 100%); 
                            border-radius: 8px; display: flex; align-items: center; justify-content: center;
                            border: 2px dashed #990000;'>
                    <div style='text-align: center; color: white;'>
                        <div style='font-size: 24px; margin-bottom: 5px;'>📺</div>
                        <div style='font-size: 11px; font-weight: bold;'>YouTube</div>
                        <div style='font-size: 9px; margin-top: 2px;'>Sin thumbnail</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Información del video
            video_date = video.get('publishedAt', {}).get('dateTime', 'Sin fecha')
            if video_date != 'Sin fecha':
                try:
                    date_obj = datetime.fromisoformat(video_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    formatted_date = video_date[:10]
            else:
                formatted_date = video_date
            
            st.markdown(f"**📅 Fecha:** {formatted_date}")
            
            # Título del video
            title = video.get('title', video.get('content', 'Sin título'))
            if title:
                title_preview = title[:100] + '...' if len(title) > 100 else title
                st.markdown(f"**🎬 Título:** {title_preview}")
            
            # Descripción
            description = video.get('description', video.get('content', ''))
            if description:
                desc_preview = description[:150] + '...' if len(description) > 150 else description
                st.markdown(f"**📝 Descripción:** {desc_preview}")
            
            # Enlace al video
            if video.get('url'):
                st.markdown(f"[🔗 Ver en YouTube]({video['url']})")
        
        with col3:
            # Métricas del video
            views = video.get('views', 0)
            likes = video.get('likes', 0)
            comments = video.get('comments', 0)
            shares = video.get('shares', 0)
            dislikes = video.get('dislikes', 0)
            
            if views > 0:
                st.metric("👁️ Vistas", f"{views:,}")
            if likes > 0:
                st.metric("👍 Likes", f"{likes:,}")
            if comments > 0:
                st.metric("💬 Comentarios", f"{comments:,}")
            if shares > 0:
                st.metric("🔄 Compartidas", f"{shares:,}")
            if dislikes > 0:
                st.metric("👎 Dislikes", f"{dislikes:,}")

# Ejecutar reporte
with st.spinner("🔄 Generando reporte de YouTube..."):
    # Debug: mostrar fechas seleccionadas
    st.sidebar.write(f"🔍 Debug - Fecha inicio: {from_date}")
    st.sidebar.write(f"🔍 Debug - Fecha fin: {to_date}")
    
    report = generate_youtube_report(client, from_date, to_date, dislikes_from_date, dislikes_to_date)
    
    # Debug: mostrar estructura del reporte
    st.sidebar.write("🔍 Debug - Claves del reporte:")
    for key, value in report.items():
        if isinstance(value, dict):
            status = value.get('status', 'Sin status')
            st.sidebar.write(f"  {key}: status {status}")
            if key == 'videos' and status == 200:
                video_count = extract_videos_count_from_posts(value)
                st.sidebar.write(f"    -> Videos encontrados: {video_count}")
        else:
            st.sidebar.write(f"  {key}: {type(value)}")
    
    # Guardar datos de YouTube en session state
    st.session_state['youtube_report'] = report

# Header del reporte
st.header("📊 Reporte Completo de YouTube")

# Métricas principales en cards
st.subheader("📈 Métricas Principales")

col1, col2, col3 = st.columns(3)

with col1:
    total_views = extract_total_value(report['views'])
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>👁️ Vistas</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_views:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_likes = extract_total_value(report['likes'])
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>👍 Likes</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_likes:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_dislikes = extract_total_value(report['dislikes'])
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>👎 Dislikes</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_dislikes:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>May-Jun 2025</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    total_comments = extract_total_value(report['comments'])
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>💬 Comentarios</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_comments:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_shares = extract_total_value(report['shares'])
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>🔄 Compartidas</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_shares:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_videos = extract_videos_count_from_posts(report['videos'])
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>📺 Videos</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_videos:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
    </div>
    """, unsafe_allow_html=True)

# Separador
st.markdown("---")

# Gráficos de timeline
st.subheader("📈 Evolución Temporal")

# Vistas
st.markdown("**👁️ Evolución de Vistas**")
views_chart = create_youtube_timeline_chart(
    report['views'], 
    "Vistas de YouTube", 
    "Vistas",
    "#F8E964"
)
st.plotly_chart(views_chart, use_container_width=True, key="youtube_views_chart")

# Likes
st.markdown("**👍 Evolución de Likes**")
likes_chart = create_youtube_timeline_chart(
    report['likes'], 
    "Likes de YouTube", 
    "Likes",
    "#00FF00"
)
st.plotly_chart(likes_chart, use_container_width=True, key="youtube_likes_chart")

# Dislikes
st.markdown("**👎 Evolución de Dislikes**")
dislikes_chart = create_youtube_timeline_chart(
    report['dislikes'], 
    "Dislikes de YouTube", 
    "Dislikes",
    "#FF6B6B"
)
st.plotly_chart(dislikes_chart, use_container_width=True, key="youtube_dislikes_chart")

# Comentarios
st.markdown("**💬 Evolución de Comentarios**")
comments_chart = create_youtube_timeline_chart(
    report['comments'], 
    "Comentarios de YouTube", 
    "Comentarios",
    "#4ECDC4"
)
st.plotly_chart(comments_chart, use_container_width=True, key="youtube_comments_chart")

# Compartidas
st.markdown("**🔄 Evolución de Compartidas**")
shares_chart = create_youtube_timeline_chart(
    report['shares'], 
    "Compartidas de YouTube", 
    "Compartidas",
    "#A8E6CF"
)
st.plotly_chart(shares_chart, use_container_width=True, key="youtube_shares_chart")

# Separador
st.markdown("---")

# Videos de YouTube
create_youtube_videos_table(report['videos'])

# Separador
st.markdown("---")

# Análisis AI para YouTube
@st.cache_data(ttl=3600)  # Cache por 1 hora
def generate_youtube_ai_analysis(_youtube_data, _instagram_data=None, _linkedin_data=None):
    """Genera análisis estratégico usando OpenAI GPT para YouTube"""
    try:
        # Función auxiliar para extraer métricas clave de YouTube
        def extract_youtube_metrics(data):
            if not data:
                return {}
            
            summary = {}
            
            # Vistas
            views_data = data.get('views', {})
            if isinstance(views_data, dict) and 'data' in views_data:
                summary['total_views'] = extract_total_value(views_data)
            
            # Likes
            likes_data = data.get('likes', {})
            if isinstance(likes_data, dict) and 'data' in likes_data:
                summary['total_likes'] = extract_total_value(likes_data)
            
            # Dislikes
            dislikes_data = data.get('dislikes', {})
            if isinstance(dislikes_data, dict) and 'data' in dislikes_data:
                summary['total_dislikes'] = extract_total_value(dislikes_data)
            
            # Comentarios
            comments_data = data.get('comments', {})
            if isinstance(comments_data, dict) and 'data' in comments_data:
                summary['total_comments'] = extract_total_value(comments_data)
            
            # Compartidas
            shares_data = data.get('shares', {})
            if isinstance(shares_data, dict) and 'data' in shares_data:
                summary['total_shares'] = extract_total_value(shares_data)
            
            # Videos (contar desde los datos de videos)
            videos_data = data.get('videos', {})
            if videos_data:
                summary['total_videos'] = extract_videos_count_from_posts(videos_data)
            
            # Videos destacados (similar a Instagram)
            videos_data = data.get('videos', {})
            if isinstance(videos_data, dict) and 'data' in videos_data:
                api_data = videos_data['data']
                if isinstance(api_data, dict):
                    videos_list = api_data.get('data', [])
                else:
                    videos_list = api_data if isinstance(api_data, list) else []
                
                if videos_list:
                    valid_videos = [video for video in videos_list if isinstance(video, dict)]
                    
                    if valid_videos:
                        # Top video por vistas
                        top_views_video = max(valid_videos, key=lambda x: x.get('views', 0))
                        if top_views_video.get('views', 0) > 0:
                            title_preview = top_views_video.get('title', top_views_video.get('content', ''))[:100] + '...' if len(top_views_video.get('title', top_views_video.get('content', ''))) > 100 else top_views_video.get('title', top_views_video.get('content', 'Sin título'))
                            summary['top_views_video'] = {
                                'views': top_views_video.get('views', 0),
                                'likes': top_views_video.get('likes', 0),
                                'comments': top_views_video.get('comments', 0),
                                'shares': top_views_video.get('shares', 0),
                                'title_preview': title_preview
                            }
            
            return summary
        
        # Extraer métricas de YouTube
        youtube_summary = extract_youtube_metrics(_youtube_data)
        
        # Crear análisis de videos destacados
        videos_analysis = ""
        if youtube_summary.get('top_views_video'):
            top_views = youtube_summary['top_views_video']
            videos_analysis += f"\n\nVIDEOS DESTACADOS YOUTUBE:\n"
            videos_analysis += f"🏆 Video con más vistas ({top_views['views']:,} vistas):\n"
            videos_analysis += f"   Likes: {top_views['likes']} | Comentarios: {top_views['comments']} | Compartidas: {top_views['shares']}\n"
            videos_analysis += f"   Título: \"{top_views['title_preview']}\"\n"
        
        # Crear prompt optimizado para YouTube
        prompt = f"""Analiza estas métricas de YouTube y proporciona un reporte estratégico enfocado en contenido audiovisual:

YOUTUBE:
- Vistas totales: {youtube_summary.get('total_views', 'N/A')}
- Likes totales: {youtube_summary.get('total_likes', 'N/A')}
- Dislikes totales: {youtube_summary.get('total_dislikes', 'N/A')}
- Comentarios totales: {youtube_summary.get('total_comments', 'N/A')}
- Compartidas totales: {youtube_summary.get('total_shares', 'N/A')}
- Videos publicados: {youtube_summary.get('total_videos', 'N/A')}{videos_analysis}

Proporciona análisis específico para YouTube:
1. RENDIMIENTO DE CONTENIDO: Análisis de vistas, engagement y retención
2. INTERACCIÓN DE AUDIENCIA: Efectividad de likes, comentarios y compartidas
3. CONTENIDO EXITOSO: Qué tipos de videos generan más engagement
4. ESTRATEGIA DE VIDEO: Recomendaciones para optimizar contenido audiovisual
5. CRECIMIENTO DE CANAL: Tácticas para aumentar suscriptores y vistas
6. PRÓXIMOS PASOS: Acciones específicas para YouTube

Enfócate en estrategias de contenido audiovisual y optimización SEO para YouTube (máximo 600 palabras)."""
        
        # Llamar a OpenAI
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un especialista en marketing de YouTube y contenido audiovisual. Proporciona análisis accionables para canales de YouTube."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generando análisis: {str(e)}"

# Sección de Análisis AI
st.header("🤖 Análisis Estratégico con IA")
st.markdown("**Análisis profesional automatizado de tus métricas de YouTube**")

# Botón para generar análisis
if st.button("🚀 Generar Análisis Estratégico", type="primary", use_container_width=True):
    with st.spinner("🤖 Analizando datos con IA... Esto puede tomar unos momentos"):
        try:
            # Obtener datos de otras plataformas si están disponibles
            instagram_data = st.session_state.get('instagram_report', None)
            linkedin_data = st.session_state.get('linkedin_report', None)
            
            # Generar análisis
            analysis = generate_youtube_ai_analysis(report, instagram_data, linkedin_data)
            
            # Mostrar el análisis
            st.markdown("### 📊 Reporte Estratégico YouTube")
            
            # Crear un contenedor con estilo para el análisis
            st.markdown("""
            <div style='background: #F8E964; color: black; 
                        padding: 30px; border-radius: 15px; border-left: 5px solid #F8E964; margin: 20px 0;'>
            """, unsafe_allow_html=True)
            
            # Mostrar el análisis con formato markdown
            st.markdown(analysis)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Opción para descargar el análisis
            st.download_button(
                label="📥 Descargar Análisis YouTube (TXT)",
                data=analysis,
                file_name=f"analisis_youtube_{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ Error generando análisis: {str(e)}")
            st.info("💡 Asegúrate de que la API key de OpenAI esté configurada correctamente")

# Información sobre el análisis AI
with st.expander("ℹ️ Sobre el Análisis Estratégico con IA"):
    st.markdown("""
    ### 🤖 ¿Qué incluye el análisis de YouTube?
    
    **📊 Análisis de Métricas de YouTube:**
    - Evaluación de vistas y engagement de videos
    - Análisis de likes, dislikes y comentarios
    - Rendimiento de contenido audiovisual
    
    **✅ Puntos Positivos:**
    - Estrategias de YouTube que generan vistas
    - Fortalezas en engagement y retención
    - Contenido que resuena con la audiencia
    
    **⚠️ Áreas de Mejora:**
    - Optimización de títulos y thumbnails
    - Mejora en engagement y comentarios
    - Estrategias de crecimiento de canal
    
    **🎯 Análisis de Contenido:**
    - Videos con mejor rendimiento
    - Tipos de contenido más efectivos
    - Oportunidades de mejora en SEO
    
    **🚀 Recomendaciones Específicas:**
    - Estrategias de contenido audiovisual
    - Optimización para algoritmo de YouTube
    - Tácticas de crecimiento de suscriptores
    - Mejoras en retención de audiencia
    
    ---
    *Análisis generado por GPT-3.5 especializado en marketing de YouTube*
    """)

# Expanders para datos raw
with st.expander("🔍 Ver datos raw - Vistas"):
    st.json(report['views'])

with st.expander("🔍 Ver datos raw - Likes"):
    st.json(report['likes'])

with st.expander("🔍 Ver datos raw - Dislikes"):
    st.json(report['dislikes'])

with st.expander("🔍 Ver datos raw - Comentarios"):
    st.json(report['comments'])

with st.expander("🔍 Ver datos raw - Compartidas"):
    st.json(report['shares'])

with st.expander("🔍 Ver datos raw - Videos"):
    st.json(report['videos'])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666; font-size: 0.9rem;'>
    📺 Datos en tiempo real de YouTube Analytics • Período: {from_date} - {to_date}<br>
    Desarrollado por Jungle Creative Agency para Widu Legal
</div>
""".format(from_date=from_date.strftime('%d/%m/%Y'), to_date=to_date.strftime('%d/%m/%Y')), unsafe_allow_html=True)
