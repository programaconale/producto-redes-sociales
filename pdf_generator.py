import streamlit as st
import io
import base64
import requests
from datetime import datetime
import json

class HTMLReportGenerator:
    def __init__(self):
        pass
    
    def get_metric_description(self, metric_name):
        """Retorna una descripción para cada métrica"""
        descriptions = {
            'followers': 'Total de seguidores en la cuenta',
            'total_followers': 'Total de seguidores en la cuenta',
            'gained_followers': 'Nuevos seguidores ganados',
            'lost_followers': 'Seguidores perdidos',
            'net_delta': 'Crecimiento neto de seguidores',
            'impressions': 'Total de impresiones del contenido',
            'engagement': 'Tasa de engagement general',
            'likes': 'Total de likes recibidos',
            'comments': 'Total de comentarios',
            'shares': 'Total de compartidos',
            'views': 'Total de visualizaciones',
            'reach': 'Alcance total del contenido'
        }
        return descriptions.get(metric_name, 'Métrica de rendimiento')
    
    def generate_html_report(self, project_name, available_networks, network_data_dict):
        """Genera un reporte HTML completo"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte Analítico Digital - {project_name}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .project-info {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-bottom: 1px solid #dee2e6;
                }}
                .networks-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .networks-table th, .networks-table td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                .networks-table th {{
                    background-color: #2E86AB;
                    color: white;
                    font-weight: bold;
                }}
                .network-section {{
                    padding: 30px;
                    border-bottom: 2px solid #e9ecef;
                }}
                .network-title {{
                    color: #A23B72;
                    font-size: 1.8em;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #A23B72;
                }}
                .metrics-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .metrics-table th, .metrics-table td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                .metrics-table th {{
                    background-color: #A23B72;
                    color: white;
                    font-weight: bold;
                }}
                .metrics-table tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                .ai-analysis {{
                    background: #e3f2fd;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #2196f3;
                }}
                .ai-analysis h3 {{
                    color: #1976d2;
                    margin-top: 0;
                }}
                .footer {{
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .metric-value {{
                    font-weight: bold;
                    color: #2E86AB;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 REPORTE ANALÍTICO DIGITAL</h1>
                    <p>Análisis completo de redes sociales con IA</p>
                </div>
                
                <div class="project-info">
                    <h2>🏢 Información del Proyecto</h2>
                    <p><strong>Proyecto:</strong> {project_name}</p>
                    <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Generado por:</strong> Jungle Creative Agency</p>
                </div>
                
                <div class="project-info">
                    <h2>📱 Redes Sociales Incluidas</h2>
                    <table class="networks-table">
                        <thead>
                            <tr>
                                <th>Red Social</th>
                                <th>Estado</th>
                                <th>Datos Disponibles</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Agregar información de redes sociales
        for network_key, network_info in available_networks.items():
            status = "✅ Incluida" if network_info.get('available', False) else "❌ No disponible"
            has_data = network_info.get('has_data', False)
            data_status = "✅ Disponible" if has_data else "⚠️ Sin datos"
            html_content += f"""
                                <tr>
                                    <td>{network_info.get('icon', '📱')} {network_info.get('name', network_key.title())}</td>
                                    <td>{status}</td>
                                    <td>{data_status}</td>
                                </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
        """
        
        # Agregar secciones de cada red social
        for network_key, network_info in available_networks.items():
            if network_info.get('available', False) and network_key in network_data_dict:
                network_data = network_data_dict[network_key]
                html_content += f"""
                <div class="network-section">
                    <h2 class="network-title">{network_info.get('icon', '📱')} {network_info.get('name', network_key.title()).upper()}</h2>
                """
                
                # Métricas principales
                if 'metrics' in network_data and network_data['metrics']:
                    html_content += """
                    <h3>📈 Métricas Principales</h3>
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Métrica</th>
                                <th>Valor</th>
                                <th>Descripción</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    
                    for metric_name, metric_value in network_data['metrics'].items():
                        html_content += f"""
                            <tr>
                                <td>{metric_name.replace('_', ' ').title()}</td>
                                <td class="metric-value">{metric_value:,}</td>
                                <td>{self.get_metric_description(metric_name)}</td>
                            </tr>
                        """
                    
                    html_content += """
                        </tbody>
                    </table>
                    """
                
                # Análisis de IA
                if 'ai_analysis' in network_data and network_data['ai_analysis']:
                    html_content += f"""
                    <div class="ai-analysis">
                        <h3>🤖 Análisis Estratégico con IA</h3>
                        <div style="white-space: pre-line;">{network_data['ai_analysis']}</div>
                    </div>
                    """
                
                # Posts destacados
                if 'top_posts' in network_data and network_data['top_posts']:
                    html_content += """
                    <h3>⭐ Contenido Destacado</h3>
                    <ul>
                    """
                    for i, post in enumerate(network_data['top_posts'][:3], 1):
                        title = post.get('title', 'Sin título')
                        engagement = post.get('engagement', 'N/A')
                        html_content += f"<li><strong>Post #{i}:</strong> {title} (Engagement: {engagement})</li>"
                    html_content += "</ul>"
                
                html_content += "</div>"
        
        # Footer
        html_content += """
                <div class="footer">
                    <p>📊 Reporte generado automáticamente con análisis de datos avanzado e inteligencia artificial</p>
                    <p>🏢 Jungle Creative Agency - Análisis de redes sociales profesionales</p>
                    <p>📅 Generado el """ + datetime.now().strftime('%d/%m/%Y a las %H:%M') + """</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

class AdvancedHTMLReportGenerator:
    def __init__(self):
        pass
    
    def get_metric_description(self, metric_name):
        """Retorna una descripción para cada métrica"""
        descriptions = {
            'followers': 'Total de seguidores en la cuenta',
            'total_followers': 'Total de seguidores en la cuenta',
            'gained_followers': 'Nuevos seguidores ganados',
            'lost_followers': 'Seguidores perdidos',
            'net_delta': 'Crecimiento neto de seguidores',
            'impressions': 'Total de impresiones del contenido',
            'engagement': 'Tasa de engagement general',
            'likes': 'Total de likes recibidos',
            'comments': 'Total de comentarios',
            'shares': 'Total de compartidos',
            'views': 'Total de visualizaciones',
            'reach': 'Alcance total del contenido',
            'engagement_rate': 'Tasa de engagement calculada',
            'total_posts': 'Total de posts publicados'
        }
        return descriptions.get(metric_name, 'Métrica de rendimiento')
    
    def chart_to_html(self, chart_fig):
        """Convierte un gráfico de Plotly a HTML"""
        if chart_fig is None:
            return "<p>No hay datos disponibles para este gráfico</p>"
        
        try:
            return chart_fig.to_html(include_plotlyjs=False, div_id="chart")
        except:
            return "<p>Error generando gráfico</p>"
    
    def generate_ai_analysis(self, network_name, metrics, posts_data):
        """Genera análisis de IA para una red social usando OpenAI"""
        try:
            import openai
            import os
            
            # Configurar OpenAI
            openai.api_key = os.getenv('OPENAI_API_KEY', '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')
            
            # Preparar datos para el análisis
            metrics_summary = {
                'total_followers': metrics.get('total_followers', 0),
                'gained_followers': metrics.get('gained_followers', 0),
                'lost_followers': metrics.get('lost_followers', 0),
                'net_delta': metrics.get('net_delta', 0),
                'engagement_rate': metrics.get('engagement_rate', 0),
                'total_posts': metrics.get('total_posts', 0),
                'total_views': metrics.get('total_views', 0),
                'total_likes': metrics.get('total_likes', 0),
                'total_comments': metrics.get('total_comments', 0),
                'total_shares': metrics.get('total_shares', 0),
                'total_impressions': metrics.get('total_impressions', 0)
            }
            
            # Preparar información de posts destacados
            top_posts_info = ""
            if posts_data and len(posts_data) > 0:
                top_posts = sorted(posts_data, key=lambda x: x.get('likes', 0) + x.get('comments', 0) + x.get('shares', 0), reverse=True)[:3]
                for i, post in enumerate(top_posts, 1):
                    top_posts_info += f"\nPost #{i}: {post.get('title', post.get('caption', 'Sin título'))[:100]}... - Likes: {post.get('likes', 0)}, Comentarios: {post.get('comments', 0)}, Compartidos: {post.get('shares', 0)}"
            
            # Crear prompt para OpenAI
            prompt = f"""
            Actúa como un analista de datos especializado en marketing digital. Analiza los siguientes datos de {network_name.upper()} del último mes:

            MÉTRICAS PRINCIPALES:
            {json.dumps(metrics_summary, indent=2)}

            POSTS DESTACADOS:
            {top_posts_info if top_posts_info else "No hay datos de posts disponibles"}

            Tu tarea es:
            1. Hacer un análisis detallado de las métricas más relevantes
            2. Explicar los puntos positivos: qué está funcionando bien
            3. Señalar los puntos negativos o áreas de mejora
            4. Elaborar un análisis técnico del comportamiento de la audiencia
            5. Dar conclusiones estratégicas y recomendaciones específicas para {network_name.upper()}
            6. Si hay posts destacados, analizar cuáles funcionaron mejor y por qué

            Formato de respuesta:
            **ANÁLISIS ESTRATÉGICO DE {network_name.upper()}**

            **Métricas Clave:**
            [Análisis de las métricas principales]

            **Puntos Positivos:**
            [Qué está funcionando bien]

            **Áreas de Mejora:**
            [Qué necesita mejorar]

            **Análisis Técnico:**
            [Comportamiento de audiencia y datos técnicos]

            **Recomendaciones Estratégicas:**
            [Próximos pasos específicos]

            **Análisis de Contenido:**
            [Si hay posts destacados, analizar cuáles funcionaron mejor]

            Responde en español, sé conciso pero detallado, y enfócate en insights accionables.
            """
            
            # Llamar a OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un analista de marketing digital experto en redes sociales."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback a análisis básico si OpenAI falla
            return f"""
            **Análisis Estratégico de {network_name.upper()}**
            
            **Métricas Clave:**
            - Total de seguidores: {metrics.get('total_followers', 0):,}
            - Crecimiento neto: {metrics.get('net_delta', 0):,} seguidores
            - Tasa de engagement: {metrics.get('engagement_rate', 0):.2f}%
            - Total de posts: {metrics.get('total_posts', 0)}
            
            **Puntos Positivos:**
            - Crecimiento consistente de la audiencia
            - Engagement saludable en el contenido
            - Diversidad en el tipo de contenido publicado
            
            **Áreas de Mejora:**
            - Optimizar horarios de publicación
            - Incrementar interacción con la audiencia
            - Diversificar formatos de contenido
            
            **Recomendaciones Estratégicas:**
            - Mantener consistencia en la frecuencia de publicación
            - Analizar posts de mayor engagement para replicar estrategias
            - Implementar campañas de engagement para fidelizar audiencia
            
            *Nota: Análisis básico generado (OpenAI no disponible)*
            """
    
    def generate_advanced_report(self, project_name, available_networks, all_network_data):
        """Genera reporte HTML avanzado con todos los datos y gráficos"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte Analítico Avanzado - {project_name}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: bold;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.2em;
                    opacity: 0.9;
                }}
                .project-info {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-bottom: 1px solid #dee2e6;
                }}
                .network-section {{
                    padding: 30px;
                    border-bottom: 2px solid #e9ecef;
                }}
                .network-title {{
                    color: #A23B72;
                    font-size: 1.8em;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #A23B72;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #2E86AB;
                }}
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #2E86AB;
                    margin: 0;
                }}
                .metric-label {{
                    color: #666;
                    font-size: 0.9em;
                    margin: 5px 0 0 0;
                }}
                .chart-container {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }}
                .chart-title {{
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: #2E86AB;
                }}
                .ai-analysis {{
                    background: #e3f2fd;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #2196f3;
                }}
                .ai-analysis h3 {{
                    color: #1976d2;
                    margin-top: 0;
                }}
                .posts-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .posts-table th, .posts-table td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }}
                .posts-table th {{
                    background-color: #A23B72;
                    color: white;
                    font-weight: bold;
                }}
                .posts-table tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                .footer {{
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 REPORTE ANALÍTICO AVANZADO</h1>
                    <p>Análisis completo con gráficos y datos del último mes</p>
                </div>
                
                <div class="project-info">
                    <h2>🏢 Información del Proyecto</h2>
                    <p><strong>Proyecto:</strong> {project_name}</p>
                    <p><strong>Período de análisis:</strong> Último mes completo</p>
                    <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Generado por:</strong> Jungle Creative Agency</p>
                </div>
        """
        
        # Agregar secciones de cada red social
        for network_key, network_info in available_networks.items():
            if network_info.get('available', False) and network_info.get('has_data', False) and network_key in all_network_data:
                network_data = all_network_data[network_key]
                html_content += f"""
                <div class="network-section">
                    <h2 class="network-title">{network_info.get('icon', '📱')} {network_info.get('name', network_key.title()).upper()}</h2>
                """
                
                # Métricas principales
                if 'metrics' in network_data and network_data['metrics']:
                    html_content += """
                    <div class="metrics-grid">
                    """
                    
                    for metric_name, metric_value in network_data['metrics'].items():
                        html_content += f"""
                        <div class="metric-card">
                            <div class="metric-value">{metric_value:,}</div>
                            <div class="metric-label">{metric_name.replace('_', ' ').title()}</div>
                        </div>
                        """
                    
                    html_content += "</div>"
                
                # Gráficos
                if 'charts' in network_data:
                    charts = network_data['charts']
                    
                    if charts.get('followers_chart'):
                        html_content += f"""
                        <div class="chart-container">
                            <div class="chart-title">📈 Evolución de Seguidores</div>
                            {self.chart_to_html(charts['followers_chart'])}
                        </div>
                        """
                    
                    if charts.get('delta_chart'):
                        html_content += f"""
                        <div class="chart-container">
                            <div class="chart-title">📊 Ganados vs Perdidos</div>
                            {self.chart_to_html(charts['delta_chart'])}
                        </div>
                        """
                    
                    if charts.get('age_chart'):
                        html_content += f"""
                        <div class="chart-container">
                            <div class="chart-title">👥 Distribución por Edad</div>
                            {self.chart_to_html(charts['age_chart'])}
                        </div>
                        """
                    
                    if charts.get('gender_chart'):
                        html_content += f"""
                        <div class="chart-container">
                            <div class="chart-title">⚥ Distribución por Género</div>
                            {self.chart_to_html(charts['gender_chart'])}
                        </div>
                        """
                    
                    if charts.get('country_chart'):
                        html_content += f"""
                        <div class="chart-container">
                            <div class="chart-title">🌍 Top 10 Países</div>
                            {self.chart_to_html(charts['country_chart'])}
                        </div>
                        """
                
                # Análisis de IA
                ai_analysis = self.generate_ai_analysis(
                    network_info.get('name', network_key.title()),
                    network_data.get('metrics', {}),
                    network_data.get('posts', [])
                )
                
                html_content += f"""
                <div class="ai-analysis">
                    <h3>🤖 Análisis Estratégico con IA</h3>
                    <div style="white-space: pre-line;">{ai_analysis}</div>
                </div>
                """
                
                # Tabla de posts destacados
                if 'posts_table' in network_data and network_data['posts_table']:
                    html_content += """
                    <h3>⭐ Posts Destacados</h3>
                    <table class="posts-table">
                        <thead>
                            <tr>
                                <th>Imagen</th>
                                <th>Descripción</th>
                                <th>Likes</th>
                                <th>Comentarios</th>
                                <th>Compartidos</th>
                                <th>Alcance</th>
                                <th>Engagement</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                    
                    for post in network_data['posts_table'][:5]:  # Top 5 posts
                        html_content += f"""
                        <tr>
                            <td><img src="{post.get('image', '')}" width="50" height="50" style="border-radius: 5px;"></td>
                            <td>{post.get('caption', 'Sin descripción')}</td>
                            <td>{post.get('likes', 0):,}</td>
                            <td>{post.get('comments', 0):,}</td>
                            <td>{post.get('shares', 0):,}</td>
                            <td>{post.get('reach', 0):,}</td>
                            <td>{post.get('engagement', 0):.2f}%</td>
                        </tr>
                        """
                    
                    html_content += """
                        </tbody>
                    </table>
                    """
                
                html_content += "</div>"
        
        # Footer
        html_content += """
                <div class="footer">
                    <p>📊 Reporte generado automáticamente con análisis de datos avanzado e inteligencia artificial</p>
                    <p>🏢 Jungle Creative Agency - Análisis de redes sociales profesionales</p>
                    <p>📅 Generado el """ + datetime.now().strftime('%d/%m/%Y a las %H:%M') + """</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

def create_pdf_button(project_name, available_networks, network_data_dict):
    """Crea el botón para generar reporte HTML en el sidebar"""
    st.sidebar.markdown("---")
    
    if st.sidebar.button("📄 Generar Reporte Completo", type="primary", use_container_width=True):
        with st.spinner("🔄 Generando reporte..."):
            try:
                html_generator = HTMLReportGenerator()
                html_content = html_generator.generate_html_report(project_name, available_networks, network_data_dict)
                
                # Crear botón de descarga
                st.sidebar.success("✅ Reporte generado exitosamente!")
                
                # Mostrar el reporte HTML en el área principal
                st.markdown("### 📊 Reporte Generado")
                st.markdown("---")
                
                # Mostrar botón de descarga
                st.download_button(
                    label="📥 Descargar Reporte HTML",
                    data=html_content,
                    file_name=f"reporte_analitico_{project_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    type="primary",
                    use_container_width=True
                )
                
                # Mostrar preview del reporte
                st.markdown("### 👀 Vista Previa del Reporte")
                st.components.v1.html(html_content, height=600, scrolling=True)
                
            except Exception as e:
                st.sidebar.error(f"❌ Error generando reporte: {str(e)}")
                st.error(f"Error generando reporte: {str(e)}")

def collect_network_data():
    """Recolecta datos de todas las redes sociales disponibles"""
    network_data = {}
    
    # Obtener datos de Instagram si está disponible
    if 'instagram_metrics' in st.session_state:
        network_data['instagram'] = {
            'metrics': st.session_state['instagram_metrics'],
            'ai_analysis': st.session_state.get('instagram_ai_analysis', 'Análisis no disponible'),
            'top_posts': st.session_state.get('instagram_top_posts', [])
        }
    
    # Obtener datos de LinkedIn si está disponible
    if 'linkedin_metrics' in st.session_state:
        network_data['linkedin'] = {
            'metrics': st.session_state['linkedin_metrics'],
            'ai_analysis': st.session_state.get('linkedin_ai_analysis', 'Análisis no disponible'),
            'top_posts': st.session_state.get('linkedin_top_posts', [])
        }
    
    # Obtener datos de Facebook si está disponible
    if 'facebook_metrics' in st.session_state:
        network_data['facebook'] = {
            'metrics': st.session_state['facebook_metrics'],
            'ai_analysis': st.session_state.get('facebook_ai_analysis', 'Análisis no disponible'),
            'top_posts': st.session_state.get('facebook_top_posts', [])
        }
    
    # Obtener datos de YouTube si está disponible
    if 'youtube_metrics' in st.session_state:
        network_data['youtube'] = {
            'metrics': st.session_state['youtube_metrics'],
            'ai_analysis': st.session_state.get('youtube_ai_analysis', 'Análisis no disponible'),
            'top_posts': st.session_state.get('youtube_top_posts', [])
        }
    
    return network_data
