
# ============================================================
# PROYECTO: SMARTPHONE MARKET ANALYTICS
# Visualización mundial de la cuota de mercado de smartphones
# Fuente de datos: Statcounter GlobalStats
# ============================================================

# 1. IMPORTACIÓN DE LIBRERÍAS

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt


# ============================================================
# 2. CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Smartphone Market Analytics",
    page_icon="📱",
    layout="wide"
)


# ============================================================
# 3. CARGA DE LOS DATOS
# ============================================================

@st.cache_data
def cargar_datos():

    df = pd.read_csv("smartphone_market.csv")

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%Y-%m",
        errors="coerce"
    )

    df = df.dropna(subset=["Date"])

    columnas_marcas = [
        columna for columna in df.columns
        if columna != "Date"
    ]

    for marca in columnas_marcas:
        df[marca] = pd.to_numeric(
            df[marca],
            errors="coerce"
        )

    return df, columnas_marcas


try:
    df, columnas_marcas = cargar_datos()

except FileNotFoundError:

    st.error(
        "No se encuentra smartphone_market.csv. "
        "Comprueba que está en la misma carpeta que "
        "smartphone_market_vsc.py."
    )

    st.stop()


# ============================================================
# 4. TÍTULO Y PRESENTACIÓN
# ============================================================

st.title("📱 SMARTPHONE MARKET ANALYTICS")

st.subheader(
    "Análisis mundial de la cuota de mercado "
    "de fabricantes de smartphones"
)

st.markdown("""
Esta aplicación permite estudiar la evolución del mercado
mundial de smartphones entre diferentes fabricantes.

Se utilizan datos históricos de cuota de mercado expresados
en porcentajes, procedentes de Statcounter GlobalStats.
""")

st.divider()


# ============================================================
# 5. BARRA LATERAL: CUATRO FILTROS
# ============================================================

st.sidebar.title("⚙️ Panel de filtros")


# FILTRO 1: FECHAS

fecha_min = df["Date"].min().date()
fecha_max = df["Date"].max().date()

