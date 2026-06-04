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
    st.markdown("Visualización integral: ERI, Flujos de Caja, Estructura WACC y Generación de Valor (EVA).")

st.markdown("---")

# ==============================================================================
# BARRA LATERAL: PANEL DE INGRESO DE DATOS
# ==============================================================================
st.sidebar.header("🛠️ Ingreso de Datos")

st.sidebar.markdown("### 📅 Período")
periodos_proyectar = st.sidebar.number_input("Período (Años a proyectar)", value=4, min_value=1, max_value=10, step=1)
crecimiento_pct = st.sidebar.number_input("Tasa de Crecimiento Anual (%)", value=10.00, step=0.10, format="%.2f")
inv_af_deprec = st.sidebar.number_input("Relación Inversión Act. Fijos / Depreciación", value=1.30, step=0.01, format="%.2f")

st.sidebar.markdown("### 🏦 Balance General")
caja_0 = st.sidebar.number_input("Caja", value=47500.00, step=0.01, format="%.2f")
cxc_0 = st.sidebar.number_input("CxC", value=28250.00, step=0.01, format="%.2f")
inventarios_0 = st.sidebar.number_input("Inventarios", value=35300.00, step=0.01, format="%.2f")

desglosar_anc = st.sidebar.checkbox("¿Deseas desglosar el Activo No Corriente?", value=False)
if desglosar_anc:
    af_bruto_0 = st.sidebar.number_input("Activo Fijo (Bruto)", value=257480.00, step=0.01, format="%.2f")
    dep_acum_ingreso = st.sidebar.number_input("Depreciación Acumulada (Valor Absoluto)", value=7300.00, step=0.01, format="%.2f")
    dep_acum_0 = -abs(dep_acum_ingreso) 
    anc_0 = af_bruto_0 + dep_acum_0
else:
    anc_0 = st.sidebar.number_input("Activo No Corriente (Valor Global)", value=250180.00, step=0.01, format="%.2f")

deuda_cp_0 = st.sidebar.number_input("Deuda Financiera Corto Plazo (DF CP)", value=13100.00, step=0.01, format="%.2f")
cxp_0 = st.sidebar.number_input("Cuentas por Pagar (CxP)", value=44020.00, step=0.01, format="%.2f")
pnc_0 = st.sidebar.number_input("Pasivo No Corriente", value=92600.00, step=0.01, format="%.2f")
patrimonio_0 = st.sidebar.number_input("PATRIMONIO (Valor Inicial)", value=211510.00, step=0.01, format="%.2f")

st.sidebar.markdown("### 📈 Cuentas del Estado de Resultados")
ingresos_op_0 = st.sidebar.number_input("Ingresos Operativos", value=198000.00, step=0.01, format="%.2f")
ing_no_op_0 = st.sidebar.number_input("Ing No Op (Ingresos No Operativos)", value=3800.00, step=0.01, format="%.2f")
costos_0 = st.sidebar.number_input("Costos ($)", value=100000.00, step=0.01, format="%.2f")
gastos_0 = st.sidebar.number_input("Gastos ($)", value=48300.00, step=0.01, format="%.2f")
depreciacion_0 = st.sidebar.number_input("Depreciación del Ejercicio", value=14500.00, step=0.01, format="%.2f")

st.sidebar.markdown("### 💳 Tasas Financieras")
tasa_i_nominal_pct = st.sidebar.number_input("Tasa de Interes Nominal (i %)", value=7.88, step=0.01, format="%.2f")
tasa_T_impuesto_pct = st.sidebar.number_input("Tasa Impuesto a la Renta (T %)", value=25.00, step=0.01, format="%.2f")

st.sidebar.markdown("### 📉 Segmento CAPM")
rf_pct = st.sidebar.number_input("Tasa Libre de Riesgo - Rf (%)", value=5.00, step=0.10, format="%.2f")
rm_pct = st.sidebar.number_input("Rendimiento del Mercado - Rm (%)", value=11.00, step=0.10, format="%.2f")
beta_u = st.sidebar.number_input("Beta Desapalancado - Bu", value=1.10, step=0.05, format="%.2f")
ano_fin_deuda = st.sidebar.slider("Año en que se termina de pagar la deuda", 1, int(periodos_proyectar), int(periodos_proyectar))

