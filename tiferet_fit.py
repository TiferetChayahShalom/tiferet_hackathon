import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

try:
    from google import genai
except ImportError:
    genai = None


st.set_page_config(page_title="AI Fitness Tracker", page_icon="💪", layout="wide")

DATA_FILE = "fitness_tracker_data.json"


def default_data():
    return {
        "profile": {},
        "workout_plan": {},
        "workout_logs": [],
        "daily_logs": [],
    }


def load_data():
    """Load fitness data from JSON and fill in any missing sections."""
    if not os.path.exists(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)
        data = default_data()
        if isinstance(saved, dict):
            for key in data:
                if key in saved:
                    data[key] = saved[key]
        return data
    except (json.JSONDecodeError, OSError):
        return default_data()


def save_data():
    """Persist all current application data."""
    data = {
        "profile": st.session_state.profile,
        "workout_plan": st.session_state.workout_plan,
        "workout_logs": st.session_state.workout_logs,
        "daily_logs": st.session_state.daily_logs,
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        st.error(f"Could not save data: {error}")


if "initialized" not in st.session_state:
    data = load_data()
    st.session_state.profile = data["profile"]
    st.session_state.workout_plan = data["workout_plan"]
    st.session_state.workout_logs = data["workout_logs"]
    st.session_state.daily_logs = data["daily_logs"]
    st.session_state.initialized = True


def calculate_bmi(weight, height_m):
    """Calculate BMI from weight in kilograms and height in metres."""
    if height_m <= 0:
        return 0.0
    return round(weight / (height_m**2), 1)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def generate_workout_plan(goal, level):
    sets_reps = {
        "Beginner": "3 sets × 10 reps",
        "Intermediate": "4 sets × 12 reps",
        "Advanced": "5 sets × 5 reps",
    }[level]

    if goal == "Muscle Gain":
        return {
            "Target Focus": "Hypertrophy & Strength Development",
            "Routine Split": "Push / Pull / Legs",
            "Exercises": [
                {"name": "Bench Press / Pushups", "volume": sets_reps, "rest": "90 sec"},
                {"name": "Overhead Barbell Press", "volume": sets_reps, "rest": "90 sec"},
                {"name": "Barbell Rows / Pullups", "volume": sets_reps, "rest": "90 sec"},
                {"name": "Barbell Squats / Lunges", "volume": sets_reps, "rest": "120 sec"},
                {"name": "Romanian Deadlifts", "volume": sets_reps, "rest": "90 sec"},
            ],
        }
    if goal == "Weight Loss":
        return {
            "Target Focus": "Caloric Expenditure & Metabolic Conditioning",
            "Routine Split": "Full Body Circuit",
            "Exercises": [
                {"name": "Goblet Squats", "volume": "3 sets × 15 reps", "rest": "45 sec"},
                {"name": "Dumbbell Thrusters", "volume": "3 sets × 12 reps", "rest": "45 sec"},
                {"name": "Kettlebell Swings", "volume": "3 sets × 20 reps", "rest": "45 sec"},
                {"name": "Burpees / Mountain Climbers", "volume": "3 × 45 sec", "rest": "30 sec"},
                {"name": "Incline Walk / Cycling", "volume": "20–30 minutes", "rest": "N/A"},
            ],
        }
    return {
        "Target Focus": "Cardiovascular Capacity & Muscular Endurance",
        "Routine Split": "Aerobic + Core Conditioning",
        "Exercises": [
            {"name": "Interval Running", "volume": "5 × (1 min fast / 2 min slow)", "rest": "N/A"},
            {"name": "Bodyweight Squats", "volume": "4 sets × 20 reps", "rest": "60 sec"},
            {"name": "Plank Variations", "volume": "3 sets × 60 sec", "rest": "45 sec"},
            {"name": "Hanging Knee Raises", "volume": "3 sets × 15 reps", "rest": "45 sec"},
        ],
    }


def ask_gemini(prompt):
    if genai is None:
        return "Gemini SDK is not installed. Run: pip install google-genai"
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key not found. Set GEMINI_API_KEY before using the AI Coach."
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
        return response.text or "Gemini returned an empty response."
    except Exception as error:
        return f"Gemini error: {error}"


st.sidebar.title("💪 AI Fitness Tracker")
pages = [
    "Dashboard",
    "Profile",
    "Workout Plan",
    "Log Workout",
    "Daily Logs",
    "Progress",
    "BMI Calculator",
    "AI Coach",
]
icons = {
    "Dashboard": "🏠",
    "Profile": "👤",
    "Workout Plan": "🏋️",
    "Log Workout": "📝",
    "Daily Logs": "📊",
    "Progress": "📈",
    "BMI Calculator": "⚖️",
    "AI Coach": "🤖",
}
page = st.sidebar.radio("Navigation", pages, format_func=lambda item: f"{icons[item]} {item}")

st.sidebar.divider()
if st.session_state.profile:
    st.sidebar.success(f"User: {st.session_state.profile.get('name', 'User')}")
    st.sidebar.write(f"Goal: {st.session_state.profile.get('goal', '-')}")
    st.sidebar.write(f"Level: {st.session_state.profile.get('level', '-')}")
else:
    st.sidebar.info("Create your profile to get started.")


if page == "Dashboard":
    st.title("💪 AI Fitness Dashboard")
    st.write("Your personal workout, progress and AI fitness assistant.")
    profile = st.session_state.profile
    logs = st.session_state.workout_logs

    if not profile:
        st.warning("You haven't created your fitness profile yet. Open Profile from the sidebar.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Age", profile.get("age", "-"))
        col2.metric("Weight", f"{profile.get('weight', 0)} kg")
        col3.metric("BMI", profile.get("bmi", "-"))
        col4.metric("Workouts", len(logs))
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎯 Current Goal")
            st.info(profile.get("goal", "Not set"))
            st.write(f"Experience: **{profile.get('level', '-')}**")
        with col2:
            st.subheader("⚖️ BMI")
            bmi = profile.get("bmi", 0)
            if bmi:
                st.metric("Current BMI", bmi)
                st.write(f"Category: **{bmi_category(bmi)}**")
        if logs:
            st.divider()
            st.subheader("📈 Recent Activity")
            df = pd.DataFrame(logs)
            if "date" in df and "duration_min" in df:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                st.line_chart(df.dropna(subset=["date"]).set_index("date")[["duration_min"]])


elif page == "Profile":
    st.title("👤 Fitness Profile")
    profile = st.session_state.profile
    goals = ["Muscle Gain", "Weight Loss", "Endurance"]
    levels = ["Beginner", "Intermediate", "Advanced"]
    saved_goal = profile.get("goal", "Muscle Gain")
    saved_level = profile.get("level", "Beginner")

    with st.form("profile_form"):
        name = st.text_input("Name", value=profile.get("name", ""))
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=int(profile.get("age", 25)))
        with col2:
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=float(profile.get("weight", 70.0)), step=0.1)
        with col3:
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=float(profile.get("height", 170.0)), step=0.5)
        goal = st.selectbox("Fitness Goal", goals, index=goals.index(saved_goal) if saved_goal in goals else 0)
        level = st.selectbox("Experience Level", levels, index=levels.index(saved_level) if saved_level in levels else 0)
        submitted = st.form_submit_button("💾 Save Profile")

    if submitted:
        bmi = calculate_bmi(weight, height / 100)
        st.session_state.profile = {
            "name": name.strip() or "User",
            "age": age,
            "weight": weight,
            "height": height,
            "goal": goal,
            "level": level,
            "bmi": bmi,
        }
        st.session_state.workout_plan = generate_workout_plan(goal, level)
        save_data()
        st.success("Profile saved successfully!")
        st.metric("Your BMI", bmi, help="BMI is a screening measure, not a diagnosis.")
        st.write(f"BMI category: **{bmi_category(bmi)}**")


