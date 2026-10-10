import time
import random
import socket
import json


HOST = "127.0.0.1"
PORT = 5005


# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Initial UAV state
uav = {
    "latitude": 23.0225,
    "longitude": 72.5714,
    "altitude": 0.0,
    "speed": 0.0,
    "heading": 90.0,
    "battery": 100.0,
    "gps_satellites": 12,
    "flight_mode": "STANDBY"
}


def update_uav():

    # Takeoff and climb
    if uav["altitude"] < 100:

        uav["flight_mode"] = "TAKEOFF"
        uav["altitude"] += 5
        uav["speed"] = 8

    # Cruise
    else:

        uav["flight_mode"] = "CRUISE"
        uav["altitude"] += random.uniform(-2, 2)
        uav["speed"] = random.uniform(15, 20)

    # Move UAV
    uav["latitude"] += 0.0001
    uav["longitude"] += 0.0001

    # Change heading
    uav["heading"] += random.uniform(-2, 2)

    # Battery consumption
    uav["battery"] -= 0.2
    # uav["battery"] -= 2

    # GPS variation
    uav["gps_satellites"] = random.randint(10, 13)


def send_telemetry():

    # Convert dictionary to JSON
    message = json.dumps(uav)

    # Convert text to bytes and send
    sock.sendto(
        message.encode("utf-8"),
        (HOST, PORT)
    )


def main():

    print("================================")
    print("      MINI UAV SIMULATOR")
    print("================================")

    print(f"Sending telemetry to {HOST}:{PORT}")
    print("UAV simulation started...\n")

    try:

        while True:

            update_uav()

            send_telemetry()

            print(
                f"Altitude: {uav['altitude']:.1f} m | "
                f"Speed: {uav['speed']:.1f} m/s | "
                f"Battery: {uav['battery']:.1f}%"
            )

            time.sleep(1)

    except KeyboardInterrupt:

        print("\nUAV simulation stopped.")

    finally:

        sock.close()


if __name__ == "__main__":
    main()