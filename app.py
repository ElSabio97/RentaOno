import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.title("¿Comprar casa o alquilar en España?")
st.write("Compara los costos de comprar una casa (con o sin socia al 50%) versus alquilar.")

# Entradas del usuario
st.sidebar.header("Parámetros")
precio_casa = st.sidebar.slider("Precio de la casa (€)", 100000, 1000000, 300000, step=10000)
alquiler_mensual = st.sidebar.slider("Alquiler mensual (€)", 500, 3000, 1000, step=50)
anos = st.sidebar.slider("Años de comparación", 5, 30, 15)
tasa_hipoteca = st.sidebar.slider("Tasa de interés hipotecario (% anual)", 1.0, 6.0, 3.5, step=0.1)
pago_inicial_porcentaje = st.sidebar.slider("Pago inicial (% del precio)", 10, 50, 20)
inflacion_alquiler = st.sidebar.slider("Inflación anual del alquiler (%)", 0.0, 5.0, 3.0, step=0.1)
revalorizacion_casa = st.sidebar.slider("Revalorización anual de la casa (%)", 0.0, 5.0, 2.0, step=0.1)
costos_iniciales_porcentaje = st.sidebar.slider("Costos iniciales de compra (% del precio)", 5, 20, 12)

# Checkbox para compra al 50%
compra_compartida = st.sidebar.checkbox("¿Compra al 50% con otra persona?", value=False)

# Cálculos
pago_inicial = precio_casa * (pago_inicial_porcentaje / 100)
costos_iniciales_compra = precio_casa * (costos_iniciales_porcentaje / 100)
monto_hipoteca = precio_casa - pago_inicial
tasa_mensual = tasa_hipoteca / 100 / 12
n_meses = anos * 12

# Pago mensual de la hipoteca (fórmula de amortización)
pago_mensual_hipoteca = monto_hipoteca * (tasa_mensual * (1 + tasa_mensual)**n_meses) / ((1 + tasa_mensual)**n_meses - 1)
if compra_compartida:
    pago_inicial = pago_inicial / 2
    costos_iniciales_compra = costos_iniciales_compra / 2
    pago_mensual_hipoteca = pago_mensual_hipoteca / 2

# Costos acumulados
costos_alquiler = []
costos_compra = []
valor_casa = []

alquiler_actual = alquiler_mensual
casa_valor = precio_casa
for i in range(anos):
    # Alquiler con inflación
    costo_anual_alquiler = alquiler_actual * 12
    costos_alquiler.append(costo_anual_alquiler)
    alquiler_actual *= (1 + inflacion_alquiler / 100)
    
    # Compra: hipoteca + costos iniciales en el primer año
    costo_anual_compra = pago_mensual_hipoteca * 12
    if i == 0:
        costo_anual_compra += pago_inicial + costos_iniciales_compra
    costos_compra.append(costo_anual_compra)
    
    # Valor de la casa con revalorización
    casa_valor *= (1 + revalorizacion_casa / 100)
    valor_casa.append(casa_valor)

# Costos acumulados totales
total_alquiler = sum(costos_alquiler)
total_compra = sum(costos_compra)
valor_final_casa = valor_casa[-1]
if compra_compartida:
    valor_final_casa = valor_final_casa / 2

# Costo neto de compra (restando el valor de la casa)
costo_neto_compra = total_compra - valor_final_casa

# Resultados
st.header("Resultados")
st.write(f"**Costo total de alquilar ({anos} años):** {total_alquiler:,.2f} €")
st.write(f"**Costo total de comprar ({anos} años):** {total_compra:,.2f} €")
st.write(f"**Valor final de la casa:** {valor_final_casa:,.2f} €")
st.write(f"**Costo neto de compra (tras revalorización):** {costo_neto_compra:,.2f} €")

# Comparación
if costo_neto_compra < total_alquiler:
    st.success(f"Comprar es más rentable por {total_alquiler - costo_neto_compra:,.2f} €")
else:
    st.warning(f"Alquilar es más rentable por {costo_neto_compra - total_alquiler:,.2f} €")

# Tabla comparativa
df = pd.DataFrame({
    "Año": range(1, anos + 1),
    "Costo Anual Alquiler (€)": [round(x) for x in costos_alquiler],
    "Costo Anual Compra (€)": [round(x) for x in costos_compra],
    "Valor Casa (€)": [round(x) for x in valor_casa]
})
st.subheader("Comparativa Anual")
st.dataframe(df)

# Gráfico
df_plot = pd.DataFrame({
    "Año": range(1, anos + 1),
    "Costo Acumulado Alquiler (€)": np.cumsum(costos_alquiler),
    "Costo Acumulado Compra (€)": np.cumsum(costos_compra),
    "Valor Casa (€)": valor_casa
})
fig = px.line(df_plot, x="Año", y=["Costo Acumulado Alquiler (€)", "Costo Acumulado Compra (€)", "Valor Casa (€)"],
              title="Evolución de Costos y Valor de la Casa")
st.plotly_chart(fig)

# Instrucciones para ejecutar
st.write("""
### Instrucciones para ejecutar:
1. Guarda este código en un archivo `house_vs_rent.py`.
2. Instala las dependencias: `pip install streamlit pandas numpy plotly`.
3. Ejecuta la aplicación: `streamlit run house_vs_rent.py`.
""")