# ==============================================================================
# CÁLCULOS BASE AÑO 0 Y VERIFICACIÓN DE CUADRE
# ==============================================================================
activo_corriente_0 = caja_0 + cxc_0 + inventarios_0
total_activo_inicial = activo_corriente_0 + anc_0
total_pasivo_patrimonio_inicial = deuda_cp_0 + cxp_0 + pnc_0 + patrimonio_0
diferencia_cuadre = total_activo_inicial - total_pasivo_patrimonio_inicial
is_cuadrado = abs(diferencia_cuadre) <= 1.00

# ==============================================================================
# DEFINICIÓN DE PESTAÑAS (CONDICIONAL AL CUADRE ABSOLUTO)
# ==============================================================================
if is_cuadrado:
    st.success(f"✅ **Balance Cuadrado** (${total_activo_inicial:,.2f})")
    nombres_pestanas = ["🏦 Año Base", "📈 Proyecciones de Flujos", "📊 WACC y EVA"]
else:
    st.error(f"⚠️ **Descuadre Detectado:** El Balance General tiene una diferencia de ${abs(diferencia_cuadre):,.2f}. Debe corregir el descuadre para poder avanzar con las proyecciones y el análisis de valor.")
    nombres_pestanas = ["🏦 Año Base"]

pestanas_activas = st.tabs(nombres_pestanas)

