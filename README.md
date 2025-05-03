# 📦 E-commerce Warehouse Location Optimization in India

## 📌 Objective  
Develop an optimization model to determine the best locations for warehouses across India, aiming to minimize total delivery cost and time under real-world constraints like limited budget and delivery time thresholds. This is a statistical optimization project using **mixed-integer programming** techniques and geospatial analysis.

---

## 👥 Team Members
- **Aditya Naskar**  
- **Sujit Kumar Nayak**  
- **Komineni Dhanunjaya Naidu**

---

## 🧰 Tools & Technologies Used

### 🧮 Data Collection & Processing
- **R** (`tidyverse`, `readr`, `dplyr`)  
  - Cleaned and filtered raw geographic and sales data  
  - Computed Haversine distances between demand and warehouse points  
  - Selected top 20 districts as warehouse candidates  
  - Output prepared as `Demand_points.csv`, `Warehouse_points.csv`, `Distance_Matrix.csv`

- **Python** (`pandas`, `numpy`, `PuLP`, `geopandas`, `folium`)  
  - MILP formulation with budget, time, and assignment constraints  
  - Optimization using the open-source CBC solver  
  - Extracted results and created interactive visualization

### 📈 Optimization
- **Mixed-Integer Linear Programming (MILP)** with `PuLP`
- **CBC Solver** (default solver in PuLP)

### 🗺️ Visualization
- **Folium + GeoPandas + Shapely**  
  - Blue gradient-coded demand points  
  - Red markers for potential/selected warehouses  
  - Violet dotted paths for demand assignment  
  - Custom interactive map with legend

### 📝 Reporting & Reproducibility
- **Quarto** (with LaTeX support) for PDF/HTML report  
- **Git + GitHub** for version control and collaboration  
- Supports deployment via **GitHub Pages** for interactive HTML outputs

---

## 🗂️ Key Files

| File                     | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| `Demand_points.csv`      | Cleaned demand data by pincode                               |
| `Warehouse_points.csv`   | Top 20 warehouse candidate locations                         |
| `Distance_Matrix.csv`    | Pairwise Haversine distances (km)                            |
| `optimisation_model.py`  | MILP model code with budget and time constraints             |
| `Demand_Allocations.csv` | Final allocation of demand points to warehouses              |
| `warehouse_optimization_map.html` | Interactive map of final optimized solution        |
| `project_report.qmd`     | Full technical report (Quarto source)                        |
| `project_report.html/pdf`| Rendered report in HTML or PDF format                        |

---
## How to View the Project Files

1. **Download and Extract**  
   Download the `report.zip` file to your local machine and extract it. This will create a folder named `report`.

2. **View the Interactive Map**  
   Open the extracted `report` folder and double-click on `warehouse_optimisation_map.html` to view the interactive map plot.

3. **View the Project Report**  
   To view the original HTML version of the project report, open `project_report.html` in the same directory.
