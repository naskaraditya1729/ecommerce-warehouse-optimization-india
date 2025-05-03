import pandas as pd
from tabulate import tabulate
import random
from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, LpStatus, PULP_CBC_CMD, LpContinuous
import sys
from datetime import datetime

def main():
    try:
        # --------------------------------------------------------------------------------
        # STEP 1: Load and validate input data
        # --------------------------------------------------------------------------------
        print("Loading data...")
        demand_df = pd.read_csv("Demand_points.csv")           # Demand data with pincode and demand values
        warehouse_df = pd.read_csv("Warehouse_points.csv")     # Potential warehouse locations
        distance_df = pd.read_csv("Distance_Matrix.csv")       # Distance from each warehouse to each pincode (Haversine matrix)

        # Ensure all demand pincodes exist in the distance matrix
        if not set(demand_df["pincode"]).issubset(set(distance_df["pincode"])):
            raise ValueError("Some demand pincodes are missing in the distance matrix")

        # --------------------------------------------------------------------------------
        # STEP 2: Define sets and parameters
        # --------------------------------------------------------------------------------
        # Warehouse names = all columns in distance matrix except the first two
        warehouse_names = [col for col in distance_df.columns if col not in ["pincode", "district"]]
        I = warehouse_names                     # List of warehouse candidates
        J = distance_df["pincode"].unique().tolist()  # List of demand pincodes

        # Demand per pincode
        demand = dict(zip(demand_df["pincode"], demand_df["Demand"]))

        # Distance dictionary: distance[(warehouse, pincode)]
        distance = {
            (i, j): distance_df.loc[distance_df["pincode"] == j, i].values[0]
            for i in I for j in J
        }

        # --------------------------------------------------------------------------------
        # STEP 3: Budget setup with random warehouse costs
        # --------------------------------------------------------------------------------
        n = len(I)          # Number of warehouse candidates
        N = 5               # Max number of warehouses to build

        # Random fixed cost per warehouse between ₹20–40 lakh
        F = [random.randint(2000000, 4000000) for _ in range(n)]

        # Create a table for console display
        warehouse_costs = [{"Warehouse": I[i], "Fixed_Cost (₹)": f"{F[i]:,}"} for i in range(len(I))]

        # Print formatted table
        print("\n📦 Fixed Costs of Warehouse Candidates:\n")
        print(tabulate(warehouse_costs, headers="keys", tablefmt="pretty"))

        # Save the generated fixed costs per warehouse to a CSV
        warehouse_costs_df = pd.DataFrame({
            "Warehouse": I,
            "Fixed_Cost": F
        })
        warehouse_costs_df.to_csv("Warehouse_Fixed_Costs.csv", index=False)
        print("Saved: Warehouse_Fixed_Costs.csv")

        # Ensure budget is realistic:
        sorted_list = sorted(F)
        sum_first_N = sum(sorted_list[:N])  # Minimum cost to build N cheapest warehouses
        max_num = sum(F)                    # Max possible cost if all are built
        B = random.randint(sum_first_N, max_num)  # Budget chosen randomly in valid range
        print('Maximum budget for setting up is assumed to be: ', B)

        max_warehouses = N

        # --------------------------------------------------------------------------------
        # STEP 4: Time and cost assumptions
        # --------------------------------------------------------------------------------
        rate = 1.775       # Assumed transport cost per km
        Avg_speed = 50     # Assumed average delivery speed (km/h)

        # Compute T_max = tight time threshold based on distance
        numeric_distances = distance_df.drop(columns=["pincode", "district"])
        T_max = (numeric_distances.max().max() - 2000) / Avg_speed  # Reasonable time limit
        print('Maximum delivery time limit:', T_max)

        # --------------------------------------------------------------------------------
        # STEP 5: Build optimization model
        # --------------------------------------------------------------------------------
        print("Building optimization model...")
        model = LpProblem("Warehouse_Location_Optimization", LpMinimize)

        # Decision variables
        x = {i: LpVariable(f"x_{i}", cat=LpBinary) for i in I}                       # Open warehouse
        y = {(i,j): LpVariable(f"y_{i}_{j}", lowBound=0, upBound=1, cat=LpContinuous) for i in I for j in J}   # Assign warehouse to pincode

        # --------------------------------------------------------------------------------
        # STEP 6: Add constraints
        # --------------------------------------------------------------------------------

        # 1. Each demand point must be fully served
        for j in J:
            model += lpSum(y[(i, j)] for i in I) == 1, f"Demand_assignment_{j}"

        # 2. Demand can only be assigned to open warehouses
        for i in I:
            for j in J:
                model += y[(i, j)] <= x[i], f"Warehouse_link_{i}_{j}"

        # 3. Budget constraint
        model += lpSum(x[I[i]] * F[i] for i in range(n)) <= B, "Budget_constraint"

        # 4. Maximum N warehouses must be opened
        model += lpSum(x[i] for i in I) <= max_warehouses, "Max_warehouses"

        # 5. Max delivery time constraint for each demand point
        for j in J:
            model += lpSum((distance[(i, j)] / Avg_speed) * y[(i, j)] for i in I) <= T_max, f"MaxDeliveryTime_{j}"

        # --------------------------------------------------------------------------------
        # STEP 7: Objective function
        # --------------------------------------------------------------------------------
        model += (
            lpSum(rate * distance[(i, j)] * demand[j] * y[(i, j)] for i in I for j in J) +  # Transport cost
            lpSum(x[I[i]] * F[i] for i in range(n))  # Setup cost
        ), "Total_transportation_cost"

        # --------------------------------------------------------------------------------
        # STEP 8: Solve the model
        # --------------------------------------------------------------------------------
        print("Solving model...")
        status = model.solve(PULP_CBC_CMD(msg=False))  # Silent solve

        if LpStatus[model.status] != "Optimal":
            raise RuntimeError(f"Solver failed with status: {LpStatus[model.status]}")

        print(f"\nOptimization successful at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total cost: {model.objective.value():,.2f} (including transport and setup)")

        # --------------------------------------------------------------------------------
        # STEP 9: Extract and save results
        # --------------------------------------------------------------------------------

        # 1. Selected warehouse locations
        selected_warehouses = [i for i in I if x[i].value() == 1]
        pd.DataFrame({"Warehouse": selected_warehouses}).to_csv("Selected_Warehouses.csv", index=False)

        # 2. Demand assignments
        allocations = pd.DataFrame(
            [(j, i, y[(i, j)].value()) for j in J for i in I if y[(i, j)].value() > 0.01],
            columns=["Pincode", "Warehouse", "Allocation"]
        )

        # Add demand and cost info
        allocations["Demand"] = allocations["Pincode"].map(demand)
        allocations["Distance"] = allocations.apply(lambda row: distance[(row["Warehouse"], row["Pincode"])], axis=1)
        allocations["WeightedCost"] = allocations["Demand"] * allocations["Distance"] * allocations["Allocation"]

        allocations.to_csv("Demand_Allocations.csv", index=False)

        # Output summary
        print("\nSelected warehouses:")
        for wh in selected_warehouses:
            print(f"- {wh}")

        print("\nResults saved to Selected_Warehouses.csv and Demand_Allocations.csv")
        return True

    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