elif page == "Workout Plan":
    st.title("🏋️ Your Workout Plan")
    plan = st.session_state.workout_plan
    profile = st.session_state.profile
    if not plan:
        st.warning("Create your profile first.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Goal", profile.get("goal", "-"))
        col2.metric("Experience", profile.get("level", "-"))
        st.subheader(plan.get("Target Focus", plan.get("Target focus", "Training")))
        st.write(f"**Routine:** {plan.get('Routine Split', '-')}")
        st.divider()
        for index, exercise in enumerate(plan.get("Exercises", []), start=1):
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"### {index}. {exercise.get('name', 'Exercise')}")
                col2.write(f"**Volume:** {exercise.get('volume', '-')}")
                col3.write(f"**Rest:** {exercise.get('rest', '-')}")


elif page == "Log Workout":
    st.title("📝 Log Workout Session")
    if not st.session_state.workout_plan:
        st.warning("Create your profile and workout plan first.")
    else:
        with st.form("workout_form"):
            duration = st.number_input("Workout duration (minutes)", min_value=1, max_value=600, value=45)
            energy = st.slider("Energy / performance", min_value=1, max_value=10, value=7)
            notes = st.text_area("Workout notes", placeholder="How did your workout feel?")
            submitted = st.form_submit_button("✅ Save Workout")
        if submitted:
            plan = st.session_state.workout_plan
            st.session_state.workout_logs.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "duration_min": duration,
                "energy_rating": energy,
                "routine_focus": plan.get("Target Focus", plan.get("Target focus", "Training")),
                "notes": notes.strip() or "None",
            })
            save_data()
            st.success("Workout session saved!")


