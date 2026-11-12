   import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuración inicial para usar toda la pantalla
st.set_page_config(page_title="Dashboard de Notas", layout="wide")

# ==========================================
# 2. BARRA LATERAL (Datos y filtros)
# ==========================================
st.sidebar.title("Datos y filtros")

# Carga de archivo
uploaded_file = st.sidebar.file_uploader("Carga el archivo de estudiantes", type=["csv"])

if uploaded_file is not None:
    # Leer el CSV indicando que está separado por punto y coma (SOLUCIÓN AL KEYERROR)
    df = pd.read_csv(uploaded_file, sep=";")
    
    # Filtro: Sexo
    sexos_disponibles = df["Sexo"].unique().tolist()
    sexo_seleccionado = st.sidebar.multiselect("Sexo", sexos_disponibles, default=sexos_disponibles)
    
    # Filtro: Sección (agregando la opción "Todas")
    secciones_disponibles = ["Todas"] + df["Sección"].unique().tolist()
    seccion_seleccionada = st.sidebar.selectbox("Sección", secciones_disponibles)
    
    # Filtro: Rango de promedio
    rango_prom = st.sidebar.slider("Rango del promedio", min_value=1.0, max_value=7.0, value=(1.0, 7.0), step=0.1)
    
    # Filtro: Asistencia
    asistencia_min = st.sidebar.number_input("Asistencia mínima (%)", min_value=0, max_value=100, value=0, step=1)
    
    st.sidebar.caption("Los filtros se combinan. Quitar ambos sexos deja la selección vacía.")
    
    # --- Procesamiento de filtros en el DataFrame ---
    df_filtrado = df[df["Sexo"].isin(sexo_seleccionado)]
    if seccion_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sección"] == seccion_seleccionada]
    
    df_filtrado = df_filtrado[(df_filtrado["Promedio"] >= rango_prom[0]) & (df_filtrado["Promedio"] <= rango_prom[1])]
    df_filtrado = df_filtrado[df_filtrado["Asistencia (%)"] >= asistencia_min]

    # ==========================================
    # 3. ÁREA PRINCIPAL
    # ==========================================
    st.title("Dashboard interactivo de notas")
    st.markdown("Explora los resultados de un curso combinando filtros. **Promedio:** 50 % de cada evaluación. **Aprobación del ejercicio:** promedio mayor o igual a 4,0. Datos ficticios.")
    
    # Texto de filtros activos
    str_sexo = ", ".join(sexo_seleccionado) if sexo_seleccionado else "Ninguno"
    st.write(f"**Filtros activos:** {str_sexo} · Sección: {seccion_seleccionada} · Promedio: {rango_prom[0]:.1f} a {rango_prom[1]:.1f} · Asistencia mínima: {asistencia_min} %")
    
    st.write("") # Espacio
    
    # --- Métricas principales (en 3 columnas) ---
    col1, col2, col3 = st.columns(3)
    total_estudiantes = len(df_filtrado)
    
    if total_estudiantes > 0:
        promedio_gen = df_filtrado["Promedio"].mean()
        aprobados = len(df_filtrado[df_filtrado["Promedio"] >= 4.0])
        porc_aprobacion = (aprobados / total_estudiantes) * 100
    else:
        promedio_gen = 0.0
        porc_aprobacion = 0.0
        
    col1.metric("Estudiantes seleccionados", total_estudiantes)
    col2.metric("Promedio general", f"{promedio_gen:.2f}".replace(".", ","))
    col3.metric("Aprobación", f"{porc_aprobacion:.2f} %".replace(".", ","))
    
    st.write("") # Espacio
    
    # --- Controles del gráfico y tabla ---
    col_opciones, col_check = st.columns([3, 1])
    with col_opciones:
        tipo_grafico = st.radio("Gráfico", ["Notas por estudiante", "Promedio por sección"], horizontal=True)
    with col_check:
        mostrar_tabla = st.checkbox("Mostrar tabla", value=True)
        
    # --- Visualizaciones (Gráfico y Tabla lado a lado) ---
    if mostrar_tabla:
        col_grafico, col_tabla = st.columns(2)
    else:
        # Si se oculta la tabla, el gráfico usa casi toda la pantalla
        col_grafico, col_tabla = st.columns([1, 0.01]) 
        
    with col_grafico:
        st.subheader("Visualización de notas")
        fig, ax = plt.subplots(figsize=(8, 5))
        
        if tipo_grafico == "Notas por estudiante":
            ax.bar(df_filtrado["Estudiante"], df_filtrado["Promedio"])
            ax.set_title("Promedio por estudiante")
            ax.set_xlabel("Estudiante")
            plt.xticks(rotation=45)
        else:
            promedio_seccion = df_filtrado.groupby("Sección")["Promedio"].mean()
            ax.bar(promedio_seccion.index, promedio_seccion.values)
            ax.set_title("Promedio por sección")
            ax.set_xlabel("Sección")
            
        ax.set_ylabel("Promedio de notas")
        ax.set_ylim(0, 7.5) # Rango de notas
        # Línea roja de aprobación
        ax.axhline(4.0, color='red', linestyle='--', label='Aprobación: 4,0')
        ax.legend()
        st.pyplot(fig)
        
    with col_tabla:
        if mostrar_tabla:
            st.subheader("Estudiantes seleccionados")
            st.dataframe(df_filtrado, hide_index=True, use_container_width=True)
            
    # --- Pie de página y Descarga ---
    st.write("")
    # También se añade sep=";" aquí para que al descargarlo abra bien en Excel
    csv_descarga = df_filtrado.to_csv(index=False, sep=";").encode('utf-8')
    st.download_button(
        label="Descargar selección CSV",
        data=csv_descarga,
        file_name='estudiantes_filtrados.csv',
        mime='text/csv'
    )
    
    total_original = len(df)
    st.caption(f"Mostrando {total_estudiantes} de {total_original} estudiantes. La asistencia solo se usa como filtro; la aprobación depende del promedio.")

else:
    # Mensaje inicial si no hay archivo cargado
    st.info("Por favor, carga el archivo 'estudiantes_notas.csv' en la barra lateral para visualizar el dashboard.")
