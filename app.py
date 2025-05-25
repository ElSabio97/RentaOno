import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.title("Compra vs. Alquiler en Madrid (2025)")
st.write("Ajusta los parámetros para comparar la compra de una vivienda (con una socia) frente al alquiler en Madrid.")

# Función para calcular amortización de hipoteca
def calcular_hipoteca(hipoteca, interes_anual, años):
    n_meses = años * 12
    interes_mensual = interes_anual / 12
    cuota = hipoteca * interes_mensual / (1 - (1 + interes_mensual) ** -n_meses)
    amortizado = []
    saldo = hipoteca
    for i in range(n_meses):
        interes = saldo * interes_mensual
        capital = cuota - interes
        saldo -= capital
        amortizado.append((i // 12, cuota, capital, interes, saldo))
    df = pd.DataFrame(amortizado, columns=["Año", "Cuota", "Capital", "Interés", "Saldo"])
    resumen = df.groupby("Año").sum(numeric_only=True).reset_index()
    return resumen, cuota

# Sidebar con parámetros ajustables
st.sidebar.header("Parámetros")
precio_casa = st.sidebar.slider("Precio de la casa (€)", 100000, 1000000, 350000, step=10000)
entrada_porcentaje = st.sidebar.slider("Entrada por persona (% del precio)", 5.0, 30.0, 10.0, step=0.5)
interes_anual = st.sidebar.slider("Interés anual hipoteca (%)", 1.0, 6.0, 3.5, step=0.1)
alquiler_mensual = st.sidebar.slider("Alquiler mensual (€)", 500, 2000, 800, step=50)
inflacion_alquiler = st.sidebar.slider("Inflación anual alquiler (%)", 0.0, 5.0, 2.0, step=0.1)
revalorizacion_anual = st.sidebar.slider("Revalorización anual vivienda (%)", 0.0, 6.0, 3.0, step=0.1)
costes_anuales_propiedad = st.sidebar.slider("Costes anuales propiedad (€)", 1000, 5000, 2200, step=100)
gastos_compra = st.sidebar.slider("Gastos de compra (€)", 10000, 50000, 30000, step=1000)
retorno_inversion = st.sidebar.slider("Retorno inversión alternativa (%)", 0.0, 10.0, 5.0, step=0.1)
deduccion_alquiler_anual = st.sidebar.slider("Deducción fiscal alquiler (€/año)", 0, 2000, 1000, step=100)
años = st.sidebar.slider("Horizonte temporal (años)", 5, 40, 30, step=1)

# Convertir porcentajes a decimales
entrada_porcentaje /= 100
interes_anual /= 100
inflacion_alquiler /= 100
revalorizacion_anual /= 100
retorno_inversion /= 100

# Cálculos
entrada_individual = precio_casa * entrada_porcentaje
entrada_total = entrada_individual * 2  # Dos socios
hipoteca_total = precio_casa - entrada_total
hipoteca_df, cuota_mensual = calcular_hipoteca(hipoteca_total, interes_anual, años)
hipoteca_df["Patrimonio_total"] = precio_casa * ((1 + revalorizacion_anual) ** hipoteca_df["Año"]) - hipoteca_df["Saldo"]
hipoteca_df["Patrimonio_individual"] = hipoteca_df["Patrimonio_total"] / 2  # Dividido entre socios
hipoteca_df["Coste_anual_compra"] = (hipoteca_df["Cuota"] + costes_anuales_propiedad) / 2  # Dividido entre socios
hipoteca_df["Coste_acumulado_compra"] = (gastos_compra + entrada_total) / 2 + hipoteca_df["Coste_anual_compra"].cumsum()
hipoteca_df["Alquiler_anual"] = alquiler_mensual * 12 * ((1 + inflacion_alquiler) ** hipoteca_df["Año"])
hipoteca_df["Alquiler_anual_con_deduccion"] = hipoteca_df["Alquiler_anual"] - deduccion_alquiler_anual
hipoteca_df["Coste_acumulado_alquiler"] = hipoteca_df["Alquiler_anual_con_deduccion"].cumsum()
hipoteca_df["Inversion_alquiler"] = entrada_individual * ((1 + retorno_inversion) ** hipoteca_df["Año"])

# Tabla resumen
st.subheader("Resumen Compra vs. Alquiler (€)")
resumen = hipoteca_df[["Año", "Coste_acumulado_compra", "Coste_acumulado_alquiler", "Patrimonio_individual", "Inversion_alquiler"]]
st.dataframe(resumen.round(2), use_container_width=True)
st.write(f"**Cuota mensual hipoteca (por persona):** {cuota_mensual/2:.2f} €")

# Gráfico
st.subheader("Evolución Económica")
fig, ax = plt.subplots(figsize=(12, 8))
ax.plot(hipoteca_df["Año"], hipoteca_df["Coste_acumulado_compra"], label="Coste acumulado compra (por persona)", color="blue")
ax.plot(hipoteca_df["Año"], hipoteca_df["Coste_acumulado_alquiler"], label="Coste acumulado alquiler", color="red")
ax.plot(hipoteca_df["Año"], hipoteca_df["Patrimonio_individual"], label="Patrimonio neto (compra, por persona)", color="green")
ax.plot(hipoteca_df["Año"], hipoteca_df["Inversion_alquiler"], label="Inversión alternativa (alquiler)", color="orange")
ax.axhline(y=0, color="black", linestyle="--", alpha=0.3)
ax.set_xlabel("Años")
ax.set_ylabel("Euros (€)")
ax.set_title("Compra vs. Alquiler en Madrid - Evolución Económica (2025)")
ax.legend()
ax.grid(True)
plt.tight_layout()
st.pyplot(fig)

# Recomendaciones
st.subheader("Consideraciones")
st.write("""
- **Compra**: Más costosa inicialmente, pero genera patrimonio a largo plazo. Asegúrate de acordar legalmente la copropiedad con tu socia.
- **Alquiler**: Mayor flexibilidad y menos desembolso inicial. La inversión de la entrada puede generar retornos significativos.
- **Punto de equilibrio**: La compra suele ser más rentable tras 7-10 años, dependiendo de la revalorización.
- **Riesgos**: Considera caídas del mercado, costes imprevistos o problemas con la copropiedad.
""")
