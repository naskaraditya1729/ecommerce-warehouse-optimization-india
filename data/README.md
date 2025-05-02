# E-commerce Warehouse Location Optimization in India

This project implements a mixed-integer linear programming model to determine optimal warehouse locations for e-commerce operations across India. The model minimizes delivery costs while meeting time constraints and budget limitations.

## Calculation Methodology

The optimization model was formulated and solved through the following approach:

1. **Demand Estimation**: Used Amazon sales data to estimate demand at pincode level across India.

2. **Warehouse Candidates**: Selected top 20 districts with highest demand as potential warehouse locations.

3. **Distance Calculation**: Created a distance matrix between all demand points and warehouse candidates using the Haversine formula:
   ```
   a = sin²(Δφ/2) + cos(φ₁) · cos(φ₂) · sin²(Δλ/2)
   Distance = R · 2 · arctan2(√a, √(1-a))
   ```
   where R is Earth's radius (6371 km).

4. **Cost Parameters**:
   - Fixed setup costs randomly generated between ₹20-40 lakhs per warehouse
   - Delivery cost calculated at ₹1.775 per kilometer
   - Budget constraint dynamically set to ensure feasibility

5. **Time Constraints**: Converted distances to delivery time using 50 km/h average speed, with maximum delivery time set by:
   ```
   Tmax = (max_distance - 2000) / 50
   ```

6. **Optimization Solution**: Implemented in Python using PuLP library with CBC solver to determine:
   - Which warehouses to activate (binary decision)
   - How to allocate demand points to warehouses (fractional assignment)

## Files Description

- `Demand_points.csv`: Pincode-level demand data with geographic coordinates
- `Warehouse_points.csv`: Candidate warehouse locations with coordinates
- `Distance_Matrix.csv`: Distances between demand points and warehouse candidates
- `Warehouse_Fixed_Costs.csv`: Setup costs for each warehouse candidate
- `Selected_Warehouses.csv`: Optimal warehouse locations from solution
- `Demand_Allocations.csv`: Assignment of demand points to warehouses
- `Map.zip`: Visualization of the optimization solution 
