# --------------------------------------------------------------------------------
# Load required packages (install if missing)
# 'tidyverse' is a collection of packages for data manipulation (dplyr, ggplot2, etc.)
# --------------------------------------------------------------------------------
if (!require("tidyverse")) install.packages("tidyverse")
library(tidyverse)

# --------------------------------------------------------------------------------
# STEP 1: Read and clean the pincode-level location dataset
# This dataset contains geographic information for delivery areas across India.
# We select only the useful columns and remove rows with missing values.
# --------------------------------------------------------------------------------

CleanData <- read_csv("pin code data warehouse optimisation.csv", show_col_types = FALSE) %>%
  select(pincode, district, latitude, longitude) %>%  # Keep relevant columns
  drop_na()  # Remove rows with NA values

# --------------------------------------------------------------------------------
# STEP 2: Process the Amazon sales dataset to extract e-commerce demand
# The sales data is grouped by pincode, and total quantity sold is calculated
# to represent demand per pincode.
# --------------------------------------------------------------------------------

pincode_demand <- read.csv("Amazon Sale Report.csv") %>%
  group_by(ship.postal.code) %>%  # Group by shipping pincode
  summarise(Demand = sum(Qty, na.rm = TRUE)) %>%  # Total quantity = demand
  drop_na() %>%  # Remove incomplete records
  rename(pincode = ship.postal.code)  # Rename to match CleanData for joining

# --------------------------------------------------------------------------------
# STEP 3: Merge demand data with location data using pincode as the key
# This creates a unified dataset: pincode, district, lat, long, and demand.
# --------------------------------------------------------------------------------

final_data <- inner_join(CleanData, pincode_demand, by = "pincode")

# --------------------------------------------------------------------------------
# STEP 4: Save the demand points dataset
# This dataset will be used for demand side in optimization and distance calculation.
# --------------------------------------------------------------------------------

write.csv(final_data, "Demand_points.csv", row.names = FALSE)

# --------------------------------------------------------------------------------
# STEP 5: Aggregate demand by district to identify potential warehouse hub locations
# For each district, we calculate total demand and the average geographic center.
# --------------------------------------------------------------------------------

district_data <- final_data %>%
  group_by(district) %>%
  summarise(
    TotalDemand = sum(Demand, na.rm = TRUE),  # Sum all demand for the district
    Latitude = mean(latitude, na.rm = TRUE),  # Average lat-long as center of district
    Longitude = mean(longitude, na.rm = TRUE)
  )

# --------------------------------------------------------------------------------
# STEP 6: Select the top 20 districts by demand as possible warehouse candidates
# These are the highest-demand areas where warehouses are likely to be effective.
# --------------------------------------------------------------------------------

hub_candidates <- district_data %>%
  arrange(desc(TotalDemand)) %>%  # Sort districts by descending demand
  slice(1:20)  # Select the top 20 as warehouse hub candidates

# --------------------------------------------------------------------------------
# STEP 7: Save the selected warehouse candidate locations to CSV
# This file will be used in the optimization model to define candidate sites.
# --------------------------------------------------------------------------------

write.csv(hub_candidates, "Warehouse_points.csv", row.names = FALSE)
