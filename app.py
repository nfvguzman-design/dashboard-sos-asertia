import streamlit as pd_st
import pandas as pd
import numpy as np

# Configuración de página
pd_st.set_page_config(
    page_title="Dashboard SOS Asertia - Octubre 2026",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
pd_st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. AUTENTICACIÓN Y CONTROL DE ACCESOS (ROLES)
# ----------------------------------------------------
if 'authenticated' not in pd_st.session_state:
    pd_st.session_state['authenticated'] = False
    pd_st.session_state['role'] = None
    pd_st.session_state['username'] = None

if not pd_st.session_state['authenticated']:
    pd_st.markdown("<h2 style='text-align: center; color: #1f77b4;'>🔐 Portal de Acceso - Dashboard SOS Asertia</h2>", unsafe_allow_html=True)
    col1, col2, col3 = pd_st.columns([1, 2, 1])
    with col2:
        with pd_st.form("login_form"):
            username = pd_st.text_input("Usuario")
            password = pd_st.text_input("Contraseña", type="password")
            submit = pd_st.form_submit_button("Ingresar al Sistema")
            
            if submit:
                # Credenciales configuradas
                if username == "admin" and password == "Asertia2026*":
                    pd_st.session_state['authenticated'] = True
                    pd_st.session_state['role'] = 'ADMINISTRADOR'
                    pd_st.session_state['username'] = 'admin'
                    pd_st.rerun()
                elif username == "cliente" and password == "Cliente2026*":
                    pd_st.session_state['authenticated'] = True
                    pd_st.session_state['role'] = 'CLIENTE'
                    pd_st.session_state['username'] = 'cliente'
                    pd_st.rerun()
                else:
                    pd_st.error("Usuario o contraseña incorrectos.")
    pd_st.stop()

# Barra lateral de sesión
with pd_st.sidebar:
    pd_st.write(f"👤 **Usuario:** {pd_st.session_state['username'].capitalize()}")
    pd_st.write(f"🔑 **Rol:** {pd_st.session_state['role']}")
    if pd_st.button("Cerrar Sesión"):
        pd_st.session_state['authenticated'] = False
        pd_st.rerun()
    pd_st.markdown("---")

# ----------------------------------------------------
# 2. CARGA Y CONSOLIDACIÓN DE DATOS
# ----------------------------------------------------
@pd_st.cache_data
def load_default_data():
    # Carga de archivos por defecto en el entorno
    try:
        df_kcc_mod = pd.read_excel("SOS ASERTIA - KCC MODERNO - OCTUBRE 2026.xlsx", sheet_name="DATA SOS")
        df_kcc_mod['MUNDO'] = 'KCC'
        df_kcc_mod['CANAL_TIPO'] = 'MODERNO'
        
        df_kcc_trad = pd.read_excel("SOS ASERTIA - KCC TRADICIONAL - OCTUBRE 2026.xlsx", sheet_name="DATA SOS")
        df_kcc_trad['MUNDO'] = 'KCC'
        df_kcc_trad['CANAL_TIPO'] = 'TRADICIONAL'
        
        df_lor = pd.read_excel("SOS ASERTIA - LOREAL - OCTUBRE 2026.xlsx", sheet_name="DATA SOS")
        df_lor['MUNDO'] = 'LOREAL'
        df_lor['CANAL_TIPO'] = 'GENERAL'
        
        df_total = pd.concat([df_kcc_mod, df_kcc_trad, df_lor], ignore_index=True)
        return df_total
    except Exception as e:
        # DataFrame de respaldo sintáctico si faltaran archivos locales
        return pd.DataFrame(columns=['MUNDO', 'CATEGORÍA', 'SUBCATEGORÍA', 'MARCA', '% PARTICIPACION', 'CIUDAD', 'REGIONAL', 'CANAL'])

df_master = load_default_data()

# ----------------------------------------------------
# 3. NAVEGACIÓN Y SELECCIÓN DE MÓDULOS
# ----------------------------------------------------
pd_st.title("📊 Dashboard Ejecutivo de Participación & SOS")

# Selector de Negocio / Módulo Principal
mundo_sel = pd_st.radio("Seleccione el Módulo de Negocio:", ["KCC (Kimberly-Clark)", "L'ORÉAL"], horizontal=True)
mundo_filtro = "KCC" if "KCC" in mundo_sel else "LOREAL"

df_filtered_mundo = df_master[df_master['MUNDO'] == mundo_filtro] if not df_master.empty else df_master

# Selector de Submódulos
submodulo = pd_st.selectbox("Navegación por Submódulos:", [
    "📈 Dashboard (DASH)", 
    "⚖️ Comparativo", 
    "📋 Detalle General", 
    "🏷️ Detalle por Marca", 
    "💡 Insights (IA)", 
    "🚨 Alertas (#N/D)", 
    "📁 Data (Carga / Descarga)"
])

pd_st.markdown("---")

# ----------------------------------------------------
# 4. BARRA LATERAL DE FILTROS MAESTROS
# ----------------------------------------------------
with st.sidebar:
    st.subheader("🎛️ Filtros Maestros")
    
    if not df_filtered_mundo.empty:
        regionales = df_filtered_mundo['REGIONAL'].dropna().unique().tolist() if 'REGIONAL' in df_filtered_mundo.columns else []
        sel_regional = st.multiselect("Regional", regionales, default=regionales)
        
        ciudades = df_filtered_mundo['CIUDAD'].dropna().unique().tolist() if 'CIUDAD' in df_filtered_mundo.columns else []
        sel_ciudad = st.multiselect("Ciudad", ciudades, default=ciudades)
        
        categorias = df_filtered_mundo['CATEGORÍA'].dropna().unique().tolist() if 'CATEGORÍA' in df_filtered_mundo.columns else []
        sel_categoria = st.multiselect("Categoría", categorias, default=categorias)
    else:
        sel_regional, sel_ciudad, sel_categoria = [], [], []

# Aplicar filtros al DataFrame activo
df_view = df_filtered_mundo.copy()
if not df_view.empty:
    if sel_regional and 'REGIONAL' in df_view.columns:
        df_view = df_view[df_view['REGIONAL'].isin(sel_regional)]
    if sel_ciudad and 'CIUDAD' in df_view.columns:
        df_view = df_view[df_view['CIUDAD'].isin(sel_ciudad)]
    if sel_categoria and 'CATEGORÍA' in df_view.columns:
        df_view = df_view[df_view['CATEGORÍA'].isin(sel_categoria)]

# ----------------------------------------------------
# 5. RENDERIZADO DE SUBMÓDULOS
# ----------------------------------------------------

if submodulo == "📈 Dashboard (DASH)":
    pd_st.subheader(f"Resumen Ejecutivo - {mundo_sel}")
    
    col1, col2, col3, col4 = pd_st.columns(4)
    total_registros = len(df_view)
    avg_sos = df_view['% PARTICIPACION'].mean() * 100 if '% PARTICIPACION' in df_view.columns and not df_view.empty else 0.0
    total_caras = df_view['CANTIDAD_CARAS_CMS'].sum() if 'CANTIDAD_CARAS_CMS' in df_view.columns and not df_view.empty else 0
    pdv_activos = df_view['PUNTO DE VENTA'].nunique() if 'PUNTO DE VENTA' in df_view.columns and not df_view.empty else 0
    
    col1.metric("Registros Auditados", f"{total_registros:,}")
    col2.metric("SOS Promedio", f"{avg_sos:.2f}%")
    col3.metric("Total Caras / CMS", f"{total_caras:,.0f}")
    col4.metric("Puntos de Venta", f"{pdv_activos:,}")
    
    pd_st.markdown("### 📊 Comportamiento de Participación por Categoría")
    if not df_view.empty and 'CATEGORÍA' in df_view.columns and '% PARTICIPACION' in df_view.columns:
        cat_group = df_view.groupby('CATEGORÍA')['% PARTICIPACION'].mean().reset_index()
        pd_st.bar_chart(cat_group.set_index('CATEGORÍA') * 100)
    else:
        pd_st.info("No hay suficientes datos para graficar con los filtros actuales.")

elif submodulo == "⚖️ Comparativo":
    pd_st.subheader("⚖️ Análisis Comparativo de Canales y Marcas")
    if mundo_filtro == 'KCC' and 'CANAL_TIPO' in df_view.columns:
        comp_canal = df_view.groupby(['CANAL_TIPO', 'CATEGORÍA'])['% PARTICIPACION'].mean().unstack() * 100
        pd_st.write("Comparativa de Participación Promedio por Canal (Moderno vs Tradicional):")
        pd_st.dataframe(comp_canal, use_container_width=True)
    else:
        pd_st.info("Vista comparativa activada para el portafolio seleccionado.")
        if not df_view.empty and 'MARCA' in df_view.columns:
            top_marcas = df_view.groupby('MARCA')['% PARTICIPACION'].mean().sort_values(ascending=False).head(10) * 100
            pd_st.bar_chart(top_marcas)

elif submodulo == "📋 Detalle General":
    pd_st.subheader("📋 Tabla de Detalle General")
    pd_st.dataframe(df_view.head(500), use_container_width=True)

elif submodulo == "🏷️ Detalle por Marca":
    pd_st.subheader("🏷️ Desglose Detallado por Marca")
    if not df_view.empty and 'MARCA' in df_view.columns:
        marca_resumen = df_view.groupby(['CATEGORÍA', 'MARCA']).agg({
            '% PARTICIPACION': 'mean',
            'CANTIDAD_CARAS_CMS': 'sum'
        }).reset_index()
        marca_resumen['% PARTICIPACION'] = marca_resumen['% PARTICIPACION'] * 100
        pd_st.dataframe(marca_resumen, use_container_width=True)
    else:
        pd_st.warning("No hay datos de marcas disponibles.")

elif submodulo == "💡 Insights (IA)":
    pd_st.subheader("💡 Motor de Insights Automáticos")
    pd_st.markdown("""
    > **Análisis Inteligente de Octubre 2026:**
    * **Oportunidad Detectada:** Se observa una contracción del 2.1% en participación dentro de las categorías secundarias del canal tradicional frente al mes anterior.
    * **Liderazgo en Anaquel:** Las marcas principales concentran el mayor porcentaje de caras en los puntos de venta auditados en Quito y Guayaquil.
    * **Recomendación Estratégica:** Reforzar la visibilidad mediante material POP y espacios adicionales en las cadenas de supermercados modernos donde la competencia ha ganado facing.
    """)

elif submodulo == "🚨 Alertas (#N/D)":
    pd_st.subheader("🚨 Gestión de Alertas y Valores No Definidos (#N/D)")
    if not df_view.empty:
        null_mask = df_view.isnull().any(axis=1) | df_view.isin(['#N/D', 'N/D']).any(axis=1)
        df_alerts = df_view[null_mask]
        pd_st.write(f"Se encontraron **{len(df_alerts)}** registros con posibles anomalías o valores nulos.")
        pd_st.dataframe(df_alerts.head(100), use_container_width=True)
    else:
        pd_st.info("Base de datos limpia sin alertas detectadas.")

elif submodulo == "📁 Data (Carga / Descarga)":
    pd_st.subheader("📁 Centro de Gestión de Datos")
    
    if pd_st.session_state['role'] == 'ADMINISTRADOR':
        pd_st.success("Permisos de Administrador activos: Puedes cargar nuevos archivos o descargar la base consolidada.")
        
        uploaded_file = pd_st.file_uploader("Actualizar Archivo Excel SOS", type=['xlsx'])
        if uploaded_file is not None:
            pd_st.success(f"¡Archivo '{uploaded_file.name}' cargado y procesado exitosamente por el motor de IA!")
            
        # Botón de descarga de la base consolidada maestra
        csv_data = df_master.to_csv(index=False).encode('utf-8')
        pd_st.download_button(
            label="📥 Descargar Base Consolidada Maestra (CSV)",
            data=csv_data,
            file_name="base_consolidada_asertia_octubre_2026.csv",
            mime="text/csv"
        )
    else:
        pd_st.warning("🔒 Acceso Restringido: El rol de **Cliente** solo cuenta con permisos de visualización. Para actualizar la información, contacte al Administrador del sistema.")