# RENDIMIENTO DE LA PESTAÑA 1 (Siempre disponible para auditoría de datos)
with pestanas_activas[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏦 Balance Año 0")
        if desglosar_anc:
            indices_b = ["Caja", "CxC", "Inventarios", "(=) ACTIVO CORRIENTE", "Activo Fijo", "Deprec. Acum.", "(=) ACTIVO NO CORRIENTE", "🏆 TOTAL ACTIVO", "Deuda CP", "CxP", "(=) PASIVO CORRIENTE", "Pasivo No Corriente (PNC)", "(=) TOTAL PASIVO", "PATRIMONIO", "🏆 TOTAL PASIVO + PATRIMONIO"]
            valores_b = [caja_0, cxc_0, inventarios_0, activo_corriente_0, af_bruto_0, dep_acum_0, anc_0, total_activo_inicial, deuda_cp_0, cxp_0, deuda_cp_0+cxp_0, pnc_0, deuda_cp_0+cxp_0+pnc_0, patrimonio_0, total_pasivo_patrimonio_inicial]
        else:
            indices_b = ["Caja", "CxC", "Inventarios", "(=) ACTIVO CORRIENTE", "Activo No Corriente (ANC)", "🏆 TOTAL ACTIVO", "Deuda CP", "CxP", "(=) PASIVO CORRIENTE", "Pasivo No Corriente (PNC)", "(=) TOTAL PASIVO", "PATRIMONIO", "🏆 TOTAL PASIVO + PATRIMONIO"]
            valores_b = [caja_0, cxc_0, inventarios_0, activo_corriente_0, anc_0, total_activo_inicial, deuda_cp_0, cxp_0, deuda_cp_0+cxp_0, pnc_0, deuda_cp_0+cxp_0+pnc_0, patrimonio_0, total_pasivo_patrimonio_inicial]
        st.dataframe(pd.DataFrame({"Monto": valores_b}, index=indices_b), width="stretch")
        
    with col2:
        st.subheader("📈 ERI Original Año 0")
        tasa_i = tasa_i_nominal_pct / 100.0
        T_impuesto = tasa_T_impuesto_pct / 100.0  
        ingresos_totales_0 = ingresos_op_0 + ing_no_op_0
        ebita_0 = ingresos_totales_0 - costos_0 - gastos_0
        uai_aj_0 = ebita_0 - depreciacion_0
        gasto_fin_0 = tasa_i * (pnc_0 + (2 * deuda_cp_0))
        uai_eri_0 = uai_aj_0 - gasto_fin_0
        imp_eri_0 = max(0.0, uai_eri_0 * T_impuesto) if uai_eri_0 > 0 else 0.0
        util_neta_0 = uai_eri_0 - imp_eri_0

        indices_e = [
            "Ingresos Operativos", "(+) Ing No Op", "(=) Total Ingresos", 
            "(-) Costos Operativos", "(-) Gastos Operativos", "(=) Utilidad Bruta", 
            "(-) Depreciación", "(=) UAII / U. Ajustada", "(-) Gasto Financiero (Fórmula)", 
            "(=) UAI", "(-) Impuesto a la Renta (Dinámico)", "🏆 UTILIDAD NETA"
        ]
        valores_e = [
            ingresos_op_0, ing_no_op_0, ingresos_totales_0, costos_0, 
            gastos_0, ebita_0, depreciacion_0, uai_aj_0, gasto_fin_0, 
            uai_eri_0, imp_eri_0, util_neta_0
        ]
        st.dataframe(pd.DataFrame({"Monto": valores_e}, index=indices_e), width="stretch")

# ==============================================================================
# CONDICIÓN DE AVANCE: SÓLO SE EJECUTA SI EL BALANCE ESTÁ PERFECTAMENTE CUADRADO
# ==============================================================================
if is_cuadrado:
    # --- PARÁMETROS DEL MOTOR ---
    margen_costos_operativos = costos_0 / ingresos_op_0 if ingresos_op_0 != 0 else 0.0
    margen_gastos_operativos = gastos_0 / ingresos_op_0 if ingresos_op_0 != 0 else 0.0
    crecimiento = crecimiento_pct / 100.0
    tasa_da = depreciacion_0 / (anc_0 + depreciacion_0) if (anc_0 + depreciacion_0) != 0 else 0.0
    lista_anos = list(range(0, int(periodos_proyectar) + 1))
    anos_v = [f"Año {t}" for t in range(1, int(periodos_proyectar) + 1)]
    
    rf = rf_pct / 100.0
    rm = rm_pct / 100.0
    rm_rf = rm - rf
    kd_neto = tasa_i * (1 - T_impuesto)
    capital_operativo_0 = cxc_0 + inventarios_0 - cxp_0
    factor_cap_trabajo = capital_operativo_0 / ingresos_op_0 if ingresos_op_0 != 0 else 0.0

    # --- LISTAS DE ALMACENAMIENTO DE PROYECCIONES ---
    proj_ingresos = [ingresos_op_0]
    proj_costos = [costos_0]
    proj_gast = [gastos_0]
    proj_ebitda = [ingresos_op_0 - costos_0 - gastos_0]
    proj_deprec = [depreciacion_0]
    proj_uaii = [0.0]
    proj_imp_ajust = [0.0]
    proj_util_ajust = [0.0]
    proj_fco = [0.0]
    
    # Listas patrimoniales / activos fijos
    list_af_inicial = [anc_0]
    list_inv_af = [0.0]
    list_af_final = [anc_0]
    
    # Desglose específico para variables dinámicas de AF Bruto y Depreciación Acumulada
    if desglosar_anc:
        list_af_bruto_din = [af_bruto_0]
        list_dep_acum_din = [dep_acum_0]
    
    list_ct_actual = [capital_operativo_0]
    list_ct_anterior = [0.0]
    list_inv_ct_total = [0.0]
    list_fci = [0.0]
    list_fcl = [0.0]

    # Inicialización Operativa Año 0
    proj_uaii[0] = proj_ebitda[0] - proj_deprec[0]
    proj_imp_ajust[0] = max(0.0, proj_uaii[0] * T_impuesto)
    proj_util_ajust[0] = proj_uaii[0] - proj_imp_ajust[0]
    proj_fco[0] = proj_util_ajust[0] + proj_deprec[0]

    # --- CICLO EJECUTOR OPERATIVO ---
    for t in range(1, int(periodos_proyectar) + 1):
        ing_t = proj_ingresos[t-1] * (1 + crecimiento)
        proj_ingresos.append(ing_t)
        proj_costos.append(ing_t * margen_costos_operativos)
        proj_gast.append(ing_t * margen_gastos_operativos)
        proj_ebitda.append(proj_ingresos[t] - proj_costos[t] - proj_gast[t])
        
        # Inversión Activos Fijos (CAPEX)
        af_ini_t = list_af_final[t-1]
        inv_af_t = proj_deprec[t-1] * inv_af_deprec
        dep_t = tasa_da * (af_ini_t + inv_af_t)
        af_fin_t = af_ini_t + inv_af_t - dep_t
        
        list_af_inicial.append(af_ini_t)
        list_inv_af.append(inv_af_t)
        proj_deprec.append(dep_t)
        list_af_final.append(af_fin_t)
        
        if desglosar_anc:
            list_af_bruto_din.append(list_af_bruto_din[-1] + inv_af_t)
            list_dep_acum_din.append(list_dep_acum_din[-1] - dep_t)
        
        # Capital de Trabajo Operativo
        ct_act_t = ing_t * factor_cap_trabajo
        ct_ant_t = list_ct_actual[t-1]
        inv_ct_t = ct_act_t - ct_ant_t
        
        list_ct_actual.append(ct_act_t)
        list_ct_anterior.append(ct_ant_t)
        list_inv_ct_total.append(inv_ct_t)
        
        # Flujos de Caja de Inversión y Operativos
        fci_t = -inv_af_t - inv_ct_t
        list_fci.append(fci_t)
        
        uaii_t = proj_ebitda[t] - dep_t
        proj_uaii.append(uaii_t)
        imp_t = max(0.0, uaii_t * T_impuesto)
        proj_imp_ajust.append(imp_t)
        util_t = uaii_t - imp_t
        proj_util_ajust.append(util_t)
        fco_t = util_t + dep_t
        proj_fco.append(fco_t)
        
        list_fcl.append(fco_t + fci_t)

    # Amortización de pasivos financieros
    deuda_total_inicial = pnc_0 + deuda_cp_0
    deudas_proyectadas = [deuda_total_inicial]
    for t in range(1, int(periodos_proyectar) + 1):
        if t <= int(ano_fin_deuda):
            d_t = deudas_proyectadas[-1] - (deuda_total_inicial / int(ano_fin_deuda))
        else:
            d_t = 0.0
        deudas_proyectadas.append(max(0.0, d_t))

    # --- PESTAÑA 2: PROYECCIONES ---
    def resaltar_max_fcl(row):
        estilos = ['' for _ in row]
        if row.name == "FLUJO DE CAJA LIBRE (FCL)":
            max_val = row.max()
            estilos = [f'background-color: #2e7d32; color: white;' if v == max_val else '' for v in row]
        return estilos

    with pestanas_activas[1]:
        st.subheader("📈 1. Estado de Resultados y Flujo de Caja Libre")
        idx_eri = ["Ingresos", "Costos", "Gastos", "EBITDA", "D&A", "UAII", "Imp. Ajustados", "Util. Ajustada", "FLUJO DE CAJA OPERATIVO (FCO)", "FLUJO DE CAJA LIBRE (FCL)"]
        df_eri = pd.DataFrame([proj_ingresos, proj_costos, proj_gast, proj_ebitda, proj_deprec, proj_uaii, proj_imp_ajust, proj_util_ajust, proj_fco, list_fcl], index=idx_eri, columns=[f"Año {t}" for t in lista_anos])
        st.dataframe(df_eri[anos_v].style.format("${:,.2f}").apply(resaltar_max_fcl, axis=1), width="stretch")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("🏢 2. Control de Activos Fijos")
            if desglosar_anc:
                idx_af = ["AF Inicial (Bruto)", "Inversión AF (CAPEX)", "D&A del Periodo", "Depreciación Acumulada", "(=) Activo No Corriente Neto"]
                df_af = pd.DataFrame([list_af_bruto_din, list_inv_af, proj_deprec, list_dep_acum_din, list_af_final], index=idx_af, columns=[f"Año {t}" for t in lista_anos])
            else:
                idx_af = ["AF Inicial Total", "Inversión AF", "D&A", "AF Final Total"]
                df_af = pd.DataFrame([list_af_inicial, list_inv_af, proj_deprec, list_af_final], index=idx_af, columns=[f"Año {t}" for t in lista_anos])
            st.dataframe(df_af[anos_v].style.format("${:,.2f}"), width="stretch")
        
        with col_c2:
            st.subheader("💼 3. Capital de Trabajo")
            idx_ct = ["CT Actual", "CT Anterior", "Inv. CT Total"]
            df_ct = pd.DataFrame([list_ct_actual, list_ct_anterior, list_inv_ct_total], index=idx_ct, columns=[f"Año {t}" for t in lista_anos])
            st.dataframe(df_ct[anos_v].style.format("${:,.2f}"), width="stretch")

        st.subheader("💸 4. Flujo de Caja de Inversión")
        idx_fci = ["INVERSION ACTIVOS FIJOS", "INVERSION CAPITAL TOTAL", "FLUJO DE CAJA DE INVERSIÓN"]
        df_fci = pd.DataFrame([list_inv_af, list_inv_ct_total, list_fci], index=idx_fci, columns=[f"Año {t}" for t in lista_anos])
        st.dataframe(df_fci[anos_v].style.format("${:,.2f}"), width="stretch")

    # ==============================================================================
    # DESARROLLO DE PESTAÑA 3: WACC Y EVA (CÁLCULO UNIFICADO)
    # ==============================================================================
    with pestanas_activas[2]:
        deuda_total_inicial = pnc_0 + deuda_cp_0
        
        # DEFINICIÓN DE VARIABLES FALTANTES PARA EVITAR EL NAMEERROR
        num_anos = int(periodos_proyectar)
        T = T_impuesto  # Mapeamos T_impuesto a 'T' para que coincida con tu fórmula interna

        # Función simuladora recursiva para resolver circularidad del Equity Año 1
        def resolver_estructuras(equity_trial):
            deudas = []
            equities = [equity_trial]
            deuda_equity = []
            wds, wes, betas_ap, kes, waccs = [], [], [], [], []
            
            # Cuadro 1: Regla de amortización de deuda lineal según slider
            for t_idx in range(1, num_anos + 1):
                if t_idx <= int(ano_fin_deuda):
                    if t_idx == 1:
                        d_t = deuda_total_inicial - (deuda_total_inicial / int(ano_fin_deuda))
                    else:
                        d_t = deudas[-1] - (deuda_total_inicial / int(ano_fin_deuda))
                else:
                    d_t = 0.0
                deudas.append(max(0.0, d_t))

            # Cuadro 2: Iteración cruzada de pesos y costos
            for t_idx in range(1, num_anos + 1):
                d_act = deudas[t_idx-1]
                e_act = equities[t_idx-1]
                de_sum = d_act + e_act
                deuda_equity.append(de_sum)
                
                wd = d_act / de_sum if de_sum > 0 else 0.0
                we = e_act / de_sum if de_sum > 0 else 0.0
                wds.append(wd)
                wes.append(we)
                
                b_ap = beta_u * (1 + (1 - T) * (d_act / e_act)) if e_act > 0 else beta_u
                betas_ap.append(b_ap)
                
                ke = rf + b_ap * rm_rf
                kes.append(ke)
                
                wacc_t = (kd_neto * wd) + (ke * we)
                waccs.append(wacc_t)
                
                if t_idx < num_anos:
                    de_sig = de_sum * (1 + wacc_t) - list_fcl[t_idx + 1]
                    equities.append(max(1.0, de_sig - deudas[t_idx]))

            # Cuadro 3: Descuento temporal
            mas_wacc = [1.0 + w for w in waccs]
            mas_wacc_act = []
            for idx, mw in enumerate(mas_wacc):
                mas_wacc_act.append(mw if idx == 0 else mw * mas_wacc_act[-1])
            factores_vp = [1.0 / mwa for mwa in mas_wacc_act]
            
            vp_fcl = sum(f * v for f, v in zip(list_fcl[1:], factores_vp))
            wacc_quinto = waccs[min(int(ano_fin_deuda)-1, len(waccs)-1)]
            vco = list_fcl[-1] * (1 + crecimiento) / (wacc_quinto - crecimiento) if (wacc_quinto - crecimiento) > 0 else 0.0
            vp_vco = vco * factores_vp[-1]
            
            val_mercado_patrimonio = (vp_fcl + vp_vco) + caja_0 - deuda_total_inicial
            return val_mercado_patrimonio - equity_trial, deudas, equities, deuda_equity, wds, wes, betas_ap, kes, waccs, factores_vp, vp_fcl, vp_vco

        # Calibrador de convergencia de circularidad
        eq_calc = patrimonio_0
        for _ in range(100):
            dif, deudas, equities, deuda_equity, wds, wes, betas_ap, kes, waccs, factores_vp, vp_fcl, vp_vco = resolver_estructuras(eq_calc)
            eq_calc += dif * 0.5
            if abs(dif) < 0.01:
                break

        # Llamado final calibrado
        dif, deudas, equities, deuda_equity, wds, wes, betas_ap, kes, waccs, factores_vp, vp_fcl, vp_vco = resolver_estructuras(eq_calc)

        # --- DESPLIEGUE CUADRO 1 ---
        st.subheader("📋 Cuadro 1: Estructura de Capital Variable")
        df_c1 = pd.DataFrame([deudas, equities, deuda_equity], index=["Deuda Financiera Total", "Equity (Valor Mercado)", "Deuda + Equity"], columns=anos_v)
        st.dataframe(df_c1.style.format("${:,.2f}"), width="stretch")

        # --- DESPLIEGUE CUADRO 2 ---
        st.subheader("📊 Cuadro 2: Variables de Costo Financiero (CAPM / WACC)")
        df_c2 = pd.DataFrame([[x*100 for x in wds], [x*100 for x in wes], betas_ap, [x*100 for x in kes], [x*100 for x in waccs]], 
                             index=["Wd (Peso Deuda %)", "We (Peso Equity %)", "Beta Apalancado", "Ke (Costo Capital %)", "WACC %"], columns=anos_v)
        st.dataframe(df_c2.style.format("{:,.2f}%").format({"Beta Apalancado": "{:,.2f}"}), width="stretch")

        # --- DESPLIEGUE CUADRO 3 ---
        st.subheader("💸 Cuadro 3: Valoración de Mercado de la Firma")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.dataframe(pd.DataFrame([list_fcl[1:], factores_vp], index=["Flujo Caja Libre", "Factor Descuento VP"], columns=anos_v).style.format("${:,.2f}").format({"Factor Descuento VP": "{:,.4f}"}), width="stretch")
        with col_m2:
            df_m = pd.DataFrame({"Monto": [vp_fcl, vp_vco, vp_fcl + vp_vco, caja_0, (vp_fcl + vp_vco) + caja_0, deuda_total_inicial, (vp_fcl + vp_vco) + caja_0 - deuda_total_inicial]},
                                index=["VP Flujos Proyectados", "VP Valor Continuidad (VCO)", "Valor Activos Operativos", "Caja Año 0", "Valor Mercado Total Activos", "Pasivo / Deuda Inicial", "VALOR MERCADO PATRIMONIO"])
            st.dataframe(df_m.style.format("${:,.2f}"), width="stretch")

        # --- CUADRO 4: CÁLCULO DEL EVA (VALOR ECONÓMICO AGREGADO) ---
        st.markdown("---")
        st.subheader("💎 Cuadro 4: Matriz de Generación de Valor Económico (EVA)")
        st.markdown("Cálculo del rendimiento real generado sobre los activos aplicados a la operación del proyecto.")

        list_inversion_eva = []
        list_roi = []
        list_eva = []

        for t_idx in range(1, num_anos + 1):
            # Inversión de cada año = Activo Fijo Neto + Capital de Trabajo Operativo
            inv_t = list_af_final[t_idx] + list_ct_actual[t_idx]
            list_inversion_eva.append(inv_t)
            
            # ROI = UAII * (1 - T) / Inversión
            uaii_t = proj_uaii[t_idx]
            nopat_t = uaii_t * (1 - T)
            roi_t = nopat_t / inv_t if inv_t > 0 else 0.0
            list_roi.append(roi_t * 100)
            
            # EVA = (ROI - WACC) * Inversión
            wacc_t = waccs[t_idx-1]
            eva_t = (roi_t - wacc_t) * inv_t
            list_eva.append(eva_t)

        df_eva = pd.DataFrame([list_inversion_eva, list_roi, [w*100 for w in waccs], list_eva],
                              index=["Inversión Operativa (AF + CT)", "ROI (Retorno de Inversión %)", "WACC Objetivo %", "💎 EVA (Valor Económico Agregado)"],
                              columns=anos_v)

        # Función para dar color dinámico a la fila de EVA
        def color_fila_eva(row):
            estilos = ['' for _ in row]
            if row.name == "💎 EVA (Valor Económico Agregado)":
                estilos = [f'background-color: #1b5e20; color: white; font-weight: bold;' if val >= 0 else f'background-color: #b71c1c; color: white; font-weight: bold;' for val in row]
            return estilos

        st.dataframe(df_eva.style.format("${:,.2f}").format({"ROI (Retorno de Inversión %)": "{:,.2f}%", "WACC Objetivo %": "{:,.2f}%"}).apply(color_fila_eva, axis=1), width="stretch")
