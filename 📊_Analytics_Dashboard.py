import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import sys
import os

# Agregar el directorio actual al path para importar mcp
sys.path.append(os.path.dirname(__file__))
from mcp import MetricoolAPIClient
from project_manager import create_project_selector, show_project_info_header

# Configuración de la página principal
st.set_page_config(
    page_title="Analytics Dashboard - Jungle Creative Agency",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de API keys desde secrets con valores por defecto
try:
    OPENAI_API_KEY = st.secrets["api_keys"]["openai_api_key"]
    METRICOOL_USER_TOKEN = st.secrets["api_keys"]["metricool_user_token"]
    METRICOOL_USER_ID = st.secrets["api_keys"]["metricool_user_id"]
except KeyError:
    # Valores por defecto si no están configurados en secrets
    OPENAI_API_KEY = "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"
    METRICOOL_USER_TOKEN = "AFILXUDKQGBHUMVPOXHFWVJEXWLVPSTTXSSVSJLPKIUZHXSHCBCRHFGLMQUYDFIA"
    METRICOOL_USER_ID = "3752757"

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #F8E964 0%, #000000 100%);
        padding: 2rem;
        border-radius: 15px;
        color: black;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .platform-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #F8E964;
        transition: transform 0.3s ease;
    }
    
    .platform-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border-left: 5px solid #000000;
    }
    
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

# Logo en sidebar
st.sidebar.image("https://widulegal.com/hubfs/raw_assets/public/widu-theme-v1/modules/global/logo.png", width=200)
st.sidebar.markdown("---")

# Selector de proyectos
project_info, profile_data, available_networks = create_project_selector()
st.sidebar.markdown("---")

# Botón para generar reporte
if project_info and available_networks:
    from page_data_capturer import create_advanced_report_button
    
    # Crear botón de reporte avanzado
    create_advanced_report_button(
        project_name=project_info.get('name', 'Proyecto'),
        available_networks=available_networks
    )


# Header principal
st.markdown("""
<div class="main-header">
    <h1 style='font-size: 3rem; margin-bottom: 1rem;'>📊 Analytics Dashboard</h1>
    <p style='font-size: 1.5rem; margin: 0; opacity: 0.9;'>Reporte Completo de Redes Sociales - Widu Legal</p>
</div>
""", unsafe_allow_html=True)

