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
    page_title="LinkedIn Analytics - Widu Legal",
    page_icon="💼",
    layout="wide"
)

# Configurar OpenAI con valor por defecto
try:
    OPENAI_API_KEY = st.secrets["api_keys"]["openai_api_key"]
except KeyError:
    OPENAI_API_KEY = "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"

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# CSS personalizado para LinkedIn
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #000000;
        margin-bottom: 1rem;
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: bold;
        color: #000000;
        margin: 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Header de LinkedIn
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.image("https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png", width=120)
    st.markdown("<p style='text-align: center; font-size: 12px; color: #666; margin-top: -10px;'>Marketing Agency</p>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #000000; margin-bottom: 5px;'>💼 Reporte de LinkedIn</h1>
        <p style='color: #666; font-size: 16px; margin: 0;'>Analytics Dashboard Profesional</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("<p style='text-align: center; font-size: 12px; color: #666; margin-top: -10px;'>Cliente</p>", unsafe_allow_html=True)

# Línea separadora con estilo LinkedIn
st.markdown("""
<hr style='border: none; height: 3px; background: linear-gradient(90deg, #F8E964 0%, #000000 50%, #005885 100%); margin: 30px 0;'>
""", unsafe_allow_html=True)

# Logo en sidebar
st.sidebar.image("https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png", width=200)
st.sidebar.markdown("---")

# Configuración de fechas en el sidebar
st.sidebar.header("⚙️ Configuración LinkedIn")
from_date = st.sidebar.date_input(
    "Fecha de inicio:",
    value=date(2025, 6, 30),
    key="from_date_linkedin"
)

to_date = st.sidebar.date_input(
    "Fecha de fin:",
    value=date(2025, 8, 1),
    key="to_date_linkedin"
)

# Selector de proyectos
project_info, profile_data, available_networks = create_project_selector()

# Verificar si LinkedIn está disponible para el proyecto actual
if not is_network_available('linkedin'):
    show_network_not_available('LinkedIn', '💼')
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

# Funciones para obtener datos de LinkedIn
@st.cache_data(ttl=1800)
def get_linkedin_followers_timeline(_client, from_date, to_date, blog_id):
    try:
        response = _client.get_timeline_analytics(
            from_date=from_date,
            to_date=to_date,
            metric="Followers",
            network="linkedin",
            subject="account"
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo datos de seguidores LinkedIn: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_linkedin_delta_followers(_client, from_date, to_date, blog_id):
    try:
        response = _client.get_timeline_analytics(
            from_date=from_date,
            to_date=to_date,
            metric="DeltaFollowers",
            network="linkedin",
            subject="account"
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo datos de delta seguidores LinkedIn: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_linkedin_impressions_timeline(_client, from_date, to_date, blog_id):
    try:
        response = _client.get_timeline_analytics(
            from_date=from_date,
            to_date=to_date,
            metric="impressionCount",
            network="linkedin",
            subject="account"
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo datos de impresiones LinkedIn: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_linkedin_distribution_data(_client, from_date, to_date, metric, blog_id):
    try:
        response = _client.get_distribution_analytics(
            from_date=from_date,
            to_date=to_date,
            metric=metric,
            network="linkedin",
            subject="account"
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo datos de {metric} LinkedIn: {str(e)}")
        return None

# Funciones para extraer datos
def extract_timeline_data(api_response):
    """Extrae datos de timeline para gráficos de línea"""
    if not api_response or api_response.get('status') != 200:
        return [], []
    
    try:
        data = api_response.get('data', {})
        if isinstance(data, dict) and 'data' in data:
            metrics_data = data['data']
            if isinstance(metrics_data, list) and len(metrics_data) > 0:
                values_data = metrics_data[0].get('values', [])
                
                dates = []
                values = []
                
                for item in values_data:
                    if 'dateTime' in item and 'value' in item:
                        dates.append(item['dateTime'])
                        values.append(item['value'])
                
                # Ordenar por fecha
                sorted_data = sorted(zip(dates, values), key=lambda x: x[0])
                if sorted_data:
                    dates, values = zip(*sorted_data)
                    return list(dates), list(values)
    except Exception as e:
        st.error(f"Error procesando datos de timeline: {str(e)}")
    
    return [], []

def extract_final_value(api_response):
    """Extrae el valor final de una serie temporal"""
    dates, values = extract_timeline_data(api_response)
    if values:
        return values[-1]
    return 0

def extract_total_impressions(api_response):
    """Extrae el total de impresiones sumando todos los valores"""
    dates, values = extract_timeline_data(api_response)
    if values:
        return sum(values)
    return 0

def extract_gained_lost_from_delta(delta_response):
    """Calcula seguidores ganados y perdidos desde delta_followers"""
    dates, values = extract_timeline_data(delta_response)
    
    gained = sum(v for v in values if v > 0)
    lost = sum(abs(v) for v in values if v < 0)
    
    return gained, lost

def get_delta_timeline_data(delta_response):
    """Extrae datos diarios de ganados/perdidos para gráficos"""
    dates, values = extract_timeline_data(delta_response)
    
    gained_data = []
    lost_data = []
    
    for i, value in enumerate(values):
        if value > 0:
            gained_data.append(value)
            lost_data.append(0)
        else:
            gained_data.append(0)
            lost_data.append(abs(value))
    
    return dates, gained_data, lost_data

# Funciones para crear gráficos
def create_linkedin_followers_timeline_chart(followers_response):
    """Crea gráfico de línea para seguidores totales"""
    fig = go.Figure()
    
    dates, values = extract_timeline_data(followers_response)
    
    if dates and values:
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Seguidores Totales',
            line=dict(color='#000000', width=3),
            marker=dict(size=6, color='#000000')
        ))
        
        # Ajustar escala Y dinámicamente
        if len(values) > 1:
            min_val = min(values)
            max_val = max(values)
            range_val = max_val - min_val
            
            if range_val < 50:
                padding = 25
            else:
                padding = range_val * 0.1
            
            y_min = max(0, min_val - padding)
            y_max = max_val + padding
            
            fig.update_layout(yaxis=dict(range=[y_min, y_max]))
    
    fig.update_layout(
        title="📈 Evolución de Seguidores Totales - LinkedIn",
        xaxis_title="Fecha",
        yaxis_title="Número de Seguidores",
        template="plotly_white",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_linkedin_delta_followers_chart(delta_response):
    """Crea gráfico de línea para seguidores ganados/perdidos"""
    fig = go.Figure()
    
    dates, gained_data, lost_data = get_delta_timeline_data(delta_response)
    
    if dates:
        # Filtro de visualización
        filter_type = st.session_state.get('linkedin_chart_filter', 'both')
        
        if filter_type in ['both', 'gained']:
            fig.add_trace(go.Scatter(
                x=dates,
                y=gained_data,
                mode='lines+markers',
                name='Seguidores Ganados',
                line=dict(color='#F8E964', width=2),
                marker=dict(size=4, color='#F8E964')
            ))
        
        if filter_type in ['both', 'lost']:
            fig.add_trace(go.Scatter(
                x=dates,
                y=lost_data,
                mode='lines+markers',
                name='Seguidores Perdidos',
                line=dict(color='#000000', width=2),
                marker=dict(size=4, color='#000000')
            ))
    
    fig.update_layout(
        title="📊 Detalle de Cambios Diarios en Seguidores",
        xaxis_title="Fecha",
        yaxis_title="Número de Seguidores",
        template="plotly_white",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_linkedin_impressions_timeline_chart(impressions_response):
    """Crea gráfico de línea para impresiones"""
    fig = go.Figure()
    
    dates, values = extract_timeline_data(impressions_response)
    
    if dates and values:
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Impresiones Diarias',
            line=dict(color='#000000', width=3),
            marker=dict(size=6, color='#000000'),
            fill='tonexty'
        ))
    
    fig.update_layout(
        title="👁️ Evolución de Impresiones Diarias - LinkedIn",
        xaxis_title="Fecha",
        yaxis_title="Número de Impresiones",
        template="plotly_white",
        height=400,
        hovermode='x unified'
    )
    
    return fig

# Función para obtener emoji de país
def get_country_flag(country_code):
    """Obtiene el emoji de la bandera del país según su código"""
    flags = {
        'VE': '🇻🇪', 'CO': '🇨🇴', 'US': '🇺🇸', 'ES': '🇪🇸', 'MX': '🇲🇽', 'AR': '🇦🇷', 
        'PE': '🇵🇪', 'CL': '🇨🇱', 'EC': '🇪🇨', 'BR': '🇧🇷', 'PA': '🇵🇦', 'CR': '🇨🇷',
        'GT': '🇬🇹', 'HN': '🇭🇳', 'NI': '🇳🇮', 'SV': '🇸🇻', 'DO': '🇩🇴', 'CU': '🇨🇺',
        'PR': '🇵🇷', 'UY': '🇺🇾', 'PY': '🇵🇾', 'BO': '🇧🇴', 'FR': '🇫🇷', 'IT': '🇮🇹',
        'DE': '🇩🇪', 'GB': '🇬🇧', 'CA': '🇨🇦', 'AU': '🇦🇺', 'JP': '🇯🇵', 'CN': '🇨🇳',
        'IN': '🇮🇳', 'RU': '🇷🇺', 'ZA': '🇿🇦', 'EG': '🇪🇬', 'MA': '🇲🇦', 'NG': '🇳🇬',
        'KE': '🇰🇪', 'GH': '🇬🇭'
    }
    return flags.get(country_code.upper(), '🌍')

def create_linkedin_horizontal_histogram(distribution_data, title, emoji, top_n=None):
    """Crea histograma horizontal para datos de distribución"""
    fig = go.Figure()
    df_data = pd.DataFrame()
    
    if distribution_data and distribution_data.get('status') == 200:
        data = distribution_data.get('data', {})
        if isinstance(data, dict) and 'data' in data:
            try:
                metrics_data = data['data']
                if isinstance(metrics_data, list) and len(metrics_data) > 0:
                    labels = []
                    values = []
                    
                    for item in metrics_data:
                        if 'key' in item and 'value' in item:
                            key = item['key']
                            value = float(item['value'])
                            
                            # Agregar emoji de bandera si es país
                            if 'País' in title:
                                key = f"{get_country_flag(key)} {key}"
                            
                            labels.append(key)
                            values.append(value)
                    
                    if labels and values:
                        # Crear DataFrame
                        df_data = pd.DataFrame({
                            'Categoría': labels,
                            'Valor': values
                        }).sort_values('Valor', ascending=False)
                        
                        # Aplicar top_n si se especifica
                        if top_n:
                            df_data = df_data.head(top_n)
                        
                        # Ordenar para el gráfico (menor a mayor para que el mayor esté arriba)
                        df_chart = df_data.sort_values('Valor', ascending=True)
                        
                        fig.add_trace(go.Bar(
                            x=df_chart['Valor'],
                            y=df_chart['Categoría'],
                            orientation='h',
                            marker_color='#000000',
                            name=title,
                            text=[f'{v:.1f}' for v in df_chart['Valor']],
                            textposition='outside'
                        ))
            except Exception as e:
                st.error(f"Error procesando datos de {title}: {str(e)}")
    
    fig.update_layout(
        title=f"{emoji} {title}",
        xaxis_title="Cantidad de Seguidores" if "Seguidores" in title else "Valor",
        yaxis_title="Categoría",
        template="plotly_white",
        height=500 if not top_n or top_n > 10 else 400
    )
    
    return fig, df_data

# Generar reporte de LinkedIn
@st.cache_data(ttl=1800)
def generate_linkedin_report(_client, from_date, to_date, blog_id):
    """Genera el reporte completo de LinkedIn"""
    from datetime import timedelta
    
    # Calcular fechas del mes anterior
    days_diff = (to_date - from_date).days + 1
    prev_to_date = from_date - timedelta(days=1)
    prev_from_date = prev_to_date - timedelta(days=days_diff-1)
    
    report = {}
    
    # Obtener datos de timeline del período actual
    report['followers'] = get_linkedin_followers_timeline(_client, from_date, to_date, blog_id)
    report['delta_followers'] = get_linkedin_delta_followers(_client, from_date, to_date, blog_id)
    report['impressions'] = get_linkedin_impressions_timeline(_client, from_date, to_date, blog_id)
    
    # Obtener datos del mes anterior para comparación
    report['followers_previous'] = get_linkedin_followers_timeline(_client, prev_from_date, prev_to_date, blog_id)
    report['delta_followers_previous'] = get_linkedin_delta_followers(_client, prev_from_date, prev_to_date, blog_id)
    report['impressions_previous'] = get_linkedin_impressions_timeline(_client, prev_from_date, prev_to_date, blog_id)
    
    # Obtener datos de distribución
    report['geo_country'] = get_linkedin_distribution_data(_client, from_date, to_date, "followerCountsByGeoCountry", blog_id)
    report['geo_area'] = get_linkedin_distribution_data(_client, from_date, to_date, "followerCountsByGeo", blog_id)
    report['industry'] = get_linkedin_distribution_data(_client, from_date, to_date, "aggregatedFollowerCountsByIndustry", blog_id)
    report['job_function'] = get_linkedin_distribution_data(_client, from_date, to_date, "followerCountsByFunction", blog_id)
    
    return report

def generate_linkedin_analysis(linkedin_data):
    """Genera análisis específico para LinkedIn con formato detallado"""
    try:
        # Extraer métricas del mes actual
        total_followers = extract_final_value(linkedin_data.get('followers', {}))
        gained_followers, lost_followers = extract_gained_lost_from_delta(linkedin_data.get('delta_followers', {}))
        net_followers = gained_followers - lost_followers
        total_impressions = extract_total_impressions(linkedin_data.get('impressions', {}))
        
        # Extraer métricas del mes anterior
        total_followers_prev = extract_final_value(linkedin_data.get('followers_previous', {}))
        gained_followers_prev, lost_followers_prev = extract_gained_lost_from_delta(linkedin_data.get('delta_followers_previous', {}))
        net_followers_prev = gained_followers_prev - lost_followers_prev
        total_impressions_prev = extract_total_impressions(linkedin_data.get('impressions_previous', {}))
        
        # Calcular cambios porcentuales
        followers_change = calculate_percentage_change(total_followers, total_followers_prev)
        gained_change = calculate_percentage_change(gained_followers, gained_followers_prev)
        lost_change = calculate_percentage_change(lost_followers, lost_followers_prev)
        net_change = calculate_percentage_change(net_followers, net_followers_prev)
        impressions_change = calculate_percentage_change(total_impressions, total_impressions_prev)
        
        # Extraer datos demográficos
        country_data = linkedin_data.get('geo_country', {})
        industry_data = linkedin_data.get('industry', {})
        
        # Obtener ubicación principal
        main_country = "Venezuela"
        if isinstance(country_data, dict) and 'data' in country_data:
            country_dist = country_data['data'].get('data', [])
            if country_dist:
                top_country = max(country_dist, key=lambda x: x.get('value', 0))
                main_country = top_country.get('key', 'Venezuela')
        
        # Obtener industrias principales
        main_industries = ["Legal", "Servicios Profesionales"]
        if isinstance(industry_data, dict) and 'data' in industry_data:
            industry_dist = industry_data['data'].get('data', [])
            if industry_dist:
                top_industries = sorted(industry_dist, key=lambda x: x.get('value', 0), reverse=True)[:3]
                main_industries = [item.get('key', 'Legal') for item in top_industries]
        
        # Crear análisis con formato específico
        analysis = f"""**Crecimiento y Competencia:**
Este mes {'aumentamos' if net_followers >= 0 else 'perdimos'} {abs(net_followers)} seguidores. Además tenemos un porcentaje de interacción {'más alto' if impressions_change >= 0 else 'más bajo'} en comparación con nuestra competencia, específicamente de un ({impressions_change:+.1f}%).
Así mismo, la cantidad de publicaciones que realizamos en LinkedIn es {'mayor' if net_followers >= 0 else 'menor'} que el número de nuestra competencia en un ({net_change:+.1f}%).

**Demografía:**
La mayoría de la audiencia se encuentra dentro de {main_country}, específicamente en las ciudades principales.
Las industrias principales de nuestros seguidores son: {', '.join(main_industries[:3])}."""
        
        return analysis
        
    except Exception as e:
        return f"Error generando análisis de LinkedIn: {str(e)}"

# Función para calcular cambio porcentual
def calculate_percentage_change(current_value, previous_value):
    """Calcula el cambio porcentual"""
    if previous_value == 0:
        return 100 if current_value > 0 else 0
    return ((current_value - previous_value) / previous_value) * 100

# Ejecutar reporte
with st.spinner("🔄 Generando reporte de LinkedIn..."):
    report = generate_linkedin_report(client, from_date, to_date, current_blog_id)

# Header del reporte
col1, col2 = st.columns([3, 1])
with col1:
    st.header("💼 Reporte Completo de LinkedIn")
    st.markdown(f"**Período:** {from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}")

with col2:
    st.markdown("""
    <div style='text-align: right; padding: 10px; background: rgba(0, 119, 181, 0.1); border-radius: 8px; border-left: 4px solid #000000;'>
        <p style='font-size: 11px; color: #666; margin: 0;'>Elaborado por:</p>
        <p style='font-size: 12px; font-weight: bold; color: #000000; margin: 0;'>🌿 Jungle Creative</p>
    </div>
    """, unsafe_allow_html=True)

# Métricas principales
st.subheader("📊 Métricas Principales")

# Extraer valores principales
total_followers = extract_final_value(report['followers'])
gained_followers, lost_followers = extract_gained_lost_from_delta(report['delta_followers'])
net_followers = gained_followers - lost_followers
total_impressions = extract_total_impressions(report['impressions'])

# Extraer valores del mes anterior para comparación
total_followers_prev = extract_final_value(report['followers_previous'])
gained_followers_prev, lost_followers_prev = extract_gained_lost_from_delta(report['delta_followers_previous'])
net_followers_prev = gained_followers_prev - lost_followers_prev
total_impressions_prev = extract_total_impressions(report['impressions_previous'])

# Calcular cambios porcentuales
followers_change = calculate_percentage_change(total_followers, total_followers_prev)
gained_change = calculate_percentage_change(gained_followers, gained_followers_prev)
lost_change = calculate_percentage_change(lost_followers, lost_followers_prev)
net_change = calculate_percentage_change(net_followers, net_followers_prev)
impressions_change = calculate_percentage_change(total_impressions, total_impressions_prev)

# Cards de métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    change_color = "#F8E964" if followers_change >= 0 else "#000000"
    change_symbol = "↗️" if followers_change >= 0 else "↘️"
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-number">{total_followers:,}</p>
        <p class="metric-label">👥 Seguidores Totales</p>
        <p class="metric-change" style="color: {change_color}; font-size: 0.9rem; margin: 5px 0 0 0;">
            {change_symbol} {followers_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    change_color = "#F8E964" if gained_change >= 0 else "#000000"
    change_symbol = "↗️" if gained_change >= 0 else "↘️"
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-number" style="color: #F8E964;">{gained_followers:,}</p>
        <p class="metric-label">➕ Nuevos Seguidores</p>
        <p class="metric-change" style="color: {change_color}; font-size: 0.9rem; margin: 5px 0 0 0;">
            {change_symbol} {gained_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    change_color = "#F8E964" if lost_change <= 0 else "#000000"
    change_symbol = "↗️" if lost_change <= 0 else "↘️"
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-number" style="color: #000000;">{lost_followers:,}</p>
        <p class="metric-label">➖ Seguidores Perdidos</p>
        <p class="metric-change" style="color: {change_color}; font-size: 0.9rem; margin: 5px 0 0 0;">
            {change_symbol} {lost_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    change_color = "#F8E964" if net_change >= 0 else "#000000"
    change_symbol = "↗️" if net_change >= 0 else "↘️"
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-number" style="color: {'#F8E964' if net_followers >= 0 else '#000000'};">
            {net_followers:+,}
        </p>
        <p class="metric-label">📈 Crecimiento Neto</p>
        <p class="metric-change" style="color: {change_color}; font-size: 0.9rem; margin: 5px 0 0 0;">
            {change_symbol} {net_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

# Separador
st.markdown("---")

# Gráfico de seguidores totales
st.subheader("📈 Evolución de Seguidores")
followers_chart = create_linkedin_followers_timeline_chart(report['followers'])
st.plotly_chart(followers_chart, use_container_width=True)

# Separador
st.markdown("---")

# Gráfico de cambios diarios con filtros
st.subheader("📊 Análisis de Cambios Diarios")

# Botones de filtro
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👥 Mostrar Ambos", key="linkedin_both"):
        st.session_state['linkedin_chart_filter'] = 'both'

with col2:
    if st.button("➕ Solo Ganados", key="linkedin_gained"):
        st.session_state['linkedin_chart_filter'] = 'gained'

with col3:
    if st.button("➖ Solo Perdidos", key="linkedin_lost"):
        st.session_state['linkedin_chart_filter'] = 'lost'

delta_chart = create_linkedin_delta_followers_chart(report['delta_followers'])
st.plotly_chart(delta_chart, use_container_width=True)

# Separador
st.markdown("---")

# Gráfico de impresiones
st.subheader("👁️ Análisis de Impresiones")

col1, col2 = st.columns([2, 1])
with col1:
    impressions_chart = create_linkedin_impressions_timeline_chart(report['impressions'])
    st.plotly_chart(impressions_chart, use_container_width=True)

with col2:
    st.markdown(f"""
    <div style='padding: 20px; background: rgba(23, 162, 184, 0.1); border-radius: 10px; border-left: 4px solid #000000; margin-top: 50px;'>
        <h3 style='color: #000000; margin-bottom: 10px;'>📊 Total de Impresiones</h3>
        <h2 style='color: #000000; font-size: 2.5rem; margin: 0;'>{total_impressions:,}</h2>
        <p style='color: #666; font-size: 0.9rem; margin: 5px 0 0 0;'>En el período seleccionado</p>
    </div>
    """, unsafe_allow_html=True)

# Separador
st.markdown("---")

# Sección de demografía profesional
st.header("🌍 Análisis Demográfico Profesional")
st.markdown("**Distribución de la audiencia por ubicación, industria y función laboral**")

# Seguidores por país
st.subheader("🌎 Distribución Geográfica")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📍 Por País**")
    country_chart, country_df = create_linkedin_horizontal_histogram(
        report['geo_country'], 
        "Seguidores por País", 
        "🌍"
    )
    st.plotly_chart(country_chart, use_container_width=True)

with col2:
    st.markdown("**🗺️ Por Área Geográfica**")
    area_chart, area_df = create_linkedin_horizontal_histogram(
        report['geo_area'], 
        "Seguidores por Área", 
        "🗺️"
    )
    st.plotly_chart(area_chart, use_container_width=True)

# Separador
st.markdown("---")

# Análisis profesional
st.subheader("💼 Análisis Profesional")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🏭 Top 10 Industrias**")
    industry_chart, industry_df = create_linkedin_horizontal_histogram(
        report['industry'], 
        "Seguidores por Industria", 
        "🏭",
        top_n=10
    )
    st.plotly_chart(industry_chart, use_container_width=True)

with col2:
    st.markdown("**👔 Top 10 Funciones Laborales**")
    function_chart, function_df = create_linkedin_horizontal_histogram(
        report['job_function'], 
        "Seguidores por Función Laboral", 
        "👔",
        top_n=10
    )
    st.plotly_chart(function_chart, use_container_width=True)

# Tablas de datos
st.subheader("📋 Tablas de Datos Detalladas")

tab1, tab2, tab3, tab4 = st.tabs(["🌍 Países", "🗺️ Áreas", "🏭 Industrias", "👔 Funciones"])

with tab1:
    if not country_df.empty:
        st.dataframe(country_df, use_container_width=True)
    else:
        st.info("No hay datos de países disponibles.")

with tab2:
    if not area_df.empty:
        st.dataframe(area_df, use_container_width=True)
    else:
        st.info("No hay datos de áreas disponibles.")

with tab3:
    if not industry_df.empty:
        st.dataframe(industry_df, use_container_width=True)
    else:
        st.info("No hay datos de industrias disponibles.")

with tab4:
    if not function_df.empty:
        st.dataframe(function_df, use_container_width=True)
    else:
        st.info("No hay datos de funciones laborales disponibles.")

@st.cache_data(ttl=3600)  # Cache por 1 hora
def generate_linkedin_ai_analysis(_linkedin_data, _instagram_data=None):
    """Genera análisis estratégico usando OpenAI GPT para LinkedIn"""
    try:
        # Función auxiliar para extraer métricas clave
        def extract_key_metrics(data, data_type="linkedin"):
            if not data:
                return {}
            
            summary = {}
            
            if data_type == "linkedin":
                # Extraer métricas clave de LinkedIn
                followers_data = data.get('followers', {})
                if isinstance(followers_data, dict) and 'data' in followers_data:
                    followers_values = followers_data['data'].get('data', [])
                    if followers_values and len(followers_values) > 0:
                        latest_followers = followers_values[0].get('values', [])
                        if latest_followers:
                            summary['total_followers'] = latest_followers[0].get('value', 0)
                
                # Impresiones
                impressions_data = data.get('impressions', {})
                if isinstance(impressions_data, dict) and 'data' in impressions_data:
                    imp_values = impressions_data['data'].get('data', [])
                    if imp_values:
                        total_impressions = sum(v.get('value', 0) for v in imp_values[0].get('values', []))
                        summary['total_impressions'] = total_impressions
                
                # Delta followers
                delta_data = data.get('delta_followers', {})
                if isinstance(delta_data, dict) and 'data' in delta_data:
                    delta_values = delta_data['data'].get('data', [])
                    if delta_values:
                        gained = sum(v.get('value', 0) for v in delta_values[0].get('values', []) if v.get('value', 0) > 0)
                        lost = sum(abs(v.get('value', 0)) for v in delta_values[0].get('values', []) if v.get('value', 0) < 0)
                        summary['followers_gained'] = gained
                        summary['followers_lost'] = lost
                        summary['net_growth'] = gained - lost
                
                # Top industrias
                industry_data = data.get('industry', {})
                if isinstance(industry_data, dict) and 'data' in industry_data:
                    industries = industry_data['data'].get('data', [])
                    if industries:
                        top_industries = sorted(industries, key=lambda x: x.get('value', 0), reverse=True)[:5]
                        summary['top_industries'] = [f"{item['key']}: {item['value']}" for item in top_industries]
                
                # Top funciones
                function_data = data.get('job_function', {})
                if isinstance(function_data, dict) and 'data' in function_data:
                    functions = function_data['data'].get('data', [])
                    if functions:
                        top_functions = sorted(functions, key=lambda x: x.get('value', 0), reverse=True)[:3]
                        summary['top_functions'] = [f"{item['key']}: {item['value']}" for item in top_functions]
                
            elif data_type == "instagram":
                # Métricas básicas de Instagram para contexto
                followers_data = data.get('followers', {})
                if isinstance(followers_data, dict) and 'data' in followers_data:
                    followers_values = followers_data['data'].get('data', [])
                    if followers_values and len(followers_values) > 0:
                        latest_followers = followers_values[0].get('values', [])
                        if latest_followers:
                            summary['total_followers'] = latest_followers[0].get('value', 0)
                
                # Posts básicos
                posts_data = data.get('posts', {})
                if isinstance(posts_data, dict) and 'data' in posts_data:
                    posts_list = posts_data['data'].get('data', [])
                    if posts_list:
                        total_posts = len(posts_list)
                        total_engagement = sum(post.get('likes', 0) + post.get('comments', 0) for post in posts_list if isinstance(post, dict))
                        summary['total_posts'] = total_posts
                        summary['total_engagement'] = total_engagement
            
            return summary
        
        # Extraer métricas clave
        linkedin_summary = extract_key_metrics(_linkedin_data, "linkedin")
        instagram_summary = extract_key_metrics(_instagram_data, "instagram") if _instagram_data else {}
        
        # Crear prompt optimizado para LinkedIn B2B
        prompt = f"""Analiza estas métricas B2B de LinkedIn y proporciona un reporte estratégico enfocado en generación de leads:

LINKEDIN (Enfoque B2B):
- Seguidores: {linkedin_summary.get('total_followers', 'N/A')}
- Crecimiento neto: {linkedin_summary.get('net_growth', 'N/A')} (Ganados: {linkedin_summary.get('followers_gained', 'N/A')}, Perdidos: {linkedin_summary.get('followers_lost', 'N/A')})
- Impresiones totales: {linkedin_summary.get('total_impressions', 'N/A')}
- Industrias principales: {', '.join(linkedin_summary.get('top_industries', ['N/A']))}
- Funciones laborales top: {', '.join(linkedin_summary.get('top_functions', ['N/A']))}

INSTAGRAM (Contexto):
- Seguidores: {instagram_summary.get('total_followers', 'N/A')}
- Posts: {instagram_summary.get('total_posts', 'N/A')}
- Engagement total: {instagram_summary.get('total_engagement', 'N/A')}

Proporciona análisis B2B enfocado en:
1. RENDIMIENTO PROFESIONAL: Análisis de networking y autoridad
2. GENERACIÓN DE LEADS: Oportunidades de conversión B2B
3. AUDIENCIA CUALIFICADA: Calidad de seguidores por industria/función
4. ESTRATEGIA DE CONTENIDO: Recomendaciones para thought leadership
5. PRÓXIMOS PASOS: Acciones específicas para LinkedIn B2B

Mantén el enfoque en ROI B2B y generación de leads (máximo 500 palabras)."""
        
        # Llamar a OpenAI con modelo optimizado
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Usar GPT-3.5 para eficiencia
            messages=[
                {"role": "system", "content": "Eres un especialista en marketing B2B y generación de leads en LinkedIn. Proporciona análisis accionables para empresas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Tokens optimizados
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generando análisis: {str(e)}"

# Guardar datos de LinkedIn en session state para uso en Instagram
st.session_state['linkedin_report'] = report

# Separador
st.markdown("---")

# Sección de Análisis AI
st.header("🤖 Análisis Estratégico con IA")
st.markdown("**Análisis profesional automatizado de tus métricas de LinkedIn**")

# Botón para generar análisis
if st.button("🚀 Generar Análisis Estratégico", type="primary", use_container_width=True):
    with st.spinner("🤖 Analizando datos con IA... Esto puede tomar unos momentos"):
        try:
            # Obtener datos de Instagram si están disponibles
            instagram_data = None
            try:
                # Intentar obtener datos de Instagram desde la sesión
                if 'instagram_report' in st.session_state:
                    instagram_data = st.session_state.instagram_report
            except:
                instagram_data = None
            
            # Generar análisis
            analysis = generate_linkedin_ai_analysis(report, instagram_data)
            
            # Mostrar el análisis
            st.markdown("### 📊 Reporte Estratégico LinkedIn")
            
            # Crear un contenedor con estilo para el análisis
            st.markdown("""
            <div style='background: #F8E964; color: black; 
                        padding: 30px; border-radius: 15px; border-left: 5px solid #000000; margin: 20px 0;'>
            """, unsafe_allow_html=True)
            
            # Mostrar el análisis con formato markdown
            st.markdown(analysis)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Opción para descargar el análisis
            st.download_button(
                label="📥 Descargar Análisis LinkedIn (TXT)",
                data=analysis,
                file_name=f"analisis_linkedin_{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ Error generando análisis: {str(e)}")
            st.info("💡 Asegúrate de que la API key de OpenAI esté configurada correctamente")

# Información sobre el análisis AI
with st.expander("ℹ️ Sobre el Análisis Estratégico con IA"):
    st.markdown("""
    ### 🤖 ¿Qué incluye el análisis de LinkedIn?
    
    **📊 Análisis de Métricas B2B:**
    - Evaluación de impresiones y alcance profesional
    - Análisis de crecimiento de seguidores cualificados
    - Identificación de tendencias de networking
    
    **✅ Puntos Positivos:**
    - Estrategias de LinkedIn que generan leads
    - Fortalezas en networking profesional
    - Oportunidades de autoridad de marca
    
    **⚠️ Áreas de Mejora:**
    - Optimización de contenido B2B
    - Mejora en engagement profesional
    - Estrategias de generación de leads
    
    **🎯 Análisis Demográfico Profesional:**
    - Distribución por industrias clave
    - Funciones laborales de la audiencia
    - Ubicación geográfica de prospectos
    
    **🚀 Recomendaciones Específicas:**
    - Estrategias de contenido para LinkedIn
    - Optimización de perfil empresarial
    - Tácticas de generación de leads B2B
    - Networking estratégico
    
    ---
    *Análisis generado por GPT-4 especializado en marketing B2B*
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666; font-size: 0.9rem;'>
    💼 Datos en tiempo real de LinkedIn Analytics • Período: {from_date} - {to_date}<br>
    Desarrollado por Jungle Creative Agency para Widu Legal
</div>
""".format(from_date=from_date.strftime('%d/%m/%Y'), to_date=to_date.strftime('%d/%m/%Y')), unsafe_allow_html=True)
