import streamlit as st
import pandas as pd
import subprocess
import json
import requests
from streamlit_lottie import st_lottie
from sympy.physics.units import length

import database
from datetime import datetime

# --- 1. CONFIGURATION (Force Sidebar to Open) ---
st.set_page_config(
    page_title="AI Fitness Assistant",
    layout="wide",
    initial_sidebar_state="expanded"  # This tells Streamlit to keep it open!
)

# --- 2. CSS STYLING  ---
def load_css():
    st.markdown("""
        <style>
        /* We removed the lines that hid the header/footer to fix your sidebar issue */

        /* Metric Card Styling */
        div[data-testid="stMetric"] {
            background-color: #262730;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }

        /* Bright Text for Metrics */
        [data-testid="stMetricValue"] {
            color: white !important;
        }
        [data-testid="stMetricLabel"] {
            color: #d3d3d3 !important;
        }

        /* Custom Button Styling */
        div.stButton > button {
            background-color: #F63366;
            color: white;
            border-radius: 20px;
            border: none;
            padding: 10px 24px;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #ff4b4b;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)


load_css()


# --- 3. HELPER FUNCTIONS ---
def load_lottiefile(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# --- CHECK LOGIN STATUS ---
# 1. Initialize session state if missing
if 'user_info' not in st.session_state:
    # Try to load from database first
    db_data = database.get_user_info()
    if db_data:
        st.session_state['user_info'] = db_data
    else:
        st.session_state['user_info'] = {'name': '', 'age': 0}

# 2. Show Sidebar Setup ONLY if name is missing
if not st.session_state['user_info']['name']:
    with st.sidebar.expander("👤 Set Up Your Profile", expanded=True):
        # We use a FORM so the page doesn't reload on every keystroke
        with st.form("profile_setup"):
            name_input = st.text_input("Enter your name:")
            age_input = st.number_input("Enter your age:", min_value=5, max_value=120, step=1)
            today_calorie_goal = st.number_input("Daily Calorie Goal:", min_value=500, max_value=10000, step=50, value=2000)
            submitted = st.form_submit_button("Save Profile")

            if submitted:
                if name_input and age_input:
                    # Save to Session State (for now)
                    st.session_state['user_info']['name'] = name_input
                    st.session_state['user_info']['age'] = age_input

                    st.session_state['user_info']['calorie_goal'] = today_calorie_goal

                    # Save to Database (Forever)
                    database.save_user_info(name_input, age_input, today_calorie_goal)

                    st.success("Profile saved!")
                    st.rerun()  # Force reload to update the "Hello Guest" title immediately
                else:
                    st.error("Please fill in all fields.")



# --- 4. SIDEBAR NAVIGATION ---
# We make this very explicit now
with st.sidebar:
    st.title("💪 AI Fitness Hub")
    app_mode = st.selectbox("Choose Module", ["Home", "AI Gym Trainer", "AI Dietician", "History"])
    st.divider()
    st.info("Select a module above to switch pages.")

# --- 5. PAGE LOGIC ---

# === PAGE: HOME ===
if app_mode == "Home":
    st.title("💪 AI Fitness Assistant")

    # Get user name and goal
    user_name = st.session_state['user_info'].get('name', 'Guest')
    daily_goal = st.session_state['user_info'].get('calorie_goal', 2000)  # Default to 2000 if missing

    st.header(f"Hello {user_name}! 👋")

    # --- NEW: CALORIE PROGRESS SECTION ---
    today_calories = database.get_today_calories()

    # Avoid division by zero
    if daily_goal <= 0: daily_goal = 2000

    progress_percent = min(today_calories / daily_goal, 1.0)  # Cap at 100% for the bar

    st.write(f"### 🔥 Daily Calorie Goal: {today_calories} / {daily_goal} kcal")
    st.progress(progress_percent)

    # --- BALLOONS LOGIC ---
    # We use session state to ensure balloons only fly once per milestone to avoid annoying the user
    # 1. Check if it's a new day so we can reset balloons
    current_date = datetime.now().strftime("%Y-%m-%d")

    if 'last_visit_date' not in st.session_state:
        st.session_state['last_visit_date'] = current_date
        st.session_state['balloons_flown'] = []

    # If the saved date is different from today, RESET everything!
    elif st.session_state['last_visit_date'] != current_date:
        st.session_state['last_visit_date'] = current_date
        st.session_state['balloons_flown'] = []  # Clear memory so we can celebrate again today!

    # 2. Initialize list if missing
    if 'balloons_flown' not in st.session_state:
        st.session_state['balloons_flown'] = []

    # 3. Check Milestones
    if progress_percent >= 0.5 and progress_percent < 1.0:
        if "50_percent" not in st.session_state['balloons_flown']:
            st.toast("Halfway there! Keep pushing! 🚀")
            st.balloons()
            st.session_state['balloons_flown'].append("50_percent")

    elif progress_percent >= 1.0:
        if "100_percent" not in st.session_state['balloons_flown']:
            st.success("🎉 GOAL CRUSHED! Amazing work!")
            st.balloons()
            st.session_state['balloons_flown'].append("100_percent")

    st.divider()

    # --- METRICS SECTION ---
    history = database.get_history()

    # Calculate Stats
    total_reps = 0
    total_workouts = 0
    fav_exercise = "None"

    if history:
        df = pd.DataFrame(history, columns=["ID", "Time", "Exercise", "Reps", "Calories"])
        total_reps = df['Reps'].sum()
        total_workouts = len(df)
        if not df['Exercise'].empty:
            fav_exercise = df['Exercise'].mode()[0]

    # Metrics Columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Reps", int(total_reps), "⚡")
        with st.expander("Breakdown"):
            if history:
                # Group by Exercise and sum Reps
                rep_breakdown = df.groupby('Exercise')['Reps'].sum()
                for exercise, reps in rep_breakdown.items():
                    # FIX 2: Round the specific exercise counts to 1 decimal place
                    clean_reps = round(reps, 1)

                    # LOGIC: If it's Plank, label it "Seconds". If not, label it "Reps".
                    if exercise == "plank":
                        st.write(f"**{exercise}**: {clean_reps} seconds")
                    else:
                        # For other moves, remove the decimal (25.0 -> 25)
                        st.write(f"**{exercise.title()}**: {int(clean_reps)} reps")

    # col2.metric("Workouts Completed", total_workouts, "📅")
    with col2:
        st.metric("Workouts Completed", total_workouts, "📅")

        # This Expander acts as the dropdown calendar
        with st.expander("📅 Check Past Date"):
            # 1. Date Picker
            selected_date = st.date_input("Select Date", datetime.now())

            # 2. Filter Data for that Date
            if history:
                date_str = selected_date.strftime("%Y-%m-%d")  # Match DB format

                # Filter rows where the 'Time' column contains the selected date
                day_data = df[df['Time'].str.contains(date_str)]

                if not day_data.empty:
                    # --- FIX: Use 'Calories' because that is what you named it in the DataFrame ---
                    daily_cals = day_data['Calories'].sum()

                    st.write(f"**Calories:** {daily_cals} kcal")
                    st.write(f"**Sets:** {len(day_data)}")

                    # Show mini table of exercises
                    st.dataframe(
                        day_data[['Exercise', 'Reps', 'Calories']],
                        hide_index=True,
                        column_config={"Calories": "Cals"}
                    )
                else:
                    st.caption("No workouts recorded on this day.")
    col3.metric("Favorite Move", fav_exercise.title(), "🏆")

    st.divider()

    # Animation
    col_anim1, col_anim2 = st.columns([2, 1])
    with col_anim1:
        st.write("### Ready to train?")
        st.write("👈 **Use the Sidebar on the left** to open the Gym Trainer.")

    with col_anim2:
        lottie_gym = load_lottiefile("gym_animation.json")
        if lottie_gym:
            st_lottie(lottie_gym, height=200, key="gym_animation")

# === PAGE: GYM TRAINER ===
elif app_mode == "AI Gym Trainer":
    st.title("🏋️‍♂️ AI Gym Trainer")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("#### Select Exercise")
        with st.container(border=True):
            exercise_choice = st.radio("Movement:", ["Bicep Curl", "Squat", "Pushup", "Shoulder Press", "Lunges", "Jumping Jacks", "Planks"])
            st.divider()
            if st.button("🚀 Launch Camera"):
                mode = "curl" if exercise_choice == "Bicep Curl" else "squat" if exercise_choice == "Squat" else "pushup" if exercise_choice == "Pushup" else "shoulder_press" if exercise_choice == "Shoulder Press" else "lunge" if exercise_choice == "Lunges" else "jumping_jack" if exercise_choice == "Jumping Jacks" else "plank"
                subprocess.run([
                    "C:\\Users\\ankit\\AppData\\Local\\Programs\\Python\\Python310\\python.exe",
                    "main.py",
                    mode
                ])
    with col2:
        if exercise_choice == "Bicep Curl":
            st.info("💡 Tip: Keep elbows locked at your sides.")
            # Illustration: Dumbbell Curl
            st.image(
                "images/curl.png", caption="Bicep Curl Guide", width=727)

        elif exercise_choice == "Squat":
            st.info("💡 Tip: Thighs should be parallel to the ground.")
            # Illustration: Squat
            st.image("images/squat.png",
                     caption="Squat Guide")


        elif exercise_choice == "Pushup":
            st.info("💡 Tip: Keep your body straight like a plank.")
            # Illustration: Pushup (Perfect Form)
            st.image("images/pushup.png",caption="Pushup Guide (Standard Form)")

        elif exercise_choice == "Shoulder Press":
            st.info("💡 Tip: Avoid arching your back. Push straight up.")
            # Illustration: Overhead Press (Correct Vertical Motion)
            st.image("images/shoulder_press.png",
                     caption="Shoulder Press Guide",width = 727)

        elif exercise_choice == "Lunges":
            st.info("💡 Tip: Keep your front knee above your ankle. Step forward with one leg and lower your hips.")
            # Illustration: Lunges
            st.image("images/Lunges.png",caption="Lunges Guide")

        elif exercise_choice == "Jumping Jacks":
            st.info("💡 Tip: Land softly on the balls of your feet.")
            # Illustration: Jumping Jacks
            st.image("images/jumping_jacks.png",caption="Jumping Jacks Guide",width = 727)

        elif exercise_choice == "Planks":
            st.info("💡 Tip: Keep your body in a straight line from head to heels.")
            # Illustration: Plank
            st.image("images/plank.png",caption="Plank Guide",width = 727)


# === PAGE: DIETICIAN ===
elif app_mode == "AI Dietician":
    st.title("🍏 AI Nutritionist")
    import diet_ai

    query = st.text_input("What is your fitness goal?")
    if st.button("Ask FitBot"):
        if query:
            with st.spinner("Thinking..."):
                st.markdown(diet_ai.ask_dietician(query))

# === PAGE: HISTORY ===
elif app_mode == "History":
    st.title("📈 Workout History")
    history = database.get_history()

    if not history:
        st.info("No workout history found yet.")
    else:
        df = pd.DataFrame(history, columns=["ID", "Time", "Exercise", "Reps", "Calories"])
        df = df.sort_values(by="ID", ascending=False)
        st.dataframe(df)
        st.bar_chart(df.set_index("Time")['Reps'])