# Logos de las empresas
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.image("https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png", width=150)
    st.markdown("<p style='text-align: center; font-size: 14px; color: #666; margin-top: -10px;'><strong>Jungle Creative Agency</strong><br>Marketing & Analytics</p>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h2 style='color: #333; margin-bottom: 10px;'>🤝 Colaboración Estratégica</h2>
        <p style='color: #666; font-size: 16px; margin: 0;'>Datos en tiempo real • Insights profesionales • Reportes automatizados</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    current_project = st.session_state.get('current_project', {'name': 'Widu Legal'})
    st.image("https://widulegal.com/hubfs/raw_assets/public/widu-theme-v1/modules/global/logo.png", width=150)
    st.markdown(f"<p style='text-align: center; font-size: 14px; color: #666; margin-top: -10px;'><strong>{current_project['name']}</strong><br>Cliente</p>", unsafe_allow_html=True)

# Línea separadora
st.markdown("""
<hr style='border: none; height: 4px; background: linear-gradient(90deg, #F8E964 0%, #000000 50%, #F8E964 100%); margin: 40px 0;'>
""", unsafe_allow_html=True)

# Información del proyecto actual
show_project_info_header()

# Bienvenida y navegación
current_project_name = st.session_state.get('current_project', {}).get('name', 'el proyecto seleccionado')
st.markdown(f"""
## 🚀 ¡Bienvenido al Dashboard de Analytics!

Este dashboard te proporciona un análisis completo y en tiempo real de todas las redes sociales de **{current_project_name}**. 
Utiliza la **barra lateral** para navegar entre las diferentes plataformas y explorar métricas detalladas.

### 📱 Plataformas Disponibles:
""")

# Cards de plataformas - filtradas según disponibilidad
available_networks = st.session_state.get('available_networks', {})

# Definir todas las plataformas posibles
all_platforms = {
    'instagram': {
        'name': 'Instagram Analytics',
        'icon': '📸',
        'color': '#F8E964',
        'description': [
            '• Seguidores totales y crecimiento neto',
            '• Análisis de ganados/perdidos diarios', 
            '• Demografía por edad, género y país',
            '• Métricas de engagement y posts'
        ]
    },
    'linkedin': {
        'name': 'LinkedIn Analytics',
        'icon': '💼', 
        'color': '#000000',
        'description': [
            '• Evolución de seguidores profesionales',
            '• Análisis de impresiones y alcance',
            '• Demografía por industria y función', 
            '• Distribución geográfica profesional'
        ]
    },
    'facebook': {
        'name': 'Facebook Analytics',
        'icon': '📘',
        'color': '#000000', 
        'description': [
            '• Seguidores y likes de página',
            '• Impresiones y visitas totales',
            '• Análisis de posts con imágenes',
            '• Demografia por país y ciudad'
        ]
    },
    'youtube': {
        'name': 'YouTube Analytics',
        'icon': '📺',
        'color': '#F8E964',
        'description': [
            '• Vistas, likes y dislikes',
            '• Comentarios y compartidas', 
            '• Análisis de videos con thumbnails',
            '• Métricas de engagement audiovisual'
        ]
    },
    'google_analytics': {
        'name': 'Google Analytics',
        'icon': '📊',
        'color': '#000000',
        'description': [
            '• Páginas visitadas y sesiones',
            '• Visitantes únicos y comportamiento', 
            '• Análisis por país con banderas',
            '• Posts del sitio web y engagement'
        ]
    }
}

# Filtrar plataformas disponibles
# Google Analytics siempre está disponible para todos los proyectos
available_platforms = {k: v for k, v in all_platforms.items() if k in available_networks or k == 'google_analytics'}

if available_platforms:
    # Mostrar plataformas disponibles
    if len(available_platforms) == 1:
        # Una sola columna si solo hay una plataforma
        cols = [st.container()]
    elif len(available_platforms) <= 2:
        # Dos columnas si hay 2 plataformas o menos
        cols = st.columns(2)
    elif len(available_platforms) <= 4:
        # Dos filas de dos columnas si hay 3-4 plataformas
        cols = st.columns(2)
    else:
        # Más columnas si hay más plataformas
        cols = st.columns(min(len(available_platforms), 3))
    
    # Mostrar las plataformas disponibles
    for i, (platform_key, platform_info) in enumerate(available_platforms.items()):
        col_index = i % len(cols)
        
        with cols[col_index]:
            network_info = available_networks.get(platform_key, {})
            extra_info = ""
            
            # Información adicional específica de la red
            if platform_key == 'instagram':
                extra_info = f"@{network_info.get('handle', '')}"
            elif platform_key == 'linkedin':
                extra_info = network_info.get('company_name', '')
            elif platform_key == 'facebook':
                extra_info = network_info.get('page_name', '')
            elif platform_key == 'youtube':
                extra_info = network_info.get('channel_name', '')
            
            st.markdown(f"""
            <div class="platform-card" style="border-left-color: {platform_info['color']};">
                <h3 style="color: {platform_info['color']}; margin-bottom: 15px;">{platform_info['icon']} {platform_info['name']}</h3>
                <p style="color: #666; margin-bottom: 15px;">
                    {'<br>'.join(platform_info['description'])}
                </p>
                <p style="color: {platform_info['color']}; font-weight: bold; margin: 0;">✅ Disponible {extra_info}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Nueva fila cada 2 plataformas si hay más de 2
        if len(available_platforms) > 2 and i == 1:
            cols = st.columns(2)
else:
    st.warning("""
    ⚠️ **No hay redes sociales disponibles para este proyecto**
    
    Por favor:
    1. Verifica que las redes estén conectadas en Metricool
    2. Selecciona un proyecto diferente
    3. Contacta al administrador para configurar las redes sociales
    """)

# Instrucciones de navegación
st.markdown("---")

st.markdown("""
## 📋 Cómo Usar el Dashboard

1. **🔍 Explora las páginas:** Utiliza la barra lateral izquierda para navegar entre Instagram, LinkedIn, Facebook, YouTube y Google Analytics
2. **📅 Configura fechas:** Cada página tiene controles de fecha independientes en el sidebar
3. **📊 Interactúa con gráficos:** Haz clic en las leyendas para filtrar datos
4. **📱 Responsive:** El dashboard se adapta a tu pantalla automáticamente
5. **🔄 Datos en tiempo real:** La información se actualiza automáticamente

### 🎯 Características Principales:
- ✅ **Métricas en tiempo real** desde la API de Metricool
- ✅ **Gráficos interactivos** con Plotly
- ✅ **Análisis demográfico** detallado
- ✅ **Exportación de datos** en tablas
- ✅ **Diseño profesional** y responsive
- ✅ **Navegación intuitiva** entre plataformas
""")

# Información técnica
with st.expander("🔧 Información Técnica"):
    st.markdown("""
    **Tecnologías utilizadas:**
    - **Streamlit** - Framework de la aplicación
    - **Plotly** - Gráficos interactivos
    - **Pandas** - Procesamiento de datos
    - **Metricool API** - Fuente de datos
    - **Python** - Lenguaje de programación
    
    **Actualización de datos:**
    - Los datos se cachean por 30 minutos para optimizar rendimiento
    - Cambios en fechas refrescan automáticamente los datos
    - Conexión directa con la API de Metricool
    
    **Desarrollado por:** Jungle Creative Agency para Widu Legal
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 30px; border-radius: 15px; margin-top: 40px;'>
    <div style='text-align: center;'>
        <h3 style='color: #333; margin-bottom: 20px;'>📊 Dashboard Powered by</h3>
        <div style='display: flex; justify-content: center; align-items: center; gap: 40px; flex-wrap: wrap;'>
            <div style='text-align: center;'>
                <img src='https://junglecreativeagency.com/wp-content/uploads/2024/02/logo-footer.png' width='100' style='margin-bottom: 10px;'>
                <p style='font-weight: bold; color: #F8E964; margin: 5px 0;'>Jungle Creative Agency</p>
                <p style='font-size: 12px; color: #666; margin: 0;'>Digital Marketing & Analytics</p>
            </div>
            <div style='text-align: center; color: #999; font-size: 24px;'>
                →
            </div>
            <div style='text-align: center;'>
                <img src='https://widulegal.com/hubfs/raw_assets/public/widu-theme-v1/modules/global/logo.png' width='100' style='margin-bottom: 10px;'>
                <p style='font-weight: bold; color: #000000; margin: 5px 0;'>Widu Legal</p>
                <p style='font-size: 12px; color: #666; margin: 0;'>Cliente</p>
            </div>
        </div>
        <p style='text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; font-size: 14px;'>
            🚀 Dashboard de Analytics • Generado automáticamente • Powered by Metricool API
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
