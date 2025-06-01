# Traffic_violation_system
Traffic Violation Monitoring &amp; Analytics System
Traffic Violation Monitoring & Analytics System
A full-stack prototype for real-time traffic violation detection, OCR-based license-plate recognition, and interactive analytics—built with edge-optimized computer vision, deep learning, and a Streamlit dashboard. Designed for Zimbabwean cities but easily extensible to other locales.

🚀 Project Overview
This system captures video streams or image snapshots at intersections, detects vehicles and red-light/speed violations using YOLO object detection, and extracts license-plate text via a Transformer-based OCR pipeline. All inference runs on a single laptop or edge node, with millisecond-level latency. Violations are automatically logged (timestamp, city, plate) and streamed to a cloud-native microservices backend for aggregation, reporting, and automated citation generation.

A Streamlit dashboard provides:

Real-time metrics: total cars, violations, violation rates, average daily violations

Time-series visualizations: weekly/daily violation trends, rolling averages, regression-based 4-week forecasts

Statistical analysis: Pearson correlation, chi-squared testing across cities

Geospatial insights: hexbin of “cars passed vs. violations” and Mapbox scatter-map of violations per city

Pictographs: icon-based charts (🚗 icons) showing relative violation counts by city

OCR performance metrics: per-inference success scatter, rolling accuracy, and a city×hour heatmap of OCR success rates

📂 Repository Contents
pgsql
Copy
Edit
📁 traffic_violation_system/
│
├── violations.csv           # Logged violations (timestamp, city, plate, snapshot filename)
├── fined_summary.csv        # Aggregated fines/violations data per timestamp & location
├── snapshots/               # Directory of captured images (e.g., "20250517_161641_37.png")
│
├── streamlit_app.py         # Main Streamlit dashboard (show_dashboard & support functions)
├── object_detection.py      # YOLOv5/YOLOv8 inference scripts for vehicle/violation detection
├── ocr_pipeline.py          # Transformer/OCR wrapper for license-plate recognition
├── utils.py                 # Helper functions (data loading, preprocessing, timestamp parsing)
│
├── requirements.txt         # Python dependencies (torch, torchvision, seaborn, plotly, streamlit, etc.)
└── README.md                # Project description (this file)
🔧 Technology Stack
Computer Vision & Detection

YOLO (v5/v8) object detector for real-time vehicle and violation detection

OpenCV for image preprocessing (cropping, deskewing, CLAHE, super-resolution)

OCR & Text Extraction

Transformer-based OCR (e.g., TrOCR, EasyOCR) fine-tuned on Zimbabwean license-plate samples

Regex-based post-filtering to enforce plate format and drop “unknown” reads

Backend & Logging

Edge-optimized inference on a standard laptop (no GPU required)

CSV logging (violations.csv) of each violation: timestamp, city, object_id, plate, snapshot file

Dashboard & Analytics

Streamlit for interactive web UI

Pandas for in-memory aggregation (resampling, grouping, statistical tests)

Plotly for rich, dark-themed charts (line, bar, pictograph, heatmap, mapbox)

Matplotlib for hexbin plots embedded via st.pyplot

SciPy (pearsonr, chi2_contingency) and scikit-learn (LinearRegression) for analytics

⚙️ Installation & Setup
Clone this repository

bash
Copy
Edit
git clone https://github.com/<your-username>/traffic_violation_system.git
cd traffic_violation_system
Create a Python virtual environment

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
Install dependencies

bash
Copy
Edit
pip install --upgrade pip
pip install -r requirements.txt
Download/Place Model Weights

Place your YOLO model weights (e.g., yolov5s.pt) in the models/ folder (create if needed).

Place any fine-tuned OCR weights in ocr_models/.

Populate Data & Snapshots

Ensure violations.csv exists (it will auto-generate on first run if empty).

Store captured images in snapshots/ using naming convention YYYYMMDD_HHMMSS_<id>.png.

▶️ Running the Dashboard
From the repository root:

bash
Copy
Edit
streamlit run streamlit_app.py
Home Page: Quick links to analytics.

Dashboard Page: Comprehensive metrics, charts, maps, and OCR performance visualizations.

Use the “City drill-down” and “Date range” selectors at the top to filter all visuals by specific cities or time windows.

📊 Key Features
Real-Time Detection (Prototype Stage)

YOLO running at ~50ms per frame on a laptop CPU (no GPU).

Edge inference produces bounding boxes and violation labels instantly.

OCR & License-Plate Logging

Transformer-based OCR processes each cropped plate.

Plates flagged “unknown” fallback to manual review.

All logs written to violations.csv with <timestamp, city, object_id, plate>.

Interactive Analytics Dashboard

Metrics cards: live counts of cars passed, total violations, violation rate, average daily violations.

Time-series charts: weekly/daily violation trends, 7-day rolling average, 4-week forecast (LinearRegression).

Statistical tests: Pearson correlation between cars passed vs. violations, chi-squared across cities.

Violation breakdown: bar chart + pictograph (🚗 icons) showing total violations by city.

Hexbin plot: “cars passed vs. violations” density analysis.

Geospatial map: Mapbox-powered bubble map of total violations per city (Zoomed into Zimbabwe).

OCR performance: per-inference success scatter, rolling accuracy line, and city×hour heatmap.

Extensible & Configurable

Easily replace YOLO weights or OCR model.

Add new cities to coords dictionary for geospatial plotting.

Modify aggregation windows (hourly/daily/weekly) by changing resample() parameters.

🚧 Future Improvements
Model Retraining & Fine-Tuning

Collect ground truth to label false positives/negatives and refine YOLO/OCR.

Integrate active learning to continuously retrain on misclassified samples.

Cloud Integration

Replace CSV logs with a small REST API + database for real-time ingestion and querying.

Deploy inference as AWS Lambda or Azure Functions for scalable edge deployments.

Mobile/Edge App

Build a lightweight mobile app wrapper for field officers to review pending “unknown” plates.

Real-time push notifications when critical thresholds (e.g., spike in violations) are crossed.

User Authentication & Reporting

Add role-based login for admins vs. traffic officers.

PDF export or scheduled email reports of weekly/monthly violation summaries.

📄 License
This project is released under the MIT License. Feel free to fork, adapt, and contribute back via pull requests.

🙏 Acknowledgments
YOLO community for open-source object detection

Hugging Face/Transformers for OCR models

Plotly & Streamlit teams for creating interactive visualization tools

Zimbabwe Traffic Authorities for collaboration and field testing
