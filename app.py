# ============================================================
# IMPORTAMOS LIBRERÍAS
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURACIÓN DE LA APP
# ============================================================

st.set_page_config(page_title="App BI", layout="wide")

# ============================================================
# SESSION STATE
# ============================================================

if "data" not in st.session_state:
    st.session_state.data = None

if "nombre_archivo" not in st.session_state:
    st.session_state.nombre_archivo = None

# ============================================================
# INTERFAZ
# ============================================================

st.title("📊 App Analizadora de Datasets")
st.sidebar.title("⚙️ Navegación")

st.write("📌 Elaborado por: Carlos Alberto Portocarrero")

# ============================================================
# MENÚ
# ============================================================

modulos = st.sidebar.selectbox(
    "Seleccione un módulo",
    ["Home", "Carga y perfil del dataset", "Procesamiento de datos", "Análisis visual"]
)

# ============================================================
# HOME
# ============================================================

if modulos == "Home":

    st.header("🏠 Presentación")

    st.write("""
    Aplicación para análisis exploratorio de datos.

    Tecnologías:
    - Python
    - Pandas
    - Streamlit
    - Plotly
    - Seaborn
    """)

# ============================================================
# CARGA
# ============================================================

elif modulos == "Carga y perfil del dataset":

    st.header("📂 Carga de dataset")

    archivo = st.file_uploader("Sube tu CSV", type=["csv"])

    if archivo is not None:

        df = pd.read_csv(archivo)

        st.session_state.data = df
        st.session_state.nombre_archivo = archivo.name

    if st.session_state.data is not None:

        df = st.session_state.data

        st.dataframe(df.head())

        col1, col2, col3 = st.columns(3)

        col1.metric("Filas", df.shape[0])
        col2.metric("Columnas", df.shape[1])
        col3.metric("Nulos", int(df.isnull().sum().sum()))

        st.write(df.dtypes)

        st.subheader("Estadística descriptiva")
        st.dataframe(df.describe())

    else:
        st.warning("Carga un archivo")

# ============================================================
# PROCESAMIENTO
# ============================================================

elif modulos == "Procesamiento de datos":

    st.header("🛠 Procesamiento")

    if st.session_state.data is None:
        st.warning("Carga datos primero")
    else:

        df = st.session_state.data.copy()

        numericas = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categoricas = df.select_dtypes(include=["object"]).columns.tolist()

        st.write("Numéricas:", numericas)
        st.write("Categóricas:", categoricas)

        st.subheader("Nulos")
        st.dataframe(df.isnull().sum().reset_index().rename(columns={"index": "Columna", 0: "Nulos"}))

        st.subheader("Duplicados")
        st.write(df.duplicated().sum())

        if len(categoricas) > 0:

            col = st.selectbox("Filtrar", categoricas)
            vals = st.multiselect("Valores", df[col].dropna().unique())

            if vals:
                df = df[df[col].isin(vals)]

        st.dataframe(df)

# ============================================================
# VISUAL
# ============================================================

elif modulos == "Análisis visual":

    st.header("📊 Análisis Visual")

    if st.session_state.data is None:
        st.warning("Carga un dataset primero")
    else:

        df = st.session_state.data.copy()

        numericas = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categoricas = df.select_dtypes(include=["object"]).columns.tolist()

        # Detectar columnas fecha
        fechas = []
        for col in df.columns:
            if "date" in col.lower() or "fecha" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")
                fechas.append(col)

        # CREACIÓN DE TABS
        tabs = st.tabs([
            "📌 Resumen",
            "📊 Univariado",
            "🔗 Bivariado",
            "🔥 Multivariado",
            "📈 Temporal",
            "💡 Insights"
        ])

        # ================= TAB 1 =================
        with tabs[0]:

            st.subheader("Información general")

            st.dataframe(df.head())

            col1, col2, col3 = st.columns(3)

            col1.metric("Filas", df.shape[0])
            col2.metric("Columnas", df.shape[1])
            col3.metric("Nulos", int(df.isnull().sum().sum()))

        # ================= TAB 2 =================
        with tabs[1]:

            st.subheader("Análisis univariado")

            col = st.selectbox("Selecciona variable", df.columns)

            if col in numericas:

                fig = px.histogram(df, x=col, title=f"Histograma de {col}")
                st.plotly_chart(fig, use_container_width=True)

                fig2 = px.box(df, y=col, title=f"Boxplot de {col}")
                st.plotly_chart(fig2, use_container_width=True)

            else:

                conteo = df[col].value_counts().reset_index()
                conteo.columns = [col, "count"]

                fig = px.bar(conteo, x=col, y="count", title=f"Conteo de {col}")
                st.plotly_chart(fig, use_container_width=True)

        # ================= TAB 3 =================
        with tabs[2]:

            st.subheader("Análisis bivariado")

            if len(numericas) >= 2:

                x = st.selectbox("Variable X", numericas, key="x_bivariado")
                y = st.selectbox("Variable Y", numericas, key="y_bivariado")

                fig = px.scatter(df, x=x, y=y, title=f"Relación entre {x} y {y}")
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("No hay suficientes variables numéricas")

        # ================= TAB 4 =================
        with tabs[3]:

            st.subheader("Análisis multivariado - Correlación")

            if len(numericas) > 1:

                corr = df[numericas].corr()

                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)

                st.pyplot(fig)

            else:
                st.warning("No hay suficientes variables numéricas")

        # ================= TAB 5 =================
        with tabs[4]:

            st.subheader("Análisis temporal")

            if len(fechas) > 0 and len(numericas) > 0:

                fecha = st.selectbox("Columna fecha", fechas)
                valor = st.selectbox("Variable numérica", numericas)

                df_temp = df.sort_values(fecha)

                fig = px.line(df_temp, x=fecha, y=valor, title=f"Evolución de {valor} por {fecha}")
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("No se detectaron columnas de fecha")

        # ================= TAB 6 =================
        with tabs[5]:

            st.subheader("Insights")

            st.success("Se identifican patrones relevantes en el dataset.")

            if len(numericas) > 0:
                st.write(f"La variable **{numericas[0]}** presenta variabilidad en sus valores.")

            if len(categoricas) > 0:
                top = df[categoricas[0]].value_counts().idxmax()
                st.write(f"La categoría más frecuente en **{categoricas[0]}** es: **{top}**")

            if len(categoricas) > 0:
                top = df[categoricas[0]].value_counts().idxmax()
                st.write(f"La categoría más frecuente en {categoricas[0]} es: {top}")
