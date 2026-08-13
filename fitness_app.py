import os
import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai

# 1. Configuration & Setup
st.set_page_config(page_title="AI Fitness Tracker", page_icon="💪", layout="wide")

# Configure Google Gemini AI (Set GEMINI_API_KEY in your environment)
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# For quick testing, you can uncomment and paste your key below:
genai.configure(api_key="YOUR_GEMINI_API_KEY")

PROGRESS_FILE = "fitness_progress.csv"

# Initialize progress tracking file if it doesn't exist
if not os.path.exists(PROGRESS_FILE):
    df_init = pd.DataFrame(columns=["Date", "Exercise", "Weight", "Reps", "Notes"])
    df_init.to_csv(PROGRESS_FILE, index=False)

# 2. AI Plan Generator Function
def generate_ai_workout(goal, level, equipment):
    prompt = f"""
    Create a personalized 3-day workout plan based on the following criteria:
    - Goal: {goal}
    - Fitness Level: {level}
    - Available Equipment: {equipment}
    
    Format the response clearly with Day 1, Day 2, and Day 3, listing specific exercises, target sets, and repetitions. Keep it concise and motivating.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating plan. Check your API key. Details: {e}"

# 3. Streamlit User Interface Layout
st.title("💪 AI-Powered Fitness Tracker & Plan Generator")
tab1, tab2, tab3 = st.tabs(["🤖 Generate Workout Plan", "📝 Log Workout", "📈 Track Progress"])

# --- TAB 1: AI Plan Generator ---
with tab1:
    st.header("Get Your Custom AI Workout Routine")
    col1, col2 = st.columns(2)
    with col1:
        goal = st.selectbox("Primary Goal", ["Weight Loss", "Muscle Building", "Endurance", "General Fitness"])
        level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    with col2:
        equipment = st.text_input("Available Equipment (e.g., Dumbbells, Barbell, Bodyweight only)")
        
    if st.button("Generate Plan"):
        with st.spinner("AI is designing your custom routine..."):
            plan = generate_ai_workout(goal, level, equipment)
            st.session_state['generated_plan'] = plan
            
    if 'generated_plan' in st.session_state:
        st.subheader("Your Personalized Routine:")
        st.markdown(st.session_state['generated_plan'])

# --- TAB 2: Log Workout ---
with tab2:
    st.header("Log Your Daily Session")
    with st.form("log_form"):
        log_date = st.date_input("Date", datetime.date.today())
        exercise = st.text_input("Exercise Name (e.g., Squat, Bench Press)")
        weight = st.number_input("Weight Used (kg / lbs)", min_value=0.0, step=0.5)
        reps = st.number_input("Repetitions Completed", min_value=0, step=1)
        notes = st.text_area("Notes / RPE (Rate of Perceived Exertion)")
        
        submitted = st.form_submit_button("Save Entry")
        if submitted:
            new_data = pd.DataFrame([[log_date, exercise, weight, reps, notes]], 
                                    columns=["Date", "Exercise", "Weight", "Reps", "Notes"])
            new_data.to_csv(PROGRESS_FILE, mode='a', header=False, index=False)
            st.success("Workout logged successfully!")

# --- TAB 3: Track Progress ---
with tab3:
    st.header("Your Progress Over Time")
    if os.path.exists(PROGRESS_FILE):
        df_progress = pd.read_csv(PROGRESS_FILE)
        if not df_progress.empty:
            st.dataframe(df_progress, use_container_width=True)
            
            # Simple Matplotlib chart for a selected exercise
            exercises = df_progress["Exercise"].unique()
            selected_ex = st.selectbox("Select exercise to visualize weight progression:", exercises)
            
            ex_data = df_progress[df_progress["Exercise"] == selected_ex]
            if not ex_data.empty:
                fig, ax = plt.subplots()
                ax.plot(pd.to_datetime(ex_data["Date"]), ex_data["Weight"], marker='o', linestyle='-', color='b')
                ax.set_title(f"Progress Over Time: {selected_ex}")
                ax.set_xlabel("Date")
                ax.set_ylabel("Weight")
                plt.xticks(rotation=45)
                st.pyplot(fig)
        else:
            st.info("No workout logs recorded yet. Use the 'Log Workout' tab to add entries.")

       