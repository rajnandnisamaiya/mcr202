import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os

# Page configuration
st.set_page_config(
    page_title="ThermoCp | Interactive Cp(T) Materials Database",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for professional NIST/MatWeb engineering aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .warning-box {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        color: #991B1B;
        margin-bottom: 1rem;
    }
    .valid-box {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        color: #166534;
        margin-bottom: 1rem;
    }
    .badge-est {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-lit {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load Database
@st.cache_data
def load_database():
    try:
        from materials_data import MATERIALS_DATA
        return pd.DataFrame(MATERIALS_DATA)
    except Exception:
        pass

    possible_paths = [
        "materials_database.json",
        os.path.join(os.path.dirname(__file__), "materials_database.json"),
        "/Users/sonam/Downloads/raju/materials_database.json"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                return df
    st.error("Database file 'materials_database.json' not found!")
    return pd.DataFrame()

df_materials = load_database()

# Vectorized Maier-Kelley calculation function: Cp(T) = a + b*T + c/T^2
def calculate_cp_mk(T_array, a, b, c):
    """
    Evaluates Maier-Kelley Equation: Cp(T) = a + b*T + c/T^2
    """
    T = np.asarray(T_array, dtype=float)
    T_safe = np.maximum(T, 1.0)
    return a + (b * T_safe) + (c / (T_safe**2))

# Header Title
st.markdown("<div class='main-header'>🔥 ThermoCp | Interactive Cp(T) Database</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Maier-Kelley thermodynamic heat capacity database & curve evaluator for 200 engineering materials</div>", unsafe_allow_html=True)

if df_materials.empty:
    st.stop()

# Sidebar Navigation & Controls
st.sidebar.header("🎯 Navigation & Controls")

# Category Filter
categories = ["All Categories"] + sorted(df_materials["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Filter Category", categories)

if selected_category != "All Categories":
    filtered_df = df_materials[df_materials["category"] == selected_category]
else:
    filtered_df = df_materials

# Material Selection
available_materials = filtered_df["name"].tolist()

default_mats = [m for m in ["Iron", "Aluminum", "Alumina", "Silicon"] if m in available_materials]
if not default_mats and available_materials:
    default_mats = [available_materials[0]]

selected_mats = st.sidebar.multiselect(
    "Select Material(s) for Comparison",
    options=available_materials,
    default=default_mats,
    help="Select one or more materials to plot and compare Cp(T) curves."
)

# Plot Temperature Range
st.sidebar.subheader("🌡️ Plot Temperature Range (K)")
col_t1, col_t2 = st.sidebar.columns(2)
t_min_input = col_t1.number_input("T Min (K)", min_value=1, max_value=4500, value=200, step=25)
t_max_input = col_t2.number_input("T Max (K)", min_value=10, max_value=5000, value=1500, step=50)

if t_min_input >= t_max_input:
    st.sidebar.error("T Min must be less than T Max!")
    t_max_input = t_min_input + 500

# Unit Basis Selection
st.sidebar.subheader("📐 Display Unit Basis")
unit_choice = st.sidebar.radio(
    "Select Cp Unit Basis",
    ["Molar Specific Heat (J/mol·K)", "Mass Specific Heat (J/kg·K)", "Mass Specific Heat (kJ/kg·K)"],
    help="Choose unit basis for Maier-Kelley coefficients (a, b, c) and plots."
)

if "J/mol·K" in unit_choice:
    unit_symbol = "J/mol·K"
    a_col, b_col, c_col = "a_molar", "b_molar", "c_molar"
elif "kJ/kg·K" in unit_choice:
    unit_symbol = "kJ/kg·K"
    a_col, b_col, c_col = "a_kJ", "b_kJ", "c_kJ"
else:
    unit_symbol = "J/kg·K"
    a_col, b_col, c_col = "a", "b", "c"

# Query Temperature Slider
st.sidebar.subheader("🔍 Single Temperature Query (K)")
query_T = st.sidebar.slider("Query Temperature (K)", min_value=int(t_min_input), max_value=int(t_max_input), value=500, step=10)

# Main App Layout
tab_graph, tab_ranking, tab_info, tab_db = st.tabs([
    "📈 Cp-T Plot & Validity", 
    "📊 Temperature Ranking", 
    "📋 Material Info & Maier-Kelley Coefficients", 
    "🗃️ Raw Database Table"
])

# --- TAB 1: GRAPH & VALIDITY ENFORCEMENT ---
with tab_graph:
    if not selected_mats:
        st.warning("Please select at least one material from the sidebar to display the Cp vs. Temperature graph.")
    else:
        fig = go.Figure()
        T_vals = np.linspace(t_min_input, t_max_input, 300)
        validity_warnings = []
        
        for mat_name in selected_mats:
            row = df_materials[df_materials["name"] == mat_name].iloc[0]
            
            a_val = row[a_col]
            b_val = row[b_col]
            c_val = row[c_col]
            v_min = row["valid_t_min"]
            v_max = row["valid_t_max"]
            
            cp_plot = calculate_cp_mk(T_vals, a_val, b_val, c_val)
            
            is_query_valid = (v_min <= query_T <= v_max)
            if not is_query_valid:
                validity_warnings.append(
                    f"⚠️ **{mat_name}**: Query T ({query_T} K) is outside valid range ({v_min:.0f}–{v_max:.0f} K). Values are extrapolated!"
                )
            
            formula_str = f" ({row['formula']})" if row['formula'] else ""
            fig.add_trace(go.Scatter(
                x=T_vals,
                y=cp_plot,
                mode='lines',
                name=f"{mat_name}{formula_str}",
                hovertemplate=(
                    f"<b>{mat_name}</b>{formula_str}<br>" +
                    "Temperature: %{x:.1f} K<br>" +
                    f"Cp: %{{y:.2f}} {unit_symbol}<br>" +
                    f"Valid Window: {v_min:.0f}–{v_max:.0f} K<br>" +
                    "<extra></extra>"
                ),
                line=dict(width=3)
            ))
            
            if v_min > t_min_input:
                fig.add_vrect(
                    x0=t_min_input, x1=min(v_min, t_max_input),
                    fillcolor="rgba(200, 200, 200, 0.15)",
                    line_width=0,
                    annotation_text=f"{mat_name} Extrapolation (<{v_min:.0f}K)",
                    annotation_position="top left",
                    annotation_font=dict(size=10, color="gray")
                )
            if v_max < t_max_input:
                fig.add_vrect(
                    x0=max(v_max, t_min_input), x1=t_max_input,
                    fillcolor="rgba(200, 200, 200, 0.15)",
                    line_width=0,
                    annotation_text=f"{mat_name} Extrapolation (>{v_max:.0f}K)",
                    annotation_position="top right",
                    annotation_font=dict(size=10, color="gray")
                )

        fig.add_vline(
            x=query_T,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Query T = {query_T} K",
            annotation_position="top",
            annotation_font=dict(color="red", size=12)
        )

        fig.update_layout(
            title=f"Specific Heat Capacity (Cp) vs. Temperature (T) [Maier-Kelley Model: Cp = a + bT + c/T²]",
            xaxis_title="Temperature, T (K)",
            yaxis_title=f"Specific Heat Capacity, Cp ({unit_symbol})",
            template="plotly_white",
            hovermode="x unified",
            height=580,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        if validity_warnings:
            st.markdown("### ⚠️ Validity Range Alerts")
            for w in validity_warnings:
                st.markdown(f"<div class='warning-box'>{w}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='valid-box'>✅ All selected materials are within their validated temperature ranges at Query T = {query_T} K.</div>", unsafe_allow_html=True)

        st.markdown("### 🔍 Live Cp Values at Query Temperature")
        lookup_data = []
        for mat_name in selected_mats:
            row = df_materials[df_materials["name"] == mat_name].iloc[0]
            cp_val = calculate_cp_mk(query_T, row[a_col], row[b_col], row[c_col])
            is_valid = (row["valid_t_min"] <= query_T <= row["valid_t_max"])
            
            lookup_data.append({
                "Material": row["name"],
                "Formula": row["formula"],
                "Category": row["category"],
                f"Cp @ {query_T} K ({unit_symbol})": round(float(cp_val), 3),
                "Valid Range (K)": f"{row['valid_t_min']:.0f} - {row['valid_t_max']:.0f}",
                "Fit Quality (R²)": f"{row['fit_r2']:.4f}",
                "Status": "✅ Valid" if is_valid else "⚠️ Extrapolated"
            })
            
        st.dataframe(pd.DataFrame(lookup_data), use_container_width=True)

# --- TAB 2: RANKING AT CUSTOM T ---
with tab_ranking:
    st.markdown(f"### 📊 Material Ranking by Specific Heat Capacity at T = {query_T} K")
    st.info("💡 **Engineering Note**: Heat capacity dictates thermal energy storage. Materials evaluated dynamically using Maier-Kelley formulation $C_p = a + bT + c/T^2$.")
    
    rank_scope = st.radio("Ranking Scope", ["Selected Materials Only", f"All Materials in {selected_category}"])
    
    if rank_scope == "Selected Materials Only":
        rank_df = df_materials[df_materials["name"].isin(selected_mats)].copy()
    else:
        rank_df = filtered_df.copy()
        
    if rank_df.empty:
        st.warning("No materials available for ranking under current filters.")
    else:
        cp_val_list = []
        valid_status = []
        
        for _, r in rank_df.iterrows():
            cp_val = calculate_cp_mk(query_T, r[a_col], r[b_col], r[c_col])
            cp_val_list.append(round(float(cp_val), 3))
            valid_status.append(r["valid_t_min"] <= query_T <= r["valid_t_max"])
            
        rank_df["Cp_value"] = cp_val_list
        rank_df["Valid"] = valid_status
        
        rank_sorted = rank_df.sort_values(by="Cp_value", ascending=False).reset_index(drop=True)
        
        fig_rank = go.Figure()
        fig_rank.add_trace(go.Bar(
            x=rank_sorted["Cp_value"],
            y=rank_sorted["name"],
            orientation='h',
            marker=dict(
                color=rank_sorted["Cp_value"],
                colorscale='Viridis'
            ),
            text=rank_sorted["Cp_value"],
            textposition='auto'
        ))
        fig_rank.update_layout(
            title=f"Top Materials Ranked by Cp ({unit_symbol}) @ {query_T} K",
            xaxis_title=f"Cp ({unit_symbol})",
            yaxis=dict(autorange="reversed"),
            height=max(400, len(rank_sorted) * 22),
            template="plotly_white"
        )
        st.plotly_chart(fig_rank, use_container_width=True)

# --- TAB 3: MATERIAL INFO & MAIER-KELLEY COEFFICIENTS ---
with tab_info:
    st.markdown("### 📋 Maier-Kelley Equation Parameters & Material Data")
    st.markdown(r"**Maier-Kelley Equation**: $C_p(T) = a + b T + \frac{c}{T^2}$")
    
    if not selected_mats:
        st.info("Select materials in the sidebar to view detailed parameters.")
    else:
        for m_name in selected_mats:
            row = df_materials[df_materials["name"] == m_name].iloc[0]
            
            formula_tag = f" ({row['formula']})" if row['formula'] else ""
            with st.expander(f"📌 {row['name']}{formula_tag} — {row['category']}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Formula**: `{row['formula']}`")
                    st.markdown(f"**Category**: {row['category']}")
                    if row['molar_mass']:
                        st.markdown(f"**Molar Mass**: {row['molar_mass']} g/mol")
                    st.markdown(f"**Data Source**: `{row['data_source']}`")
                    
                with col2:
                    st.markdown(f"**Valid T Range**: {row['valid_t_min']:.0f} K – {row['valid_t_max']:.0f} K")
                    st.markdown(f"**Fit Quality (R²)**: `{row['fit_r2']:.6f}`")
                    est_badge = "<span class='badge-est'>Estimated Parameter Fit</span>" if row['estimated'] else "<span class='badge-lit'>Literature JANAF / NIST Sourced</span>"
                    st.markdown(f"**Fit Status**: {est_badge}", unsafe_allow_html=True)
                    
                with col3:
                    st.markdown(f"**Maier-Kelley Coefficients ({unit_symbol})**:")
                    a_val = row[a_col]
                    b_val = row[b_col]
                    c_val = row[c_col]
                    st.latex(r"a = " + f"{a_val}")
                    st.latex(r"b = " + f"{b_val:.6e}")
                    st.latex(r"c = " + f"{c_val}")

# --- TAB 4: RAW DATABASE ---
with tab_db:
    st.markdown("### 🗃️ Complete 200-Material Database Table")
    excluded_cols = ['a', 'b', 'c', 'a_molar', 'b_molar', 'c_molar', 'a_kJ', 'b_kJ', 'c_kJ', 'fit_r2']
    df_display = df_materials[[c for c in df_materials.columns if not c.startswith('_') and c not in excluded_cols]]
    st.dataframe(df_display, use_container_width=True)
    
    csv_bytes = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Complete Database as CSV",
        data=csv_bytes,
        file_name="materials_database.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("👨‍🔬 **ThermoCp Project** | Developed for College Materials Engineering Thermodynamics Assignment.")
