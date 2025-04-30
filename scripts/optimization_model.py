import pandas as pd
from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, lpSum, LpStatus, PULP_CBC_CMD
import sys
from datetime import datetime

def main():
    try:
        # Load and validate data
        print("Loading data...")
        demand_df = pd.read_csv("Demand_points.csv")
        warehouse_df = pd.read_csv("Warehouse_points.csv")
        distance_df = pd.read_csv("Distance_Matrix.csv")

        # Data validation
        if not set(demand_df["pincode"]).issubset(set(distance_df["pincode"])):
            raise ValueError("Some demand pincodes are missing in distance matrix")

        # Define sets
        warehouse_names = [col for col in distance_df.columns
                         if col not in ["pincode", "district"]]
        I = warehouse_names
        J = distance_df["pincode"].unique().tolist()  # Ensure unique pincodes

        # Parameters
        demand = dict(zip(demand_df["pincode"], demand_df["Demand"]))
        distance = {
            (i, j): distance_df.loc[distance_df["pincode"] == j, i].values[0]
            for i in I for j in J
        }
        max_warehouses = 5

        # Model setup
        print("Building optimization model...")
        model = LpProblem("Warehouse_Location_Optimization", LpMinimize)

        # Variables
        x = {i: LpVariable(f"x_{i}", cat=LpBinary) for i in I}
        y = {(i, j): LpVariable(f"y_{i}_{j}", cat=LpBinary) for i in I for j in J}

        # Constraints
        for j in J:
            model += lpSum(y[(i, j)] for i in I) == 1, f"Demand_assignment_{j}"

        for i in I:
            for j in J:
                model += y[(i, j)] <= x[i], f"Warehouse_link_{i}_{j}"

        model += lpSum(x[i] for i in I) == max_warehouses, "Max_warehouses"  # Changed to ==

        # Objective
        model += lpSum(
            distance[(i, j)] * demand[j] * y[(i, j)]
            for i in I for j in J
        ), "Total_transportation_cost"

        # Solve
        print("Solving model...")
        status = model.solve(PULP_CBC_CMD(msg=False))  # Silent mode

        # Results handling
        if LpStatus[model.status] != "Optimal":
            raise RuntimeError(f"Solver failed with status: {LpStatus[model.status]}")

        print(f"\nOptimization successful at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total cost: {model.objective.value():,.2f} demand-km")

        # Prepare results
        selected_warehouses = [i for i in I if x[i].value() == 1]
        allocations = pd.DataFrame(
            [(j, i, y[(i, j)].value())
             for j in J for i in I if y[(i, j)].value() > 0.01],
            columns=["Pincode", "Warehouse", "Allocation"]
        )

        print("\nSelected warehouses:")
        for wh in selected_warehouses:
            print(f"- {wh}")

        # Save outputs
        pd.DataFrame({"Warehouse": selected_warehouses}).to_csv(
            "Selected_Warehouses.csv", index=False
        )
        allocations["Demand"] = allocations["Pincode"].map(demand)
        allocations["Distance"] = allocations.apply(
            lambda row: distance[(row["Warehouse"], row["Pincode"])], axis=1
        )
        allocations["WeightedCost"] = (
            allocations["Demand"] * allocations["Distance"] * allocations["Allocation"]
        )
        allocations.to_csv("Demand_Allocations.csv", index=False)

        print("\nResults saved to Selected_Warehouses.csv and Demand_Allocations.csv")
        return True

    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
