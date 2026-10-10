import pandas as pd
import plotly.express as px

# -----------------------------
# Load telemetry data
# -----------------------------

DATA_FILE = "data/telemetry.csv"

df = pd.read_csv(DATA_FILE)

print("================================")
print("       TELEMETRY ANALYZER")
print("================================")

print("\nTotal telemetry records:", len(df))

print("\nAvailable columns:")
print(df.columns.tolist())

print("\nFirst 5 telemetry records:")
print(df.head())

# -----------------------------
# Flight statistics
# -----------------------------

print("\n================================")
print("       FLIGHT STATISTICS")
print("================================")

print(f"\nMaximum Altitude : {df['altitude'].max():.2f} m")

print(f"Maximum Speed    : {df['speed'].max():.2f} m/s")

print(f"Average Speed    : {df['speed'].mean():.2f} m/s")

print(f"Minimum Battery  : {df['battery'].min():.2f}%")

print(f"Average Battery  : {df['battery'].mean():.2f}%")

print(f"Minimum GPS      : {df['gps_satellites'].min()} satellites")

print(f"Average GPS      : {df['gps_satellites'].mean():.2f} satellites")

print(f"Flight Modes     : {df['flight_mode'].unique()}")

# -----------------------------
# Telemetry graphs
# -----------------------------

print("\nGenerating telemetry graphs...")

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Altitude graph
fig_altitude = px.line(
    df,
    x="timestamp",
    y="altitude",
    title="UAV Altitude vs Time",
    labels={
        "timestamp": "Time",
        "altitude": "Altitude (m)"
    }
)

fig_altitude.show()


# Speed graph
fig_speed = px.line(
    df,
    x="timestamp",
    y="speed",
    title="UAV Speed vs Time",
    labels={
        "timestamp": "Time",
        "speed": "Speed (m/s)"
    }
)

fig_speed.show()


# Battery graph
fig_battery = px.line(
    df,
    x="timestamp",
    y="battery",
    title="UAV Battery vs Time",
    labels={
        "timestamp": "Time",
        "battery": "Battery (%)"
    }
)

fig_battery.show()


# GPS graph
fig_gps = px.line(
    df,
    x="timestamp",
    y="gps_satellites",
    title="GPS Satellites vs Time",
    labels={
        "timestamp": "Time",
        "gps_satellites": "GPS Satellites"
    }
)

fig_gps.show()