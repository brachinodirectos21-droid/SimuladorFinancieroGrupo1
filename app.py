import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA WEB
# ==============================================================================
st.set_page_config(
    page_title="Simulador de Valoración Completo",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador Financiero Grupo 1")
st.markdown("El modelo integra proyecciones, flujos, EVA, ratios y un panel de interpretación.")
st.markdown("---")

# ==============================================================================
# BARRA LATERAL: PANEL DE INGRESO DE DATOS (INPUTS)
# ==============================================================================
st.sidebar.header("Ingreso de Datos")

# --- SECCIÓN 1: CONFIGURACIÓN GENERAL Y PROYECCIÓN ---
st.sidebar.markdown("### 📅 Configuración del Período")
periodos_proyectar = st.sidebar.number_input("Período (Años a proyectar)", value=4, min_value=1, max_value=10, step=1)
crecimiento_pct = st.sidebar.number_input("Tasa de Crecimiento Anual (%)", value=10.0, step=1.0, format="%.1f")
g_perpetuidad_pct = st.sidebar.number_input("Crecimiento a Perpetuidad g (%)", value=1.0, step=0.5, format="%.1f")
inv_af_deprec = st.sidebar.number_input("Relación Inversión Act. Fijos / Depreciación", value=1.3, step=0.1)

# --- VARIABLE CONTROL DE DEUDA ---
ano_pago_deuda = st.sidebar.slider("Año en que se termina de pagar la deuda", min_value=1, max_value=int(periodos_proyectar), value=int(periodos_proyectar))

# --- SECCIÓN 2: CUENTAS DEL BALANCE GENERAL (AÑO 0) ---
st.sidebar.markdown("### 🏦 Cuentas del Balance General")
caja_0 = st.sidebar.number_input("Caja", value=2300.0, step=100.0)
cxc_0 = st.sidebar.number_input("CxC", value=2400.0, step=100.0)
inventarios_0 = st.sidebar.number_input("Inventarios", value=1300.0, step=100.0)
anc_0 = st.sidebar.number_input("Activo No Corriente (Valor)", value=10000.0, step=500.0)

deuda_cp_0 = st.sidebar.number_input("Deuda Financiera Corto Plazo (DF CP)", value=2200.0, step=100.0)
cxp_0 = st.sidebar.number_input("Cuentas por Pagar (CxP)", value=1600.0, step=100.0)
pnc_0 = st.sidebar.number_input("Pasivo No Corriente (PNC / Deuda LP)", value=4900.0, step=500.0)
patrimonio_0 = st.sidebar.number_input("PATRIMONIO (Valor Inicial)", value=7300.0, step=500.0)

# --- SECCIÓN 3: CUENTAS DEL ESTADO DE RESULTADOS (AÑO 0) ---
st.sidebar.markdown("### 📈 Cuentas del Estado de Resultados")
ingresos_0 = st.sidebar.number_input("Ingresos", value=12000.0, step=500.0)
costos_0 = st.sidebar.number_input("Costos", value=2000.0, step=100.0)
gastos_0 = st.sidebar.number_input("Gastos", value=1000.0, step=100.0)
depreciacion_0 = st.sidebar.number_input("Depreciación", value=500.0, step=50.0)

# --- SECCIÓN 4: VARIABLES METODOLÓGICAS (i y T) ---
st.sidebar.markdown("### 💳 Tasas Financieras e Impuestos")
tasa_i_nominal_pct = st.sidebar.number_input("Tasa de Interes Nominal (i %)", value=12.0, step=0.5, format="%.1f")
tasa_T_impuesto_pct = st.sidebar.number_input("Tasa Impuesto a la Renta (T %)", value=25.0, step=1.0, format="%.1f")

# --- SECCIÓN 5: VARIABLES MACRO Y PARAMETROS CAPM ---
st.sidebar.markdown("### 🌐 Parámetros de Mercado (CAPM)")
rf_pct = st.sidebar.number_input("Tasa Libre de Riesgo - Rf (%)", value=2.5, step=0.1, format="%.2f")
bu = st.sidebar.number_input("Beta Desapalancado (Bu)", value=0.75, step=0.05, format="%.2f")
rm_pct = st.sidebar.number_input("Rentabilidad del Mercado - Rm (%)", value=7.8, step=0.1, format="%.2f")

# ==============================================================================
# LÓGICA DE CÁLCULO BASE (AÑO 0)
# ==============================================================================
i_nominal = tasa_i_nominal_pct / 100.0 
T_impuesto = tasa_T_impuesto_pct / 100.0  
rf = rf_pct / 100.0
rm = rm_pct / 100.0
crecimiento = crecimiento_pct / 100.0

kd_neto = i_nominal * (1 - T_impuesto)
deuda_total_0 = deuda_cp_0 + pnc_0
gasto_fin_0 = deuda_total_0 * i_nominal

tasa_depreciacion = depreciacion_0 / (anc_0 - depreciacion_0) if (anc_0 - depreciacion_0) != 0 else 0.0
margen_costos_operativos = costos_0 / ingresos_0 if ingresos_0 != 0 else 0.0
margen_gastos_operativos = gastos_0 / ingresos_0 if ingresos_0 != 0 else 0.0

# ==============================================================================
# MOTOR DE PROYECCIÓN MULTI-AÑO COMPLETO
# ==============================================================================
lista_anos = list(range(0, int(periodos_proyectar) + 1))

proj_ingresos, proj_costos, proj_gast = [ingresos_0], [costos_0], [gastos_0]
proj_ebita = [ingresos_0 - costos_0 - gastos_0] 
proj_deprec = [depreciacion_0]
proj_uai_ajustada = [proj_ebita[0] - depreciacion_0] 
proj_imp_t = [proj_uai_ajustada[0] * T_impuesto]
proj_util_ajustada = [proj_uai_ajustada[0] - proj_imp_t[0]] 

proj_fco = [proj_util_ajustada[0] + depreciacion_0]
proj_fcl = [0.0]
proj_wacc = []
proj_eva = [0.0]

proj_caja, proj_cxc, proj_inventarios, proj_anc_neto = [caja_0], [cxc_0], [inventarios_0], [anc_0]
proj_deuda_cp, proj_cxp, proj_pnc, proj_patrimonio = [deuda_cp_0], [cxp_0], [pnc_0], [patrimonio_0]

proj_gasto_fin = [gasto_fin_0]
uai_eri_0 = proj_uai_ajustada[0] - gasto_fin_0
imp_eri_0 = uai_eri_0 * T_impuesto
proj_utilidad_neta_eri = [uai_eri_0 - imp_eri_0]

amortizacion_anual = (deuda_cp_0 + pnc_0) / ano_pago_deuda

razon_d_e_0 = (deuda_total_0 / patrimonio_0) if patrimonio_0 > 0 else 0.0
bl_0 = bu * (1 + (1 - T_impuesto) * razon_d_e_0)
ke_0 = rf + (bl_0 * (rm - rf))
val_firm_0 = deuda_total_0 + patrimonio_0
wacc_0 = (kd_neto * (deuda_total_0 / val_firm_0)) + (ke_0 * (patrimonio_0 / val_firm_0)) if val_firm_0 > 0 else ke_0
proj_wacc.append(wacc_0)

for t in range(1, int(periodos_proyectar) + 1):
    ing_t = proj_ingresos[t-1] * (1 + crecimiento)
    proj_ingresos.append(ing_t)
    proj_costos.append(ing_t * margen_costos_operativos)
    proj_gast.append(ing_t * margen_gastos_operativos)
    
    ebita_t = ing_t - proj_costos[t] - proj_gast[t]
    proj_ebita.append(ebita_t)
    
    dep_t = proj_anc_neto[t-1] * tasa_depreciacion
    proj_deprec.append(dep_t)
    
    uai_aj_t = ebita_t - dep_t
    proj_uai_ajustada.append(uai_aj_t)
    
    imp_t = max(0.0, uai_aj_t * T_impuesto)
    proj_imp_t.append(imp_t)
    
    u_ajustada_t = uai_aj_t - imp_t
    proj_util_ajustada.append(u_ajustada_t)
    
    fco_t = u_ajustada_t + dep_t
    proj_fco.append(fco_t)
    
    proj_cxc.append(ing_t * (cxc_0 / ingresos_0))
    proj_inventarios.append(ing_t * (inventarios_0 / ingresos_0))
    proj_cxp.append(ing_t * (cxp_0 / ingresos_0))
    
    inv_capital_fijo = dep_t * inv_af_deprec
    proj_anc_neto.append(proj_anc_neto[t-1] + inv_capital_fijo - dep_t)
    
    deuda_total_ant = proj_deuda_cp[t-1] + proj_pnc[t-1]
    if t <= ano_pago_deuda:
        deuda_total_t = max(0.0, (deuda_cp_0 + pnc_0) - (amortizacion_anual * t))
    else:
        deuda_total_t = 0.0
        
    if deuda_total_t > 0:
        proj_deuda_cp.append(deuda_total_t * (deuda_cp_0 / (deuda_cp_0 + pnc_0)))
        proj_pnc.append(deuda_total_t * (pnc_0 / (deuda_cp_0 + pnc_0)))
    else:
        proj_deuda_cp.append(0.0)
        proj_pnc.append(0.0)
        
    ct_op_t = proj_cxc[t] + proj_inventarios[t] - proj_cxp[t]
    ct_op_ant = proj_cxc[t-1] + proj_inventarios[t-1] - proj_cxp[t-1]
    inc_kt_t = ct_op_t - ct_op_ant
    proj_fcl.append(fco_t - inv_capital_fijo - inc_kt_t)
    
    gf_t = i_nominal * deuda_total_ant
    proj_gasto_fin.append(gf_t)
    uai_eri_t = uai_aj_t - gf_t
    imp_eri_t = max(0.0, uai_eri_t * T_impuesto)
    util_neta_eri_t = uai_eri_t - imp_eri_t
    proj_utilidad_neta_eri.append(util_neta_eri_t)
    
    proj_patrimonio.append(proj_patrimonio[t-1] + util_neta_eri_t)
    proj_caja.append(proj_caja[t-1] * (1 + crecimiento))

proj_ac = [c + cx + i for c, cx, i in zip(proj_caja, proj_cxc, proj_inventarios)]
proj_at = [ac + anc for ac, anc in zip(proj_ac, proj_anc_neto)]
proj_pc = [d + cp for d, cp in zip(proj_deuda_cp, proj_cxp)]
proj_pt = [pc + pnc for pc, pnc in zip(proj_pc, proj_pnc)]
proj_pas_mas_pat = [p + pat for p, pat in zip(proj_pt, proj_patrimonio)]

# --- RATIOS ---
list_liq_corriente, list_liq_inmediata, list_ct_operativo = [], [], []
list_pm_cobro, list_pm_inventario, list_pm_pago, list_ciclo_caja = [], [], [], []
list_ct_teorico, list_factor_seguridad, list_razon_deuda = [], [], []
list_mult_inventario, list_cobertura_interes = [], []
list_roe, list_roa, list_roi, list_roa_ajustado, list_roi_ajustado = [], [], [], [], []

for t in lista_anos:
    ct_op = proj_cxc[t] + proj_inventarios[t] - proj_cxp[t]
    list_ct_operativo.append(ct_op)
    list_liq_corriente.append(proj_ac[t] / proj_pc[t] if proj_pc[t] > 0 else 0.0)
    list_liq_inmediata.append(proj_caja[t] / proj_pc[t] if proj_pc[t] > 0 else 0.0)
    
    pmc = (proj_cxc[t] / proj_ingresos[t] * 360) if proj_ingresos[t] > 0 else 0.0
    pmi = (proj_inventarios[t] / proj_costos[t] * 360) if proj_costos[t] > 0 else 0.0
    pmp = (proj_cxp[t] / proj_costos[t] * 360) if proj_costos[t] > 0 else 0.0
    list_pm_cobro.append(pmc)
    list_pm_inventario.append(pmi)
    list_pm_pago.append(pmp)
    
    cc = pmc + pmi - pmp
    list_ciclo_caja.append(cc)
    
    ct_teorico = (cc * proj_costos[t]) / 360
    list_ct_teorico.append(ct_teorico)
    list_factor_seguridad.append(ct_op / ct_teorico if ct_teorico != 0 else 0.0)
    
    list_razon_deuda.append((proj_pt[t] / proj_at[t]) * 100 if proj_at[t] > 0 else 0.0)
    list_mult_inventario.append(proj_at[t] / proj_patrimonio[t] if proj_patrimonio[t] > 0 else 0.0)
    list_cobertura_interes.append(proj_uai_ajustada[t] / proj_gasto_fin[t] if proj_gasto_fin[t] > 0 else np.nan)
    
    list_roe.append((proj_utilidad_neta_eri[t] / proj_patrimonio[t]) * 100 if proj_patrimonio[t] > 0 else 0.0)
    list_roa.append((proj_utilidad_neta_eri[t] / proj_at[t]) * 100 if proj_at[t] > 0 else 0.0)
    
    if t > 0:
        deuda_fin_t = proj_deuda_cp[t] + proj_pnc[t]
        razon_d_e_t = (deuda_fin_t / proj_patrimonio[t]) if proj_patrimonio[t] > 0 else 0.0
        bl_t = bu * (1 + (1 - T_impuesto) * razon_d_e_t)
        ke_t = rf + (bl_t * (rm - rf))
        val_firm = deuda_fin_t + proj_patrimonio[t]
        wacc_t = (kd_neto * (deuda_fin_t / val_firm)) + (ke_t * (proj_patrimonio[t] / val_firm)) if val_firm > 0 else ke_t
        proj_wacc.append(wacc_t)
    
    inversion_t = proj_anc_neto[t] + ct_op
    roi_t = (proj_util_ajustada[t] / inversion_t) if inversion_t > 0 else 0.0
    list_roi.append(roi_t * 100)
    list_roa_ajustado.append((proj_util_ajustada[t] / proj_at[t]) * 100 if proj_at[t] > 0 else 0.0)
    list_roi_ajustado.append((proj_utilidad_neta_eri[t] / inversion_t) * 100 if inversion_t > 0 else 0.0)
    
    if t > 0:
        inv_ant = proj_anc_neto[t-1] + list_ct_operativo[t-1]
        proj_eva.append((roi_t - proj_wacc[t]) * inv_ant)

# ==============================================================================
# VISUALIZACIÓN EN PANTALLA Y PESTAÑAS
# ==============================================================================
diferencia_cuadre = proj_at[0] - proj_pas_mas_pat[0]
if abs(diferencia_cuadre) < 0.01:
    st.success(f"✅ **¡Balance General Inicial Cuadrado!** Activo = Pasivo + Patr = ${proj_at[0]:,.2f}")
else:
    st.error(f"❌ **NOTA DE CORRECCIÓN:** Tu Balance Inicial Año 0 NO cuadra por ${diferencia_cuadre:,.2f}")

tab_base, tab_proyecciones_flujos, tab_ratios, tab_diagnostico = st.tabs([
    "🏦 Año 0 (Bases)", 
    "📈 Proyecciones, Flujos y EVA", 
    "📊 Indicadores Financieros",
    "🔍 Diagnóstico Automático"
])

with tab_base:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("🏦 BALANCE GENERAL COMPLETO (Año 0)")
        db_0 = pd.DataFrame({
            "Estructura Contable": [
                "Caja", "CxC", "Inventarios", "  (=) ACTIVO CORRIENTE", "Activo No Corriente (ANC)", "🏆 TOTAL ACTIVO",
                "--------------------------------------------------",
                "Deuda Financiera CP", "Cuentas por Pagar (CxP)", "  (=) PASIVO CORRIENTE", "Pasivo No Corriente (PNC)", "  (=) TOTAL PASIVO",
                "PATRIMONIO", "🏆 TOTAL PASIVO + PATRIMONIO"
            ],
            "Monto": [
                caja_0, cxc_0, inventarios_0, proj_ac[0], anc_0, proj_at[0], None,
                deuda_cp_0, cxp_0, proj_pc[0], pnc_0, proj_pt[0], patrimonio_0, proj_pas_mas_pat[0]
            ]
        })
        st.dataframe(db_0.style.format({"Monto": lambda x: f"${x:,.2f}" if pd.notnull(x) else ""}), hide_index=True, use_container_width=True)
        
    with col_t2:
        st.subheader("📈 ESTADO DE RESULTADOS INTEGRAL (Año 0)")
        er_0 = pd.DataFrame({
            "Concepto": ["Ingresos", "(-) Costos Operativos", "(-) Gastos Operativos", "(=) Utilidad Bruta", "(-) Depreciación", "(=) UAII", "(-) Gasto Financiero", "(=) UAI", f"(-) Impuesto a la Renta T ({tasa_T_impuesto_pct}%)", "🏆 UTILIDAD NETA"], 
            "Monto": [ingresos_0, costos_0, gastos_0, proj_ebita[0], depreciacion_0, proj_uai_ajustada[0], gasto_fin_0, uai_eri_0, imp_eri_0, proj_utilidad_neta_eri[0]]
        })
        st.dataframe(er_0.style.format({"Monto": "${:,.2f}"}), hide_index=True, use_container_width=True)

with tab_proyecciones_flujos:
    st.subheader("📈 Matriz Unificada: Proyecciones, Flujos de Caja y EVA")
    data_unificada = {
        "Año": [f"Año {t}" for t in lista_anos],
        "ingresos": proj_ingresos, "costos": proj_costos, "gastos": proj_gast, "EBITA (Utilidad Bruta)": proj_ebita, "DEPRECIACIÓN": proj_deprec, "UAI AJUSTADA": proj_uai_ajustada, "IMPUESTOS": proj_imp_t, "UTILIDAD AJUSTADA": proj_util_ajustada, "FLUJO DE CAJA OPERATIVA": proj_fco, "FLUJO DE CAJA LIBRE": proj_fcl,
        "--------------------------------------------------": [np.nan] * len(lista_anos),
        "WACC (%)": [w * 100 for w in proj_wacc], "EVA ($)": proj_eva
    }
    df_unificada = pd.DataFrame(data_unificada).set_index("Año").T
    st.dataframe(df_unificada.style.format(formatter=lambda x: f"${x:,.2f}" if (pd.notnull(x) and (x > 100 or x < -100)) else (f"{x:,.2f}%" if (pd.notnull(x) and x < 100 and x > -100) else ""), na_rep=""), use_container_width=True)

with tab_ratios:
    st.subheader("📊 Matriz Completa de Indicadores de Gestión (360 Días)")
    data_ratios = {
        "Año": [f"Año {t}" for t in lista_anos], "LIQUIDEZ CORRIENTE (AC/PC)": list_liq_corriente, "LIQUIDEZ INMEDIATA (CAJA/PC)": list_liq_inmediata, "CAPITAL DE TRABAJO OPERATIVO ($)": list_ct_operativo, "PERIODO MEDIO DE COBRO (Días)": list_pm_cobro, "PERIODO MEDIO DE INVENTARIO (Días)": list_pm_inventario, "PERIODO MEDIO DE PAGO (Días)": list_pm_pago, "CICLO DE CAJA (Días)": list_ciclo_caja, "CAPITAL DE TRABAJO TEORICO": list_ct_teorico, "FACTOR DE SEGURIDAD": list_factor_seguridad, "RAZON DEUDA TOTAL (PT/AT %)": list_razon_deuda, "MULTIPLICADOR DE INVENTARIO (AT/PAT)": list_mult_inventario, "COBERTURA DE INTERESES (UAII/GF)": list_cobertura_interes, "RENTABILIDAD SOBRE PATRIMONIO (ROE %)": list_roe, "RENTABILIDAD SOBRE ACTIVO (ROA %)": list_roa, "RENTABILIDAD SOBRE INVERSION (ROI %)": list_roi, "RENTABILIDAD SOBRE EL ACTIVO (UT AJUSTADA %)": list_roa_ajustado, "RENTABILIDAD SOBRE INVERSION (UT AJUSTADA %)": list_roi_ajustado
    }
    df_ratios = pd.DataFrame(data_ratios).set_index("Año").T
    st.dataframe(df_ratios.style.format("{:,.2f}"), use_container_width=True)

# ==============================================================================
# LÓGICA DE DIAGNÓSTICO MATEMÁTICO (REGLAS FIJAS SIN IA)
# ==============================================================================
with tab_diagnostico:
    st.subheader("🔍 Diagnóstico de Salud Financiera Comercial")
    st.markdown("Análisis algorítmico inmediato de las métricas clave de la simulación.")
    st.markdown("---")
    
    # Tomamos los datos del año final proyectado para hacer la evaluación técnica
    liq_final = list_liq_corriente[-1]
    ciclo_final = list_ciclo_caja[-1]
    eva_final = proj_eva[-1]
    roi_final = list_roi_ajustado[-1]
    wacc_final = proj_wacc[-1] * 100
    
    col_d1, col_d2, col_d3 = st.columns(3)
    
    # 1. Evaluación de Liquidez
    with col_d1:
        st.markdown("### 💧 Solvencia a Corto Plazo")
        if liq_final > 1.5:
            st.success(f"🟢 **Óptima ({liq_final:.2f}):** La empresa cuenta con activos suficientes para cubrir holgadamente sus deudas de corto plazo.")
        elif 1.0 <= liq_final <= 1.5:
            st.warning(f"🟡 **Ajustada ({liq_final:.2f}):** La liquidez corriente es suficiente, pero deja poco margen operativo ante imprevistos.")
        else:
            st.error(f"🔴 **Riesgo ({liq_final:.2f}):** Activos corrientes por debajo de pasivos corrientes. Riesgo potencial de cesación de pagos.")

    # 2. Evaluación del Ciclo de Caja
    with col_d2:
        st.markdown("### 🔄 Eficiencia Operativa")
        if ciclo_final < 60:
            st.success(f"🟢 **Eficiente ({ciclo_final:.1f} días):** El ciclo de conversión de efectivo es ágil, lo que reduce la necesidad de financiamiento externo.")
        elif 60 <= ciclo_final <= 90:
            st.warning(f"🟡 **Moderado ({ciclo_final:.1f} días):** Los tiempos de cobro e inventario comienzan a presionar la caja operativa.")
        else:
            st.error(f"🔴 **Ineficiente ({ciclo_final:.1f} días):** Demasiado tiempo invertido en recuperar el dinero. Revisa políticas de cobro y rotación.")

    # 3. Evaluación de Valor Financiero (EVA)
    with col_d3:
        st.markdown("### 💎 Creación de Valor (EVA)")
        if eva_final > 0:
            st.success(f"🟢 **Genera Valor:** El negocio rinde por encima de su costo de capital (ROI {roi_final:.1f}% > WACC {wacc_final:.1f}%). EVA positivo de ${eva_final:,.2f}.")
        else:
            st.error(f"🔴 **Destruye Valor:** A pesar de haber utilidades, la rentabilidad no cubre el costo del riesgo (ROI {roi_final:.1f}% < WACC {wacc_final:.1f}%). EVA de ${eva_final:,.2f}.")

    # --- RECOMENDACIONES AUTOMÁTICAS ---
    st.markdown("---")
    st.markdown("### 🛠️ Plan de Acción Sugerido")
    
    recomendaciones = []
    if liq_final < 1.3:
        recomendaciones.append("* **Optimizar el pasivo corriente:** Buscar reestructurar deuda financiera de corto plazo hacia el largo plazo para aliviar la presión de caja.")
    if ciclo_final > 75:
        recomendaciones.append("* **Estrategia Comercial:** Reducir los días de cobro (PMC) mediante descuentos por pronto pago e incrementar la rotación de stocks.")
    if eva_final <= 0:
        recomendaciones.append("* **Revisión de Inversiones:** El EVA es negativo debido a un WACC alto o un margen operativo bajo. Evalúa reducir deuda costosa o recortar costos directos para expandir el ROI.")
    if len(recomendaciones) == 0:
        recomendaciones.append("* **Mantener la estrategia actual:** Las métricas muestran un balance equilibrado, eficiente y generador de rentabilidad económica real.")
        
    for rec in recomendaciones:
        st.markdown(rec)