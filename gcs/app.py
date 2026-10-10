import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.anomaly_detector import (load_or_train_model,detect_anomaly)

# import socket
# import json
from pymavlink import mavutil
import folium
from streamlit_folium import st_folium
import csv
import os
from datetime import datetime
import time
import pandas as pd
import plotly.express as px
import math






@st.cache_resource
def get_anomaly_model():
    return load_or_train_model()

anomaly_model = get_anomaly_model()


# -----------------------------
# Configuration
# -----------------------------

# HOST = "127.0.0.1"
# PORT = 5005

DATA_FILE = "data/telemetry.csv"


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Mini UAV Ground Station",
    page_icon="🚁",
    layout="wide"
)


# -----------------------------
# Title
# -----------------------------

st.title("🚁 Mini UAV Ground Control Station")

st.write("Real-time UAV telemetry monitoring system")


# -----------------------------
# UDP socket
# -----------------------------

# @st.cache_resource
# def create_socket():

#     sock = socket.socket(
#         socket.AF_INET,
#         socket.SOCK_DGRAM
#     )

#     sock.bind((HOST, PORT))

#     sock.settimeout(0.5)

#     return sock


# sock = create_socket()

MAVLINK_PORT = "udpin:127.0.0.1:14550"


@st.cache_resource
def create_mavlink_connection():

    connection = mavutil.mavlink_connection(
        MAVLINK_PORT
    )

    return connection


connection = create_mavlink_connection()

if "mission" not in st.session_state:
    st.session_state.mission = {
        "current_waypoint": 1,
        "total_waypoints": 5,
        "status": "ACTIVE"
    }

if "telemetry" not in st.session_state:

    st.session_state.telemetry = {
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0.0,
        "speed": 0.0,
        "heading": 0.0,
        "battery": 0.0,
        "gps_satellites": 0,
        "flight_mode": "UNKNOWN"
    }





if "last_telemetry_time" not in st.session_state:
    st.session_state.last_telemetry_time = time.time()

if "mission_start_time" not in st.session_state:
    # st.session_state.mission_start_time = time.time()
    st.session_state.mission_start_time = None

# -----------------------------
# Flight path storage
# -----------------------------

if "flight_path" not in st.session_state:
    st.session_state.flight_path = []

if "max_altitude" not in st.session_state:
    st.session_state.max_altitude = 0.0

if "max_speed" not in st.session_state:
            st.session_state.max_speed = 0.0

if "starting_battery" not in st.session_state:
    st.session_state.starting_battery = None

if "battery_used" not in st.session_state:
    st.session_state.battery_used = 0.0

if "total_distance" not in st.session_state:
    st.session_state.total_distance = 0.0

if "previous_position" not in st.session_state:
    st.session_state.previous_position = None


# -----------------------------
# Telemetry logger
# -----------------------------

def log_telemetry(telemetry):

    file_exists = os.path.exists(DATA_FILE)

    with open(DATA_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        # Create header if file is empty
        if not file_exists or os.path.getsize(DATA_FILE) == 0:

            writer.writerow([
                "timestamp",
                "latitude",
                "longitude",
                "altitude",
                "speed",
                "heading",
                "battery",
                "gps_satellites",
                "flight_mode"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            telemetry["latitude"],
            telemetry["longitude"],
            telemetry["altitude"],
            telemetry["speed"],
            telemetry["heading"],
            telemetry["battery"],
            telemetry["gps_satellites"],
            telemetry["flight_mode"]
        ])



def show_telemetry_graphs():

    if not os.path.exists(DATA_FILE):
        st.info("No telemetry data available yet.")
        return

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.info("No telemetry data available yet.")
        return

    df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
    )

    df = df.dropna(subset=["timestamp"])

    st.divider()
    st.subheader("📊 Telemetry Analysis")

    # Altitude
    fig_altitude = px.line(
        df,
        x="timestamp",
        y="altitude",
        title="Altitude vs Time"
    )
    st.plotly_chart(fig_altitude, width="stretch")

    # Speed
    fig_speed = px.line(
        df,
        x="timestamp",
        y="speed",
        title="Speed vs Time"
    )
    st.plotly_chart(fig_speed, width="stretch")

    # Battery
    fig_battery = px.line(
        df,
        x="timestamp",
        y="battery",
        title="Battery vs Time"
    )
    st.plotly_chart(fig_battery, width="stretch")

    # GPS
    fig_gps = px.line(
        df,
        x="timestamp",
        y="gps_satellites",
        title="GPS Satellites vs Time"
    )
    st.plotly_chart(fig_gps, width="stretch")