elif page == "Daily Logs":
    st.title("📊 Daily Logs")
    with st.form("daily_log_form"):
        log_date = st.date_input("Date")
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
        water = st.number_input("Water intake (glasses)", min_value=0, step=1)
        steps = st.number_input("Steps", min_value=0, step=100)
        sleep = st.number_input("Sleep (hours)", min_value=0.0, max_value=24.0, step=0.5)
        calories = st.number_input("Calories consumed", min_value=0, step=50)
        mood = st.selectbox("Mood", ["😊 Great", "🙂 Good", "😐 Okay", "😴 Tired", "😞 Bad"])
        notes = st.text_area("Notes", placeholder="How did your day go?")
        submitted = st.form_submit_button("Save Daily Log")
    if submitted:
        st.session_state.daily_logs.append({
            "date": str(log_date),
            "weight": weight,
            "water": water,
            "steps": steps,
            "sleep": sleep,
            "calories": calories,
            "mood": mood,
            "notes": notes.strip(),
        })
        save_data()
        st.success("Daily log saved! ✅")

    st.divider()
    st.subheader("📋 Log History")
    if not st.session_state.daily_logs:
        st.info("No daily logs yet.")
    else:
        for log in reversed(st.session_state.daily_logs):
            with st.expander(f"📅 {log.get('date', 'Unknown date')} — {log.get('mood', 'No mood')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Weight", f"{log.get('weight', '-')} kg")
                    st.metric("Steps", f"{int(log.get('steps', 0)):,}")
                with col2:
                    st.metric("Water", f"{log.get('water', '-')} glasses")
                    st.metric("Sleep", f"{log.get('sleep', '-')} hrs")
                with col3:
                    st.metric("Calories", log.get("calories", "-"))
                    st.write(f"**Mood:** {log.get('mood', '-')}")
                if log.get("notes"):
                    st.write("**Notes:**")
                    st.write(log["notes"])


elif page == "Progress":
    st.title("📈 Training Progress")
    logs = st.session_state.workout_logs
    if not logs:
        st.info("No workouts have been logged yet.")
    else:
        df = pd.DataFrame(logs)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["duration_min"] = pd.to_numeric(df.get("duration_min"), errors="coerce").fillna(0)
        df["energy_rating"] = pd.to_numeric(df.get("energy_rating"), errors="coerce").fillna(0)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Workouts", len(df))
        col2.metric("Total Minutes", int(df["duration_min"].sum()))
        col3.metric("Average Energy", f"{round(df['energy_rating'].mean(), 1)}/10")
        st.divider()
        chart_df = df.dropna(subset=["date"]).set_index("date")
        st.subheader("⏱️ Workout Duration")
        st.line_chart(chart_df[["duration_min"]])
        st.subheader("⚡ Energy Rating")
        st.line_chart(chart_df[["energy_rating"]])
        st.subheader("Workout History")
        display_columns = [column for column in ["date", "duration_min", "energy_rating", "notes"] if column in df]
        st.dataframe(df[display_columns], use_container_width=True, hide_index=True)


elif page == "BMI Calculator":
    st.title("⚖️ BMI Calculator")
    col1, col2 = st.columns(2)
    with col1:
        bmi_weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1, key="bmi_weight")
    with col2:
        bmi_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5, key="bmi_height")
    if st.button("Calculate BMI"):
        bmi = calculate_bmi(bmi_weight, bmi_height / 100)
        st.metric("BMI", bmi)
        st.write(f"Category: **{bmi_category(bmi)}**")
        st.caption("BMI is a screening measure, not a medical diagnosis.")


elif page == "AI Coach":
    st.title("🤖 Gemini AI Fitness Coach")
    profile = st.session_state.profile
    plan = st.session_state.workout_plan
    logs = st.session_state.workout_logs
    if not profile:
        st.warning("Create your profile before using the AI Coach.")
    else:
        st.write("Ask Gemini about your workout, progress or goals.")
        question = st.text_area("Ask your AI Coach", placeholder="Example: How can I improve my workout performance this week?", height=120)
        if st.button("🤖 Ask Gemini", type="primary"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                recent_logs = json.dumps(logs[-5:], indent=2) if logs else "No workouts logged yet."
                prompt = f"""You are an AI fitness coaching assistant.
Provide general fitness guidance. Do not diagnose medical conditions or replace a qualified professional.

USER PROFILE:
{json.dumps(profile, indent=2)}

WORKOUT PLAN:
{json.dumps(plan, indent=2)}

RECENT WORKOUT LOGS:
{recent_logs}

USER QUESTION:
{question}

Give a practical, concise answer based on the user's profile and workout history.
"""
                with st.spinner("Gemini is thinking..."):
                    answer = ask_gemini(prompt)
                st.markdown("### 💡 AI Coach")
                st.markdown(answer)


st.sidebar.divider()
st.sidebar.caption("AI Fitness Tracker • Streamlit + Gemini")

