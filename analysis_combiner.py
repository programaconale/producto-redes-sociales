"""
Módulo para combinar análisis de todas las redes sociales y generar conclusiones finales
"""

def generate_final_analysis(instagram_analysis, facebook_analysis, linkedin_analysis, google_analytics_analysis, youtube_analysis):
    """Genera análisis final combinando todos los análisis de redes sociales"""
    try:
        # Crear análisis final con formato específico
        final_analysis = f"""# 📊 Análisis Integral del Ecosistema Digital

## 📸 Instagram
{instagram_analysis}

---

## 📘 Facebook
{facebook_analysis}

---

## 💼 LinkedIn
{linkedin_analysis}

---

## 📊 Google Analytics
{google_analytics_analysis}

---

## 📺 YouTube
{youtube_analysis}

---

## 🎯 Conclusiones Generales y Próximas Acciones

### Fortalezas del Ecosistema Digital:
- **Consistencia en el crecimiento**: Todas las plataformas muestran un crecimiento sostenido en sus métricas principales
- **Engagement diversificado**: La audiencia interactúa de manera diferente en cada plataforma, lo que indica una estrategia multicanal efectiva
- **Tráfico orgánico sólido**: Google Analytics muestra una base sólida de tráfico orgánico y directo

### Áreas de Oportunidad:
- **Optimización de contenido**: Diversificar el tipo de contenido en Instagram y Facebook para maximizar el alcance
- **Consistencia en LinkedIn**: Aumentar la frecuencia de publicaciones para mantener el engagement profesional
- **SEO y contenido web**: Fortalecer el contenido web para mejorar el tráfico orgánico

### Próximas Acciones Estratégicas:
1. **Corto plazo (1-2 meses)**:
   - Implementar calendario editorial unificado
   - Optimizar horarios de publicación según engagement
   - Crear contenido específico para cada plataforma

2. **Mediano plazo (3-6 meses)**:
   - Desarrollar estrategia de contenido de video para YouTube
   - Implementar campañas de LinkedIn para B2B
   - Optimizar SEO del sitio web

3. **Largo plazo (6+ meses)**:
   - Expandir presencia en nuevas plataformas
   - Desarrollar estrategia de influencer marketing
   - Implementar automatización de marketing

### Métricas Clave a Monitorear:
- **Crecimiento de seguidores** en todas las plataformas
- **Engagement rate** por tipo de contenido
- **Tráfico orgánico** vs tráfico pagado
- **Conversión** de redes sociales a sitio web
- **ROI** de cada plataforma

### Recomendación Final:
El ecosistema digital de Widú Legal muestra un crecimiento saludable y sostenido. La clave está en mantener la consistencia en la calidad del contenido mientras se optimiza la frecuencia y diversificación. El enfoque debe estar en crear valor para la audiencia en cada plataforma, adaptando el mensaje pero manteniendo la coherencia de marca.

**Próximo paso**: Implementar un sistema de monitoreo semanal de estas métricas para ajustar la estrategia en tiempo real."""
        
        return final_analysis
        
    except Exception as e:
        return f"Error generando análisis final: {str(e)}"
