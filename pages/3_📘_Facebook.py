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
    page_title="Facebook Analytics - Widu Legal",
    page_icon="📘",
    layout="wide"
)

# Configurar OpenAI
OPENAI_API_KEY = "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"
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Selector de proyectos
project_info, profile_data, available_networks = create_project_selector()

# Verificar si Facebook está disponible para el proyecto actual
if not is_network_available('facebook'):
    show_network_not_available('Facebook', '📘')
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

# CSS personalizado para Facebook
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
    .facebook-header {
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
    <div class='facebook-header'>
        <h1>📘 Facebook Analytics</h1>
        <p>Dashboard completo de métricas de Facebook</p>
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
        value=date(2025, 5, 31),  # Para impresiones, visitas y posts
        key="facebook_from_date"
    )

with col2:
    to_date = st.date_input(
        "📅 Fecha fin", 
        value=date(2025, 6, 30),  # Para impresiones, visitas y posts
        key="facebook_to_date"
    )

# Información sobre períodos de datos disponibles
st.sidebar.info("""
📅 **Períodos de datos disponibles:**
- Seguidores/Likes: Abr-May 2025
- Impresiones/Visitas/Posts: May-Jun 2025
- Demografía: May-Jun 2025
""")

# Fechas alternativas para seguidores y likes
followers_from_date = date(2025, 4, 30)
followers_to_date = date(2025, 5, 30)

# Botón de test (después de definir el cliente)
if st.sidebar.button("🧪 Test API Facebook"):
    st.sidebar.write("🔍 Probando API...")
    test_response = client.get_facebook_timeline(
        from_date=datetime.combine(followers_from_date, datetime.min.time()),
        to_date=datetime.combine(followers_to_date, datetime.max.time()),
        metric='pageFollows'
    )
    
    if test_response:
        st.sidebar.write(f"✅ Status: {test_response.get('status')}")
        st.sidebar.write(f"🔗 URL: {test_response.get('url', 'No URL')}")
        if test_response.get('data'):
            st.sidebar.write("📊 Datos recibidos correctamente")
        else:
            st.sidebar.write("❌ Sin datos en respuesta")
    else:
        st.sidebar.write("❌ Sin respuesta de la API")

