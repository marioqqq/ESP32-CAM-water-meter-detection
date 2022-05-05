# ESP32-CAM-water-meter-detection
Detect value of water meter using ESP32-CAM module and Raspberry Pi

This project uses ESP32-CAM camera module with modifications (HW and SW) to reduce power consumption. The module send picture to the server via MQTT (Raspberry Pi), where it modifies it, sends it for detection and saves the data. Then data are showed on grafana. Accuracy of my settings is more then 80%.

## ESP32-CAM
I used concept of this project ldab/ESP32-CAM-MQTT (https://github.com/ldab/ESP32-CAM-MQTT) and modify source code for my needs. I also made LED ring for better illumination of image. For powering I removed built-in LED and use that pad for powering my LED ring. Then I printed holder that fits on my water meter.

<p align="center">
  <img src="https://user-images.githubusercontent.com/93001533/165036330-9b6be7a9-bf80-417b-b244-fe3f3a429f48.png" alt="Schematic" height="350"/>
  <img src="https://user-images.githubusercontent.com/93001533/165036760-9d0ab7e6-6bdd-4bc4-bec4-07aaecccbb99.png" alt="Holder" height="350"/>
  <img src="https://user-images.githubusercontent.com/93001533/165036355-49c77b59-7057-4476-9c2e-15483e40d283.png" alt="Water meter" height="350"/>
</p>

### ESP32-CAM very low power application
In software I turned off few things and reduced CPU clock frequency to reduce power consumption. I also changed voltage regulator for AP2210N-3.3. And finally I did a hardware modification shown on the schematic. After these modifications, on one charge of 2,5 Ah battery can last 3-4 months, depending on frequency of scanning water meter value per day.

<p align="center">
  <img src="https://user-images.githubusercontent.com/93001533/165039323-fad308d3-c15c-46ce-819a-2e651f4b62ac.png" alt="Schematic" width="400"/>
</p>

## Raspberry Pi
You can use any hardware. I used Raspberry Pi with Raspberry Pi OS, because it's cheap and powerful for my application. Required software: Node-RED, MQTT broaker, OpenCV (For Rpi https://learn.circuit.rocks/introduction-to-opencv-using-the-raspberry-pi), Database (I used MariaDB), Grafana. Almost whole system is runnig locally, except Google Cloud Vision (https://www.youtube.com/watch?v=eaUBSNRKv1A). It's free for 1000 detections/month.

<p align="center">
  <img src="https://user-images.githubusercontent.com/93001533/165040818-18f7e09e-a50c-4717-8c48-ee41d6d78d75.png" alt="Node-RED" height="250"/>
  <img src="https://user-images.githubusercontent.com/93001533/165035822-d5094441-1f8e-47e0-95d2-24953932a834.png" alt="Grafana" height="300"/>
  </p>

## Use
From all python programs you only need main2.py and values.py. Other programs were only to fine tune filters. In main.py you need to tweak parameters for your needs.

## Final words
This is my first commit, so if something is not clear or missing, please let me know via issues or via discord (marioqqq#5119). Thanks :)
