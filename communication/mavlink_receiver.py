from pymavlink import mavutil

# Create MAVLink connection
connection = mavutil.mavlink_connection(
    "udpin:127.0.0.1:14550"
)

print("================================")
print("      MAVLINK RECEIVER")
print("================================")
print("Waiting for MAVLink messages...\n")


while True:

    message = connection.recv_match(
        blocking=True
    )

    if message:

        print(
            f"Message received: "
            f"{message.get_type()}"
        )

        print(message)
        print()