def check_alerts(telemetry):

    alerts = []

    # Low battery
    if telemetry["battery"] < 20:
        alerts.append("🔴 CRITICAL: Battery level is below 20%")

    elif telemetry["battery"] < 30:
        alerts.append("🟡 WARNING: Battery level is below 30%")

    # GPS satellites
    if telemetry["gps_satellites"] < 6:
        alerts.append("🔴 CRITICAL: GPS signal is weak")

    elif telemetry["gps_satellites"] < 8:
        alerts.append("🟡 WARNING: GPS satellite count is low")

    # Geo-fence
    latitude = telemetry["latitude"]
    longitude = telemetry["longitude"]

    if not (23.0200 <= latitude <= 23.0300):
        alerts.append("🔴 ALERT: UAV has crossed the latitude geo-fence")

    if not (72.5700 <= longitude <= 72.5800):
        alerts.append("🔴 ALERT: UAV has crossed the longitude geo-fence")

    return alerts



def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371000  # metres

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c



def receive_mavlink():

    telemetry = st.session_state.telemetry

    messages_received = False

    while True:

        message = connection.recv_match(
            blocking=False
        )

        if message is None:
            break

        messages_received = True

        message_type = message.get_type()

        if message_type == "HEARTBEAT":

            if message.custom_mode == 1:
                telemetry["flight_mode"] = "TAKEOFF"

            elif message.custom_mode == 2:
                telemetry["flight_mode"] = "CRUISE"
            
            elif message.custom_mode == 3:
                telemetry["flight_mode"] = "LANDING"

            elif message.custom_mode == 4:
                telemetry["flight_mode"] = "LANDED"

            else:
                telemetry["flight_mode"] = "UNKNOWN"

        elif message_type == "GLOBAL_POSITION_INT":

            telemetry["latitude"] = (
                message.lat / 10000000
            )

            telemetry["longitude"] = (
                message.lon / 10000000
            )

            telemetry["altitude"] = (
                message.relative_alt / 1000
            )

            telemetry["speed"] = (
                (message.vx ** 2 + message.vy ** 2) ** 0.5
                / 100
            )

            telemetry["heading"] = (
                message.hdg / 100
            )

        elif message_type == "SYS_STATUS":

            if message.battery_remaining >= 0:

                telemetry["battery"] = (
                    message.battery_remaining
                )

        elif message_type == "GPS_RAW_INT":

            telemetry["gps_satellites"] = (
                message.satellites_visible
            )
        elif message_type == "MISSION_CURRENT":

            waypoint = message.seq + 1

            st.session_state.mission["current_waypoint"] = waypoint

    st.session_state.telemetry = telemetry

    return messages_received



# -----------------------------
# Live telemetry section
# -----------------------------

@st.fragment(run_every="1s")
def live_telemetry():

    received = receive_mavlink()
    telemetry = st.session_state.telemetry

    # Start the mission only after valid telemetry arrives
    valid_position = (
        -90 <= telemetry["latitude"] <= 90
        and -180 <= telemetry["longitude"] <= 180
        and (
            telemetry["latitude"] != 0
            or telemetry["longitude"] != 0
        )
        and telemetry["gps_satellites"] >= 4
    )

    valid_battery = (
        0 < telemetry["battery"] <= 100
    )

    if (
        received
        and valid_position
        and valid_battery
        and st.session_state.mission_start_time is None
    ):
        st.session_state.mission_start_time = time.time()

        

    if st.session_state.mission_start_time is None:
        mission_duration = 0
    else:
        mission_duration = (
            time.time()
            - st.session_state.mission_start_time
        )


    completed_waypoints = max(
        0,
        st.session_state.mission["current_waypoint"] - 1
    )

    minutes = int(mission_duration // 60)
    seconds = int(mission_duration % 60)

    st.subheader("🗺️ Mission Status")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Mission",
            st.session_state.mission["status"]
        )

    with col2:
        st.metric(
            "Current Waypoint",
            f"{st.session_state.mission['current_waypoint']} / "
            f"{st.session_state.mission['total_waypoints']}"
        )

    with col3:
        st.metric(
            "Flight Mode",
            telemetry["flight_mode"]
        )

    with col4:
        st.metric(
            "Mission Duration",
            f"{minutes:02d}:{seconds:02d}"
        )
    
    with col5:
        st.metric(
            "Waypoints Completed",
            f"{completed_waypoints} / "
            f"{st.session_state.mission['total_waypoints']}"
        )
