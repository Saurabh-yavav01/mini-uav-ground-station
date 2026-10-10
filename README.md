# Mini UAV Ground Station + Telemetry Analyzer

A Python-based Ground Control Station (GCS) for simulated Unmanned Aerial Vehicle (UAV) telemetry monitoring, mission tracking, flight analytics, and machine-learning-based anomaly detection.

## Overview

This project simulates UAV telemetry using MAVLink and displays live flight information through a Streamlit dashboard. It monitors aircraft status, tracks mission waypoints, records telemetry data, and identifies unusual flight readings.

**Project status:** Functional prototype with simulated UAV telemetry.

## Features

* **Live telemetry monitoring:** Displays altitude, speed, battery percentage, GPS satellites, heading, and position.
* **MAVLink communication:** Exchanges UAV telemetry using the MAVLink protocol.
* **Interactive ground station:** Streamlit dashboard with a map and live flight information.
* **Mission waypoint tracking:** Simulates waypoint navigation and monitors mission progress.
* **Flight-mode monitoring:** Displays TAKEOFF, CRUISE, LANDING, and LANDED states.
* **Battery safety alerts:** Flags critically low battery levels and simulates descent after battery depletion.
* **Communication-loss detection:** Detects when telemetry stops arriving and reports reconnection when it resumes.
* **Machine learning anomaly detection:** Uses an Isolation Forest model to identify unusual telemetry readings.
* **Telemetry logging:** Saves flight data to CSV for further analysis.
* **Flight analytics:** Calculates metrics such as maximum altitude, maximum speed, battery usage, and distance travelled.
* **Telemetry visualization:** Displays flight data through interactive graphs.

## Technology Stack

* Python
* Streamlit
* pymavlink
* Pandas
* Plotly
* Folium
* Scikit-learn
* Joblib
* CSV

## Project Structure

mini-uav-gcs/
|-- analyzer/
|   `-- telemetry_analyzer.py
|-- communication/
|   |-- mavlink_receiver.py
|   |-- mavlink_receiver_gcs.py
|   |-- mavlink_sender.py
|   |-- mavlink_telemetry_sender.py
|   `-- udp_receiver.py
|-- data/
|   `-- telemetry.csv
|-- gcs/
|   `-- app.py
|-- ml/
|   |-- __init__.py
|   |-- anomaly_detector.py
|   `-- anomaly_model.joblib
|-- simulator/
|   `-- uav_simulator.py
|-- README.md
`-- requirements.txt

## Setup and Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd mini-uav-gcs
```

Replace the placeholder with your actual repository URL after creating the GitHub repository.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Ground Control Station

```bash
streamlit run gcs/app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

### 5. Start the simulated telemetry sender

Open a second PowerShell terminal in the project directory, activate the virtual environment, and run:

```powershell
python communication/mavlink_telemetry_sender.py
```

The sender and GCS must use compatible MAVLink connection settings.

## Machine Learning

The project uses an Isolation Forest model to detect unusual combinations of UAV telemetry features:

* Altitude
* Speed
* Battery percentage
* GPS satellite count

A separate rule-based safety check flags battery levels at or below 10%. This complements the ML model; it is not itself an ML prediction.

## Testing

The following behaviors have been implemented and tested in the simulation:

* Live telemetry updates
* Critical battery alert
* Simulated battery depletion and descent
* TAKEOFF, CRUISE, LANDING, and LANDED status reporting
* Communication-loss detection and recovery
* Anomaly detection with test telemetry
* Telemetry logging and flight analytics

## Limitations

This is an educational simulation, not a flight-certified system. The simulated descent and battery behavior are simplified and do not represent a validated aircraft dynamics model. ML alerts are intended for experimentation and should not be used as the sole basis for real UAV safety decisions.

## Future Improvements

* Add automated tests for telemetry parsing and alert logic.
* Improve flight dynamics and battery modelling.
* Add more robust data storage and historical flight reports.
* Improve anomaly detection with representative flight datasets.
* Add screenshots, architecture diagrams, and a demonstration video.

## Author

Developed as a hands-on project to explore UAV ground control systems, telemetry communication, data visualization, and machine learning.
