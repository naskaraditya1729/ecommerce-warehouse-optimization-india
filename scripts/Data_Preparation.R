# Load required packages (install if missing)
if (!require("tidyverse")) install.packages("tidyverse")
library(tidyverse)

# --------------------------------------------------------------------------------
# STEP 1: Read and clean the pincode-level location dataset
# This dataset contains geographic information for each pincode (lat, long, district)
# --------------------------------------------------------------------------------

CleanData <- read_csv("pin code data warehouse optimisation.csv", show_col_types = FALSE) %>%
  select(pincode, district, latitude, longitude) %>%  # Keep only useful columns
  drop_na()  # Remove rows with any missing values

# --------------------------------------------------------------------------------
# STEP 2: Process the Amazon sales dataset to extract e-commerce demand
# Group by pincode and sum up quantity sold to get total demand per pincode
# --------------------------------------------------------------------------------

pincode_demand <- read.csv("Amazon Sale Report.csv") %>%
  group_by(ship.postal.code) %>%  # Group by shipping postal code
  summarise(Demand = sum(Qty, na.rm = TRUE)) %>%  # Sum quantity sold for each pincode
  drop_na() %>%  # Remove any missing values
  rename(pincode = ship.postal.code)  # Rename column to match CleanData for merging

# --------------------------------------------------------------------------------
# STEP 3: Merge demand data with location data using pincode as key
# This gives the final dataset containing:
# pincode, district, latitude, longitude, and total demand
# --------------------------------------------------------------------------------

final_data <- inner_join(CleanData, pincode_demand, by = "pincode")

# --------------------------------------------------------------------------------
# STEP 4: Preview and save the final dataset to CSV
# This will be used as input for distance calculation and optimization model
# --------------------------------------------------------------------------------

head(final_data)  # Show first few rows to verify

write.csv(final_data, "Final_Data.csv", row.names = FALSE)  # Save cleaned dataset
