import cv2
import mediapipe as mp
import numpy as np
import sys
import database  # Import your database to save results

# --- 1. SETUP & SOUND SAFETY ---
# This block ensures the code runs on any computer without crashing
try:
    import winsound


    def play_sound():
        try:
            winsound.Beep(1000, 200)
        except:
            pass
except ImportError:
    # If winsound is missing (Mac/Linux), create a dummy function
    def play_sound():
        pass

# Get the mode from the app
if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    mode = "curl"

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# --- 2. ANGLE CALCULATION FUNCTION ---
def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


# --- 3. VIDEO CAPTURE ---
cap = cv2.VideoCapture(0)

# Global Variables
counter = 0
stage = None

# Setup MediaPipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = pose.process(image)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # ==========================================================
            # ISLAND 1: BICEP CURL
            # ==========================================================
            if mode == "curl":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = calculate_angle(shoulder, elbow, wrist)

                if angle > 160:
                    stage = "down"
                if angle < 30 and stage == 'down':
                    stage = "up"
                    counter += 1
                    play_sound()  # Safe sound call

                cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # ==========================================================
            # ISLAND 2: SQUAT
            # ==========================================================
            elif mode == "squat":
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                angle = calculate_angle(hip, knee, ankle)

                if angle > 170:
                    stage = "up"
                if angle < 90 and stage == 'up':
                    stage = "down"
                    counter += 1
                    play_sound()

                cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(knee, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # ==========================================================
            # ISLAND 3: PUSHUP
            # ==========================================================
            elif mode == "pushup":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = calculate_angle(shoulder, elbow, wrist)

                if angle <= 80:
                    stage = "down"
                if angle > 160 and stage == 'down':
                    stage = "up"
                    counter += 1
                    play_sound()

                cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # ==========================================================
            # ISLAND 4: SHOULDER PRESS
            # ==========================================================
            elif mode == "shoulder_press":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = calculate_angle(shoulder, elbow, wrist)

                if angle < 90:
                    stage = "down"
                if angle > 140 and stage == 'down':
                    stage = "up"
                    counter += 1
                    play_sound()

                cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # ==========================================================
            # ISLAND 5: LUNGE
            # ==========================================================
            elif mode == "lunge":
                l_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                l_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                l_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                r_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                r_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                r_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                l_angle = calculate_angle(l_hip, l_knee, l_ankle)
                r_angle = calculate_angle(r_hip, r_knee, r_ankle)
                ankle_distance = abs(l_ankle[0] - r_ankle[0])

                if l_angle > 140 and r_angle > 140:
                    stage = "up"

                if stage == 'up':
                    if (l_angle < 110 or r_angle < 110):
                        if ankle_distance > 0.15:
                            stage = "down"
                            counter += 1
                            play_sound()
                        else:
                            cv2.putText(image, "SPREAD LEGS!", (50, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                h, w, _ = image.shape
                l_pos = tuple(np.multiply(l_knee, [w, h]).astype(int))
                cv2.putText(image, str(int(l_angle)), l_pos,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f"Spread: {round(ankle_distance, 2)}", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # ==========================================================
            # ISLAND 6: JUMPING JACKS
            # ==========================================================
            elif mode == "jumping_jack":
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                ankle_distance = abs(left_ankle[0] - right_ankle[0])
                are_hands_up = (left_wrist[1] < left_shoulder[1]) and (right_wrist[1] < right_shoulder[1])
                are_feet_apart = ankle_distance > 0.2

                if not are_hands_up and not are_feet_apart:
                    stage = "down"
                if are_hands_up and are_feet_apart and stage == "down":
                    stage = "up"
                    counter += 1
                    play_sound()

                cv2.putText(image, f"Ankle Dist: {round(ankle_distance, 2)}", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # ==========================================================
            # ISLAND 7: PLANK
            # ==========================================================
            elif mode == "plank":
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                shoulder_hip_angle = calculate_angle(left_shoulder, left_hip, left_ankle)
                height_diff = abs(left_shoulder[1] - left_ankle[1])

                if shoulder_hip_angle > 160 and height_diff < 0.3:
                    stage = "holding"
                else:
                    stage = "not holding"

                if stage == "holding":
                    counter += 0.033

                if stage == "not holding":
                    if height_diff >= 0.3:
                        cv2.putText(image, "GET ON FLOOR!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    elif shoulder_hip_angle <= 160:
                        cv2.putText(image, "STRAIGHTEN BACK!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.putText(image, f"Angle: {int(shoulder_hip_angle)}", (10, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, f"Time: {int(counter)}s", (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        except:
            pass

        # --- DRAW THE BOX & TEXT (Shared Visuals) ---
        cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)

        cv2.putText(image, 'REPS/TIME', (15, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # Smart display logic: int for reps, float for plank
        display_score = int(counter) if mode != "plank" else round(counter, 1)

        cv2.putText(image, str(display_score),
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(image, 'STAGE', (65, 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(stage),
                    (60, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                  )

        cv2.imshow('Mediapipe Feed', image)

        # EXIT LOGIC
        if cv2.waitKey(10) & 0xFF == ord('q'):
            if counter > 0:
                # 1. CALCULATE CALORIES
                cal_factor = 0.15
                if mode == "squat":
                    cal_factor = 0.50
                elif mode == "pushup":
                    cal_factor = 0.40
                elif mode == "shoulder_press":
                    cal_factor = 0.35
                elif mode == "lunge":
                    cal_factor = 0.45
                elif mode == "jumping_jack":
                    cal_factor = 0.20
                elif mode == "plank":
                    cal_factor = 0.06

                calories_burned = round(counter * cal_factor, 2)

                # 2. SAVE TO DATABASE
                data = {
                    'exercise_type': mode,
                    'reps': counter,
                    'score': calories_burned
                }
                database.save_workout(data)
                print(f"Session Saved: {counter} reps, {calories_burned} calories.")
            break

    cap.release()
    cv2.destroyAllWindows()