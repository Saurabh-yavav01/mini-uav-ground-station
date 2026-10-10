from pymavlink import mavutil
import time
import random

connection = mavutil.mavlink_connection(
    "udpout:127.0.0.1:14550"
)

latitude = 23.0225
longitude = 72.5714
altitude = 0.0
speed = 0.0
heading = 90.0
battery = 100.0
# battery = 30
gps_satellites = 12

# Mission waypoints
waypoints = [
    (23.0225, 72.5714),
    (23.0240, 72.5730),
    (23.0260, 72.5750),
    (23.0280, 72.5730),
    (23.0260, 72.5710),
]

current_waypoint = 0

print("================================")
print("   MAVLINK UAV TELEMETRY")
print("================================")
print("Sending UAV telemetry...")
print()


def send_heartbeat(flight_mode):

    if flight_mode == "TAKEOFF":
        custom_mode = 1

    elif flight_mode == "CRUISE":
        custom_mode = 2
    
    elif flight_mode == "LANDING":
        custom_mode = 3

    elif flight_mode == "LANDED":
        custom_mode = 4

    else:
        custom_mode = 0

    connection.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_QUADROTOR,
        mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
        0,
        custom_mode,
        mavutil.mavlink.MAV_STATE_ACTIVE
    )


def send_gps():

    global latitude
    global longitude

    lat = int(latitude * 10000000)
    lon = int(longitude * 10000000)

    vx = int(speed * 100)
    vy = 0

    connection.mav.global_position_int_send(
        int(time.time() * 1000) % 4294967295,
        lat,
        lon,
        int(altitude * 1000),
        int(altitude * 1000),
        vx,
        vy,
        0,
        int(heading * 100)
    )


def send_battery():

    connection.mav.sys_status_send(
        0,                  # onboard_control_sensors_present
        0,                  # onboard_control_sensors_enabled
        0,                  # onboard_control_sensors_health
        0,                  # load
        12000,              # voltage_battery (mV)
        -1,                 # current_battery (cA)
        int(battery),       # battery_remaining (%)
        0,                  # drop_rate_comm
        0,                  # errors_comm
        0,                  # errors_count1
        0,                  # errors_count2
        0,                  # errors_count3
        0                   # errors_count4
    )


def send_gps_status():

    connection.mav.gps_raw_int_send(
        int(time.time() * 1000000),
        3,
        int(latitude * 10000000),
        int(longitude * 10000000),
        int(altitude * 1000),
        100,
        100,
        0,
        0,
        gps_satellites
    )

def send_mission_status():
    connection.mav.mission_current_send(
        current_waypoint
    )

def move_towards_waypoint():

    global latitude
    global longitude
    global current_waypoint

    target_lat, target_lon = waypoints[current_waypoint]

    lat_diff = target_lat - latitude
    lon_diff = target_lon - longitude

    # Move toward the waypoint
    step = 0.00005

    if abs(lat_diff) > step:
        latitude += step if lat_diff > 0 else -step
    else:
        latitude = target_lat

    if abs(lon_diff) > step:
        longitude += step if lon_diff > 0 else -step
    else:
        longitude = target_lon

    # Check if waypoint reached
    if (
        abs(latitude - target_lat) < 0.00001
        and
        abs(longitude - target_lon) < 0.00001
    ):

        print(
            f"✅ Waypoint {current_waypoint + 1} reached"
        )

        current_waypoint += 1

        # Restart mission after final waypoint
        if current_waypoint >= len(waypoints):
            current_waypoint = 0

        print(
            f"➡️ Heading to waypoint "
            f"{current_waypoint + 1}"
        )




try:
    while True:

        # Normal flight while battery remains
        if battery > 0:

            if altitude < 100:
                altitude = min(100, altitude + 5)
                speed = 8
                flight_mode = "TAKEOFF"

            else:
                altitude += random.uniform(-2, 2)
                speed = random.uniform(15, 20)
                flight_mode = "CRUISE"

            # Move only while powered
            move_towards_waypoint()
            battery = max(0, battery - 0.2)
            # battery = max(0, battery - 0.5)

        # Simulated power loss and descent
        elif altitude > 0:
            flight_mode = "LANDING"

            speed = max(0, speed - 2)
            altitude = max(0, altitude - 2)

            print("⚠️ Battery depleted! UAV descending.")

        # UAV has landed
        else:
            flight_mode = "LANDED"
            speed = 0
            altitude = 0

        # Update other simulated values
        heading = (heading + random.uniform(-2, 2)) % 360
        gps_satellites = random.randint(10, 13)

        # Send MAVLink messages
        send_heartbeat(flight_mode)
        send_gps()
        send_battery()
        send_gps_status()
        send_mission_status()

        print(
            f"Mode: {flight_mode} | "
            f"Altitude: {altitude:.1f} m | "
            f"Speed: {speed:.1f} m/s | "
            f"Battery: {battery:.1f}% | "
            f"GPS: {gps_satellites}"
        )

        time.sleep(1)

except KeyboardInterrupt:
    print("\nMAVLink UAV simulator stopped.")