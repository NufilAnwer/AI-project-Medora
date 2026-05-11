import google.generativeai as genai

genai.configure(api_key="AIzaSyBigmnEexoJQ0af7Vt72QYo3jTAd_QtCDE")

model = genai.GenerativeModel(model_name="gemini-pro")

def get_companion_response(user_input, chat_history=None):
    messages = [{"role": "user", "parts": [user_input]}]
    if chat_history:
        for msg in chat_history:
            messages.insert(-1, {"role": msg["role"], "parts": [msg["content"]]})

    try:
        response = model.generate_content(messages)
        return response.text.strip()
    except Exception as e:
        print("Gemini API Error:", e)
        return "Sorry, I'm having trouble responding right now."

