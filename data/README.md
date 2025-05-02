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
  ```
  +--------+---------+----------+-----------+--------+
  | pincode| district| latitude | longitude | Demand |
  +--------+---------+----------+-----------+--------+
  | 516356 | Y.S.R.  | 14.71833 | 78.66676  |   3    |
  | 516356 | Y.S.R.  | 14.77071 | 78.66351  |   3    |
  | 516175 | Y.S.R.  | 14.92793 | 78.62389  |   1    |
  +--------+---------+----------+-----------+--------+
  ```

- `Warehouse_points.csv`: Candidate warehouse locations with coordinates
  ```
  +----------------+------------+------------------+------------------+
  | district       | TotalDemand| Latitude         | Longitude        |
  +----------------+------------+------------------+------------------+
  | BENGALURU URBAN| 31343      | 12.9358502891188 | 77.5818111190038 |
  | PUNE           | 15479      | 18.5898385005948 | 73.8826938710409 |
  | THANE          | 13018      | 19.2681331497409 | 72.9476622088083 |
  +----------------+------------+------------------+------------------+
  ```

- `Distance_Matrix.csv`: Distances between demand points and warehouse candidates
  ```
  +--------+---------+----------------+----------+-------------+------------+
  | pincode| district| BENGALURU URBAN| -------- | THANE       | MUMBAI     |
  +--------+---------+----------------+----------+-------------+------------+
  | 516356 | Y.S.R.  | 230.230205     | -------- | 667.028635  | 790.913207 |
  | 516356 | Y.S.R.  | 235.081966     | -------- | 662.968110  | 786.871875 |
  | 516175 | Y.S.R.  | 248.421315     | -------- | 648.464265  | 772.398190 |
  +--------+---------+----------------+----------+-------------+------------+
  ```

- `Warehouse_Fixed_Costs.csv`: Setup costs for each warehouse candidate
  ```
  +----------------+------------+
  | Warehouse      | Fixed_Cost |
  +----------------+------------+
  | BENGALURU URBAN| 3676046    |
  | PUNE           | 2477628    |
  | THANE          | 3697904    |
  +----------------+------------+
  ```

- `Selected_Warehouses.csv`: Optimal warehouse locations from solution
  ```
  +-------------------+
  | Warehouse         |
  +-------------------+
  | BENGALURU URBAN   |
  | MUMBAI SUBURBAN   |
  | HYDERABAD         |
  | 24 PARAGANAS NORTH|
  | SOUTH             |
  +-------------------+
  ```
  
- `Demand_Allocations.csv`: Assignment of demand points to warehouses
  ```
  +--------+----------------+------------+--------+------------------+---------------+
  | Pincode| Warehouse      | Allocation | Demand | Distance         | WeightedCost  |
  +--------+----------------+------------+--------+------------------+---------------+
  | 516356 | BENGALURU URBAN| 1.0        | 3      | 230.230205429288 | 690.690616288 |
  | 516175 | BENGALURU URBAN| 1.0        | 1      | 248.421314557407 | 248.421314557 |
  | 516434 | BENGALURU URBAN| 1.0        | 8      | 226.053445308177 | 1808.42756247 |
  +--------+----------------+------------+--------+------------------+---------------+
  ```

- `Map.zip`: Zip file containing visualization of the optimization solution
