  # PRNU-Based Image Forensics & Forgery Detection
  📌 Overview
  
  This repository contains the source code for a multi-module digital forensics system designed for **camera source identification** and **image forgery detection**. By extracting and analyzing the Photo Response Non-Uniformity (PRNU) — the unique, invisible sensor noise pattern inherent to every digital camera — this tool can verify an image's authenticity and localize tampered regions with high precision.
  This system was developed as a comprehensive final-year research project focusing on advanced threat intelligence, system integrity, and digital evidence verification.
  
 # ✨ Key Features
  
* PRNU Pattern Extraction: Utilizes advanced denoising filters and extraction algorithms to isolate the unique sensor fingerprint from digital images.
* Camera Source Identification: Cross-correlates extracted noise patterns against known camera profiles to accurately identify the source device.
* Tamper Localization: Detects and visualizes modified or spliced regions within an image by identifying inconsistencies in the PRNU noise floor.
* Multi-Module Architecture: Highly modular design separating pre-processing, extraction, statistical analysis, and visualization components.
* Interactive Visualization Dashboard: A user-friendly graphical interface for uploading images, viewing extraction heatmaps, and analyzing cross-correlation results in real-time.

# 🏗️ System Architecture
 
The pipeline is divided into the following core modules:
1. Image Pre-processing: Grayscale conversion, flattening, and artifact removal.
2. Noise Extraction: Applying denoising algorithms to separate image content from the high-frequency sensor noise.
3. Statistical Analysis & Cross-Correlation: Calculating statistical metrics to match digital fingerprints against reference profiles.
4. Interactive Dashboard: The frontend visualization layer built for forensic analysts to easily interpret the data.

# 🔮 Future Scope

* Performance Optimization: Optimizing extraction algorithms for faster processing of high-resolution images.
* Machine Learning Integration: Implementing automated, dynamic thresholding for anomaly detection.
* Expanded Format Support: Enhancing the system's resilience against heavily compressed images and social media scrubbing.

# Contact
Lokesh - @https://www.linkedin.com/in/lokeshsaravanan/ -@https://www.instagram.com/n__e__r___d
