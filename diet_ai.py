import google.generativeai as genai
import database
import os

# --- CONFIGURATION ---
# 1. Path to your API Key file
# We use 'os.path.join' to make sure it works on both Windows and Mac
api_key_path = os.path.join(".streamlit", "API.txt")

# 2. Read the Key securely
try:
    with open(api_key_path, "r") as f:
        API_KEY = f.read().strip()  # .strip() removes any accidental spaces or newlines
except FileNotFoundError:
    API_KEY = "KEY_NOT_FOUND"
    print("❌ ERROR: API.txt not found in .streamlit folder!")

# 3. Configure Gemini
if API_KEY != "KEY_NOT_FOUND":
    genai.configure(api_key=API_KEY)
    # Using the flash model for faster responses
    model = genai.GenerativeModel('models/gemini-1.5-flash')
else:
    model = None


def ask_dietician(user_question):
    # Safety Check
    if model is None:
        return "⚠️ **Error:** API Key is missing. Please check `.streamlit/API.txt`."

    # Get User Context from Database
    user_info = database.get_user_info()
    user_age = user_info['age'] if user_info else 25  # Default to 25 if unknown
    user_name = user_info['name'] if user_info else "User"

    # Strict System Prompt (The "Brain" of the AI)
    system_instruction = f"""
    You are 'FitBot', an elite Sports Nutritionist. 
    The user is {user_name}, aged {user_age}.

    Rules:
    1. Keep answers SHORT (max 3-4 bullet points).
    2. Be encouraging but scientific.
    3. If they ask about non-fitness topics, politely refuse.
    4. Use emojis.
    """

    try:
        # Combine instructions with user question
        full_prompt = f"{system_instruction}\n\nUser Question: {user_question}"

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **AI Error:** {str(e)}"