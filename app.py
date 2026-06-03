import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Simulador de Valoración",
    page_icon="📊",
    layout="wide"
)

# ==============================================================================
# 2. ENCABEZADO CON LOGO LOCAL Y TÍTULO
# ==============================================================================
col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    st.image("logo.png", width=150)

with col_titulo:
    st.title("📊 Simulador Financiero Grupo 1")
    st.markdown("El modelo integra proyecciones, flujos, EVA, ratios, análisis estructural y un panel de interpretación de pérdidas/ganancias.")

st.markdown("---")

# ==============================================================================
# BARRA LATERAL: PANEL DE INGRESO DE DATOS (INPUTS)
# ==============================================================================
st.sidebar.header("🛠️ Ingreso de Datos")

# --- SECCIÓN 1: CONFIGURACIÓN GENERAL Y PROYECCIÓN ---
st.sidebar.markdown("### 📅 Período")
periodos_proyectar = st.sidebar.number_input("Período (Años a proyectar)", value=4, min_value=1, max_value=10, step=1)
crecimiento_pct = st.sidebar.number_input("Tasa de Crecimiento Anual (%)", value=10.0, step=1.0, format="%.1f")
g_perpetuidad_pct = st.sidebar.number_input("Crecimiento a Perpetuidad g (%)", value=1.0, step=0.5, format="%.1f")
inv_af_deprec = st.sidebar.number_input("Relación Inversión Act. Fijos / Depreciación", value=1.3, step=0.1)

# --- VARIABLE CONTROL DE DEUDA ---
ano_pago_deuda = st.sidebar.slider("Año en que se termina de pagar la deuda", min_value=1, max_value=int(periodos_proyectar), value=int(periodos_proyectar))

# --- SECCIÓN 2: CUENTAS DEL BALANCE GENERAL (AÑO 0) ---
st.sidebar.markdown("### 🏦 Balance General")
caja_0 = st.sidebar.number_input("Caja", value=2300.0, step=100.0)
cxc_0 = st.sidebar.number_input("CxC", value=2400.0, step=100.0)
inventarios_0 = st.sidebar.number_input("Inventarios", value=1300.0, step=100.0)
anc_0 = st.sidebar.number_input("Activo No Corriente (Valor)", value=10000.0, step=500.0)

deuda_cp_0 = st.sidebar.number_input("Deuda Financiera Corto Plazo (DF CP)", value=2200.0, step=100.0)
cxp_0 = st.sidebar.number_input("Cuentas por Pagar (CxP)", value=1600.0, step=100.0)
pnc_0 = st.sidebar.number_input("Pasivo No Corriente", value=4900.0, step=500.0)
patrimonio_0 = st.sidebar.number_input("PATRIMONIO (Valor Inicial)", value=7300.0, step=500.0)

# --- SECCIÓN 3: CUENTAS DEL ESTADO DE RESULTADOS (AÑO 0) Y LÓGICA DE BLOQUEO ---
st.sidebar.markdown("### 📈 Cuentas del Estado de Resultados")
ingresos_0 = st.sidebar.number_input("Ingresos", value=12000.0, step=500.0)

if 'costos_dinero' not in st.session_state: st.session_state.costos_dinero = 2000.0
if 'costos_pct' not in st.session_state: st.session_state.costos_pct = 0.0
if 'gastos_dinero' not in st.session_state: st.session_state.gastos_dinero = 1000.0
if 'gastos_pct' not in st.session_state: st.session_state.gastos_pct = 0.0

