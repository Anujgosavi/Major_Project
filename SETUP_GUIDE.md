# 🚀 AI Posture Monitor - Setup Guide

Welcome! This guide will help you easily get the Live Posture Monitor running on your computer. Follow these steps carefully.

---

### 📦 Prerequisites
Before you start, please make sure you have the following installed on your computer:
1. **Python (version 3.9 or higher)** - Make sure to check the box that says "Add Python to PATH" during installation.
2. **Node.js** - For running the frontend.
3. **Git** - For downloading the code.

---

### Step 1: Download the Project
1. Open your terminal (Command Prompt or PowerShell on Windows, or Terminal on Mac).
2. Download the latest code by running:
   ```bash
   git pull origin main
   ```
   *(If you don't have the folder yet, clone it using `git clone <your-repository-link>` and then type `cd Major_Project` to enter the folder).*

---

### Step 2: Set up the Backend (AI & Camera)
1. In your terminal, make sure you are in the main project folder (`Major_Project`).
2. Install all the necessary Python libraries by running:
   ```bash
   pip install -r requirements.txt
   ```
3. Once that finishes, start the AI server by typing:
   ```bash
   cd backend
   python api/server.py
   ```
4. **Leave this terminal open!** You should see messages indicating the Flask server has started.

---

### Step 3: Set up the Frontend (Website)
1. Open a **new** terminal window (keep the first one running).
2. Navigate into the frontend folder:
   ```bash
   cd frontend
   ```
   *(If you are starting from a completely new terminal, make sure to `cd` into your `Major_Project/frontend` folder first).*
3. Install the required website files by running:
   ```bash
   npm install
   ```
4. Start the website by running:
   ```bash
   npm start
   ```

---

### Step 4: Start Monitoring!
1. Your browser should automatically open to **http://localhost:3000**.
2. If it doesn't, open Chrome/Edge and go to `http://localhost:3000`.
3. Click the **"Start Monitor"** button.
4. Make sure to **Allow Camera Permissions** when your browser asks for it.
5. Sit up straight and enjoy!

---
*Note: To stop the project, go to your terminals and press `Ctrl + C`.*