# Funciones para obtener datos de Facebook
@st.cache_data(ttl=1800)
def get_facebook_page_follows(_client, from_date, to_date):
    """Obtiene los seguidores de página de Facebook"""
    try:
        # Debug: convertir fechas a datetime
        from datetime import datetime
        if isinstance(from_date, date):
            from_date_dt = datetime.combine(from_date, datetime.min.time())
        else:
            from_date_dt = from_date
            
        if isinstance(to_date, date):
            to_date_dt = datetime.combine(to_date, datetime.max.time())
        else:
            to_date_dt = to_date
        
        st.sidebar.write(f"🔍 Debug pageFollows - from_date: {from_date_dt}")
        st.sidebar.write(f"🔍 Debug pageFollows - to_date: {to_date_dt}")
        
        response = _client.get_facebook_timeline(
            from_date=from_date_dt,
            to_date=to_date_dt,
            metric='pageFollows'
        )
        
        # Debug: mostrar respuesta
        if response:
            st.sidebar.write(f"🔍 Debug pageFollows - URL: {response.get('url', 'No URL')}")
            st.sidebar.write(f"🔍 Debug pageFollows - Status: {response.get('status', 'No status')}")
        
        return response
    except Exception as e:
        st.error(f"Error obteniendo seguidores de Facebook: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_facebook_likes(_client, from_date, to_date):
    """Obtiene los likes de página de Facebook"""
    try:
        response = _client.get_facebook_timeline(
            from_date=from_date,
            to_date=to_date,
            metric='likes'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo likes de Facebook: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_facebook_impressions(_client, from_date, to_date):
    """Obtiene las impresiones de página de Facebook"""
    try:
        response = _client.get_facebook_timeline(
            from_date=from_date,
            to_date=to_date,
            metric='pageImpressions'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo impresiones de Facebook: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_facebook_page_views(_client, from_date, to_date):
    """Obtiene las visitas a la página de Facebook"""
    try:
        response = _client.get_facebook_timeline(
            from_date=from_date,
            to_date=to_date,
            metric='pageViews'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo visitas de página de Facebook: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_facebook_posts_count(_client, from_date, to_date):
    """Obtiene el conteo de posts de Facebook"""
    try:
        response = _client.get_facebook_timeline(
            from_date=from_date,
            to_date=to_date,
            metric='postsCount'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo conteo de posts de Facebook: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_facebook_posts(_client, from_date, to_date):
    """Obtiene los posts de Facebook"""
    try:
        response = _client.get_facebook_posts(
            from_date=from_date,
            to_date=to_date
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo posts de Facebook: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_facebook_followers_by_country(_client, from_date, to_date):
    """Obtiene seguidores por país de Facebook"""
    try:
        response = _client.get_facebook_distribution(
            from_date=from_date,
            to_date=to_date,
            metric='followersByCountry'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo seguidores por país de Facebook: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_facebook_followers_by_city(_client, from_date, to_date):
    """Obtiene seguidores por ciudad de Facebook"""
    try:
        response = _client.get_facebook_distribution(
            from_date=from_date,
            to_date=to_date,
            metric='followersByCity'
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo seguidores por ciudad de Facebook: {str(e)}")
        return None

# Función para generar reporte completo
@st.cache_data(ttl=1800)
def generate_facebook_report(_client, from_date, to_date, followers_from_date, followers_to_date):
    """Genera reporte completo de Facebook con fechas específicas por métrica"""
    from datetime import timedelta
    
    # Calcular fechas del mes anterior
    days_diff = (to_date - from_date).days + 1
    prev_to_date = from_date - timedelta(days=1)
    prev_from_date = prev_to_date - timedelta(days=days_diff-1)
    
    # Calcular fechas del mes anterior para seguidores/likes
    followers_days_diff = (followers_to_date - followers_from_date).days + 1
    prev_followers_to_date = followers_from_date - timedelta(days=1)
    prev_followers_from_date = prev_followers_to_date - timedelta(days=followers_days_diff-1)
    
    report = {}
    
    # Métricas con fechas específicas para seguidores/likes (Abr-May 2025)
    report['page_follows'] = get_facebook_page_follows(_client, followers_from_date, followers_to_date)
    report['likes'] = get_facebook_likes(_client, followers_from_date, followers_to_date)
    
    # Métricas con fechas principales (May-Jun 2025)
    report['impressions'] = get_facebook_impressions(_client, from_date, to_date)
    report['page_views'] = get_facebook_page_views(_client, from_date, to_date)
    report['posts_count'] = get_facebook_posts_count(_client, from_date, to_date)
    report['posts'] = get_facebook_posts(_client, from_date, to_date)
    report['followers_by_country'] = get_facebook_followers_by_country(_client, from_date, to_date)
    report['followers_by_city'] = get_facebook_followers_by_city(_client, from_date, to_date)
    
    # Datos del mes anterior para comparación
    report['page_follows_previous'] = get_facebook_page_follows(_client, prev_followers_from_date, prev_followers_to_date)
    report['likes_previous'] = get_facebook_likes(_client, prev_followers_from_date, prev_followers_to_date)
    report['impressions_previous'] = get_facebook_impressions(_client, prev_from_date, prev_to_date)
    report['page_views_previous'] = get_facebook_page_views(_client, prev_from_date, prev_to_date)
    report['posts_count_previous'] = get_facebook_posts_count(_client, prev_from_date, prev_to_date)
    
    return report

def generate_facebook_analysis(facebook_data):
    """Genera análisis profundo de Facebook con insights valiosos"""
    try:
        # Extraer métricas del mes actual
        page_follows = extract_final_value(facebook_data.get('page_follows', {}))
        likes = extract_final_value(facebook_data.get('likes', {}))
        total_impressions = extract_total_value(facebook_data.get('impressions', {}))
        total_page_views = extract_total_value(facebook_data.get('page_views', {}))
        total_posts = extract_total_value(facebook_data.get('posts_count', {}))
        
        # Extraer métricas del mes anterior
        page_follows_prev = extract_final_value(facebook_data.get('page_follows_previous', {}))
        likes_prev = extract_final_value(facebook_data.get('likes_previous', {}))
        total_impressions_prev = extract_total_value(facebook_data.get('impressions_previous', {}))
        total_page_views_prev = extract_total_value(facebook_data.get('page_views_previous', {}))
        total_posts_prev = extract_total_value(facebook_data.get('posts_count_previous', {}))
        
        # Calcular cambios porcentuales
        followers_change = calculate_percentage_change(page_follows, page_follows_prev)
        likes_change = calculate_percentage_change(likes, likes_prev)
        impressions_change = calculate_percentage_change(total_impressions, total_impressions_prev)
        page_views_change = calculate_percentage_change(total_page_views, total_page_views_prev)
        posts_change = calculate_percentage_change(total_posts, total_posts_prev)
        
        # Análisis de posts
        posts_data = facebook_data.get('posts', [])
        total_posts_real = len(posts_data) if isinstance(posts_data, list) else 0
        
        # Calcular métricas avanzadas de posts
        total_post_likes = sum(post.get('likes', 0) for post in posts_data if isinstance(post, dict))
        total_post_comments = sum(post.get('comments', 0) for post in posts_data if isinstance(post, dict))
        total_post_shares = sum(post.get('shares', 0) for post in posts_data if isinstance(post, dict))
        total_post_reach = sum(post.get('reach', 0) for post in posts_data if isinstance(post, dict))
        
        # Calcular engagement rate de la página
        page_engagement_rate = 0
        if page_follows > 0 and total_posts_real > 0:
            total_engagement = total_post_likes + total_post_comments + total_post_shares
            page_engagement_rate = (total_engagement / (page_follows * total_posts_real)) * 100
        
        # Análisis de rendimiento por tipo de post
        post_types = {}
        if isinstance(posts_data, list):
            for post in posts_data:
                if isinstance(post, dict):
                    post_type = post.get('type', 'unknown')
                    if post_type not in post_types:
                        post_types[post_type] = {
                            'count': 0, 'total_likes': 0, 'total_comments': 0, 
                            'total_shares': 0, 'total_reach': 0
                        }
                    post_types[post_type]['count'] += 1
                    post_types[post_type]['total_likes'] += post.get('likes', 0)
                    post_types[post_type]['total_comments'] += post.get('comments', 0)
                    post_types[post_type]['total_shares'] += post.get('shares', 0)
                    post_types[post_type]['total_reach'] += post.get('reach', 0)
        
        # Encontrar el mejor tipo de post
        best_post_type = "foto"
        best_engagement = 0
        for post_type, metrics in post_types.items():
            if metrics['count'] > 0:
                avg_engagement = (metrics['total_likes'] + metrics['total_comments'] + metrics['total_shares']) / metrics['count']
                if avg_engagement > best_engagement:
                    best_engagement = avg_engagement
                    best_post_type = post_type
        
        # Análisis demográfico avanzado
        country_data = facebook_data.get('followers_by_country', {})
        city_data = facebook_data.get('followers_by_city', {})
        
        # Distribución geográfica
        country_distribution = {}
        if isinstance(country_data, dict) and 'data' in country_data:
            country_dist = country_data['data'].get('data', [])
            for country in country_dist:
                country_distribution[country.get('key', '')] = country.get('value', 0)
        
        city_distribution = {}
        if isinstance(city_data, dict) and 'data' in city_data:
            city_dist = city_data['data'].get('data', [])
            for city in city_dist:
                city_distribution[city.get('key', '')] = city.get('value', 0)
        
        # Calcular métricas de alcance
        avg_impressions_per_post = total_impressions / total_posts_real if total_posts_real > 0 else 0
        avg_reach_per_post = total_post_reach / total_posts_real if total_posts_real > 0 else 0
        ctr = (total_page_views / total_impressions * 100) if total_impressions > 0 else 0
        
        # Análisis de crecimiento
        growth_velocity = (page_follows - page_follows_prev) / 30 if page_follows_prev > 0 else 0
        engagement_velocity = (page_engagement_rate - (total_post_likes + total_post_comments + total_post_shares) / (page_follows_prev * total_posts_real * 100)) if page_follows_prev > 0 and total_posts_real > 0 else 0
        
        # Insights de rendimiento
        performance_level = "Excelente" if page_engagement_rate > 5 else "Bueno" if page_engagement_rate > 2 else "Necesita mejora"
        reach_efficiency = "Alto" if avg_reach_per_post > 1000 else "Moderado" if avg_reach_per_post > 500 else "Bajo"
        
        # Crear análisis profundo
        analysis = f"""## 📘 Análisis Profundo de Facebook - {page_follows:,} Seguidores

### 🚀 Crecimiento y Alcance
**Crecimiento de Seguidores:** {page_follows:,} ({followers_change:+.1f}% vs mes anterior)
- **Velocidad de crecimiento:** {growth_velocity:+.1f} seguidores/día
- **Total de impresiones:** {total_impressions:,} ({impressions_change:+.1f}% vs mes anterior)
- **Total de visitas a la página:** {total_page_views:,} ({page_views_change:+.1f}% vs mes anterior)
- **CTR (Click Through Rate):** {ctr:.2f}%

### 📊 Rendimiento de Contenido
**Métricas de Posts del Mes:**
- **Posts publicados:** {total_posts_real}
- **Total de likes en posts:** {total_post_likes:,}
- **Total de comentarios:** {total_post_comments:,}
- **Total de compartidos:** {total_post_shares:,}
- **Total de alcance de posts:** {total_post_reach:,}

**Engagement Rate de la Página:** {page_engagement_rate:.2f}% ({performance_level})
**Mejor tipo de post:** {best_post_type} (Engagement promedio: {best_engagement:.0f})
**Alcance promedio por post:** {avg_reach_per_post:.0f} personas ({reach_efficiency})

### 🎯 Análisis Demográfico Avanzado
**Distribución por País:**
{chr(10).join([f"- {country}: {followers:,} seguidores" for country, followers in sorted(country_distribution.items(), key=lambda x: x[1], reverse=True)[:3]])}

**Distribución por Ciudad:**
{chr(10).join([f"- {city}: {followers:,} seguidores" for city, followers in sorted(city_distribution.items(), key=lambda x: x[1], reverse=True)[:3]])}

### 💡 Insights Estratégicos
**Fortalezas Identificadas:**
- {'Crecimiento sostenido de seguidores' if followers_change > 0 else 'Base de seguidores estable'}
- {'Alto engagement en posts' if page_engagement_rate > 3 else 'Engagement moderado' if page_engagement_rate > 1 else 'Oportunidad de mejora en engagement'}
- {'Alcance eficiente' if reach_efficiency == 'Alto' else 'Alcance moderado' if reach_efficiency == 'Moderado' else 'Necesita optimización de alcance'}

**Oportunidades de Mejora:**
- {'Aumentar frecuencia de publicación' if total_posts_real < 10 else 'Mantener frecuencia actual'}
- {'Optimizar horarios de publicación' if page_engagement_rate < 2 else 'Explorar nuevos formatos de contenido'}
- {'Mejorar CTR' if ctr < 2 else 'Mantener estrategia de alcance actual'}

**Análisis de Contenido:**
- **Tipo más efectivo:** {best_post_type} con {best_engagement:.0f} interacciones promedio
- **Frecuencia óptima:** {'Aumentar a 2-3 posts/día' if total_posts_real < 20 else 'Mantener frecuencia actual'}
- **Horarios recomendados:** {'Mañanas (8-10 AM) y tardes (6-8 PM)' if page_engagement_rate > 2 else 'Experimentar con diferentes horarios'}

### 📈 Proyección del Próximo Mes
Basado en la tendencia actual:
- **Crecimiento esperado:** {int(growth_velocity * 30):+} seguidores
- **Impresiones estimadas:** {int(total_impressions * 1.1):,}
- **Engagement esperado:** {page_engagement_rate * 1.05:.2f}%
- **Alcance estimado por post:** {int(avg_reach_per_post * 1.1):,} personas

### 🎯 Recomendaciones Específicas
1. **Contenido:** Enfocar en {best_post_type} que genera {best_engagement:.0f} interacciones promedio
2. **Frecuencia:** {'Aumentar a 2-3 posts diarios' if total_posts_real < 20 else 'Mantener ritmo actual'}
3. **Alcance:** {'Optimizar targeting' if reach_efficiency == 'Bajo' else 'Mantener estrategia actual'}
4. **Engagement:** {'Mejorar calidad visual' if page_engagement_rate < 2 else 'Experimentar con nuevos formatos'}"""
        
        return analysis
        
    except Exception as e:
        return f"Error generando análisis de Facebook: {str(e)}"

# Función para calcular cambio porcentual
def calculate_percentage_change(current_value, previous_value):
    """Calcula el cambio porcentual"""
    if previous_value == 0:
        return 100 if current_value > 0 else 0
    return ((current_value - previous_value) / previous_value) * 100

# Funciones para crear gráficos
def create_facebook_timeline_chart(data, title, metric_name, color="#F8E964"):
    """Crea gráfico de línea temporal para Facebook"""
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
            title=f"📘 {title}",
            xaxis_title="Fecha",
            yaxis_title=metric_name,
            template="plotly_white",
            hovermode='x unified',
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)

def extract_final_value(data):
    """Extrae el último valor de una métrica de timeline"""
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
            if values_data:
                return values_data[0].get('value', 0)
        
        return 0
    except:
        return 0

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

def create_facebook_horizontal_bar_chart(data, title, emoji="📊", top_n=10):
    """Crea gráfico de barras horizontales para distribución de Facebook"""
    if not data or not isinstance(data, dict) or data.get('status') != 200:
        return go.Figure().add_annotation(text="No hay datos disponibles", showarrow=False), pd.DataFrame()
    
    try:
        api_data = data.get('data', {})
        if isinstance(api_data, dict):
            distribution_data = api_data.get('data', [])
        else:
            distribution_data = api_data if isinstance(api_data, list) else []
        
        if not distribution_data:
            return go.Figure().add_annotation(text="No hay datos disponibles", showarrow=False), pd.DataFrame()
        
        # Crear DataFrame
        df_data = []
        for item in distribution_data:
            if isinstance(item, dict):
                key = item.get('key', 'Sin datos')
                value = item.get('value', 0)
                df_data.append({'Categoría': key, 'Valor': value})
        
        if not df_data:
            return go.Figure().add_annotation(text="No hay datos válidos", showarrow=False), pd.DataFrame()
        
        df = pd.DataFrame(df_data)
        df = df.sort_values('Valor', ascending=False).head(top_n)
        
        # Crear gráfico
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['Valor'],
            y=df['Categoría'],
            orientation='h',
            marker=dict(color='#F8E964'),
            hovertemplate='<b>%{y}</b><br>Valor: %{x:,}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"{emoji} {title}",
            xaxis_title="Cantidad",
            yaxis_title="",
            template="plotly_white",
            height=400,
            yaxis=dict(autorange="reversed")
        )
        
        return fig, df
        
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False), pd.DataFrame()

# Función para agregar banderas de países
def get_country_flag(country_code):
    """Obtiene emoji de bandera para código de país"""
    flags = {
        'VE': '🇻🇪', 'CO': '🇨🇴', 'US': '🇺🇸', 'ES': '🇪🇸', 'MX': '🇲🇽',
        'AR': '🇦🇷', 'PE': '🇵🇪', 'CL': '🇨🇱', 'EC': '🇪🇨', 'PA': '🇵🇦',
        'CR': '🇨🇷', 'GT': '🇬🇹', 'HN': '🇭🇳', 'SV': '🇸🇻', 'NI': '🇳🇮',
        'DO': '🇩🇴', 'PR': '🇵🇷', 'CU': '🇨🇺', 'BO': '🇧🇴', 'UY': '🇺🇾',
        'PY': '🇵🇾', 'BR': '🇧🇷', 'FR': '🇫🇷', 'DE': '🇩🇪', 'IT': '🇮🇹',
        'GB': '🇬🇧', 'CA': '🇨🇦', 'AU': '🇦🇺', 'JP': '🇯🇵', 'CN': '🇨🇳',
        'IN': '🇮🇳', 'RU': '🇷🇺', 'KR': '🇰🇷', 'TH': '🇹🇭', 'SG': '🇸🇬'
    }
    return flags.get(country_code.upper(), '🏳️')

def create_facebook_posts_table(posts_data):
    """Crea tabla de posts de Facebook similar a Instagram"""
    if not posts_data:
        st.info("No hay datos de posts disponibles para el período seleccionado.")
        return
    
    # Manejar la estructura de respuesta de Metricool API
    if isinstance(posts_data, dict):
        if posts_data.get('status') != 200:
            st.error(f"Error en la API: Status {posts_data.get('status', 'desconocido')}")
            if posts_data.get('error'):
                st.error(f"Mensaje de error: {posts_data['error']}")
            return
        
        api_data = posts_data.get('data', {})
        if isinstance(api_data, dict):
            data = api_data.get('data', [])
        else:
            data = api_data if isinstance(api_data, list) else []
    elif isinstance(posts_data, list):
        data = posts_data
    else:
        st.error(f"Formato de datos inesperado: {type(posts_data)}")
        return
    
    if not data:
        st.info("No se encontraron posts en el período seleccionado.")
        return
    
    st.subheader("📱 Posts de Facebook")
    
    # Estadísticas generales
    total_posts = len(data)
    total_likes = sum(post.get('likes', 0) for post in data if isinstance(post, dict))
    total_comments = sum(post.get('comments', 0) for post in data if isinstance(post, dict))
    total_shares = sum(post.get('shares', 0) for post in data if isinstance(post, dict))
    total_reach = sum(post.get('reach', 0) for post in data if isinstance(post, dict))
    
    # Mostrar estadísticas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📱 Total Posts", total_posts)
    
    with col2:
        if total_likes > 0:
            st.metric("👍 Total Likes", f"{total_likes:,}")
    
    with col3:
        if total_comments > 0:
            st.metric("💬 Total Comentarios", f"{total_comments:,}")
    
    with col4:
        if total_shares > 0:
            st.metric("🔄 Total Compartidas", f"{total_shares:,}")
    
    with col5:
        if total_reach > 0:
            st.metric("👁️ Total Alcance", f"{total_reach:,}")
    
    # Paginación
    posts_per_page = 5
    total_pages = (len(data) - 1) // posts_per_page + 1
    
    if 'facebook_current_page' not in st.session_state:
        st.session_state.facebook_current_page = 1
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Anterior", key="facebook_prev_page") and st.session_state.facebook_current_page > 1:
            st.session_state.facebook_current_page -= 1
    
    with col2:
        st.write(f"Página {st.session_state.facebook_current_page} de {total_pages}")
    
    with col3:
        if st.button("Siguiente ➡️", key="facebook_next_page") and st.session_state.facebook_current_page < total_pages:
            st.session_state.facebook_current_page += 1
    
    # Mostrar posts de la página actual
    start_idx = (st.session_state.facebook_current_page - 1) * posts_per_page
    end_idx = start_idx + posts_per_page
    current_posts = data[start_idx:end_idx]
    
    for i, post in enumerate(current_posts):
        if not isinstance(post, dict):
            continue
        
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin: 20px 0;'>
            <h4 style='color: #F8E964; margin-bottom: 15px;'>📱 Post {start_idx + i + 1}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Imagen en miniatura con manejo de errores
            if post.get('imageUrl'):
                try:
                    image_url = post['imageUrl']
                    # Verificar si la URL es válida
                    image_url_str = str(image_url) if image_url is not None else ""
                    if (image_url and 
                        image_url_str.strip() and 
                        image_url_str != '0' and 
                        image_url != 0 and
                        'http' in image_url_str.lower()):
                        st.image(image_url, width=150, caption="📘")
                    else:
                        # Placeholder para URL inválida
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
                    # Placeholder para error de carga
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
                # Placeholder cuando no hay imagen
                st.markdown("""
                <div style='width: 150px; height: 150px; background: linear-gradient(135deg, #e2e3e5 0%, #d1ecf1 100%); 
                            border-radius: 8px; display: flex; align-items: center; justify-content: center;
                            border: 2px dashed #6c757d;'>
                    <div style='text-align: center; color: #495057;'>
                        <div style='font-size: 24px; margin-bottom: 5px;'>📝</div>
                        <div style='font-size: 11px; font-weight: bold;'>Sin imagen</div>
                        <div style='font-size: 9px; margin-top: 2px;'>Post de texto</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Información del post
            post_date = post.get('publishedAt', {}).get('dateTime', 'Sin fecha')
            if post_date != 'Sin fecha':
                try:
                    date_obj = datetime.fromisoformat(post_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    formatted_date = post_date[:10]
            else:
                formatted_date = post_date
            
            st.markdown(f"**📅 Fecha:** {formatted_date}")
            st.markdown(f"**📝 Tipo:** {post.get('type', 'Desconocido')}")
            
            # Contenido
            content = post.get('content', '')
            if content:
                content_preview = content[:200] + '...' if len(content) > 200 else content
                st.markdown(f"**💬 Contenido:** {content_preview}")
            
            # Enlace
            if post.get('url'):
                st.markdown(f"[🔗 Ver en Facebook]({post['url']})")
        
        with col3:
            # Métricas
            likes = post.get('likes', 0)
            comments = post.get('comments', 0)
            shares = post.get('shares', 0)
            reach = post.get('reach', 0)
            
            if likes > 0:
                st.metric("👍 Likes", f"{likes:,}")
            if comments > 0:
                st.metric("💬 Comentarios", f"{comments:,}")
            if shares > 0:
                st.metric("🔄 Compartidas", f"{shares:,}")
            if reach > 0:
                st.metric("👁️ Alcance", f"{reach:,}")

# Ejecutar reporte
with st.spinner("🔄 Generando reporte de Facebook..."):
    # Debug: mostrar fechas seleccionadas
    st.sidebar.write(f"🔍 Debug - Fecha inicio: {from_date}")
    st.sidebar.write(f"🔍 Debug - Fecha fin: {to_date}")
    
    report = generate_facebook_report(client, from_date, to_date, followers_from_date, followers_to_date)
    
    # Debug: mostrar estructura del reporte
    st.sidebar.write("🔍 Debug - Claves del reporte:")
    for key, value in report.items():
        if isinstance(value, dict):
            status = value.get('status', 'Sin status')
            st.sidebar.write(f"  {key}: status {status}")
        else:
            st.sidebar.write(f"  {key}: {type(value)}")
    
    # Guardar datos de Facebook en session state
    st.session_state['facebook_report'] = report

# Header del reporte
st.header("📊 Reporte Completo de Facebook")

# Métricas principales en cards
st.subheader("📈 Métricas Principales")

# Calcular métricas actuales y del mes anterior
page_follows = extract_final_value(report['page_follows'])
likes = extract_final_value(report['likes'])
total_impressions = extract_total_value(report['impressions'])
total_page_views = extract_total_value(report['page_views'])
total_posts = extract_total_value(report['posts_count'])

page_follows_prev = extract_final_value(report['page_follows_previous'])
likes_prev = extract_final_value(report['likes_previous'])
total_impressions_prev = extract_total_value(report['impressions_previous'])
total_page_views_prev = extract_total_value(report['page_views_previous'])
total_posts_prev = extract_total_value(report['posts_count_previous'])

# Calcular cambios porcentuales
followers_change = calculate_percentage_change(page_follows, page_follows_prev)
likes_change = calculate_percentage_change(likes, likes_prev)
impressions_change = calculate_percentage_change(total_impressions, total_impressions_prev)
page_views_change = calculate_percentage_change(total_page_views, total_page_views_prev)
posts_change = calculate_percentage_change(total_posts, total_posts_prev)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    change_color = "#F8E964" if followers_change >= 0 else "#000000"
    change_symbol = "↗️" if followers_change >= 0 else "↘️"
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>👥 Seguidores</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{page_follows:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Último día</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem; color: {change_color};'>
            {change_symbol} {followers_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    change_color = "#F8E964" if likes_change >= 0 else "#000000"
    change_symbol = "↗️" if likes_change >= 0 else "↘️"
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>👍 Me Gusta</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{likes:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Último día</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem; color: {change_color};'>
            {change_symbol} {likes_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    change_color = "#F8E964" if impressions_change >= 0 else "#000000"
    change_symbol = "↗️" if impressions_change >= 0 else "↘️"
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>👁️ Impresiones</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_impressions:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem; color: {change_color};'>
            {change_symbol} {impressions_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    change_color = "#F8E964" if page_views_change >= 0 else "#000000"
    change_symbol = "↗️" if page_views_change >= 0 else "↘️"
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>📄 Visitas</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_page_views:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem; color: {change_color};'>
            {change_symbol} {page_views_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    change_color = "#F8E964" if posts_change >= 0 else "#000000"
    change_symbol = "↗️" if posts_change >= 0 else "↘️"
    st.markdown(f"""
    <div style='background: #F8E964; padding: 20px; border-radius: 10px; text-align: center; color: black; margin-bottom: 15px;'>
        <h3 style='margin: 0 0 10px 0;'>📱 Posts</h3>
        <h2 style='margin: 0; font-size: 2rem;'>{total_posts:,}</h2>
        <p style='margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;'>Total período</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem; color: {change_color};'>
            {change_symbol} {posts_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

# Separador
st.markdown("---")

# Gráficos de timeline
st.subheader("📈 Evolución Temporal")

# Seguidores
st.markdown("**👥 Evolución de Seguidores**")
page_follows_chart = create_facebook_timeline_chart(
    report['page_follows'], 
    "Seguidores de Facebook", 
    "Seguidores",
    "#F8E964"
)
st.plotly_chart(page_follows_chart, use_container_width=True, key="facebook_page_follows_chart")

# Likes
st.markdown("**👍 Evolución de Me Gusta**")
likes_chart = create_facebook_timeline_chart(
    report['likes'], 
    "Me Gusta de Facebook", 
    "Me Gusta",
    "#42B883"
)
st.plotly_chart(likes_chart, use_container_width=True, key="facebook_likes_chart")

# Impresiones
st.markdown("**👁️ Evolución de Impresiones**")
impressions_chart = create_facebook_timeline_chart(
    report['impressions'], 
    "Impresiones de Facebook", 
    "Impresiones",
    "#FF6B6B"
)
st.plotly_chart(impressions_chart, use_container_width=True, key="facebook_impressions_chart")

# Visitas a la página
st.markdown("**📄 Evolución de Visitas a la Página**")
page_views_chart = create_facebook_timeline_chart(
    report['page_views'], 
    "Visitas a la Página de Facebook", 
    "Visitas",
    "#4ECDC4"
)
st.plotly_chart(page_views_chart, use_container_width=True, key="facebook_page_views_chart")

# Posts
st.markdown("**📱 Evolución de Posts**")
posts_count_chart = create_facebook_timeline_chart(
    report['posts_count'], 
    "Cantidad de Posts de Facebook", 
    "Posts",
    "#A8E6CF"
)
st.plotly_chart(posts_count_chart, use_container_width=True, key="facebook_posts_count_chart")

# Separador
st.markdown("---")

# Posts de Facebook
create_facebook_posts_table(report['posts'])

# Separador
st.markdown("---")

# Análisis demográfico
st.header("🌍 Análisis Demográfico")
st.markdown("**Distribución de la audiencia por ubicación geográfica**")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌎 Seguidores por País")
    country_chart, country_df = create_facebook_horizontal_bar_chart(
        report['followers_by_country'], 
        "Seguidores por País", 
        "🌍"
    )
    st.plotly_chart(country_chart, use_container_width=True, key="facebook_country_chart")
    
    # Agregar banderas a la tabla
    if not country_df.empty:
        country_df['🏳️ País'] = country_df['Categoría'].apply(lambda x: f"{get_country_flag(x)} {x}")
        country_df_display = country_df[['🏳️ País', 'Valor']].copy()
        st.dataframe(country_df_display, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🏙️ Seguidores por Ciudad")
    city_chart, city_df = create_facebook_horizontal_bar_chart(
        report['followers_by_city'], 
        "Seguidores por Ciudad", 
        "🏙️"
    )
    st.plotly_chart(city_chart, use_container_width=True, key="facebook_city_chart")
    
    if not city_df.empty:
        st.dataframe(city_df, use_container_width=True, hide_index=True)

# Separador
st.markdown("---")

# Análisis AI para Facebook
@st.cache_data(ttl=3600)  # Cache por 1 hora
def generate_facebook_ai_analysis(_facebook_data, _instagram_data=None, _linkedin_data=None):
    """Genera análisis estratégico usando OpenAI GPT para Facebook"""
    try:
        # Función auxiliar para extraer métricas clave de Facebook
        def extract_facebook_metrics(data):
            if not data:
                return {}
            
            summary = {}
            
            # Seguidores
            page_follows_data = data.get('page_follows', {})
            if isinstance(page_follows_data, dict) and 'data' in page_follows_data:
                summary['page_follows'] = extract_final_value(page_follows_data)
            
            # Likes
            likes_data = data.get('likes', {})
            if isinstance(likes_data, dict) and 'data' in likes_data:
                summary['likes'] = extract_final_value(likes_data)
            
            # Impresiones
            impressions_data = data.get('impressions', {})
            if isinstance(impressions_data, dict) and 'data' in impressions_data:
                summary['total_impressions'] = extract_total_value(impressions_data)
            
            # Visitas
            page_views_data = data.get('page_views', {})
            if isinstance(page_views_data, dict) and 'data' in page_views_data:
                summary['total_page_views'] = extract_total_value(page_views_data)
            
            # Posts
            posts_count_data = data.get('posts_count', {})
            if isinstance(posts_count_data, dict) and 'data' in posts_count_data:
                summary['total_posts'] = extract_total_value(posts_count_data)
            
            # Posts destacados (similar a Instagram)
            posts_data = data.get('posts', {})
            if isinstance(posts_data, dict) and 'data' in posts_data:
                api_data = posts_data['data']
                if isinstance(api_data, dict):
                    posts_list = api_data.get('data', [])
                else:
                    posts_list = api_data if isinstance(api_data, list) else []
                
                if posts_list:
                    valid_posts = [post for post in posts_list if isinstance(post, dict)]
                    
                    if valid_posts:
                        # Top post por likes
                        top_likes_post = max(valid_posts, key=lambda x: x.get('likes', 0))
                        if top_likes_post.get('likes', 0) > 0:
                            content_preview = top_likes_post.get('content', '')[:100] + '...' if len(top_likes_post.get('content', '')) > 100 else top_likes_post.get('content', 'Sin contenido')
                            summary['top_likes_post'] = {
                                'likes': top_likes_post.get('likes', 0),
                                'comments': top_likes_post.get('comments', 0),
                                'shares': top_likes_post.get('shares', 0),
                                'reach': top_likes_post.get('reach', 0),
                                'content_preview': content_preview,
                                'type': top_likes_post.get('type', 'unknown')
                            }
            
            # Demografía
            country_data = data.get('followers_by_country', {})
            if isinstance(country_data, dict) and 'data' in country_data:
                api_data = country_data['data']
                if isinstance(api_data, dict):
                    countries = api_data.get('data', [])
                else:
                    countries = api_data if isinstance(api_data, list) else []
                
                if countries:
                    top_countries = sorted(countries, key=lambda x: x.get('value', 0), reverse=True)[:5]
                    summary['top_countries'] = [f"{item['key']}: {item['value']}" for item in top_countries]
            
            return summary
        
        # Extraer métricas de Facebook
        facebook_summary = extract_facebook_metrics(_facebook_data)
        
        # Crear análisis de posts destacados
        posts_analysis = ""
        if facebook_summary.get('top_likes_post'):
            top_likes = facebook_summary['top_likes_post']
            posts_analysis += f"\n\nPOSTS DESTACADOS FACEBOOK:\n"
            posts_analysis += f"🏆 Post con más likes ({top_likes['likes']} likes):\n"
            posts_analysis += f"   Tipo: {top_likes['type']} | Alcance: {top_likes['reach']} | Comentarios: {top_likes['comments']} | Compartidas: {top_likes['shares']}\n"
            posts_analysis += f"   Contenido: \"{top_likes['content_preview']}\"\n"
        
        # Crear prompt optimizado para Facebook
        prompt = f"""Analiza estas métricas de Facebook y proporciona un reporte estratégico enfocado en engagement y alcance:

FACEBOOK:
- Seguidores: {facebook_summary.get('page_follows', 'N/A')}
- Me Gusta de página: {facebook_summary.get('likes', 'N/A')}
- Impresiones totales: {facebook_summary.get('total_impressions', 'N/A')}
- Visitas a la página: {facebook_summary.get('total_page_views', 'N/A')}
- Posts publicados: {facebook_summary.get('total_posts', 'N/A')}
- Países principales: {', '.join(facebook_summary.get('top_countries', ['N/A']))}{posts_analysis}

Proporciona análisis específico para Facebook:
1. RENDIMIENTO DE PÁGINA: Análisis de seguidores, likes y engagement
2. ALCANCE E IMPRESIONES: Efectividad de contenido y visibilidad
3. CONTENIDO EXITOSO: Qué tipos de posts generan más interacción
4. AUDIENCIA GEOGRÁFICA: Análisis de distribución por países
5. ESTRATEGIA DE CONTENIDO: Recomendaciones para maximizar alcance orgánico
6. PRÓXIMOS PASOS: Acciones específicas para Facebook

Enfócate en estrategias orgánicas de Facebook y engagement comunitario (máximo 600 palabras)."""
        
        # Llamar a OpenAI
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un especialista en marketing de Facebook y engagement orgánico. Proporciona análisis accionables para páginas de Facebook."},
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
st.markdown("**Análisis profesional automatizado de tus métricas de Facebook**")

# Botón para generar análisis
if st.button("🚀 Generar Análisis Estratégico", type="primary", use_container_width=True):
    with st.spinner("🤖 Analizando datos con IA... Esto puede tomar unos momentos"):
        try:
            # Obtener datos de otras plataformas si están disponibles
            instagram_data = st.session_state.get('instagram_report', None)
            linkedin_data = st.session_state.get('linkedin_report', None)
            
            # Generar análisis
            analysis = generate_facebook_ai_analysis(report, instagram_data, linkedin_data)
            
            # Mostrar el análisis
            st.markdown("### 📊 Reporte Estratégico Facebook")
            
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
                label="📥 Descargar Análisis Facebook (TXT)",
                data=analysis,
                file_name=f"analisis_facebook_{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ Error generando análisis: {str(e)}")
            st.info("💡 Asegúrate de que la API key de OpenAI esté configurada correctamente")

# Información sobre el análisis AI
with st.expander("ℹ️ Sobre el Análisis Estratégico con IA"):
    st.markdown("""
    ### 🤖 ¿Qué incluye el análisis de Facebook?
    
    **📊 Análisis de Métricas de Facebook:**
    - Evaluación de seguidores y engagement de página
    - Análisis de impresiones y alcance orgánico
    - Rendimiento de contenido y posts destacados
    
    **✅ Puntos Positivos:**
    - Estrategias de Facebook que generan engagement
    - Fortalezas en alcance orgánico
    - Contenido que resuena con la audiencia
    
    **⚠️ Áreas de Mejora:**
    - Optimización de contenido para Facebook
    - Mejora en engagement comunitario
    - Estrategias de crecimiento orgánico
    
    **🎯 Análisis Demográfico:**
    - Distribución geográfica de seguidores
    - Oportunidades por países/ciudades
    - Insights de audiencia local
    
    **🚀 Recomendaciones Específicas:**
    - Estrategias de contenido para Facebook
    - Optimización de posts para alcance
    - Tácticas de engagement comunitario
    - Crecimiento orgánico de página
    
    ---
    *Análisis generado por GPT-3.5 especializado en marketing de Facebook*
    """)

# Expanders para datos raw
with st.expander("🔍 Ver datos raw - Seguidores"):
    st.json(report['page_follows'])

with st.expander("🔍 Ver datos raw - Me Gusta"):
    st.json(report['likes'])

with st.expander("🔍 Ver datos raw - Impresiones"):
    st.json(report['impressions'])

with st.expander("🔍 Ver datos raw - Visitas"):
    st.json(report['page_views'])

with st.expander("🔍 Ver datos raw - Posts"):
    st.json(report['posts'])

with st.expander("🔍 Ver datos raw - Países"):
    st.json(report['followers_by_country'])

with st.expander("🔍 Ver datos raw - Ciudades"):
    st.json(report['followers_by_city'])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666; font-size: 0.9rem;'>
    📘 Datos en tiempo real de Facebook Analytics • Período: {from_date} - {to_date}<br>
    Desarrollado por Jungle Creative Agency para Widu Legal
</div>
""".format(from_date=from_date.strftime('%d/%m/%Y'), to_date=to_date.strftime('%d/%m/%Y')), unsafe_allow_html=True)
