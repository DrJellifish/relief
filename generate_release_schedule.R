# Bottle Raft Release Schedule Generator
# Generates a CSV of 30 locations, every 15 minutes (HH:MM:SS) in a single day

# ---- 1. Release location data ----
release_locs <- data.frame(
  release_id = 1:30,
  lat = c(31.265,31.325,31.321,31.290,31.350,31.215,31.416,34.550,35.000,35.400,
          35.125,34.900,34.675,34.433,33.900,33.560,33.272,36.800,36.587,36.885,
          35.350,34.500,34.000,34.000,31.300,31.350,35.800,33.500,31.400,34.800),
  lon = c(32.301,32.750,33.768,34.230,33.500,29.955,31.813,33.050,34.600,33.900,
          33.950,33.650,33.042,35.833,35.483,35.370,35.193,34.617,36.173,30.705,
          33.000,33.800,34.500,32.700,34.000,33.250,34.000,35.000,33.800,32.500)
)

# ---- 2. Create 15-min time intervals (HH:MM:SS only) ----
release_times <- format(seq(
  as.POSIXct("2020-01-01 00:00:00", tz = "UTC"),
  as.POSIXct("2020-01-01 23:45:00", tz = "UTC"),
  by = "15 min"
), "%H:%M:%S")

# ---- 3. Cross join locations with times ----
release_schedule <- merge(release_locs, data.frame(release_time = release_times))[
  , c("release_id", "lat", "lon", "release_time")]

# ---- 4. Save to CSV ----
write.csv(release_schedule, "release_schedule_15min.csv", row.names = FALSE)

cat("release_schedule_15min.csv written to current directory.\n")
