# Interactive $C_p(T)$ Materials Database & Computational Evaluator

An interactive computational platform developed for engineering thermodynamics to evaluate, plot, analyze, and rank the variation of specific heat capacity at constant pressure ($C_p$) with temperature ($T$) across **200 engineering materials**.

---

## Project Overview

Specific heat capacity ($C_p$) is a fundamental thermodynamic property governing heat storage, thermal management, and energy transfer in materials processing. **ThermoCp** provides a dynamic computational platform powered by the **Maier-Kelley Empirical Equation**:

$$C_p(T) = a + b \cdot T + \frac{c}{T^2}$$

The platform incorporates literature-sourced data (NIST-JANAF Thermochemical Tables, MatWeb, NIMS AtomWork, AZoM) with dynamic unit conversion, temperature validity enforcement, multi-material curve comparison, live temperature ranking, and full database exports.

---

## Key Features

1. **200-Material Database**:
   - Covers 8 engineering material classes: **Metals & Alloys**, **Ceramics**, **Semiconductors**, **Polymers**, **Glasses**, **Refractories**, **Composites**, and **Other**.

2. **Maier-Kelley Thermodynamic Evaluator**:
   - Evaluates specific heat capacity using empirical parameters ($a, b, c$) derived via least-squares fitting over validated temperature bounds ($R^2 > 99\%$).
   - Dynamic unit switching:
     - **Molar Specific Heat**: $\text{J/mol}\cdot\text{K}$
     - **Mass Specific Heat**: $\text{J/kg}\cdot\text{K}$
     - **Mass Specific Heat**: $\text{kJ/kg}\cdot\text{K}$

3. **Temperature Validity Enforcement**:
   - Visualizes each material's validated temperature range ($T_{\min} - T_{\max}$).
   - Automatically shades extrapolation zones on charts and displays alerts when query temperature exceeds literature bounds.

4. **Multi-Material Comparison & Plotting**:
   - Interactive Plotly visualization comparing up to 5 materials simultaneously with unified hover inspection and dynamic legend controls.

5. **Live Temperature Probe & Material Ranking**:
   - Real-time slider to probe heat capacity values at any custom temperature ($T_{\text{query}}$).
   - Dynamic bar chart ranking materials by heat capacity ($C_p$).

6. **Raw Data Inspection & CSV Export**:
   - Searchable raw database table with one-click CSV export functionality.

---

## Thermodynamic Formulation

### Maier-Kelley Equation
The specific heat capacity at constant pressure is evaluated as:
$$C_p(T) = a + b \cdot T + \frac{c}{T^2}$$

- **$a$**: Constant term ($\text{J/mol}\cdot\text{K}$ or $\text{J/kg}\cdot\text{K}$)
- **$b$**: Linear temperature coefficient ($\text{J/mol}\cdot\text{K}^2$ or $\text{J/kg}\cdot\text{K}^2$)
- **$c$**: Inverse-square temperature coefficient ($\text{J}\cdot\text{K}/\text{mol}$ or $\text{J}\cdot\text{K}/\text{kg}$)

---

## Repository & Directory Structure

```text
mcr202/
├── app.py                   # Streamlit web application & interactive UI
├── materials_data.py        # Python module containing 200 materials database
├── materials_database.json  # Complete 200-material JSON dataset
├── materials_database.csv   # Exportable CSV database file
└── README.md                # Project documentation
```

---

## Getting Started

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system along with the required libraries:

```bash
pip install streamlit pandas numpy plotly
```

### 2. Running the Application
Navigate to the project folder and launch the Streamlit server:

```bash
cd /Users/sonam/Downloads/raju
streamlit run app.py
```

The application will launch automatically in your web browser at:
`http://localhost:8501`

---

## Database Summary

| Material Class | Count | Key Example Materials |
| :--- | :---: | :--- |
| **Metals & Alloys** | 47 | Iron ($\text{Fe}$), Aluminum ($\text{Al}$), Copper ($\text{Cu}$), Stainless Steel 304, Inconel 718 |
| **Ceramics** | 30 | Alumina ($\text{Al}_2\text{O}_3$), Zirconia ($\text{ZrO}_2$), Silicon Carbide ($\text{SiC}$), Magnetite |
| **Semiconductors** | 20 | Silicon ($\text{Si}$), Germanium ($\text{Ge}$), Gallium Arsenide ($\text{GaAs}$), Indium Phosphide |
| **Polymers** | 25 | Polyethylene (HDPE), Polypropylene, PVC, PTFE (Teflon), Nylon 6,6 |
| **Glasses** | 15 | Borosilicate Glass (Pyrex), Fused Quartz, Soda-Lime Glass, E-Glass Fiber |
| **Refractories** | 15 | Magnesite Brick ($\text{MgO}$), Fireclay Brick, Silica Brick, Zirconia Refractory |
| **Composites** | 20 | Carbon Fiber Composite (CFRP), GFRP, Kevlar/Epoxy, Cermet ($\text{WC-Co}$) |
| **Other** | 28 | Water, Ice, Titanium Nitride ($\text{TiN}$), Uranium Dioxide ($\text{UO}_2$), Graphite |
| **Total** | **200** | |

---

## Authors & Acknowledgment

Developed By Rajnandni Samaiya (25035054) for College Engineering Materials & Thermodynamics Assignment. 
Data curated from NIST-JANAF Thermochemical Tables, NIST Chemistry WebBook, and literature sources.
