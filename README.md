# ESP32-S3 Multi-Axis Motion Control & G-Code Processing GUI System

![HCMUT Logo](https://img.shields.io/badge/University-HCMUT%20%2F%20Bach%20Khoa%20TPHCM-blue.svg)
![Author](https://img.shields.io/badge/Author-Cao%20Tuan%20Minh-yellow.svg)
![Status](https://img.shields.io/badge/Status-Completed-green.svg)
![License](https://img.shields.io/badge/License-Copyright%20©%202026%20Cao%20Tuan%20Minh-orange.svg)

An open-loop, real-time multi-axis CNC motion control system and G-code execution engine developed by **Cao Tuấn Minh** at **Ho Chi Minh City University of Technology (HCMUT / Trường Đại học Bách Khoa TP.HCM)**. The project was successfully implemented and completed during the **Summer Semester 253**.

---

## 📌 Project Architecture & Development Tasks

The project is structured into two main sequential milestones (Tasks):

```
                       ┌─────────────────────────────────────────┐
                       │               MAIN PROJECT              │
                       └────────────────────┬────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
     ┌─────────────────────────────┐                 ┌─────────────────────────────┐
     │  TASK 1: Software Path      │                 │  TASK 2: MCU Motion         │
     │  Visualization Engine       │                 │  Control Engine             │
     ├─────────────────────────────┤                 ├─────────────────────────────┤
     │ • G0, G1, G2, G3, G90, G91  │                 │ • G0, G1, G90, G91          │
     │ • Interactive Command Input │                 │ • ESP32-S3 Firmware (C++)   │
     │ • Trajectory Plotting (GUI) │                 │ • Nema 17 Motor Execution   │
     └─────────────────────────────┘                 └─────────────────────────────┘
```

---

### 🟢 Task 1: G-Code Trajectory Plotting & GUI Visualization
* **Focus:** Software-level G-code parsing, mathematical arc interpolation, and 2D/3D trajectory rendering.
* **Supported Commands:** `G0`, `G1`, `G2` (CW Arc), `G3` (CCW Arc), `G90` (Absolute), `G91` (Incremental).
* **Workflow:** Allows users to manually enter single G-code commands or load scripts to visualize planned toolpaths, formula plots, and linear/circular moves prior to physical execution.

#### 📸 Task 1 Visual Preview
![Task 1 - GUI Trajectory Plotting](images/gui_interface_task1.png)
*Figure 1: Task 1 Host GUI displaying G-code input panel and interactive trajectory plotting for linear and circular arcs ($G2/G3$).*

---

### 🔵 Task 2: ESP32-S3 Embedded Motion Control & Hardware Execution
* **Focus:** Real-time multi-axis stepper motor actuation, dual-core timing execution, and bidirectional UART telemetry synchronization.
* **Supported Commands:** `G0`, `G1`, `G90`, `G91`.
* **Workflow:** G-code streaming over USB-UART to the ESP32-S3 MCU, which executes synchronized pulse generation via Bresenham's line algorithm and trapezoidal velocity profiling to actuate physical Nema 17 stepper motors.

#### 📸 Task 2 Visual Previews
| Hardware Experimental Platform | Real-Time Telemetry Interface |
| :---: | :---: |
| ![Task 2 - Physical Model](images/physical_model.png) | ![Task 2 - Telemetry GUI](images/gui_interface_task3.png) |
| *Figure 2: Physical experimental setup featuring ESP32-S3, CNC Shield V3, and Nema 17 stepper motors.* | *Figure 3: Host PC GUI tracking real-time toolhead coordinates, step counts, and status telemetry.* |

---

## 🛠️ Feature Comparison Matrix

| Feature / Capability | Task 1 (Path Simulator) | Task 2 (Hardware Control) |
| :--- | :---: | :---: |
| **Linear Motion (`G0`, `G1`)** | ✅ | ✅ |
| **Circular Arc Interpolation (`G2`, `G3`)** | ✅ | ❌ (Future Scope) |
| **Positioning Modes (`G90`, `G91`)** | ✅ | ✅ |
| **Interactive Command Input & Plotting** | ✅ | ✅ |
| **ESP32-S3 Hardware Integration** | ❌ | ✅ |
| **Nema 17 Physical Motor Actuation** | ❌ | ✅ |
| **Real-Time Telemetry Stream over UART** | ❌ | ✅ |

---

## 🤖 Hardware Architecture (Task 2)

* **Main Controller:** ESP32-S3 (Dual-core Xtensa LX7, 240 MHz).
* **Actuators:** 3× Nema 17 Stepper Motors (42mm frame, 1.8° step angle, $200	ext{ steps/rev}$).
* **Drivers & Expansion:** CNC Shield V3 with A4988 microstepping drivers ($1/16$ microstepping mode).
* **Power Supply:** 12V 5A DC Switching Power Supply.
* **Kinematics Resolution:** 400	steps/mm scale factor on lead screw drives.

---

## 🎓 Skills & Knowledge Acquired

Through the successful completion of both Task 1 and Task 2 during the summer term, key engineering competencies were established:

1. **Python GUI & Trajectory Software Engineering:**
   * Developing interactive graphical interfaces (PyQt / PySide) for G-code parsing.
   * Implementing mathematical path generation for linear lines and trigonometric circular arcs ($G2/G3$).
   * Asynchronous serial communication handling and telemetry stream parsing.

2. **Embedded C++ & ESP32-S3 Firmware Development:**
   * Real-time task distribution across ESP32-S3 dual cores using FreeRTOS.
   * Deterministic microsecond step pulse timing using **Bresenham's Line Algorithm**.
   * Implementing trapezoidal acceleration/deceleration curves to eliminate motor step skipping.

3. **Mechatronics & Motion Control Systems:**
   * Motor driver tuning (Vref current adjustment) and microstepping configuration.
   * Lead screw kinematics, quantization errors, and open-loop position tracking.

---

## Copyright & Terms of Use

```text
================================================================================
PROJECT COPYRIGHT & TERMS OF USE
================================================================================
Copyright (c) 2026 Cao Tuấn Minh. All Rights Reserved.
Ho Chi Minh City University of Technology (HCMUT - Trường Đại học Bách Khoa TP.HCM)

This project, source code, hardware schematics, and documentation were created 
by Cao Tuấn Minh for academic coursework and research at HCMUT.

Permission is hereby granted for educational and non-commercial review. 
Unauthorized distribution, commercial exploitation, or reproduction 
without explicit written permission from the author is strictly prohibited.
================================================================================
```
