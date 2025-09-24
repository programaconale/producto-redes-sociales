import streamlit as st
import requests
import json
from datetime import datetime, date
import sys
import os

# Agregar el directorio padre al path para importar mcp
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from mcp import MetricoolAPIClient
from project_manager import create_client_for_current_project

class PageDataCapturer:
    def __init__(self):
        self.client = None
        self.current_project = None
        
    def setup_client(self):
        """Configura el cliente para el proyecto actual"""
        self.current_project = st.session_state.get('current_project')
        if not self.current_project:
            return False
        
        self.client = create_client_for_current_project()
        return True
    
    def get_last_month_dates(self):
        """Obtiene las fechas del último mes completo"""
        today = date.today()
        
        # Si estamos en septiembre, el último mes completo es agosto
        if today.month == 1:
            # Si estamos en enero, el último mes es diciembre del año anterior
            last_month = 12
            year = today.year - 1
        else:
            last_month = today.month - 1
            year = today.year
        
        # Primer día del último mes
        from_date = date(year, last_month, 1)
        
        # Último día del último mes
        if last_month == 12:
            to_date = date(year + 1, 1, 1) - date.resolution
        else:
            to_date = date(year, last_month + 1, 1) - date.resolution
        
        return from_date, to_date
    
    def capture_instagram_data(self):
        """Captura todos los datos de la página de Instagram"""
        if not self.setup_client():
            return None
        
        from_date, to_date = self.get_last_month_dates()
        
        try:
            # Importar funciones de Instagram
            sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))
            from pages.instagram_data_capturer import InstagramDataCapturer
            
            capturer = InstagramDataCapturer(self.client)
            return capturer.capture_all_data(from_date, to_date)
            
        except Exception as e:
            st.error(f"Error capturando datos de Instagram: {str(e)}")
            return None
    
    def capture_linkedin_data(self):
        """Captura todos los datos de la página de LinkedIn"""
        if not self.setup_client():
            return None
        
        from_date, to_date = self.get_last_month_dates()
        
        try:
            # Importar funciones de LinkedIn
            sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))
            from pages.linkedin_data_capturer import LinkedInDataCapturer
            
            capturer = LinkedInDataCapturer(self.client)
            return capturer.capture_all_data(from_date, to_date)
            
        except Exception as e:
            st.error(f"Error capturando datos de LinkedIn: {str(e)}")
            return None
    
    def capture_facebook_data(self):
        """Captura todos los datos de la página de Facebook"""
        if not self.setup_client():
            return None
        
        from_date, to_date = self.get_last_month_dates()
        
        try:
            # Importar funciones de Facebook
            sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))
            from pages.facebook_data_capturer import FacebookDataCapturer
            
            capturer = FacebookDataCapturer(self.client)
            return capturer.capture_all_data(from_date, to_date)
            
        except Exception as e:
            st.error(f"Error capturando datos de Facebook: {str(e)}")
            return None
    
    def capture_youtube_data(self):
        """Captura todos los datos de la página de YouTube"""
        if not self.setup_client():
            return None
        
        from_date, to_date = self.get_last_month_dates()
        
        try:
            # Importar funciones de YouTube
            sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))
            from pages.youtube_data_capturer import YouTubeDataCapturer
            
            capturer = YouTubeDataCapturer(self.client)
            return capturer.capture_all_data(from_date, to_date)
            
        except Exception as e:
            st.error(f"Error capturando datos de YouTube: {str(e)}")
            return None
    
    def capture_all_networks_data(self, available_networks):
        """Captura datos de todas las redes sociales disponibles"""
        all_data = {}
        
        # Progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_networks = len([k for k, v in available_networks.items() if v.get('available', False) and v.get('has_data', False)])
        current_network = 0
        
        for network_key, network_info in available_networks.items():
            if not network_info.get('available', False) or not network_info.get('has_data', False):
                continue
            
            current_network += 1
            status_text.text(f"🔄 Capturando datos de {network_info.get('name', network_key)}...")
            progress_bar.progress(current_network / total_networks)
            
            if network_key == 'instagram':
                all_data[network_key] = self.capture_instagram_data()
            elif network_key == 'linkedin':
                all_data[network_key] = self.capture_linkedin_data()
            elif network_key == 'facebook':
                all_data[network_key] = self.capture_facebook_data()
            elif network_key == 'youtube':
                all_data[network_key] = self.capture_youtube_data()
        
        status_text.text("✅ Captura de datos completada")
        progress_bar.progress(1.0)
        
        return all_data

def create_advanced_report_button(project_name, available_networks):
    """Crea el botón para generar reporte completo con todos los datos"""
    st.sidebar.markdown("---")
    
    if st.sidebar.button("📄 Generar Reporte Completo", type="primary", use_container_width=True):
        with st.spinner("🔄 Generando reporte avanzado..."):
            try:
                # Crear capturador de datos
                capturer = PageDataCapturer()
                
                # Capturar datos de todas las redes
                all_network_data = capturer.capture_all_networks_data(available_networks)
                
                # Generar reporte HTML avanzado
                from pdf_generator import AdvancedHTMLReportGenerator
                generator = AdvancedHTMLReportGenerator()
                
                html_content = generator.generate_advanced_report(
                    project_name, 
                    available_networks, 
                    all_network_data
                )
                
                # Mostrar resultado
                st.sidebar.success("✅ Reporte avanzado generado!")
                
                # Mostrar el reporte
                st.markdown("### 📊 Reporte Avanzado Generado")
                st.markdown("---")
                
                # Botón de descarga
                st.download_button(
                    label="📥 Descargar Reporte Avanzado",
                    data=html_content,
                    file_name=f"reporte_avanzado_{project_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    type="primary",
                    use_container_width=True
                )
                
                # Vista previa
                st.markdown("### 👀 Vista Previa del Reporte Avanzado")
                st.components.v1.html(html_content, height=800, scrolling=True)
                
            except Exception as e:
                st.sidebar.error(f"❌ Error generando reporte avanzado: {str(e)}")
                st.error(f"Error generando reporte avanzado: {str(e)}")