fechas = st.sidebar.date_input(
    "1. Selecciona el periodo",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

if isinstance(fechas, (tuple, list)) and len(fechas) == 2:

    fecha_inicio = pd.Timestamp(fechas[0])
    fecha_final = pd.Timestamp(fechas[1])

else:

    fecha_inicio = pd.Timestamp(fecha_min)
    fecha_final = pd.Timestamp(fecha_max)


# FILTRO 2: FABRICANTES

marcas_seleccionadas = st.sidebar.multiselect(
    "2. Selecciona los fabricantes",
    options=columnas_marcas,
    default=[
        marca for marca in
        ["Apple", "Samsung", "Xiaomi", "Huawei", "Oppo"]
        if marca in columnas_marcas
    ]
)


# FILTRO 3: AÑO

df["Año"] = df["Date"].dt.year

anios_disponibles = sorted(df["Año"].unique())

anios_seleccionados = st.sidebar.multiselect(
    "3. Selecciona los años",
    options=anios_disponibles,
    default=anios_disponibles
)


# FILTRO 4: TIPO DE ANÁLISIS

tipo_analisis = st.sidebar.selectbox(
    "4. Tipo de análisis",
    [
        "Evolución temporal",
        "Comparación de fabricantes",
        "Distribución del mercado"
    ]
)


# ============================================================
# 6. APLICACIÓN DE LOS FILTROS
# ============================================================

df_filtrado = df[
    (df["Date"] >= fecha_inicio) &
    (df["Date"] <= fecha_final) &
    (df["Año"].isin(anios_seleccionados))
].copy()


if not marcas_seleccionadas:

    st.warning("Selecciona al menos un fabricante.")

    st.stop()


if df_filtrado.empty:

    st.warning("No hay datos para los filtros seleccionados.")

    st.stop()


# FECHAS REALES DEL PERIODO FILTRADO

fecha_inicio_real = df_filtrado["Date"].min()
fecha_final_real = df_filtrado["Date"].max()

periodo_texto = (
    f"Periodo seleccionado: "
    f"{fecha_inicio_real.strftime('%m/%Y')} - "
    f"{fecha_final_real.strftime('%m/%Y')}"
)


st.success(
    f"Análisis de {len(df_filtrado)} registros "
    f"y {len(marcas_seleccionadas)} fabricantes."
)


# ============================================================
# 7. MÉTRICAS PRINCIPALES
# ============================================================

st.header("📊 Indicadores principales")

medias = (
    df_filtrado[marcas_seleccionadas]
    .mean()
    .sort_values(ascending=False)
)

marca_lider = medias.index[0]
cuota_lider = medias.iloc[0]

maximo = (
    df_filtrado[marcas_seleccionadas]
    .max()
    .max()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Fabricante líder",
    marca_lider
)

col2.metric(
    "Cuota media del líder",
    f"{cuota_lider:.2f}%"
)

col3.metric(
    "Máxima cuota registrada",
    f"{maximo:.2f}%"
)

col4.metric(
    "Registros analizados",
    len(df_filtrado)
)

st.divider()


# ============================================================
# 8. GRÁFICO 1: EVOLUCIÓN TEMPORAL (LÍNEAS)
# ============================================================

st.header("📈 1. Evolución temporal de las marcas")

st.caption(periodo_texto)

datos_lineas = df_filtrado[
    ["Date"] + marcas_seleccionadas
].melt(
    id_vars="Date",
    var_name="Fabricante",
    value_name="Cuota"
)

fig_lineas = px.line(
    datos_lineas,
    x="Date",
    y="Cuota",
    color="Fabricante",
    markers=True,
    title="Evolución mundial de la cuota de mercado",
    labels={
        "Date": "Fecha",
        "Cuota": "Cuota de mercado (%)",
        "Fabricante": "Fabricante"
    },
    template="plotly_white"
)

fig_lineas.update_layout(
    hovermode="x unified",
    legend_title="Fabricantes"
)

st.plotly_chart(
    fig_lineas,
    use_container_width=True
)

st.caption(
    "Este gráfico permite observar cómo evoluciona "
    "la cuota de mercado de cada fabricante a lo largo del tiempo."
)


# ============================================================
# 9. GRÁFICO 2: COMPARACIÓN DE MARCAS (BARRAS)
# ============================================================

st.header("📊 2. Comparación de fabricantes")

st.caption(periodo_texto)

medias = (
    df_filtrado[marcas_seleccionadas]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

medias.columns = ["Fabricante", "Cuota media"]

fig_barras = px.bar(
    medias,
    x="Fabricante",
    y="Cuota media",
    color="Cuota media",
    color_continuous_scale="Blues",
    text_auto=".2f",
    title="Cuota media de mercado por fabricante",
    labels={
        "Fabricante": "Fabricante",
        "Cuota media": "Cuota media (%)"
    },
    template="plotly_white"
)

fig_barras.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig_barras,
    use_container_width=True
)

st.caption(
    "Se comparan las cuotas medias de los fabricantes "
    "durante el periodo seleccionado."
)


# ============================================================
# 10. GRÁFICO 3: DISTRIBUCIÓN DEL MERCADO (PASTEL)
# ============================================================

st.header("🥧 3. Distribución del mercado")

ultima_fecha = df_filtrado["Date"].max()

st.caption(
    f"Fecha de los datos: {ultima_fecha.strftime('%m/%Y')}"
)

ultima_fila = df_filtrado[
    df_filtrado["Date"] == ultima_fecha
].iloc[0]

datos_pastel = pd.DataFrame({
    "Fabricante": marcas_seleccionadas,
    "Cuota": [
        ultima_fila[marca]
        for marca in marcas_seleccionadas
    ]
})

datos_pastel = datos_pastel.dropna()

fig_pastel = px.pie(
    datos_pastel,
    names="Fabricante",
    values="Cuota",
    title=(
        "Distribución de la cuota de mercado "
        f"en {ultima_fecha.strftime('%m/%Y')}"
    ),
    hole=0.35,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_pastel.update_traces(
    textposition="inside",
    textinfo="percent+label",
    pull=[
        0.08 if marca == marca_lider else 0
        for marca in datos_pastel["Fabricante"]
    ]
)

st.plotly_chart(
    fig_pastel,
    use_container_width=True
)

st.caption(
    "Representación de la cuota de los fabricantes "
    "en el último mes disponible del periodo filtrado."
)


# ============================================================
# 11. GRÁFICO ESTADÍSTICO: HEATMAP
# ============================================================

st.header("🔥 4. Mapa de calor de correlaciones")

st.caption(periodo_texto)

st.markdown("""
Este gráfico muestra la correlación entre las cuotas de
mercado de los fabricantes seleccionados.

Los valores próximos a 1 indican una relación positiva,
los valores próximos a -1 indican una relación negativa
y los valores próximos a 0 indican una relación lineal débil.
""")

if len(marcas_seleccionadas) >= 2:

    correlacion = df_filtrado[
        marcas_seleccionadas
    ].corr()

    fig, ax = plt.subplots(figsize=(10, 7))

    sns.heatmap(
        correlacion,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        linewidths=0.5,
        center=0,
        ax=ax
    )

    ax.set_title(
        "Correlación entre fabricantes de smartphones"
    )

    st.pyplot(fig)

    plt.close(fig)

else:

    st.info(
        "Selecciona al menos dos fabricantes "
        "para mostrar el mapa de calor."
    )


# ============================================================
# 12. TABLA DE DATOS
# ============================================================

st.divider()

st.header("📋 5. Tabla de datos")

st.caption(periodo_texto)

st.markdown(
    "Consulta los valores de cuota de mercado "
    "de los fabricantes seleccionados."
)

tabla = df_filtrado[
    ["Date"] + marcas_seleccionadas
].copy()

tabla["Date"] = tabla["Date"].dt.strftime("%Y-%m")

st.dataframe(
    tabla,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 13. DESCARGA DE DATOS
# ============================================================

csv = tabla.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Descargar datos filtrados en CSV",
    data=csv,
    file_name="smartphone_market_filtrado.csv",
    mime="text/csv"
)


# ============================================================
# 14. CONCLUSIONES AUTOMÁTICAS
# ============================================================

st.divider()

st.header("📝 6. Conclusiones del análisis")

st.write(
    f"El fabricante con mayor cuota media durante "
    f"el periodo seleccionado es **{marca_lider}**, "
    f"con un {cuota_lider:.2f}%."
)

st.write(
    f"Se han analizado {len(df_filtrado)} registros "
    f"de {len(marcas_seleccionadas)} fabricantes."
)

st.write(
    f"La última fecha analizada es "
    f"{ultima_fecha.strftime('%m/%Y')}."
)

st.write(
    "Los resultados permiten comparar la evolución "
    "y la distribución de la cuota de mercado "
    "de los fabricantes de smartphones."
)


# ============================================================
# 15. INFORMACIÓN DEL PROYECTO
# ============================================================

st.divider()

with st.expander("ℹ️ Información del proyecto"):

    st.write("""
    **Nombre:** Smartphone Market Analytics

    **Objetivo:** Analizar la evolución mundial de la
    cuota de mercado de los fabricantes de smartphones.

    **Fuente:** Statcounter GlobalStats.

    **Formato de los datos:** CSV.

    **Herramientas utilizadas:**
    - Python
    - Pandas
    - Streamlit
    - Plotly
    - Matplotlib
    - Seaborn

    **Tipo de análisis:** Análisis exploratorio y
    visualización de datos.
    """)

st.caption(
    "Proyecto final de programación en Python | "
    "Smartphone Market Analytics"
)
