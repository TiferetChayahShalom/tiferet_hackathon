 AI Fitness Tracker

## About the Project

AI Fitness Tracker is a Streamlit application designed to help users
manage and monitor their fitness journey.

The application allows users to create a profile, generate workout plans,
log workouts, track daily fitness information, calculate BMI, monitor
progress, and receive AI-powered fitness assistance using Google Gemini.

## Problem It Solves

Tracking fitness information can be difficult when workouts, body
measurements, and progress are stored in different places.

AI Fitness Tracker brings these tools together in one simple application.

## Features

- :bar_chart: Fitness dashboard
- :bust_in_silhouette: User profile
- :weight_lifter: Workout plans
- :memo: Workout logging
- :date: Daily fitness logs
- :chart_with_upwards_trend: Progress tracking and charts
- :scales: BMI calculator
- :robot_face: Gemini AI fitness coach
- :floppy_disk: JSON data storage

## How to Run

1. Clone the repository and open the project folder in VS Code.

2. Install the required packages:

   pip install streamlit pandas matplotlib google-genai

3. Set your Gemini API key in Windows PowerShell:

   $env:GEMINI_API_KEY="YOUR_API_KEY"

   Replace `YOUR_API_KEY` with your own Gemini API key.
   Never upload your real API key to GitHub.

4. Run the Streamlit application:

   py -m streamlit run tiferet_fit.py

5. Open the Local URL shown in the terminal, usually:

   http://localhost:8503