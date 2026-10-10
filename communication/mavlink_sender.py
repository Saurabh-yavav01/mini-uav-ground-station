from pymavlink import mavutil
import time

# Create MAVLink connection
connection = mavutil.mavlink_connection(
    "udpout:127.0.0.1:14550"
)

print("================================")
print("       MAVLINK SENDER")
print("================================")
print("Sending MAVLink heartbeat...")
print("Waiting for receiver...\n")


while True:

    # Send heartbeat message
    connection.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_QUADROTOR,
        mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
        0,
        0,
        mavutil.mavlink.MAV_STATE_ACTIVE
    )

    print("Heartbeat sent")

    time.sleep(1)