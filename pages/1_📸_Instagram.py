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
    page_title="Instagram Analytics - Widu Legal",
    page_icon="📸",
    layout="wide"
)

# Configurar OpenAI con valor por defecto
try:
    OPENAI_API_KEY = st.secrets["api_keys"]["openai_api_key"]
except KeyError:
    OPENAI_API_KEY = "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"

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# CSS personalizado para Instagram
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #F8E964;
        margin-bottom: 1rem;
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: bold;
        color: #F8E964;
        margin: 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Header de Instagram
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.image("https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png", width=120)
    st.markdown("<p style='text-align: center; font-size: 12px; color: #666; margin-top: -10px;'>Marketing Agency</p>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #F8E964; margin-bottom: 5px;'>📸 Reporte de Instagram</h1>
        <p style='color: #666; font-size: 16px; margin: 0;'>Analytics Dashboard Profesional</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("<p style='text-align: center; font-size: 12px; color: #666; margin-top: -10px;'>Cliente</p>", unsafe_allow_html=True)

# Línea separadora con estilo
st.markdown("""
<hr style='border: none; height: 3px; background: linear-gradient(90deg, #F8E964 0%, #000000 50%, #F8E964 100%); margin: 30px 0;'>
""", unsafe_allow_html=True)

# Información del proyecto actual
show_project_info_header()

# Logo en sidebar
st.sidebar.image("https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png", width=200)
st.sidebar.markdown("---")

# Selector de proyectos
project_info, profile_data, available_networks = create_project_selector()
st.sidebar.markdown("---")

# Verificar si Instagram está disponible
if not is_network_available('instagram'):
    show_network_not_available('Instagram', '📸')
    st.stop()

# Configuración de fechas en el sidebar
st.sidebar.header("⚙️ Configuración")
from_date = st.sidebar.date_input(
    "Fecha de inicio:",
    value=date(2025, 7, 1),
    key="from_date_instagram"
)

to_date = st.sidebar.date_input(
    "Fecha de fin:",
    value=date(2025, 7, 31),
    key="to_date_instagram"
)

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


# Funciones para obtener datos de Instagram
@st.cache_data(ttl=1800)
def get_instagram_posts(_client, from_date, to_date, blog_id):
    """Obtiene los posts de Instagram del período especificado"""
    try:
        response = _client.get_instagram_posts(
            from_date=from_date,
            to_date=to_date
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo posts de Instagram: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_followers_analytics(_client, from_date, to_date, blog_id):
    try:
        response = _client.get_timeline_analytics(
            from_date=from_date,
            to_date=to_date,
            metric="followers",
            network="instagram",
            subject="account"
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo datos de seguidores: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_delta_followers_analytics(_client, from_date, to_date, blog_id):
    try:
        response = _client.get_timeline_analytics(
            from_date=from_date,
            to_date=to_date,
            metric="delta_followers",
            network="instagram",
            subject="account"
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo datos de delta followers: {str(e)}")
        return None

# Función para calcular cambio porcentual
def calculate_percentage_change(current_value, previous_value):
    """Calcula el cambio porcentual"""
    if previous_value == 0:
        return 100 if current_value > 0 else 0
    return ((current_value - previous_value) / previous_value) * 100

@st.cache_data(ttl=1800)
def get_distribution_analytics(_client, from_date, to_date, metric, blog_id):
    try:
        response = _client.get_distribution_analytics(
            from_date=from_date,
            to_date=to_date,
            metric=metric,
            network="instagram",
            subject="account"
        )
        return response
    except Exception as e:
        st.error(f"Error obteniendo datos de {metric}: {str(e)}")
        return None

# Funciones para extraer datos
def extract_final_value(api_response):
    """Extrae el valor final de una serie temporal"""
    if not api_response or api_response.get('status') != 200:
        return 0
    
    try:
        data = api_response.get('data', {})
        if isinstance(data, dict) and 'data' in data:
            metrics_data = data['data']
            if isinstance(metrics_data, list) and len(metrics_data) > 0:
                values_data = metrics_data[0].get('values', [])
                
                if values_data:
                    # Para followers, tomar el último valor ordenado por fecha
                    if 'followers' in str(api_response):
                        sorted_values = sorted(values_data, key=lambda x: x.get('dateTime', ''))
                        if sorted_values:
                            return sorted_values[-1].get('value', 0)
                    else:
                        # Para otros métricas, sumar todos los valores
                        return sum(item.get('value', 0) for item in values_data)
    except Exception as e:
        st.error(f"Error procesando datos: {str(e)}")
    
    return 0

def extract_gained_lost_from_delta(delta_response):
    """Calcula seguidores ganados y perdidos desde delta_followers"""
    if not delta_response or delta_response.get('status') != 200:
        return 0, 0
    
    try:
        data = delta_response.get('data', {})
        if isinstance(data, dict) and 'data' in data:
            metrics_data = data['data']
            if isinstance(metrics_data, list) and len(metrics_data) > 0:
                values_data = metrics_data[0].get('values', [])
                
                gained = sum(item.get('value', 0) for item in values_data if item.get('value', 0) > 0)
                lost = sum(abs(item.get('value', 0)) for item in values_data if item.get('value', 0) < 0)
                
                return gained, lost
    except Exception as e:
        st.error(f"Error procesando delta followers: {str(e)}")
    
    return 0, 0

def extract_timeline_data(api_response):
    """Extrae datos de timeline para gráficos"""
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
        st.error(f"Error procesando timeline: {str(e)}")
    
    return [], []

def get_delta_timeline_data(delta_response):
    """Extrae datos diarios de ganados/perdidos para gráficos"""
    dates, values = extract_timeline_data(delta_response)
    
    gained_data = []
    lost_data = []
    
    for value in values:
        if value > 0:
            gained_data.append(value)
            lost_data.append(0)
        else:
            gained_data.append(0)
            lost_data.append(abs(value))
    
    return dates, gained_data, lost_data

# Funciones para crear gráficos
def create_total_followers_chart(followers_response):
    """Crea gráfico de línea para seguidores totales"""
    fig = go.Figure()
    
    dates, values = extract_timeline_data(followers_response)
    values_sorted = []
    
    if dates and values:
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name='Seguidores Totales',
            line=dict(color='#F8E964', width=3),
            marker=dict(size=6, color='#000000')
        ))
        
        values_sorted = sorted(values)
        
        # Ajustar escala Y dinámicamente
        if len(values_sorted) > 1:
            min_val = min(values_sorted)
            max_val = max(values_sorted)
            range_val = max_val - min_val
            
            if range_val < 50:
                padding = 25
            else:
                padding = range_val * 0.1
            
            y_min = max(0, min_val - padding)
            y_max = max_val + padding
            
            fig.update_layout(yaxis=dict(range=[y_min, y_max]))
    
    fig.update_layout(
        title="📈 Total de Seguidores",
        xaxis_title="Fecha",
        yaxis_title="Número de Seguidores",
        template="plotly_white",
        height=400
    )
    
    return fig

def create_filtered_growth_chart(delta_response, filter_type='both'):
    """Crea gráfico filtrado de crecimiento"""
    fig = go.Figure()
    
    dates, gained_data, lost_data = get_delta_timeline_data(delta_response)
    
    if dates:
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
        title="📊 Detalle de Cambios Diarios",
        xaxis_title="Fecha",
        yaxis_title="Número de Seguidores",
        template="plotly_white",
        height=400
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

# Funciones para crear gráficos demográficos
def create_age_histogram(age_data):
    """Crea histograma vertical para distribución por edad"""
    fig = go.Figure()
    
    if age_data and age_data.get('status') == 200:
        data = age_data.get('data')
        if data and isinstance(data, dict) and 'data' in data:
            try:
                metrics_data = data['data']
                if isinstance(metrics_data, list) and len(metrics_data) > 0:
                    age_groups = []
                    percentages = []
                    
                    for item in metrics_data:
                        if 'key' in item and 'value' in item:
                            age_groups.append(item['key'])
                            percentages.append(float(item['value']))
                    
                    if age_groups and percentages:
                        # Ordenar por edad
                        age_order = ['13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
                        sorted_data = []
                        
                        for age_range in age_order:
                            if age_range in age_groups:
                                idx = age_groups.index(age_range)
                                sorted_data.append((age_range, percentages[idx]))
                        
                        for i, age_range in enumerate(age_groups):
                            if age_range not in age_order:
                                sorted_data.append((age_range, percentages[i]))
                        
                        if sorted_data:
                            sorted_ages, sorted_percentages = zip(*sorted_data)
                            
                            fig.add_trace(go.Bar(
                                x=sorted_ages,
                                y=sorted_percentages,
                                marker_color='#F8E964',
                                name='Distribución por Edad',
                                text=[f'{p:.1f}%' for p in sorted_percentages],
                                textposition='outside'
                            ))
            except Exception as e:
                st.error(f"Error procesando datos de edad: {str(e)}")
    
    fig.update_layout(
        title="📊 Distribución por Edad",
        xaxis_title="Grupo de Edad",
        yaxis_title="Porcentaje (%)",
        template="plotly_white",
        height=400
    )
    
    return fig

def create_gender_donut(gender_data):
    """Crea gráfico de donut para distribución por género"""
    fig = go.Figure()
    df_gender = pd.DataFrame()
    
    if gender_data and gender_data.get('status') == 200:
        data = gender_data.get('data')
        if data and isinstance(data, dict) and 'data' in data:
            try:
                metrics_data = data['data']
                if isinstance(metrics_data, list) and len(metrics_data) > 0:
                    labels = []
                    percentages = []
                    
                    for item in metrics_data:
                        if 'key' in item and 'value' in item:
                            gender_key = item['key']
                            if gender_key.lower() == 'male':
                                gender_label = 'Hombre'
                            elif gender_key.lower() == 'female':
                                gender_label = 'Mujer'
                            elif gender_key.lower() == 'unknown':
                                gender_label = 'Desconocido'
                            else:
                                gender_label = gender_key
                            
                            labels.append(gender_label)
                            percentages.append(float(item['value']))
                    
                    if labels and percentages:
                        df_gender = pd.DataFrame({
                            'Género': labels,
                            'Porcentaje': [f"{p:.1f}%" for p in percentages]
                        })
                        
                        colors = ['#ff69b4', '#4169e1', '#808080']
                        
                        fig.add_trace(go.Pie(
                            labels=labels,
                            values=percentages,
                            hole=0.4,
                            marker=dict(colors=colors[:len(labels)]),
                            textinfo='label+percent',
                            textposition='outside'
                        ))
            except Exception as e:
                st.error(f"Error procesando datos de género: {str(e)}")
    
    fig.update_layout(
        title="⚧ Distribución por Género",
        template="plotly_white",
        height=400,
        showlegend=True
    )
    
    return fig, df_gender

def create_country_analysis(country_data):
    """Crea tabla paginada y histograma horizontal para países"""
    df_countries = pd.DataFrame()
    fig = go.Figure()
    
    if country_data and country_data.get('status') == 200:
        data = country_data.get('data')
        if data and isinstance(data, dict) and 'data' in data:
            try:
                metrics_data = data['data']
                if isinstance(metrics_data, list) and len(metrics_data) > 0:
                    countries = []
                    percentages = []
                    country_flags = []
                    
                    for item in metrics_data:
                        if 'key' in item and 'value' in item:
                            country_code = item['key']
                            countries.append(country_code)
                            percentages.append(float(item['value']))
                            country_flags.append(f"{get_country_flag(country_code)} {country_code}")
                    
                    if countries and percentages:
                        df_countries = pd.DataFrame({
                            'País': country_flags,
                            'Porcentaje': [f"{p:.1f}%" for p in percentages]
                        }).sort_values('Porcentaje', key=lambda x: x.str.replace('%', '').astype(float), ascending=False)
                        
                        df_sorted = pd.DataFrame({
                            'País': country_flags,
                            'Porcentaje_num': percentages
                        }).sort_values('Porcentaje_num', ascending=True)
                        
                        top_10 = df_sorted.tail(10)
                        
                        fig.add_trace(go.Bar(
                            x=top_10['Porcentaje_num'],
                            y=top_10['País'],
                            orientation='h',
                            marker_color='#F8E964',
                            name='Porcentaje por País',
                            text=[f'{p:.1f}%' for p in top_10['Porcentaje_num']],
                            textposition='outside'
                        ))
            except Exception as e:
                st.error(f"Error procesando datos de países: {str(e)}")
    
    fig.update_layout(
        title="🌍 Top 10 Países",
        xaxis_title="Porcentaje (%)",
        yaxis_title="País",
        template="plotly_white",
        height=500
    )
    
    return fig, df_countries

# Generar reporte principal
@st.cache_data(ttl=1800)
def generate_followers_report(_client, from_date, to_date, blog_id):
    """Genera el reporte completo de seguidores de Instagram"""
    from datetime import timedelta
    
    # Calcular fechas del mes anterior
    days_diff = (to_date - from_date).days + 1
    prev_to_date = from_date - timedelta(days=1)
    prev_from_date = prev_to_date - timedelta(days=days_diff-1)
    
    report = {}
    
    # Obtener datos principales del período actual
    report['followers'] = get_followers_analytics(_client, from_date, to_date, blog_id)
    report['delta_followers'] = get_delta_followers_analytics(_client, from_date, to_date, blog_id)
    
    # Obtener datos del mes anterior para comparación
    report['followers_previous'] = get_followers_analytics(_client, prev_from_date, prev_to_date, blog_id)
    report['delta_followers_previous'] = get_delta_followers_analytics(_client, prev_from_date, prev_to_date, blog_id)
    
    # Obtener datos demográficos
    report['age'] = get_distribution_analytics(_client, from_date, to_date, "age", blog_id)
    report['gender'] = get_distribution_analytics(_client, from_date, to_date, "gender", blog_id)
    report['country'] = get_distribution_analytics(_client, from_date, to_date, "country", blog_id)
    
    # Obtener posts de Instagram
    report['posts'] = get_instagram_posts(_client, from_date, to_date, blog_id)
    
    return report

# Ejecutar reporte
with st.spinner("🔄 Generando reporte de Instagram..."):
    report = generate_followers_report(client, from_date, to_date, current_blog_id)
    
    # Guardar datos de Instagram en session state para uso en PDF y otras páginas
    st.session_state['instagram_report'] = report
    
    # Extraer métricas principales para el PDF
    def extract_gained_followers(delta_data):
        """Extrae el número de seguidores ganados"""
        if not delta_data or delta_data.get('status') != 200:
            return 0
        values = delta_data.get('data', {}).get('data', [])
        if not values:
            return 0
        gained = sum(value.get('value', 0) for value in values if value.get('value', 0) > 0)
        return gained

    def extract_lost_followers(delta_data):
        """Extrae el número de seguidores perdidos"""
        if not delta_data or delta_data.get('status') != 200:
            return 0
        values = delta_data.get('data', {}).get('data', [])
        if not values:
            return 0
        lost = abs(sum(value.get('value', 0) for value in values if value.get('value', 0) < 0))
        return lost

    def extract_net_delta(delta_data):
        """Extrae el delta neto de seguidores"""
        if not delta_data or delta_data.get('status') != 200:
            return 0
        values = delta_data.get('data', {}).get('data', [])
        if not values:
            return 0
        net_delta = sum(value.get('value', 0) for value in values)
        return net_delta

    def calculate_engagement_rate(posts_data):
        """Calcula la tasa de engagement promedio"""
        if not posts_data or not isinstance(posts_data, list):
            return 0
        total_engagement = 0
        valid_posts = 0
        for post in posts_data:
            if isinstance(post, dict):
                likes = post.get('likes', 0) or 0
                comments = post.get('comments', 0) or 0
                shares = post.get('shares', 0) or 0
                reach = post.get('reach', 0) or 0
                if reach > 0:
                    engagement = (likes + comments + shares) / reach * 100
                    total_engagement += engagement
                    valid_posts += 1
        return total_engagement / valid_posts if valid_posts > 0 else 0

    metrics = {
        'total_followers': extract_final_value(report['followers']),
        'gained_followers': extract_gained_followers(report['delta_followers']),
        'lost_followers': extract_lost_followers(report['delta_followers']),
        'net_delta': extract_net_delta(report['delta_followers']),
        'engagement': calculate_engagement_rate(report['posts']) if report['posts'] else 0,
        'total_posts': len(report['posts']) if report['posts'] else 0
    }
    
    # Guardar métricas para PDF
    st.session_state['instagram_metrics'] = metrics

# Header del reporte
col1, col2 = st.columns([3, 1])
with col1:
    st.header("📊 Reporte Completo de Seguidores")
    st.markdown(f"**Período:** {from_date.strftime('%d/%m/%Y')} - {to_date.strftime('%d/%m/%Y')}")

with col2:
    st.markdown("""
    <div style='text-align: right; padding: 10px; background: rgba(225, 48, 108, 0.1); border-radius: 8px; border-left: 4px solid #F8E964;'>
        <p style='font-size: 11px; color: #666; margin: 0;'>Elaborado por:</p>
        <p style='font-size: 12px; font-weight: bold; color: #F8E964; margin: 0;'>🌿 Jungle Creative</p>
    </div>
    """, unsafe_allow_html=True)

# Extraer métricas principales
total_followers = extract_final_value(report['followers'])
gained_followers, lost_followers = extract_gained_lost_from_delta(report['delta_followers'])
net_followers = gained_followers - lost_followers

# Extraer métricas del mes anterior para comparación
total_followers_prev = extract_final_value(report['followers_previous'])
gained_followers_prev, lost_followers_prev = extract_gained_lost_from_delta(report['delta_followers_previous'])
net_followers_prev = gained_followers_prev - lost_followers_prev

# Calcular cambios porcentuales
followers_change = calculate_percentage_change(total_followers, total_followers_prev)
gained_change = calculate_percentage_change(gained_followers, gained_followers_prev)
lost_change = calculate_percentage_change(lost_followers, lost_followers_prev)
net_change = calculate_percentage_change(net_followers, net_followers_prev)

# Cards de métricas principales
st.subheader("📊 Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    change_color = "#F8E964" if followers_change >= 0 else "#000000"
    change_symbol = "↗️" if followers_change >= 0 else "↘️"
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-number">{total_followers:,}</p>
        <p class="metric-label">👥 Seguidores</p>
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
        <p class="metric-label">➕ Empezaron a seguirte</p>
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
        <p class="metric-label">➖ Dejaron de seguirte</p>
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
        <p class="metric-label">📈 Total (Neto)</p>
        <p class="metric-change" style="color: {change_color}; font-size: 0.9rem; margin: 5px 0 0 0;">
            {change_symbol} {net_change:+.1f}% vs mes anterior
        </p>
    </div>
    """, unsafe_allow_html=True)

# Separador
st.markdown("---")

# Gráfico de seguidores totales
st.subheader("📈 Evolución de Seguidores")
followers_chart = create_total_followers_chart(report['followers'])
st.plotly_chart(followers_chart, use_container_width=True)

# Separador
st.markdown("---")

# Gráfico de cambios diarios con filtros
st.subheader("📊 Detalle de Cambios Diarios")

# Botones de filtro
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👥 Mostrar Ambos", key="both"):
        st.session_state['chart_filter'] = 'both'

with col2:
    if st.button("➕ Solo Ganados", key="gained"):
        st.session_state['chart_filter'] = 'gained'

with col3:
    if st.button("➖ Solo Perdidos", key="lost"):
        st.session_state['chart_filter'] = 'lost'

# Crear gráfico con filtro
filter_type = st.session_state.get('chart_filter', 'both')
growth_chart = create_filtered_growth_chart(report['delta_followers'], filter_type)
st.plotly_chart(growth_chart, use_container_width=True)

# Separador
st.markdown("---")

# Sección de Demografía
st.header("👥 Análisis Demográfico")
st.markdown("**Distribución de la audiencia por edad, género y país**")

# Crear gráficos demográficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribución por Edad")
    age_chart = create_age_histogram(report['age'])
    st.plotly_chart(age_chart, use_container_width=True)

with col2:
    st.subheader("⚧ Distribución por Género")
    gender_chart, gender_df = create_gender_donut(report['gender'])
    st.plotly_chart(gender_chart, use_container_width=True)
    
    if not gender_df.empty:
        st.dataframe(gender_df, use_container_width=True)

# Separador
st.markdown("---")

# Análisis por países
st.subheader("🌍 Análisis por Países")

col1, col2 = st.columns([2, 1])

with col1:
    country_chart, country_df = create_country_analysis(report['country'])
    st.plotly_chart(country_chart, use_container_width=True)

with col2:
    st.markdown("**📋 Tabla de Países**")
    if not country_df.empty:
        # Paginación simple
        items_per_page = 10
        total_items = len(country_df)
        total_pages = (total_items - 1) // items_per_page + 1
        
        page = st.selectbox("Página", range(1, total_pages + 1), key="country_page")
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        st.dataframe(country_df.iloc[start_idx:end_idx], use_container_width=True)
        st.caption(f"Mostrando {start_idx + 1}-{min(end_idx, total_items)} de {total_items} países")
    else:
        st.info("No hay datos de países disponibles.")

# Separador
st.markdown("---")

# Sección de Posts
st.header("📱 Análisis de Posts de Instagram")
st.markdown("**Posts publicados en el período seleccionado con métricas de engagement**")

def create_posts_table(posts_data):
    """Crea una tabla interactiva con los posts de Instagram"""
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
        
        # La respuesta de Metricool tiene la estructura: {status: 200, data: {...}}
        # Y dentro de data está: {data: [posts...]}
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
    
    st.markdown(f"**📊 Total de posts encontrados:** {len(data)}")
    
    # Configuración de paginación
    posts_per_page = 5
    total_posts = len(data)
    total_pages = (total_posts - 1) // posts_per_page + 1
    
    if total_pages > 1:
        page = st.selectbox("Página", range(1, total_pages + 1), key="posts_page")
        start_idx = (page - 1) * posts_per_page
        end_idx = min(start_idx + posts_per_page, total_posts)
        posts_to_show = data[start_idx:end_idx]
        st.caption(f"Mostrando posts {start_idx + 1}-{end_idx} de {total_posts}")
    else:
        posts_to_show = data
    
    # Crear tabla de posts
    for i, post in enumerate(posts_to_show):
        # Verificar que el post sea un diccionario válido
        if not isinstance(post, dict):
            st.warning(f"Post {i+1} tiene formato inesperado y será omitido.")
            continue
            
        with st.container():
            # Card para cada post
            st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 4px solid #F8E964;'>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                # Imagen en miniatura con manejo de errores
                if post.get('imageUrl'):
                    try:
                        image_url = post['imageUrl']
                        # Verificar si la URL es válida (manejar tanto strings como números)
                        image_url_str = str(image_url) if image_url is not None else ""
                        if (image_url and 
                            image_url_str.strip() and 
                            image_url_str != '0' and 
                            image_url != 0 and
                            'http' in image_url_str.lower()):
                            st.image(image_url, width=150, caption="📸")
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
                    # Formatear fecha
                    from datetime import datetime
                    try:
                        date_obj = datetime.fromisoformat(post_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%d/%m/%Y %H:%M')
                    except:
                        formatted_date = post_date[:16].replace('T', ' ')
                else:
                    formatted_date = post_date
                
                st.markdown(f"**📅 Fecha:** {formatted_date}")
                st.markdown(f"**📋 Tipo:** {post.get('type', 'UNKNOWN').replace('FEED_', '').replace('_', ' ')}")
                
                if post.get('url'):
                    st.markdown(f"**🔗 Enlace:** [Ver en Instagram]({post['url']})")
                
                # Contenido (primeras líneas)
                content = post.get('content', '')
                if content:
                    content_preview = content[:150] + '...' if len(content) > 150 else content
                    st.markdown(f"**💬 Contenido:** {content_preview}")
                
                # Usuario
                if post.get('userId'):
                    st.markdown(f"**👤 Usuario:** {post['userId']}")
            
            with col3:
                # Métricas principales en formato compacto
                st.markdown("**📊 Métricas**")
                
                # Métricas básicas
                likes = post.get('likes', 0)
                comments = post.get('comments', 0)
                shares = post.get('shares', 0)
                saved = post.get('saved', 0)
                
                st.markdown(f"❤️ **Likes:** {likes:,}")
                st.markdown(f"💬 **Comentarios:** {comments:,}")
                st.markdown(f"🔄 **Compartidas:** {shares:,}")
                st.markdown(f"💾 **Guardados:** {saved:,}")
                
                # Métricas de alcance
                reach = post.get('reach', 0)
                views = post.get('views', 0)
                impressions = post.get('impressions', 0)
                
                if reach > 0:
                    st.markdown(f"👁️ **Alcance:** {reach:,}")
                if views > 0:
                    st.markdown(f"📺 **Vistas:** {views:,}")
                if impressions > 0:
                    st.markdown(f"👀 **Impresiones:** {impressions:,}")
                
                # Engagement
                engagement = post.get('engagement', 0)
                if engagement > 0:
                    st.markdown(f"📈 **Engagement:** {engagement:.1f}%")
            
            st.markdown("---")
    
    # Estadísticas generales
    if data:
        st.subheader("📊 Estadísticas Generales del Período")
        
        total_likes = sum(post.get('likes', 0) for post in data)
        total_comments = sum(post.get('comments', 0) for post in data)
        total_shares = sum(post.get('shares', 0) for post in data)
        total_saved = sum(post.get('saved', 0) for post in data)
        total_reach = sum(post.get('reach', 0) for post in data)
        total_views = sum(post.get('views', 0) for post in data)
        avg_engagement = sum(post.get('engagement', 0) for post in data) / len(data) if data else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='background: rgba(225, 48, 108, 0.1); padding: 15px; border-radius: 8px; text-align: center;'>
                <h3 style='color: #F8E964; margin: 0; font-size: 1.5rem;'>{total_likes:,}</h3>
                <p style='color: #666; margin: 5px 0 0 0; font-size: 0.9rem;'>❤️ Total Likes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: rgba(40, 167, 69, 0.1); padding: 15px; border-radius: 8px; text-align: center;'>
                <h3 style='color: #F8E964; margin: 0; font-size: 1.5rem;'>{total_comments:,}</h3>
                <p style='color: #666; margin: 5px 0 0 0; font-size: 0.9rem;'>💬 Total Comentarios</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: rgba(23, 162, 184, 0.1); padding: 15px; border-radius: 8px; text-align: center;'>
                <h3 style='color: #000000; margin: 0; font-size: 1.5rem;'>{total_reach:,}</h3>
                <p style='color: #666; margin: 5px 0 0 0; font-size: 0.9rem;'>👁️ Alcance Total</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style='background: rgba(255, 193, 7, 0.1); padding: 15px; border-radius: 8px; text-align: center;'>
                <h3 style='color: #F8E964; margin: 0; font-size: 1.5rem;'>{avg_engagement:.1f}%</h3>
                <p style='color: #666; margin: 5px 0 0 0; font-size: 0.9rem;'>📈 Engagement Promedio</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Métricas adicionales si existen
        if total_shares > 0 or total_saved > 0 or total_views > 0:
            st.markdown("### 📊 Métricas Adicionales")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if total_shares > 0:
                    st.metric("🔄 Total Compartidas", f"{total_shares:,}")
            
            with col2:
                if total_saved > 0:
                    st.metric("💾 Total Guardados", f"{total_saved:,}")
            
            with col3:
                if total_views > 0:
                    st.metric("📺 Total Vistas", f"{total_views:,}")

# Mostrar tabla de posts
create_posts_table(report['posts'])

# Separador
st.markdown("---")

# Sección de Top Posts
st.header("🏆 Posts Destacados")
st.markdown("**Los posts con mejor rendimiento en cada métrica**")

def create_top_posts_section(posts_data):
    """Crea la sección de posts destacados por métrica"""
    if not posts_data:
        st.info("No hay datos de posts disponibles para mostrar posts destacados.")
        return
    
    # Obtener los datos de posts (misma lógica que en create_posts_table)
    if isinstance(posts_data, dict):
        if posts_data.get('status') != 200:
            st.error("No se pueden mostrar posts destacados debido a un error en la API.")
            return
        api_data = posts_data.get('data', {})
        if isinstance(api_data, dict):
            data = api_data.get('data', [])
        else:
            data = api_data if isinstance(api_data, list) else []
    elif isinstance(posts_data, list):
        data = posts_data
    else:
        return
    
    if not data or not isinstance(data, list):
        st.info("No hay posts disponibles para mostrar destacados.")
        return
    
    # Definir métricas a analizar
    metrics_config = {
        'likes': {'name': 'Likes', 'emoji': '❤️', 'color': '#F8E964'},
        'comments': {'name': 'Comentarios', 'emoji': '💬', 'color': '#F8E964'},
        'views': {'name': 'Vistas', 'emoji': '📺', 'color': '#000000'},
        'engagement': {'name': 'Engagement', 'emoji': '📈', 'color': '#F8E964'},
        'reach': {'name': 'Alcance', 'emoji': '👁️', 'color': '#000000'},
        'shares': {'name': 'Compartidas', 'emoji': '🔄', 'color': '#F8E964'}
    }
    
    # Función auxiliar para encontrar el post con mayor valor en una métrica
    def get_top_post(metric_key):
        try:
            valid_posts = [post for post in data if isinstance(post, dict) and post.get(metric_key, 0) > 0]
            if not valid_posts:
                return None
            return max(valid_posts, key=lambda x: x.get(metric_key, 0))
        except Exception as e:
            return None
    
    # Encontrar los posts top para cada métrica
    top_posts = {}
    for metric_key, config in metrics_config.items():
        top_post = get_top_post(metric_key)
        if top_post:
            post_id = top_post.get('id', f"post_{id(top_post)}")  # Usar ID único del post
            if post_id not in top_posts:
                top_posts[post_id] = {
                    'post': top_post,
                    'metrics': []
                }
            top_posts[post_id]['metrics'].append({
                'key': metric_key,
                'name': config['name'],
                'emoji': config['emoji'],
                'color': config['color'],
                'value': top_post.get(metric_key, 0)
            })
    
    if not top_posts:
        st.info("No hay posts con métricas destacadas disponibles.")
        return
    
    # Función auxiliar para mostrar un post con múltiples métricas destacadas
    def show_combined_top_post(post_data):
        post = post_data['post']
        metrics = post_data['metrics']
        
        # Extraer información del post
        likes = post.get('likes', 0)
        comments = post.get('comments', 0)
        shares = post.get('shares', 0)
        reach = post.get('reach', 0)
        views = post.get('views', 0)
        engagement = post.get('engagement', 0)
        
        # Formatear fecha
        post_date = post.get('publishedAt', {}).get('dateTime', 'Sin fecha')
        if post_date != 'Sin fecha':
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(post_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%d/%m/%Y')
            except:
                formatted_date = post_date[:10]
        else:
            formatted_date = post_date
        
        # Contenido preview
        content = post.get('content', '')
        content_preview = content[:100] + '...' if len(content) > 100 else content
        
        # URL del post
        post_url = post.get('url', '')
        
        # Crear título con todas las métricas destacadas
        metrics_title = " • ".join([f"{m['emoji']} {m['name']}" for m in metrics])
        
        # Usar el color del primer métrica como color principal
        primary_color = metrics[0]['color']
        
        # Crear gradiente de colores si hay múltiples métricas
        if len(metrics) > 1:
            colors_list = [m['color'] for m in metrics]
            # Convertir hex a rgba para el gradiente
            def hex_to_rgba(hex_color, alpha=0.1):
                hex_color = hex_color.lstrip('#')
                return f"rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, {alpha})"
            
            gradient = f"linear-gradient(135deg, {hex_to_rgba(colors_list[0], 0.2)}, {hex_to_rgba(colors_list[-1], 0.2)})"
        else:
            # Convertir hex a rgba
            hex_color = primary_color.lstrip('#')
            gradient = f"rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, 0.1)"
        
        # Crear el contenedor principal con Streamlit nativo
        with st.container():
            # Badge y título
            col_badge, col_title = st.columns([3, 1])
            with col_badge:
                st.markdown(f"### {metrics_title}")
            with col_title:
                st.markdown(f"<span style='background: {primary_color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold;'>🏆 SÚPER POST</span>", unsafe_allow_html=True)
            
            # Crear layout principal: información del post a la izquierda, métricas a la derecha
            col_info, col_metrics = st.columns([2, 1])
            
            with col_info:
                # Información del post
                st.markdown(f"**📅 Fecha:** {formatted_date}")
                st.markdown(f"**💬 Contenido:** {content_preview}")
                if post_url:
                    st.markdown(f"[🔗 Ver en Instagram]({post_url})")
                
                # Métricas adicionales en líneas separadas para mejor legibilidad
                st.markdown("**Métricas completas:**")
                additional_metrics = []
                additional_metrics.append(f"❤️ {likes:,} likes")
                additional_metrics.append(f"💬 {comments:,} comentarios") 
                additional_metrics.append(f"👁️ {reach:,} alcance")
                if views > 0:
                    additional_metrics.append(f"📺 {views:,} vistas")
                if engagement > 0:
                    additional_metrics.append(f"📈 {engagement:.1f}% engagement")
                
                st.markdown(" • ".join(additional_metrics))
            
            with col_metrics:
                # Métricas destacadas en la columna derecha
                st.markdown("**🏆 Métricas Destacadas:**")
                for metric in metrics:
                    st.metric(
                        label=f"{metric['emoji']} {metric['name']}", 
                        value=f"{metric['value']:,}"
                    )
            
            # Separador visual para SÚPER POST
            st.markdown("---")
        
        # Mostrar imagen si está disponible
        if post.get('imageUrl'):
            metrics_names = " + ".join([m['name'] for m in metrics])
            with st.expander(f"🖼️ Ver imagen del SÚPER POST ({metrics_names})"):
                try:
                    # Verificar si la URL parece válida (manejar tanto strings como números)
                    image_url = post['imageUrl']
                    image_url_str = str(image_url) if image_url is not None else ""
                    if (image_url and 
                        image_url_str.strip() and 
                        image_url_str != '0' and 
                        image_url != 0 and
                        'http' in image_url_str.lower()):
                        st.image(image_url, caption=f"SÚPER POST: {metrics_names}", width=400)
                    else:
                        st.info("🖼️ Imagen no disponible o URL inválida")
                        st.code(f"URL: {image_url} (tipo: {type(image_url).__name__})")
                except Exception as e:
                    st.error("❌ Error al cargar la imagen")
                    st.info("🔗 Intenta acceder directamente:")
                    st.code(post['imageUrl'])
                    st.caption(f"Error: {str(e)}")
        else:
            metrics_names = " + ".join([m['name'] for m in metrics])
            with st.expander(f"🖼️ Ver imagen del SÚPER POST ({metrics_names})"):
                st.info("🖼️ No hay imagen disponible para este post")
    
    # Función auxiliar para mostrar métricas sin posts destacados
    def show_no_data_metric(metric_name, emoji):
        st.markdown(f"""
        <div style='background: rgba(108, 117, 125, 0.1); padding: 15px; border-radius: 10px; 
                    border-left: 4px solid #6c757d; margin-bottom: 15px;'>
            <h5 style='color: #6c757d; margin: 0 0 5px 0;'>{emoji} {metric_name}</h5>
            <p style='color: #666; margin: 0; font-style: italic; font-size: 0.9rem;'>No hay datos disponibles</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Separar posts por número de métricas destacadas
    super_posts = {k: v for k, v in top_posts.items() if len(v['metrics']) > 1}
    single_posts = {k: v for k, v in top_posts.items() if len(v['metrics']) == 1}
    
    # Mostrar SÚPER POSTS primero (posts que destacan en múltiples métricas)
    if super_posts:
        st.subheader("🏆 SÚPER POSTS")
        st.markdown("*Posts que destacan en múltiples métricas*")
        
        for post_id, post_data in super_posts.items():
            show_combined_top_post(post_data)
        
        st.markdown("---")
    
    # Mostrar posts individuales
    if single_posts:
        st.subheader("⭐ Posts Destacados Individuales")
        
        # Crear layout en columnas dinámicas según la cantidad de posts
        num_posts = len(single_posts)
        if num_posts <= 2:
            cols = st.columns(num_posts)
        else:
            cols = st.columns(2)
        
        col_index = 0
        for post_id, post_data in single_posts.items():
            with cols[col_index % len(cols)]:
                show_combined_top_post(post_data)
            col_index += 1
    
    # Mostrar métricas sin datos disponibles
    all_metrics_with_data = set()
    for post_data in top_posts.values():
        for metric in post_data['metrics']:
            all_metrics_with_data.add(metric['key'])
    
    missing_metrics = []
    for metric_key, config in metrics_config.items():
        if metric_key not in all_metrics_with_data:
            missing_metrics.append((config['name'], config['emoji']))
    
    if missing_metrics:
        st.subheader("📊 Métricas sin datos destacados")
        
        # Mostrar métricas sin datos en una grilla compacta
        missing_cols = st.columns(min(3, len(missing_metrics)))
        for i, (metric_name, emoji) in enumerate(missing_metrics):
            with missing_cols[i % len(missing_cols)]:
                show_no_data_metric(metric_name, emoji)

@st.cache_data(ttl=3600)  # Cache por 1 hora
def generate_ai_analysis(_instagram_data, _linkedin_data=None):
    """Genera análisis estratégico usando OpenAI GPT"""
    try:
        # Función auxiliar para extraer métricas clave
        def extract_key_metrics(data, data_type="instagram"):
            if not data:
                return {}
            
            summary = {}
            
            if data_type == "instagram":
                # Extraer solo métricas clave de Instagram
                followers_data = data.get('followers', {})
                if isinstance(followers_data, dict) and 'data' in followers_data:
                    followers_values = followers_data['data'].get('data', [])
                    if followers_values and len(followers_values) > 0:
                        latest_followers = followers_values[0].get('values', [])
                        if latest_followers:
                            summary['total_followers'] = latest_followers[0].get('value', 0)
                
                # Delta followers resumido
                delta_data = data.get('delta_followers', {})
                if isinstance(delta_data, dict) and 'data' in delta_data:
                    delta_values = delta_data['data'].get('data', [])
                    if delta_values:
                        gained = sum(v.get('value', 0) for v in delta_values[0].get('values', []) if v.get('value', 0) > 0)
                        lost = sum(abs(v.get('value', 0)) for v in delta_values[0].get('values', []) if v.get('value', 0) < 0)
                        summary['followers_gained'] = gained
                        summary['followers_lost'] = lost
                        summary['net_growth'] = gained - lost
                
                # Posts resumidos y análisis de top performers
                posts_data = data.get('posts', {})
                if isinstance(posts_data, dict) and 'data' in posts_data:
                    posts_list = posts_data['data'].get('data', [])
                    if posts_list:
                        total_posts = len(posts_list)
                        total_likes = sum(post.get('likes', 0) for post in posts_list if isinstance(post, dict))
                        total_comments = sum(post.get('comments', 0) for post in posts_list if isinstance(post, dict))
                        total_reach = sum(post.get('reach', 0) for post in posts_list if isinstance(post, dict))
                        
                        summary['posts_metrics'] = {
                            'total_posts': total_posts,
                            'avg_likes': round(total_likes / total_posts) if total_posts > 0 else 0,
                            'avg_comments': round(total_comments / total_posts) if total_posts > 0 else 0,
                            'avg_reach': round(total_reach / total_posts) if total_posts > 0 else 0,
                            'total_engagement': total_likes + total_comments
                        }
                        
                        # Análisis de posts destacados
                        valid_posts = [post for post in posts_list if isinstance(post, dict)]
                        
                        # Top post por likes
                        if valid_posts:
                            top_likes_post = max(valid_posts, key=lambda x: x.get('likes', 0))
                            if top_likes_post.get('likes', 0) > 0:
                                content_preview = top_likes_post.get('content', '')[:100] + '...' if len(top_likes_post.get('content', '')) > 100 else top_likes_post.get('content', 'Sin contenido')
                                summary['top_likes_post'] = {
                                    'likes': top_likes_post.get('likes', 0),
                                    'comments': top_likes_post.get('comments', 0),
                                    'reach': top_likes_post.get('reach', 0),
                                    'views': top_likes_post.get('views', 0),
                                    'content_preview': content_preview,
                                    'type': top_likes_post.get('type', 'unknown'),
                                    'date': top_likes_post.get('publishedAt', {}).get('dateTime', 'Sin fecha')[:10] if top_likes_post.get('publishedAt') else 'Sin fecha'
                                }
                        
                        # Top post por engagement (likes + comentarios)
                        if valid_posts:
                            top_engagement_post = max(valid_posts, key=lambda x: x.get('likes', 0) + x.get('comments', 0))
                            total_engagement = top_engagement_post.get('likes', 0) + top_engagement_post.get('comments', 0)
                            if total_engagement > 0:
                                content_preview = top_engagement_post.get('content', '')[:100] + '...' if len(top_engagement_post.get('content', '')) > 100 else top_engagement_post.get('content', 'Sin contenido')
                                summary['top_engagement_post'] = {
                                    'total_engagement': total_engagement,
                                    'likes': top_engagement_post.get('likes', 0),
                                    'comments': top_engagement_post.get('comments', 0),
                                    'reach': top_engagement_post.get('reach', 0),
                                    'content_preview': content_preview,
                                    'type': top_engagement_post.get('type', 'unknown'),
                                    'date': top_engagement_post.get('publishedAt', {}).get('dateTime', 'Sin fecha')[:10] if top_engagement_post.get('publishedAt') else 'Sin fecha'
                                }
                        
                        # Top post por alcance
                        if valid_posts:
                            top_reach_post = max(valid_posts, key=lambda x: x.get('reach', 0))
                            if top_reach_post.get('reach', 0) > 0:
                                content_preview = top_reach_post.get('content', '')[:100] + '...' if len(top_reach_post.get('content', '')) > 100 else top_reach_post.get('content', 'Sin contenido')
                                summary['top_reach_post'] = {
                                    'reach': top_reach_post.get('reach', 0),
                                    'likes': top_reach_post.get('likes', 0),
                                    'comments': top_reach_post.get('comments', 0),
                                    'content_preview': content_preview,
                                    'type': top_reach_post.get('type', 'unknown'),
                                    'date': top_reach_post.get('publishedAt', {}).get('dateTime', 'Sin fecha')[:10] if top_reach_post.get('publishedAt') else 'Sin fecha'
                                }
                
                # Demografía simplificada
                age_data = data.get('age', {})
                if isinstance(age_data, dict) and 'data' in age_data:
                    age_dist = age_data['data'].get('data', [])
                    if age_dist:
                        top_age_groups = sorted(age_dist, key=lambda x: x.get('value', 0), reverse=True)[:3]
                        summary['top_age_groups'] = [f"{item['key']}: {item['value']:.1f}%" for item in top_age_groups]
                
            elif data_type == "linkedin":
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
                
                # Top industrias
                industry_data = data.get('industry', {})
                if isinstance(industry_data, dict) and 'data' in industry_data:
                    industries = industry_data['data'].get('data', [])
                    if industries:
                        top_industries = sorted(industries, key=lambda x: x.get('value', 0), reverse=True)[:5]
                        summary['top_industries'] = [f"{item['key']}: {item['value']}" for item in top_industries]
            
            return summary
        
        # Extraer solo métricas clave
        instagram_summary = extract_key_metrics(_instagram_data, "instagram")
        linkedin_summary = extract_key_metrics(_linkedin_data, "linkedin") if _linkedin_data else {}
        
        # Crear prompt optimizado con análisis de posts destacados
        posts_analysis = ""
        
        # Agregar análisis de posts destacados si existen
        if instagram_summary.get('top_likes_post'):
            top_likes = instagram_summary['top_likes_post']
            posts_analysis += f"\n\nPOSTS DESTACADOS INSTAGRAM:\n"
            posts_analysis += f"🏆 Post con más likes ({top_likes['likes']} likes, {top_likes['date']}):\n"
            posts_analysis += f"   Tipo: {top_likes['type']} | Alcance: {top_likes['reach']} | Contenido: \"{top_likes['content_preview']}\"\n"
        
        if instagram_summary.get('top_engagement_post'):
            top_eng = instagram_summary['top_engagement_post']
            posts_analysis += f"🏆 Post con más engagement ({top_eng['total_engagement']} interacciones, {top_eng['date']}):\n"
            posts_analysis += f"   Tipo: {top_eng['type']} | Alcance: {top_eng['reach']} | Contenido: \"{top_eng['content_preview']}\"\n"
        
        if instagram_summary.get('top_reach_post'):
            top_reach = instagram_summary['top_reach_post']
            posts_analysis += f"🏆 Post con más alcance ({top_reach['reach']} personas, {top_reach['date']}):\n"
            posts_analysis += f"   Tipo: {top_reach['type']} | Engagement: {top_reach['likes']} likes, {top_reach['comments']} comentarios | Contenido: \"{top_reach['content_preview']}\"\n"
        
        prompt = f"""Analiza estas métricas de redes sociales y proporciona un reporte estratégico conciso:

INSTAGRAM:
- Seguidores: {instagram_summary.get('total_followers', 'N/A')}
- Crecimiento neto: {instagram_summary.get('net_growth', 'N/A')} (Ganados: {instagram_summary.get('followers_gained', 'N/A')}, Perdidos: {instagram_summary.get('followers_lost', 'N/A')})
- Posts: {instagram_summary.get('posts_metrics', {}).get('total_posts', 'N/A')} publicaciones
- Engagement promedio: {instagram_summary.get('posts_metrics', {}).get('avg_likes', 'N/A')} likes, {instagram_summary.get('posts_metrics', {}).get('avg_comments', 'N/A')} comentarios
- Alcance promedio: {instagram_summary.get('posts_metrics', {}).get('avg_reach', 'N/A')}
- Grupos etarios principales: {', '.join(instagram_summary.get('top_age_groups', ['N/A']))}{posts_analysis}

LINKEDIN:
- Seguidores: {linkedin_summary.get('total_followers', 'N/A')}
- Impresiones totales: {linkedin_summary.get('total_impressions', 'N/A')}
- Industrias principales: {', '.join(linkedin_summary.get('top_industries', ['N/A']))}

Proporciona:
1. ANÁLISIS: Rendimiento actual y tendencias clave
2. FORTALEZAS: Qué está funcionando bien (ESPECIALMENTE analiza por qué los posts destacados funcionaron mejor)
3. OPORTUNIDADES: Áreas de mejora específicas
4. ANÁLISIS DE CONTENIDO: Qué tipos de posts y temas generan más engagement y alcance
5. RECOMENDACIONES: 3-5 acciones concretas basadas en los posts exitosos
6. ESTRATEGIA: Próximos pasos para replicar el éxito de los mejores posts

Mantén el análisis conciso pero profesional (máximo 600 palabras)."""
        
        # Llamar a OpenAI con modelo más eficiente
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Usar GPT-3.5 que es más rápido y económico
            messages=[
                {"role": "system", "content": "Eres un analista de marketing digital experto. Proporciona análisis concisos y accionables."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1800,  # Aumentar ligeramente para análisis de contenido
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generando análisis: {str(e)}"

def generate_instagram_analysis(instagram_data):
    """Genera análisis profundo de Instagram con insights valiosos"""
    try:
        # Extraer métricas del mes actual
        total_followers = extract_final_value(instagram_data.get('followers', {}))
        gained_followers, lost_followers = extract_gained_lost_from_delta(instagram_data.get('delta_followers', {}))
        net_followers = gained_followers - lost_followers
        
        # Extraer métricas del mes anterior
        total_followers_prev = extract_final_value(instagram_data.get('followers_previous', {}))
        gained_followers_prev, lost_followers_prev = extract_gained_lost_from_delta(instagram_data.get('delta_followers_previous', {}))
        net_followers_prev = gained_followers_prev - lost_followers_prev
        
        # Calcular cambios porcentuales
        followers_change = calculate_percentage_change(total_followers, total_followers_prev)
        gained_change = calculate_percentage_change(gained_followers, gained_followers_prev)
        lost_change = calculate_percentage_change(lost_followers, lost_followers_prev)
        net_change = calculate_percentage_change(net_followers, net_followers_prev)
        
        # Análisis profundo de posts
        posts_data = instagram_data.get('posts', [])
        total_posts = len(posts_data) if isinstance(posts_data, list) else 0
        
        # Calcular métricas avanzadas
        total_likes = sum(post.get('likes', 0) for post in posts_data if isinstance(post, dict))
        total_comments = sum(post.get('comments', 0) for post in posts_data if isinstance(post, dict))
        total_reach = sum(post.get('reach', 0) for post in posts_data if isinstance(post, dict))
        total_views = sum(post.get('views', 0) for post in posts_data if isinstance(post, dict))
        total_shares = sum(post.get('shares', 0) for post in posts_data if isinstance(post, dict))
        
        # Engagement rate real
        avg_engagement_rate = 0
        if total_followers > 0 and total_posts > 0:
            avg_engagement_rate = ((total_likes + total_comments + total_shares) / (total_followers * total_posts)) * 100
        
        # Análisis de rendimiento por tipo de contenido
        content_analysis = {}
        if isinstance(posts_data, list):
            for post in posts_data:
                if isinstance(post, dict):
                    post_type = post.get('type', 'unknown')
                    if post_type not in content_analysis:
                        content_analysis[post_type] = {
                            'count': 0, 'total_likes': 0, 'total_comments': 0, 
                            'total_reach': 0, 'total_views': 0, 'total_shares': 0
                        }
                    content_analysis[post_type]['count'] += 1
                    content_analysis[post_type]['total_likes'] += post.get('likes', 0)
                    content_analysis[post_type]['total_comments'] += post.get('comments', 0)
                    content_analysis[post_type]['total_reach'] += post.get('reach', 0)
                    content_analysis[post_type]['total_views'] += post.get('views', 0)
                    content_analysis[post_type]['total_shares'] += post.get('shares', 0)
        
        # Encontrar el mejor tipo de contenido
        best_content_type = "fotos"
        best_engagement_rate = 0
        for content_type, metrics in content_analysis.items():
            if metrics['count'] > 0:
                avg_reach = metrics['total_reach'] / metrics['count']
                avg_engagement = (metrics['total_likes'] + metrics['total_comments'] + metrics['total_shares']) / metrics['count']
                engagement_rate = (avg_engagement / avg_reach * 100) if avg_reach > 0 else 0
                if engagement_rate > best_engagement_rate:
                    best_engagement_rate = engagement_rate
                    best_content_type = content_type
        
        # Análisis de horarios (simulado basado en datos)
        peak_performance = "mañanas (9-11 AM)" if net_change > 0 else "tardes (2-4 PM)"
        
        # Análisis demográfico avanzado
        age_data = instagram_data.get('age', {})
        country_data = instagram_data.get('country', {})
        gender_data = instagram_data.get('gender', {})
        
        # Distribución de edad
        age_distribution = {}
        if isinstance(age_data, dict) and 'data' in age_data:
            age_dist = age_data['data'].get('data', [])
            for age_group in age_dist:
                age_distribution[age_group.get('key', '')] = age_group.get('value', 0)
        
        # Distribución geográfica
        country_distribution = {}
        if isinstance(country_data, dict) and 'data' in country_data:
            country_dist = country_data['data'].get('data', [])
            for country in country_dist:
                country_distribution[country.get('key', '')] = country.get('value', 0)
        
        # Distribución de género
        gender_distribution = {}
        if isinstance(gender_data, dict) and 'data' in gender_data:
            gender_dist = gender_data['data'].get('data', [])
            for gender in gender_dist:
                gender_distribution[gender.get('key', '')] = gender.get('value', 0)
        
        # Insights avanzados
        retention_rate = (gained_followers / (gained_followers + lost_followers) * 100) if (gained_followers + lost_followers) > 0 else 0
        growth_velocity = net_change / 30 if net_change != 0 else 0  # Crecimiento por día
        
        # Análisis de calidad de audiencia
        audience_quality = "Excelente" if retention_rate > 80 else "Buena" if retention_rate > 60 else "Necesita mejora"
        
        # Crear análisis profundo
        analysis = f"""## 📸 Análisis Profundo de Instagram - {total_followers:,} Seguidores

### 🚀 Crecimiento y Retención
**Crecimiento Neto:** {net_followers:+,} seguidores ({net_change:+.1f}% vs mes anterior)
- **Nuevos seguidores:** {gained_followers:,} ({gained_change:+.1f}% vs mes anterior)
- **Seguidores perdidos:** {lost_followers:,} ({lost_change:+.1f}% vs mes anterior)
- **Tasa de retención:** {retention_rate:.1f}% ({audience_quality})
- **Velocidad de crecimiento:** {growth_velocity:+.1f} seguidores/día

### 📊 Rendimiento de Contenido
**Métricas Totales del Mes:**
- **Posts publicados:** {total_posts}
- **Total de likes:** {total_likes:,}
- **Total de comentarios:** {total_comments:,}
- **Total de alcance:** {total_reach:,}
- **Total de visualizaciones:** {total_views:,}
- **Total de compartidos:** {total_shares:,}

**Engagement Rate Promedio:** {avg_engagement_rate:.2f}%
**Mejor tipo de contenido:** {best_content_type} (Engagement: {best_engagement_rate:.1f}%)

### 🎯 Análisis Demográfico Avanzado
**Distribución por Edad:**
{chr(10).join([f"- {age}: {percentage:.1f}%" for age, percentage in sorted(age_distribution.items(), key=lambda x: x[1], reverse=True)[:3]])}

**Distribución Geográfica:**
{chr(10).join([f"- {country}: {percentage:.1f}%" for country, percentage in sorted(country_distribution.items(), key=lambda x: x[1], reverse=True)[:3]])}

**Distribución por Género:**
{chr(10).join([f"- {gender}: {percentage:.1f}%" for gender, percentage in sorted(gender_distribution.items(), key=lambda x: x[1], reverse=True)])}

### 💡 Insights Estratégicos
**Fortalezas Identificadas:**
- {'Crecimiento sostenido' if net_change > 0 else 'Estabilidad en la base de seguidores'}
- {'Alto engagement' if avg_engagement_rate > 3 else 'Engagement moderado' if avg_engagement_rate > 1 else 'Engagement bajo'}
- {'Audiencia de calidad' if retention_rate > 70 else 'Oportunidad de mejora en retención'}

**Oportunidades de Mejora:**
- {'Optimizar horarios de publicación' if avg_engagement_rate < 2 else 'Mantener estrategia actual'}
- {'Diversificar tipos de contenido' if len(content_analysis) < 3 else 'Explorar nuevos formatos'}
- {'Mejorar retención de seguidores' if retention_rate < 70 else 'Mantener calidad de audiencia'}

**Recomendaciones Específicas:**
1. **Contenido:** Enfocar en {best_content_type} que genera {best_engagement_rate:.1f}% de engagement
2. **Horarios:** Publicar en {peak_performance} para maximizar alcance
3. **Audiencia:** {'Mantener estrategia actual' if retention_rate > 80 else 'Mejorar calidad de contenido para reducir pérdida de seguidores'}
4. **Crecimiento:** {'Acelerar frecuencia de publicación' if growth_velocity < 1 else 'Mantener ritmo actual'}

### 📈 Proyección del Próximo Mes
Basado en la tendencia actual, se proyecta:
- **Crecimiento esperado:** {int(growth_velocity * 30):+} seguidores
- **Alcance estimado:** {int(total_reach * 1.1):,} personas
- **Engagement esperado:** {avg_engagement_rate * 1.05:.2f}%"""
        
        return analysis
        
    except Exception as e:
        return f"Error generando análisis de Instagram: {str(e)}"

# Mostrar sección de top posts
create_top_posts_section(report['posts'])

# Expanders para datos raw
with st.expander("🔍 Ver datos raw - Posts"):
    st.json(report['posts'])

with st.expander("🔍 Ver datos raw - Edad"):
    st.json(report['age'])

with st.expander("🔍 Ver datos raw - Género"):
    st.json(report['gender'])

with st.expander("🔍 Ver datos raw - País"):
    st.json(report['country'])

# Separador
st.markdown("---")

# Sección de Análisis AI
st.header("🤖 Análisis Estratégico con IA")
st.markdown("**Análisis profesional automatizado de tus métricas de redes sociales**")

# Botón para generar análisis
if st.button("🚀 Generar Análisis Estratégico", type="primary", use_container_width=True):
    with st.spinner("🤖 Analizando datos con IA... Esto puede tomar unos momentos"):
        try:
            # Generar análisis específico de Instagram
            analysis = generate_instagram_analysis(report)
            
            # Mostrar el análisis
            st.markdown("### 📊 Análisis de Instagram")
            
            # Crear un contenedor con estilo para el análisis
            st.markdown("""
            <div style='background: #F8E964; 
                        padding: 30px; border-radius: 15px; border-left: 5px solid #000000; margin: 20px 0; color: black;'>
            """, unsafe_allow_html=True)
            
            # Mostrar el análisis con formato markdown
            st.markdown(analysis)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Opción para descargar el análisis
            st.download_button(
                label="📥 Descargar Análisis (TXT)",
                data=analysis,
                file_name=f"analisis_estrategico_{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"❌ Error generando análisis: {str(e)}")
            st.info("💡 Asegúrate de que la API key de OpenAI esté configurada correctamente")

# Información sobre el análisis AI
with st.expander("ℹ️ Sobre el Análisis Estratégico con IA"):
    st.markdown("""
    ### 🤖 ¿Qué incluye el análisis?
    
    **📊 Análisis de Métricas:**
    - Evaluación detallada de alcance, engagement, crecimiento
    - Identificación de tendencias y patrones
    - Comparación con benchmarks del sector
    
    **✅ Puntos Positivos:**
    - Estrategias que están funcionando bien
    - Fortalezas de la marca en redes sociales
    - Oportunidades identificadas
    
    **⚠️ Áreas de Mejora:**
    - Puntos débiles detectados
    - Razones técnicas de bajo rendimiento
    - Recomendaciones específicas
    
    **🎯 Estrategia por Red Social:**
    - **Instagram:** Branding, comunidad, tendencias
    - **LinkedIn:** Leads, autoridad, networking
    
    **🚀 Conclusiones Estratégicas:**
    - Situación actual en el ecosistema digital
    - Aprendizajes clave del período
    - Próximos pasos recomendados
    
    ---
    *Análisis generado por GPT-4 con datos reales de tus métricas*
    """)

# Funciones auxiliares para PDF
def calculate_engagement_rate(posts_data):
    """Calcula la tasa de engagement promedio"""
    if not posts_data or not isinstance(posts_data, list):
        return 0
    
    total_engagement = 0
    valid_posts = 0
    
    for post in posts_data:
        if isinstance(post, dict):
            likes = post.get('likes', 0) or 0
            comments = post.get('comments', 0) or 0
            shares = post.get('shares', 0) or 0
            reach = post.get('reach', 0) or 0
            
            if reach > 0:
                engagement = (likes + comments + shares) / reach * 100
                total_engagement += engagement
                valid_posts += 1
    
    return total_engagement / valid_posts if valid_posts > 0 else 0

def extract_gained_followers(delta_data):
    """Extrae el número de seguidores ganados"""
    if not delta_data or delta_data.get('status') != 200:
        return 0
    
    values = delta_data.get('data', {}).get('data', [])
    if not values:
        return 0
    
    gained = sum(value.get('value', 0) for value in values if value.get('value', 0) > 0)
    return gained

def extract_lost_followers(delta_data):
    """Extrae el número de seguidores perdidos"""
    if not delta_data or delta_data.get('status') != 200:
        return 0
    
    values = delta_data.get('data', {}).get('data', [])
    if not values:
        return 0
    
    lost = abs(sum(value.get('value', 0) for value in values if value.get('value', 0) < 0))
    return lost

def extract_net_delta(delta_data):
    """Extrae el delta neto de seguidores"""
    if not delta_data or delta_data.get('status') != 200:
        return 0
    
    values = delta_data.get('data', {}).get('data', [])
    if not values:
        return 0
    
    net_delta = sum(value.get('value', 0) for value in values)
    return net_delta

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666; font-size: 0.9rem;'>
    📈 Datos en tiempo real de Instagram Analytics • Período: {from_date} - {to_date}<br>
    Desarrollado por Jungle Creative Agency para Widu Legal
</div>
""".format(from_date=from_date.strftime('%d/%m/%Y'), to_date=to_date.strftime('%d/%m/%Y')), unsafe_allow_html=True)
