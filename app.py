import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(page_title="Dashboard de Notas", layout="wide")

st.sidebar.title("Datos y filtros")

uploaded_file = st.sidebar.file_uploader("Carga el archivo de estudiantes", type=["csv"])

if uploaded_file is not None:
  
    df = pd.read_csv(uploaded_file)
  
    df["Promedio"] = (df["nota_1"] + df["nota_2"]) / 2
 
    df = df.rename(columns={
        "id": "ID",
        "estudiante": "Estudiante",
        "sexo": "Sexo",
        "seccion": "Sección",
        "asistencia": "Asistencia (%)"
    })
 
    sexos_disponibles = df["Sexo"].unique().tolist()
    sexo_seleccionado = st.sidebar.multiselect("Sexo", sexos_disponibles, default=sexos_disponibles)
  
    secciones_disponibles = ["Todas"] + df["Sección"].unique().tolist()
    seccion_seleccionada = st.sidebar.selectbox("Sección", secciones_disponibles)
   
    rango_prom = st.sidebar.slider("Rango del promedio", min_value=1.0, max_value=7.0, value=(1.0, 7.0), step=0.1)

    asistencia_min = st.sidebar.number_input("Asistencia mínima (%)", min_value=0, max_value=100, value=0, step=1)
    
    st.sidebar.caption("Los filtros se combinan. Quitar ambos sexos deja la selección vacía.")
   
    df_filtrado = df[df["Sexo"].isin(sexo_seleccionado)]
    if seccion_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Sección"] == seccion_seleccionada]
    
    df_filtrado = df_filtrado[(df_filtrado["Promedio"] >= rango_prom[0]) & (df_filtrado["Promedio"] <= rango_prom[1])]
    df_filtrado = df_filtrado[df_filtrado["Asistencia (%)"] >= asistencia_min]

    st.title("Dashboard interactivo de notas")
    st.markdown("Explora los resultados de un curso combinando filtros. **Promedio:** 50 % de cada evaluación. **Aprobación del ejercicio:** promedio mayor o igual a 4,0. Datos ficticios.")

    str_sexo = ", ".join(sexo_seleccionado) if sexo_seleccionado else "Ninguno"
    st.write(f"**Filtros activos:** {str_sexo} · Sección: {seccion_seleccionada} · Promedio: {rango_prom[0]:.1f} a {rango_prom[1]:.1f} · Asistencia mínima: {asistencia_min} %")
    
    st.write("") # Espacio

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
   
    col_opciones, col_check = st.columns([3, 1])
    with col_opciones:
        tipo_grafico = st.radio("Gráfico", ["Notas por estudiante", "Promedio por sección"], horizontal=True)
    with col_check:
        mostrar_tabla = st.checkbox("Mostrar tabla", value=True)
   
    if mostrar_tabla:
        col_grafico, col_tabla = st.columns(2)
    else:
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

        ax.axhline(4.0, color='red', linestyle='--', label='Aprobación: 4,0')
        ax.legend()
        st.pyplot(fig)
        
    with col_tabla:
        if mostrar_tabla:
            st.subheader("Estudiantes seleccionados")
           
            columnas_finales = ["ID", "Estudiante", "Sexo", "Sección", "Promedio", "Asistencia (%)"]
            st.dataframe(df_filtrado[columnas_finales], hide_index=True, use_container_width=True)
 
    st.write("")
    csv_descarga = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar selección CSV",
        data=csv_descarga,
        file_name='estudiantes_filtrados.csv',
        mime='text/csv'
    )
    
    total_original = len(df)
    st.caption(f"Mostrando {total_estudiantes} de {total_original} estudiantes. La asistencia solo se usa como filtro; la aprobación depende del promedio.")

else:
   
    st.info("Por favor, carga el archivo 'estudiantes_notas.csv' en la barra lateral para visualizar el dashboard.")
