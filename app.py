# ============================================================
# IMPORTAMOS LIBRERÍAS
# ============================================================

# Importamos Streamlit para crear la aplicación web interactiva
import streamlit as st

# Importamos Pandas para manipulación de datos
import pandas as pd

# Librerías de visualización
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURACIÓN DE LA APP
# ============================================================

st.set_page_config(page_title="App BI", layout="wide")


# ============================================================
# SESSION STATE (MEMORIA DE LA APP)
# ============================================================

# Guardamos el dataset cargado para que no se pierda al navegar
if "data" not in st.session_state:
    st.session_state.data = None

# Guardamos el nombre del archivo
if "nombre_archivo" not in st.session_state:
    st.session_state.nombre_archivo = None


# ============================================================
# TÍTULO E INTERFAZ
# ============================================================

st.title("📊 App Analizadora de Datasets")

st.sidebar.title("⚙️ Navegación")

st.write("📌 Elaborado por: Carlos Alberto Portocarrero")


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

modulos = st.sidebar.selectbox(
    "Seleccione un módulo",
    ["Home", "Carga y perfil del dataset", "Procesamiento de datos", "Análisis visual"]
)


# ============================================================
# MÓDULO 1: HOME
# ============================================================

if modulos == "Home":

    st.header("🏠 Presentación del proyecto")

    st.write("""
    Esta aplicación permite realizar análisis exploratorio de datos (EDA).

    🔹 Permite cargar archivos CSV  
    🔹 Detecta tipos de variables  
    🔹 Genera visualizaciones dinámicas  
    🔹 Facilita la toma de decisiones  

    Tecnologías usadas:
    - Python
    - Pandas
    - Streamlit
    - Plotly
    - Seaborn

    ⚠️ Nota: Este análisis es exploratorio.
    """)


# ============================================================
# MÓDULO 2: CARGA Y PERFIL
# ============================================================

elif modulos == "Carga y perfil del dataset":

    st.header("📂 Carga de dataset")

    # Subida de archivo
    archivo = st.file_uploader("Sube tu archivo CSV", type=["csv"])

    if archivo is not None:

        df = pd.read_csv(archivo)

        # Guardamos en memoria
        st.session_state.data = df
        st.session_state.nombre_archivo = archivo.name

    if st.session_state.data is not None:

        df = st.session_state.data

        st.subheader("Vista previa")
        st.dataframe(df.head())

        st.subheader("Información general")

        col1, col2, col3 = st.columns(3)

        col1.metric("Filas", df.shape[0])
        col2.metric("Columnas", df.shape[1])
        col3.metric("Nulos", df.isnull().sum().sum())

        st.write("Columnas:", df.columns.tolist())
        st.write("Tipos de datos:", df.dtypes)

        # Estadística descriptiva (REQUERIDO)
        st.subheader("Estadística descriptiva")
        st.dataframe(df.describe())

    else:
        st.warning("⚠️ Carga un archivo primero")


# ============================================================
# MÓDULO 3: PROCESAMIENTO
# ============================================================

elif modulos == "Procesamiento de datos":

    st.header("🛠 Procesamiento de datos")

    if st.session_state.data is None:
        st.warning("Debes cargar un dataset")
    else:

        df = st.session_state.data

        # Detectamos tipos automáticamente
        numericas = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categoricas = df.select_dtypes(include=['object']).columns.tolist()

        st.subheader("Tipos de variables")

        st.write("Numéricas:", numericas)
        st.write("Categóricas:", categoricas)

        # Nulos
        st.subheader("Valores nulos")
        st.dataframe(df.isnull().sum())

        # Duplicados
        st.subheader("Duplicados")
        st.write(df.duplicated().sum())

        # Filtro dinámico
        if len(categoricas) > 0:

            columna = st.selectbox("Filtrar por categoría", categoricas)
            valores = st.multiselect("Valores", df[columna].unique())

            if valores:
                df = df[df[columna].isin(valores)]

        st.dataframe(df)


# ============================================================
# MÓDULO 4: ANÁLISIS VISUAL (CORE)
# ============================================================

elif modulos == "Análisis visual":

    st.header("📊 Análisis Visual")

    if st.session_state.data is None:
        st.warning("Carga un dataset primero")
    else:

        df = st.session_state.data

        numericas = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categoricas = df.select_dtypes(include=['object']).columns.tolist()

        # Detectar posibles fechas
        fechas = []
        for col in df.columns:
            if "date" in col.lower():
                fechas.append(col)
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # =========================================================
        # CREACIÓN DE TABS (OBLIGATORIO)
        # =========================================================

        tabs = st.tabs([
            "📌 Resumen",
            "📊 Univariado",
            "🔗 Bivariado",
            "🔥 Multivariado",
            "📈 Temporal",
            "💡 Insights"
        ])

        # =========================
        # TAB 1: RESUMEN
        # =========================
        with tabsst.subheader("Información general")

            st.dataframe(df.head())

            col1, col2, col3 = st.columns(3)

            col1.metric("Filas", df.shape[0])
            col2.metric("Columnas", df.shape[1])
            col3.metric("Nulos", df.isnull().sum().sum())

        # =========================
        # TAB 2: UNIVARIADO
        # =========================
        with tabsst.subheader("Distribución de variables")

            col = st.selectbox("Selecciona variable", df.columns)

            # Histograma
            if col in numericas:
                st.plotly_chart(px.histogram(df, x=col))
                st.plotly_chart(px.box(df, y=col))  # outliers

            # Barras
            else:
                conteo = df[col].value_counts().reset_index()
                conteo.columns = [col, "count"]
                st.plotly_chart(px.bar(conteo, x=col, y="count"))

        # =========================
        # TAB 3: BIVARIADO
        # =========================
        with tabsst.subheader("Relación entre variables")

            if len(numericas) >= 2:
                x = st.selectbox("X", numericas)
                y = st.selectbox("Y", numericas)
                st.plotly_chart(px.scatter(df, x=x, y=y))

        # =========================
        # TAB 4: MULTIVARIADO
        # =========================
        with tabsst.subheader("Correlación")

            if len(numericas) > 1:
                corr = df[numericas].corr()
                fig, ax = plt.subplots()
                sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
                st.pyplot(fig)

        # =========================
        # TAB 5: TEMPORAL
        # =========================
        with tabsst.subheader("Análisis temporal")

            if len(fechas) > 0 and len(numericas) > 0:

                fecha = st.selectbox("Fecha", fechas)
                valor = st.selectbox("Valor", numericas)

                df_temp = df.sort_values(by=fecha)

                fig = px.line(df_temp, x=fecha, y=valor)
                st.plotly_chart(fig)

            else:
                st.info("No hay variables de fecha")

        # =========================
        # TAB 6: INSIGHTS
        # =========================
        with tabsst.subheader("Hallazgos")

            st.success("Los datos muestran patrones importantes que pueden apoyar decisiones.")

            if len(numericas) > 0:
                col = numericas[0]
                st.write(f"Ejemplo: La variable {col} tiene tendencia variable.")

            if len(categoricas) > 0:
                col = categoricas[0]
                st.write(f"La categoría más frecuente en {col} es:")
                st.write(df[col].value_counts().idxmax())
