# 🖼️ Python Web Watermark Studio

A lightweight, feature-rich web application built with **Flask** and **Pillow (PIL)** that allows users to automatically apply professional text or image watermarks to single photos or batch folders.

![Python Watermark Studio](https://img.shields.io/badge/Python-3.13%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🚀 Features

* **Single & Batch Processing:** Upload 1 photo for an immediate visual preview, or select multiple photos (2+) to process them in bulk packaged into a single downloadable `.zip` archive.
* **Dual Watermark Sources:** Switch seamlessly between a customized **Text Watermark** or an uploaded **Transparent Logo Watermark (`.png`)**.
* **Flexible Positioning:** Choose from 6 standard corner/edge placements (*Bottom-Right, Bottom-Left, Top-Right, Top-Left, Mid-Right, Mid-Left*) or a customizable **Diagonal Grid Pattern**.
* **Advanced Customization Sliders:**
  * **Opacity Slider:** Adjust watermark strength/transparency (`40` to `255`).
  * **Slanted Grid Angle Slider:** Dynamically appears when the grid pattern is selected, allowing rotation adjustment from `-90°` to `90°`.
* **Dynamic Sizing & Font Styles:** Choose between Small, Medium, and Large sizing options, plus fallback typography styles (*Sans-Serif, Serif, Monospace*).

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Werkzeug
* **Image Processing:** Pillow (`PIL`)
* **Frontend:** HTML5, Bootstrap 5, Custom JavaScript

---

## ⚙️ Installation & Running Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/python-web-watermark-studio.git](https://github.com/yourusername/python-web-watermark-studio.git)
   cd python-web-watermark-studio


2. **Navigate into the directory:**
    ```bash
    cd tic-tac-toe-web

3. **Open the game:**
    ```bash
    Double-click index.html to open it directly in your web browser, or use an extension like Live Server in Visual Studio Code.

---

## 📄 License
This project is open-source and available under the MIT License.