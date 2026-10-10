from pymavlink import mavutil


# --------------------------------
# MAVLink connection
# --------------------------------

connection = mavutil.mavlink_connection(
    "udpin:127.0.0.1:14550"
)


# --------------------------------
# Telemetry storage
# --------------------------------

telemetry = {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "speed": 0.0,
    "heading": 0.0,
    "battery": 0.0,
    "gps_satellites": 0,
    "flight_mode": "UNKNOWN"
}


print("================================")
print("      GCS MAVLINK RECEIVER")
print("================================")
print("Waiting for MAVLink telemetry...")
print()


# --------------------------------
# Receive messages
# --------------------------------

while True:

    message = connection.recv_match(
        blocking=True
    )

    if not message:
        continue


    message_type = message.get_type()


    # --------------------------------
    # Heartbeat
    # --------------------------------

    if message_type == "HEARTBEAT":

        if message.custom_mode == 1:

            telemetry["flight_mode"] = "TAKEOFF"

        elif message.custom_mode == 2:

            telemetry["flight_mode"] = "CRUISE"

        else:

            telemetry["flight_mode"] = "UNKNOWN"

        print(
            "HEARTBEAT | "
            f"Flight Mode: {telemetry['flight_mode']}"
        )


    # --------------------------------
    # GPS / Position
    # --------------------------------

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
            (message.vx ** 2 + message.vy ** 2) ** 0.5 / 100
        )

        telemetry["heading"] = (
            message.hdg / 100
        )

        print(
            f"GPS | "
            f"Lat: {telemetry['latitude']:.6f} | "
            f"Lon: {telemetry['longitude']:.6f} | "
            f"Alt: {telemetry['altitude']:.1f} m | "
            f"Speed: {telemetry['speed']:.1f} m/s"
        )


    # --------------------------------
    # Battery
    # --------------------------------

    elif message_type == "SYS_STATUS":

        if message.battery_remaining >= 0:

            telemetry["battery"] = (
                message.battery_remaining
            )

            print(
                f"BATTERY | "
                f"{telemetry['battery']:.1f}%"
            )


        elif message_type == "GPS_RAW_INT":

            telemetry["gps_satellites"] = (
                message.satellites_visible
            )

            print(
                f"GPS STATUS | "
                f"Satellites: {telemetry['gps_satellites']}"
            )


    print()