costos_0 = st.sidebar.number_input("Costos ($)", value=2000.0, step=100.0, disabled=(st.session_state.costos_pct > 0.0), key="costos_dinero_input")
costo_ingreso_manual = st.sidebar.number_input("Relación Costos / Ingresos Proyectada (%)", value=0.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f", disabled=(costos_0 > 0.0), key="costos_pct_input")

st.session_state.costos_dinero = costos_0
st.session_state.costos_pct = costo_ingreso_manual

gastos_0 = st.sidebar.number_input("Gastos ($)", value=1000.0, step=100.0, disabled=(st.session_state.gastos_pct > 0.0), key="gastos_dinero_input")
gasto_ingreso_manual = st.sidebar.number_input("Relación Gastos / Ingresos Proyectada (%)", value=0.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f", disabled=(gastos_0 > 0.0), key="gastos_pct_input")

st.session_state.gastos_dinero = gastos_0
st.session_state.gastos_pct = gasto_ingreso_manual

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
# EVALUACIÓN DE RESTRICCIÓN Y CÁLCULOS BASE AÑO 0
# ==============================================================================
total_activo_inicial = caja_0 + cxc_0 + inventarios_0 + anc_0
total_pasivo_patrimonio_inicial = deuda_cp_0 + cxp_0 + pnc_0 + patrimonio_0
diferencia_cuadre = total_activo_inicial - total_pasivo_patrimonio_inicial
is_cuadrado = abs(diferencia_cuadre) <= 0.05

if costo_ingreso_manual > 0.0:
    margen_costos_operativos = costo_ingreso_manual / 100.0
    costos_0_calc = ingresos_0 * margen_costos_operativos
else:
    margen_costos_operativos = costos_0 / ingresos_0 if ingresos_0 != 0 else 0.0
    costos_0_calc = costos_0

if gasto_ingreso_manual > 0.0:
    margen_gastos_operativos = gasto_ingreso_manual / 100.0
    gastos_0_calc = ingresos_0 * margen_gastos_operativos
else:
    margen_gastos_operativos = gastos_0 / ingresos_0 if ingresos_0 != 0 else 0.0
    gastos_0_calc = gastos_0

# ==============================================================================
# CONTROL DE PESTAÑAS DINÁMICO
# ==============================================================================
if is_cuadrado:
    st.success(f"✅ **¡Balance General Inicial Cuadrado!** Activo = Pasivo + Patr = ${total_activo_inicial:,.2f}")
    nombres_pestanas = ["🏦 Año Base (Bases Año 0)", "📈 Proyecciones, Flujos y EVA", "📊 Análisis Estructural (V/H)", "📊 Indicadores Financieros", "🔍 Diagnóstico Automático"]
else:
    st.error(f"⚠️ **ALERTA DE DESCUADRE:** El Balance Inicial Año 0 tiene una diferencia de **${abs(diferencia_cuadre):,.2f}** (Activo: ${total_activo_inicial:,.2f} | Pasivo+Patr: ${total_pasivo_patrimonio_inicial:,.2f}).")
    st.info("👉 **Pestañas bloqueadas provisionalmente.** Revisa abajo las tablas del Año Base para encontrar el error y ajústalo desde la barra lateral.")
    nombres_pestanas = ["🏦 Año Base (Bases Año 0)"]

pestanas_activas = st.tabs(nombres_pestanas)

# --- RESTRICCIÓN DE PRIMERA PESTAÑA (SIEMPRE VISIBLE) ---
with pestanas_activas[0]:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("🏦 BALANCE GENERAL (Año 0)")
        indices_balance_0 = ["Caja", "CxC", "Inventarios", "(=) ACTIVO CORRIENTE", "Activo No Corriente (ANC)", "🏆 TOTAL ACTIVO", "Deuda Financiera CP", "Cuentas por Pagar (CxP)", "(=) PASIVO CORRIENTE", "Pasivo No Corriente (PNC)", "(=) TOTAL PASIVO", "PATRIMONIO", "🏆 TOTAL PASIVO + PATRIMONIO"]
        valores_balance_0 = [caja_0, cxc_0, inventarios_0, caja_0+cxc_0+inventarios_0, anc_0, total_activo_inicial, deuda_cp_0, cxp_0, deuda_cp_0+cxp_0, pnc_0, deuda_cp_0+cxp_0+pnc_0, patrimonio_0, total_pasivo_patrimonio_inicial]
        
        db_0 = pd.DataFrame({"Monto": valores_balance_0}, index=indices_balance_0).reset_index()
        st.dataframe(db_0.style.format({"Monto": "${:,.2f}"}), hide_index=True, use_container_width=True)
        
    with col_t2:
        st.subheader("📈 ESTADO DE RESULTADOS INTEGRAL (Año 0)")
        indices_eri_0 = ["Ingresos", "(-) Costos Operativos", "(-) Gastos Operativos", "(=) Utilidad Bruta", "(-) Depreciación", "(=) UAII / U. Ajustada", "(-) Gasto Financiero", "(=) UAI", "(-) Impuesto a la Renta", "🏆 UTILIDAD NETA"]
        
        ebita_0 = ingresos_0 - costos_0_calc - gastos_0_calc
        uai_aj_0 = ebita_0 - depreciacion_0
        gasto_fin_0 = (tasa_i_nominal_pct / 100.0) * (pnc_0 + (2 * deuda_cp_0))
        uai_eri_0 = uai_aj_0 - gasto_fin_0
        imp_eri_0 = max(0.0, uai_eri_0 * (tasa_T_impuesto_pct / 100.0)) if uai_eri_0 > 0 else 0.0
        util_neta_0 = uai_eri_0 - imp_eri_0
        
        valores_eri_0 = [ingresos_0, costos_0_calc, gastos_0_calc, ebita_0, depreciacion_0, uai_aj_0, gasto_fin_0, uai_eri_0, imp_eri_0, util_neta_0]
        er_0 = pd.DataFrame({"Monto": valores_eri_0}, index=indices_eri_0).reset_index()
        st.dataframe(er_0.style.format({"Monto": "${:,.2f}"}), hide_index=True, use_container_width=True)

# ==============================================================================
# MOTOR DE PROYECCIÓN AVANZADO
# ==============================================================================
if is_cuadrado:
    i_nominal = tasa_i_nominal_pct / 100.0 
    T_impuesto = tasa_T_impuesto_pct / 100.0  
    rf = rf_pct / 100.0
    rm = rm_pct / 100.0
    crecimiento = crecimiento_pct / 100.0
    kd_puro = i_nominal 
    deuda_total_0 = deuda_cp_0 + pnc_0
    tasa_depreciacion = depreciacion_0 / (anc_0 - depreciacion_0) if (anc_0 - depreciacion_0) != 0 else 0.0

    lista_anos = list(range(0, int(periodos_proyectar) + 1))
    proj_ingresos, proj_costos, proj_gast = [ingresos_0], [costos_0_calc], [gastos_0_calc]
    proj_ebita, proj_deprec, proj_uai_ajustada = [ebita_0], [depreciacion_0], [uai_aj_0]
    
    proj_imp_t = [max(0.0, uai_aj_0 * T_impuesto) if uai_aj_0 > 0 else 0.0]
    proj_util_ajustada = [uai_aj_0 - proj_imp_t[0]]
    
    proj_fco, proj_fcl, proj_wacc, proj_eva = [proj_util_ajustada[0] + depreciacion_0], [0.0], [], [0.0]
    proj_inv_operativa = [anc_0 + (cxc_0 + inventarios_0 - cxp_0)]
    
    proj_caja, proj_cxc, proj_inventarios, proj_anc_neto = [caja_0], [cxc_0], [inventarios_0], [anc_0]
    proj_deuda_cp, proj_cxp, proj_pnc, proj_patrimonio = [deuda_cp_0], [cxp_0], [pnc_0], [patrimonio_0]
    proj_gasto_fin = [gasto_fin_0]
    proj_utilidad_neta_eri = [util_neta_0]
    
    amortizacion_anual = (deuda_cp_0 + pnc_0) / ano_pago_deuda
    
    razon_d_e_0 = (deuda_total_0 / patrimonio_0) if patrimonio_0 > 0 else 0.0
    bl_0 = bu * (1 + razon_d_e_0)  
    ke_0 = rf + (bl_0 * (rm - rf))
    val_firm_0 = deuda_total_0 + patrimonio_0
    wacc_0 = (kd_puro * (deuda_total_0 / val_firm_0)) + (ke_0 * (patrimonio_0 / val_firm_0)) if val_firm_0 > 0 else ke_0
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
        
        imp_t = max(0.0, uai_aj_t * T_impuesto) if uai_aj_t > 0 else 0.0
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
        
        pnc_ant, deuda_cp_ant = proj_pnc[t-1], proj_deuda_cp[t-1]
        deuda_total_t = max(0.0, (deuda_cp_0 + pnc_0) - (amortizacion_anual * t)) if t <= ano_pago_deuda else 0.0
            
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
        
        gf_t = i_nominal * (pnc_ant + (2 * deuda_cp_ant))
        proj_gasto_fin.append(gf_t)
        
        uai_eri_t = uai_aj_t - gf_t
        imp_eri_t = uai_eri_t * T_impuesto if uai_eri_t > 0 else 0.0
        util_neta_eri_t = uai_eri_t - imp_eri_t
        proj_utilidad_neta_eri.append(util_neta_eri_t)
        
        proj_patrimonio.append(proj_patrimonio[t-1] + util_neta_eri_t)
        proj_caja.append(proj_caja[t-1] * (1 + crecimiento))

    proj_ac = [c + cx + i for c, cx, i in zip(proj_caja, proj_cxc, proj_inventarios)]
    proj_at = [ac + anc for ac, anc in zip(proj_ac, proj_anc_neto)]
    proj_pc = [d + cp for d, cp in zip(proj_deuda_cp, proj_cxp)]
    proj_pt = [pc + pnc for pc, pnc in zip(proj_pc, proj_pnc)]
    proj_pas_mas_pat = [p + pat for p, pat in zip(proj_pt, proj_patrimonio)]

    indices_eri = ["Ingresos", "(-) Costos Operativos", "(-) Gastos Operativos", "(=) Utilidad Bruta", "(-) Depreciación", "(=) UAII / U. Ajustada", "(-) Gasto Financiero", "(=) UAI", "(-) Impuesto a la Renta", "🏆 UTILIDAD NETA"]
    matrix_eri = pd.DataFrame([proj_ingresos, proj_costos, proj_gast, proj_ebita, proj_deprec, proj_uai_ajustada, proj_gasto_fin, [uai_eri_0] + [proj_uai_ajustada[t] - proj_gasto_fin[t] for t in range(1, len(lista_anos))], proj_imp_t, proj_utilidad_neta_eri], index=indices_eri, columns=[f"Año {t}" for t in lista_anos])
    matrix_eri.at["(=) UAI", "Año 0"] = uai_eri_0
    matrix_eri.at["(-) Impuesto a la Renta", "Año 0"] = imp_eri_0

    indices_balance = ["Caja", "CxC", "Inventarios", "(=) ACTIVO CORRIENTE", "Activo No Corriente (ANC)", "🏆 TOTAL ACTIVO", "Deuda Financiera CP", "Cuentas por Pagar (CxP)", "(=) PASIVO CORRIENTE", "Pasivo No Corriente (PNC)", "(=) TOTAL PASIVO", "PATRIMONIO", "🏆 TOTAL PASIVO + PATRIMONIO"]
    matrix_balance = pd.DataFrame([proj_caja, proj_cxc, proj_inventarios, proj_ac, proj_anc_neto, proj_at, proj_deuda_cp, proj_cxp, proj_pc, proj_pnc, proj_pt, proj_patrimonio, proj_pas_mas_pat], index=indices_balance, columns=[f"Año {t}" for t in lista_anos])

    # --- RECONSTRUCCIÓN COMPLETA DE RATIOS ---
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
            val_firm = deuda_fin_t + proj_patrimonio[t]
            wacc_t = (kd_puro * (deuda_fin_t / val_firm)) + ((rf + (bu * (1 + (deuda_fin_t / proj_patrimonio[t]))) * (rm - rf)) * (proj_patrimonio[t] / val_firm)) if val_firm > 0 else rf
            proj_wacc.append(wacc_t)
            
        inversion_t = proj_anc_neto[t] + ct_op
        if t > 0: proj_inv_operativa.append(inversion_t)
            
        roi_t = (proj_util_ajustada[t] / inversion_t) if inversion_t > 0 else 0.0
        list_roi.append(roi_t * 100)
        list_roa_ajustado.append((proj_util_ajustada[t] / proj_at[t]) * 100 if proj_at[t] > 0 else 0.0)
        list_roi_ajustado.append((proj_utilidad_neta_eri[t] / inversion_t) * 100 if inversion_t > 0 else 0.0)
        
        if t > 0:
            inv_ant = proj_anc_neto[t-1] + list_ct_operativo[t-1]
            proj_eva.append((roi_t - proj_wacc[t]) * inv_ant)

    matrix_valor = pd.DataFrame([[w * 100 for w in proj_wacc], proj_inv_operativa, proj_eva, proj_fco, proj_fcl], index=["WACC (%)", "Inversión Neta Operativa ($)", "EVA ($)", "Flujo de Caja Operativa (FCO)", "Flujo de Caja Libre (FCL)"], columns=[f"Año {t}" for t in lista_anos])

    # --- PESTAÑA 2: PROYECCIONES ---
    with pestanas_activas[1]:
        st.subheader("📈 1. Matriz del Estado de Resultados Integral Proyectado")
        st.dataframe(matrix_eri.style.format("${:,.2f}"), use_container_width=True)
        st.subheader("🏦 2. Evolución del Balance General Proyectado")
        st.dataframe(matrix_balance.style.format("${:,.2f}"), use_container_width=True)
        st.subheader("💎 3. Métricas de Creación de Valor, Flujos de Caja y Costo de Capital")
        st.dataframe(matrix_valor.style.format(formatter=lambda x: f"{x:,.2f}%" if (x < 100 and x > -100 and any(idx in str(matrix_valor.index) for idx in ["WACC"])) else f"${x:,.2f}"), use_container_width=True)

    # --- PESTAÑA 3: ESTRUCTURAL ---
    with pestanas_activas[2]:
        st.subheader("📊 Análisis Financiero de Estructura y Tendencias")
        subtab_vertical, subtab_horizontal = st.tabs(["🔍 Análisis Vertical (%)", "🔀 Análisis Horizontal (%)"])
        with subtab_vertical:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown("#### Estructura del Estado de Resultados (Base = Ingresos 100%)")
                df_vertical_eri = matrix_eri.copy()
                for col in df_vertical_eri.columns: df_vertical_eri[col] = (df_vertical_eri[col] / matrix_eri.loc["Ingresos", col]) * 100
                st.dataframe(df_vertical_eri.style.format("{:,.2f}%"), use_container_width=True)
            with col_v2:
                st.markdown("#### Estructura del Balance General (Base = Totales Corp. 100%)")
                df_vertical_balance = matrix_balance.copy()
                for col in df_vertical_balance.columns:
                    for cuenta in indices_balance:
                        if cuenta in ["Caja", "CxC", "Inventarios", "(=) ACTIVO CORRIENTE", "🏆 TOTAL ACTIVO"]:
                            df_vertical_balance.at[cuenta, col] = (matrix_balance.at[cuenta, col] / matrix_balance.at["🏆 TOTAL ACTIVO", col]) * 100
                        else:
                            df_vertical_balance.at[cuenta, col] = (matrix_balance.at[cuenta, col] / matrix_balance.at["🏆 TOTAL PASIVO + PATRIMONIO", col]) * 100
                st.dataframe(df_vertical_balance.style.format("{:,.2f}%"), use_container_width=True)
        with subtab_horizontal:
            col_h1, col_h2 = st.columns(2)
            df_horizontal_eri = pd.DataFrame(index=indices_eri)
            df_horizontal_balance = pd.DataFrame(index=indices_balance)
            for t in range(1, len(lista_anos)):
                ano_actual, ano_anterior = f"Año {t}", f"Año {t-1}"
                df_horizontal_eri[f"Var {ano_anterior} -> {ano_actual}"] = ((matrix_eri[ano_actual] - matrix_eri[ano_anterior]) / matrix_eri[ano_anterior].replace(0, np.nan)) * 100
                df_horizontal_balance[f"Var {ano_anterior} -> {ano_actual}"] = ((matrix_balance[ano_actual] - matrix_balance[ano_anterior]) / matrix_balance[ano_anterior].replace(0, np.nan)) * 100
            df_horizontal_eri.fillna(0, inplace=True)
            df_horizontal_balance.fillna(0, inplace=True)
            with col_h1:
                st.dataframe(df_horizontal_eri.style.format("{:,.2f}%"), use_container_width=True)
            with col_h2:
                st.dataframe(df_horizontal_balance.style.format("{:,.2f}%"), use_container_width=True)

    # --- PESTAÑA 4: RATIOS (RECONSTRUIDO CON TODOS LOS DE LA LISTA) ---
    with pestanas_activas[3]:
        st.subheader("📊 Matriz Completa de Indicadores de Gestión Financiera")
        data_ratios = {
            "Año": [f"Año {t}" for t in lista_anos],
            "LIQUIDEZ CORRIENTE (AC/PC)": list_liq_corriente,
            "LIQUIDEZ INMEDIATA (CAJA/PC)": list_liq_inmediata,
            "CAPITAL DE TRABAJO OPERATIVO ($)": list_ct_operativo,
            "PERIODO MEDIO DE COBRO (Días)": list_pm_cobro,
            "PERIODO MEDIO DE INVENTARIO (Días)": list_pm_inventario,
            "PERIODO MEDIO DE PAGO (Días)": list_pm_pago,
            "CICLO DE CAJA (Días)": list_ciclo_caja,
            "CAPITAL DE TRABAJO TEORICO": list_ct_teorico,
            "FACTOR DE SEGURIDAD": list_factor_seguridad,
            "RAZON DEUDA TOTAL (PT/AT %)": list_razon_deuda,
            "MULTIPLICADOR DEL ACTIVO (AT/PAT)": list_mult_inventario,
            "COBERTURA DE INTERESES (UAII/GF)": list_cobertura_interes,
            "ROE (%)": list_roe,
            "ROA (%)": list_roa,
            "ROI (%)": list_roi,
            "ROA AJUSTADO (UT AJUSTADA %)": list_roa_ajustado,
            "ROI AJUSTADO (UT NETA/INV %)": list_roi_ajustado
        }
        df_ratios_completo = pd.DataFrame(data_ratios).set_index("Año").T
        st.dataframe(df_ratios_completo.style.format("{:,.2f}"), use_container_width=True)

    # --- PESTAÑA 5: DIAGNÓSTICO FINANCIERO (TEXTO COMPLETO AUTOMATIZADO) ---
    with pestanas_activas[4]:
        st.subheader("🔍 Diagnóstico Financiero de Rendimiento y Creación de Valor")
        
        liq_final = list_liq_corriente[-1]
        ciclo_final = list_ciclo_caja[-1]
        eva_final = proj_eva[-1]
        
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.markdown("### 💧 Solvencia a Corto Plazo")
            if liq_final > 1.5:
                st.success(f"🟢 **Óptima ({liq_final:.2f})**")
                st.write("La empresa cuenta con activos corrientes robustos para cubrir con comodidad sus compromisos inmediatos.")
            elif 1.0 <= liq_final <= 1.5:
                st.warning(f"🟡 **Ajustada ({liq_final:.2f})**")
                st.write("La liquidez opera en niveles mínimos de seguridad. Cualquier retraso en cobranzas requerirá financiamiento adicional.")
            else:
                st.error(f"🔴 **Riesgo ({liq_final:.2f})**")
                st.write("Déficit de cobertura corriente. Alto riesgo de iliquidez técnica si las obligaciones de corto plazo vencen rápido.")
                
        with col_d2:
            st.markdown("### 🔄 Eficiencia Operativa")
            if ciclo_final < 60:
                st.success(f"🟢 **Eficiente ({ciclo_final:.1f} días)**")
                st.write("El ciclo de conversión de efectivo es veloz, minimizando los recursos atrapados en la operación corriente.")
            elif 60 <= ciclo_final <= 90:
                st.warning(f"🟡 **Moderado ({ciclo_final:.1f} días)**")
                st.write("Tiempos de rotación estándar. Se recomienda revisar plazos de inventarios y presionar la gestión de cobros.")
            else:
                st.error(f"🔴 **Ineficiente ({ciclo_final:.1f} días)**")
                st.write("El dinero tarda demasiado en regresar a la caja. Alto costo de oportunidad por ineficiencia en el capital de trabajo.")
                
        with col_d3:
            st.markdown("### 💎 Creación de Valor (EVA)")
            if eva_final > 0:
                st.success(f"🟢 **Genera Valor:** EVA de ${eva_final:,.2f}")
                st.write("Excelente. La rentabilidad operativa supera con creces el costo de oportunidad del capital invertido por los socios (WACC).")
            else:
                st.error(f"🔴 **Destruye Valor:** EVA de ${eva_final:,.2f}")
                st.write("Alerta. A pesar de poder registrar utilidades contables netas positivas, el rendimiento no cubre el costo de capital exigido.")
