### 🏋️‍♂️ **AI Fitness Assistant**

**A Computer Vision-based Workout Tracker & AI Nutritionist**

The **AI Fitness Assistant** is a full-stack application that acts as your personal gym trainer. It uses **Artificial Intelligence (MediaPipe)** to track your body movements in real-time through your webcam, counting repetitions, checking your form, and calculating calories burned. It also features an AI Dietician to answer your nutrition questions.

### 🌟 **Features**
1. **AI Gym Trainer (Computer Vision)**

    Real-time pose estimation tracks key body landmarks to verify form and count reps for:

    💪 **Bicep Curls**: Tracks elbow angle (Extension > 160°, Contraction < 30°).

    🦵 **Squats**: Tracks knee angle and hip depth.

    🤸 **Pushups**: Monitors elbow flexion and body alignment.

    🏋️ **Shoulder Press**: Tracks arm extension overhead.

    🏃 **Lunges**: Uses "Ankle Spread" logic to differentiate lunges from squats.

    ⭐ **Jumping Jacks**: Tracks hand height and leg spread simultaneously.

    ⏱️ **Plank**: Measures body straightness (180°) and horizontal alignment for a timer-based hold.


2. **Analytics & Gamification**

    📊 **History Tracking**: Automatically saves every workout session to a database.

    📈 **Progress Visualization**: View total reps, calories burned, and daily breakdown.

    🎉 **Gamification**: Balloons fly when you hit 50% or 100% of your daily calorie goal.

    🔊 **Audio Feedback**: Beeps on successful reps or form errors (Windows compatible).


3. **AI Dietician**

 
🍏 **Chatbot Interface**: Ask questions like "What should I eat after a workout?" (Powered by LLM integration in `diet_ai.py`).

🛠️ **Tech Stack**

**Language**: Python 3.10+

**Frontend**: Streamlit (Web Dashboard)

**Computer Vision**: OpenCV, MediaPipe (Google)

**Data Processing**: NumPy, Pandas

**Database**: SQLite (Embedded relational DB)

**Visualization**: Streamlit Charts, Lottie Animations

📂 **Project Structure**

## 📂 Project Structure

```text
AI_Fitness_Project/
├── .streamlit/             # Streamlit Configuration
│   ├── config.toml         # UI Theme settings (Dark mode, colors)
│   └── API.txt             # API Key for the Dietician AI
├── images/                 # Directory for UI assets
│   ├── curl.png            # Guide image for Bicep Curls
│   ├── squat.png           # Guide image for Squats
│   ├── pushup.png          # Guide image for Pushups
│   ├── lunge.png           # Guide image for Lunges
│   ├── jump.png            # Guide image for Jumping Jacks
│   ├── plank.png           # Guide image for Planks
│   └── shoulder_press.png  # Guide image for Shoulder Press
├── app.py                  # Main Frontend Application (Streamlit Dashboard)
├── main.py                 # Computer Vision Engine (OpenCV & MediaPipe Logic)
├── database.py             # Database Management (SQLite connection & queries)
├── diet_ai.py              # AI Dietician Logic (Chatbot integration)
├── fitness_logs.db         # SQLite Database (Stores user profiles and workout logs)
├── gym_animation.json      # Lottie Animation file for the Home Dashboard
├── requirements.txt        # List of Python dependencies
└── README.md               # Project Documentation
```

### 🚀 **Installation & Setup**
1. **Prerequisites**
Ensure you have Python installed on your system.

2. **Install Dependencies**
Open your terminal/command prompt in the project folder and run:

`pip install -r requirements.txt`

If **requirements.txt** is missing, install manually:

`pip install streamlit opencv-python mediapipe pandas numpy streamlit-lottie sympy requests`
3. **Image Assets**
Ensure the following images are in your project folder for the UI to load correctly:

`curl.png, squat.png, pushup.png, lunge.png, jump.png, plank.png`

🏃‍♂️ **How to Run**
Open your terminal in the project directory.

Run the Streamlit app:

`streamlit run app.py`


The application will open in your default web browser (usually at http://localhost:8501).

### 🧠 How It Works (Under the Hood)
1. **The Architecture**
The app uses a Multi-Process Architecture:

    **Process A (Frontend)**: **app.py** runs the web interface. When you click "🚀 Launch Camera", it uses Python's **subprocess** library to spawn a separate script.

    **Process B (Backend)**: **main.py** opens the camera and handles the heavy computer vision processing independently. This ensures the web UI doesn't freeze while the camera is running.
2. **Logic FlowSelection**: User selects an exercise (e.g., "Bicep Curl") in the UI.
3. **Launch**: Streamlit executes: **python main.py curl**.
4. **Detection**: **main.py** initializes MediaPipe Pose to detect 33 body landmarks (shoulders, elbows, hips, knees, etc.).
5. **Geometry Calculation**:

    The app calculates angles (e.g., Angle at Elbow = $\arctan2(wrist) - \arctan2(shoulder)$).

    State Machine: It tracks the "Stage" of the rep (e.g., **UP** or **DOWN**). A rep is only counted if the user completes the full range of motion.

6. **Storage**: When the user presses **q** to quit, the session data (Reps, Calories) is saved to **fitness.db**.
7. **Update**: The user refreshes the web page to see the updated stats in the "History" tab.

⚠**️ Troubleshooting**

**Camera not opening**: Ensure no other app (Zoom, Teams) is using the webcam.

**Sound not working**: The beep sound uses **winsound**, which is Windows-only. The code includes a safety check so it won't crash on Mac/Linux, but sound will be disabled on those platforms.

**"Dietician"** **error**: Ensure **diet_ai.py** is properly configured with your API key if you are using an external LLM provider.

📜 **License**

This project was developed for educational purposes as a Major Project for AI/ML course.