#---------------------------------------
# Misssion performance display

    st.subheader("📊 Mission Performance")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Maximum Altitude",
            f"{st.session_state.max_altitude:.1f} m"
        )

    with col2:
        st.metric(
            "Maximum Speed",
            f"{st.session_state.max_speed:.1f} m/s"
        )
    
    with col3:
        st.metric(
            "Battery Used",
            f"{st.session_state.battery_used:.1f}%"
        )

    with col4:
        st.metric(
            "Distance Traveled",
            f"{st.session_state.total_distance:.1f} m"
        )

    # if received:

    #     st.session_state.last_telemetry_time = time.time()

    # Update timestamp only when a MAVLink message is received
    if received:
        st.session_state.last_telemetry_time = time.time()

    time_since_last = (
        time.time() - st.session_state.last_telemetry_time
    )


    # -------------------------
    # Display telemetry
    # -------------------------

    # Update timestamp only when a MAVLink message arrives
    if received:
        st.session_state.last_telemetry_time = time.time()

    time_since_last = (
        time.time()
        - st.session_state.last_telemetry_time
    )

    if time_since_last <= 3:

        # Save telemetry to CSV only when new data arrives
        if received:
            log_telemetry(telemetry)

        st.success("🟢 UAV CONNECTED")


        # -------------------------
        # System Alerts
        # -------------------------

        alerts = check_alerts(telemetry)

        st.subheader("🚨 System Alerts")

        if alerts:

            for alert in alerts:
                st.warning(alert)

        else:
            st.success("✅ All UAV systems operating normally")


        # -------------------------
        # Get telemetry values
        # -------------------------

        latitude = telemetry["latitude"]
        longitude = telemetry["longitude"]
        altitude = telemetry["altitude"]
        speed = telemetry["speed"]
        heading = telemetry["heading"]
        battery = telemetry["battery"]
        gps = telemetry["gps_satellites"]
        flight_mode = telemetry["flight_mode"]



        
        # -------------------------
        # ML Anomaly Detection
        # -------------------------

        st.subheader("🤖 ML Anomaly Detection")

        try:
            is_anomaly = detect_anomaly(
                anomaly_model,
                telemetry
            )
            # TEMPORARY TEST ONLY
            # test_telemetry = {
            #     "altitude": 1000.0,
            #     "speed": 100.0,
            #     "battery": 1.0,
            #     "gps_satellites": 0
            # }

            # is_anomaly = detect_anomaly(
            #     anomaly_model,
            #     test_telemetry
            # )

            if is_anomaly:
                st.warning(
                    "⚠️ ML Alert: Unusual UAV telemetry detected. "
                    "Check altitude, speed, battery, and GPS."
                )
            else:
                st.success(
                    "✅ ML Status: No unusual telemetry detected."
                )

        except Exception as e:
            st.error(
                f"ML anomaly detection failed: {e}"
            )


        #mission performance calculation
        #-----------------------



        st.session_state.max_altitude = max(
            st.session_state.max_altitude,
            altitude
        )

        st.session_state.max_speed = max(
            st.session_state.max_speed,
            speed
        )

        # Calculate battery usage only from valid readings
        if 0 < battery <= 100:

            if st.session_state.starting_battery is None:
                st.session_state.starting_battery = battery

            st.session_state.battery_used = max(
                0.0,
                st.session_state.starting_battery - battery
            )

        # Calculate total distance travelled safely
        valid_position = (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
            and (latitude != 0 or longitude != 0)
            and gps >= 4
        )

        if valid_position:

            current_position = (latitude, longitude)

            if st.session_state.previous_position is not None:

                previous_lat, previous_lon = (
                    st.session_state.previous_position
                )

                distance = calculate_distance(
                    previous_lat,
                    previous_lon,
                    latitude,
                    longitude
                )

                # Ignore implausible GPS jumps between updates
                if 0 < distance <= 100:
                    st.session_state.total_distance += distance

            # Always establish a new baseline
            st.session_state.previous_position = current_position

        else:
            # Never calculate distance from an invalid position
            st.session_state.previous_position = None



        # -------------------------
        # Telemetry Cards
        # -------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🔋 Battery",
                f"{battery:.1f}%"
            )

        with col2:
            st.metric(
                "📏 Altitude",
                f"{altitude:.1f} m"
            )

        with col3:
            st.metric(
                "🚀 Speed",
                f"{speed:.1f} m/s"
            )

        with col4:
            st.metric(
                "🛰️ GPS",
                gps
            )


        st.divider()


        # -------------------------
        # Position Information
        # -------------------------

        st.subheader("📍 UAV Position")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Latitude**")
            st.write(f"{latitude:.6f}")

        with col2:
            st.write("**Longitude**")
            st.write(f"{longitude:.6f}")

        with col3:
            st.write("**Heading**")
            st.write(f"{heading:.1f}°")


        # -------------------------
        # Flight Status
        # -------------------------

        st.subheader("✈️ Flight Status")

        if flight_mode == "TAKEOFF":

            st.warning("🟡 UAV is taking off")

        elif flight_mode == "CRUISE":

            st.success("🟢 UAV is cruising")

        else:

            st.info(
                f"Flight Mode: {flight_mode}"
            )


        # -------------------------
        # Save UAV Position
        # -------------------------

        st.session_state.flight_path.append(
            [latitude, longitude]
        )

        if len(st.session_state.flight_path) > 200:
            st.session_state.flight_path.pop(0)


        # -------------------------
        # UAV Map
        # -------------------------

        st.divider()

        st.subheader("🗺️ UAV Live Location")
        waypoints = [
            (23.0225, 72.5714),
            (23.0240, 72.5730),
            (23.0260, 72.5750),
            (23.0280, 72.5730),
            (23.0260, 72.5710),
        ]

        uav_map = folium.Map(
            location=[latitude, longitude],
            zoom_start=15
        )


        # UAV Marker
        folium.Marker(
            [latitude, longitude],

            popup=f"""
            <b>UAV</b><br>
            Altitude: {altitude:.1f} m<br>
            Speed: {speed:.1f} m/s<br>
            Battery: {battery:.1f}%
            """,

            tooltip="🚁 UAV Position"

        ).add_to(uav_map)


        # Flight Path
        if len(st.session_state.flight_path) > 1:

            folium.PolyLine(
                st.session_state.flight_path,
                weight=4,
                tooltip="UAV Flight Path"
            ).add_to(uav_map)

        # Add waypoint markers
        # -------------------------


        # -------------------------
        # Mission Waypoints
        # -------------------------

        # st.metric(
        #     "Mission Duration",     
        #     f"{minutes:02d}:{seconds:02d}"
        # )

        current_wp = st.session_state.mission["current_waypoint"]

        for i, (lat, lon) in enumerate(waypoints):

            waypoint_number = i + 1

            # Determine waypoint status
            if waypoint_number < current_wp:
                icon_color = "green"
                icon_symbol = "check"

            elif waypoint_number == current_wp:
                icon_color = "orange"
                icon_symbol = "flag"

            else:
                icon_color = "blue"
                icon_symbol = "flag"

            folium.Marker(
                location=[lat, lon],

                popup=f"""
                <b>Waypoint {waypoint_number}</b><br>
                Status:
                {"Completed" if waypoint_number < current_wp
                else "Current" if waypoint_number == current_wp
                else "Upcoming"}
                """,

                tooltip=f"WP{waypoint_number}",

                icon=folium.Icon(
                    color=icon_color,
                    icon=icon_symbol,
                    prefix="fa"
                )

            ).add_to(uav_map)


        # Planned Mission Route
        folium.PolyLine(
            locations=waypoints,
            weight=3,
            tooltip="Planned Mission Route"
        ).add_to(uav_map)

        # Display Map
        st_folium(
            uav_map,
            width=1200,
            height=500
        )


    
    # -------------------------
    # Communication Loss
    # -------------------------

    else:
        time_since_last = (
            time.time()
            - st.session_state.last_telemetry_time
        )

        if time_since_last > 3:
            st.error("🔴 COMMUNICATION LOST")
            st.warning(
                f"No UAV telemetry received for "
                f"{time_since_last:.1f} seconds."
            )
        else:
            st.warning(
                "🟡 Waiting for UAV telemetry..."
            )

# -----------------------------
# Start live telemetry
# -----------------------------

live_telemetry()


# -----------------------------
# Telemetry graphs
# -----------------------------

show_telemetry_graphs()