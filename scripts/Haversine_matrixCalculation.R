# ------------------------------------------------------------------------
# Load necessary packages
# ------------------------------------------------------------------------
library(tidyverse)  # Includes dplyr, purrr, readr etc.
library(purrr)      # Specifically for pmap() to process rows with proper types

# ------------------------------------------------------------------------
# STEP 1: Read the processed demand and warehouse datasets
# ------------------------------------------------------------------------
demand_data <- read_csv("Demand_points.csv", show_col_types = FALSE)
warehouse_data <- read_csv("Warehouse_points.csv", show_col_types = FALSE)

# ------------------------------------------------------------------------
# STEP 2: Define the Haversine formula
# Calculates great-circle distance between two lat-long points on Earth
# ------------------------------------------------------------------------
haversine <- function(lat1, lon1, lat2, lon2) {
  R <- 6371  # Radius of Earth in kilometers
  dlat <- (lat2 - lat1) * pi / 180
  dlon <- (lon2 - lon1) * pi / 180
  lat1 <- lat1 * pi / 180
  lat2 <- lat2 * pi / 180
  
  a <- sin(dlat / 2)^2 + cos(lat1) * cos(lat2) * sin(dlon / 2)^2
  c <- 2 * atan2(sqrt(a), sqrt(1 - a))
  
  R * c  # Final output in kilometers
}

# ------------------------------------------------------------------------
# STEP 3: Calculate distances from each demand point to all warehouses
# We use pmap() to process each demand point row (lat1, lon1)
# For each, we apply mapply() to compute distances to all warehouse locations
# ------------------------------------------------------------------------

# This adds a new column: list of distances for each row in demand_data
dist_matrix_values <- demand_data %>%
  mutate(
    dist_vector = pmap(
      list(latitude, longitude),  # Input lat1, lon1 from demand point
      function(lat1, lon1) {
        mapply(function(lat2, lon2) {
          haversine(as.numeric(lat1), as.numeric(lon1),
                    as.numeric(lat2), as.numeric(lon2))
        }, warehouse_data$Latitude, warehouse_data$Longitude)
      }
    )
  )

# ------------------------------------------------------------------------
# STEP 4: Convert list-column of vectors into a proper distance matrix
# Each row corresponds to a demand point, each column is a warehouse
# ------------------------------------------------------------------------

# Combine the vectors into a full matrix (rows = demand points, cols = warehouses)
distance_matrix <- dist_matrix_values$dist_vector %>%
  do.call(rbind, .)

# Assign column names using warehouse district names
colnames(distance_matrix) <- warehouse_data$district

# ------------------------------------------------------------------------
# STEP 5: Merge the distance matrix with basic demand info (pincode, district)
# ------------------------------------------------------------------------

# Bind the distance matrix to the demand point identifiers
final_dist_matrix <- bind_cols(
  demand_data %>% select(pincode, district),
  as.data.frame(distance_matrix)
)

# ------------------------------------------------------------------------
# STEP 6: Save the final matrix to a CSV
# This file will be used in the Python optimization model
# ------------------------------------------------------------------------
write.csv(final_dist_matrix, "Distance_Matrix.csv", row.names = FALSE)
