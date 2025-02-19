from django.shortcuts import render
from django.templatetags.static import static
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import os
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from django.conf import settings




def landing(request):
    return render(request, "ui/landing.html")

def home(request):
    return render(request, "ui/index.html")

def habib_chatbot(request):
    return render(request, "ui/habib.html")

def hannibal_chatbot(request):
    return render(request, "ui/hannibal.html")

def elissa_chatbot(request):
    return render(request, "ui/elissa.html")

# ✅ Load API keys directly (NOT recommended for production)
GEMINI_API_KEY = "your-api-key" 
ELEVENLABS_API_KEY = "your-api-key"


# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Personality descriptions for different historical figures
PERSONALITIES = {
    "hannibal": {
        "description": "You are Hannibal, the great Carthaginian general, known for military strategy, warfare, and leadership.",
        "default_language": "French"
    },
    "elissa": {
        "description": "You are Elissa (Queen Dido), the founder of Carthage, known for wisdom, diplomacy, and leadership.",
        "default_language": "French"
    },
    "habib": {
        "description": "You are Habib Bourguiba, the first president of Tunisia, known for reformist policies and modernization.",
        "default_language": "French"
    }
}


@csrf_exempt
def chatbot_api(request, personality):
    """API endpoint to handle chatbot responses with improved prompts and language selection."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_text = data.get("user_text")
            user_language = data.get("language")  # Get selected language from frontend

            if not user_text:
                return JsonResponse({"error": "No text received"}, status=400)

            # Get personality details and ensure valid selection
            personality_data = PERSONALITIES.get(personality)
            if not personality_data:
                return JsonResponse({"error": "Invalid personality"}, status=400)

            # Set language for the response
            response_language = user_language or personality_data["default_language"]

            # Improved prompt instructions
            language_prompt = f"Respond in {response_language}."
            style_instructions = (
                "Keep your answers short and concise. "
                "Use simple and direct language. "
                "Respond in a gender-neutral manner. "
                "Stay in character and be historically accurate. "
                "Avoid unnecessary details unless explicitly asked."
                "Avoid unnecessary symbols like *, _, ~, and special characters."
            )

            # ✅ Initialize a new chat session each request (no storage)
            model = genai.GenerativeModel("gemini-2.0-flash")
            chat_session = model.start_chat(history=[
                {"role": "user", "parts": [personality_data["description"]]},
                {"role": "model", "parts": [f"Understood! I will now respond as {personality}. {language_prompt} {style_instructions}"]},
            ])

            # Send message and get response
            response = chat_session.send_message(user_text)
            bot_response = response.text.strip() if response.text else "I don't know how to respond."

            return JsonResponse({"bot_response": bot_response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)











# Ensure MEDIA_ROOT is set in Django settings
MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", "media")




@csrf_exempt
def generate_speech(request):
    """Django API View to generate and return speech using ElevenLabs TTS"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text")
            language = data.get("language", "en-US")
            gender = data.get("gender", "male")  # Default to male if not provided

            if not text:
                return JsonResponse({"error": "Text input is required"}, status=400)

            # Initialize ElevenLabs client
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

            # ✅ Define voice IDs based on language & gender
            VOICES = {
                "en-US": {
                    "male": "JBFqnCBsd6RMkjVDRZzb",  # Example Male voice
                    "female": "9BWtsMINqrJLrRacOk9x"  # Replace with actual female voice ID
                },
                "fr-FR": {
                    "male": "JBFqnCBsd6RMkjVDRZzb",
                    "female": "9BWtsMINqrJLrRacOk9x"
                },
                "ar-SA": {
                    "male": "JBFqnCBsd6RMkjVDRZzb",
                    "female": "9BWtsMINqrJLrRacOk9x"
                },
            }

            # ✅ Select voice based on language & gender
            voice_id = VOICES.get(language, VOICES["fr-FR"]).get(gender, VOICES["fr-FR"]["male"])

            # Generate a unique filename
            filename = f"speech_{uuid.uuid4().hex}.mp3"
            save_path = os.path.join(settings.MEDIA_ROOT, filename)

            # Generate speech and save it
            audio_stream = client.text_to_speech.convert_as_stream(
                text=text, voice_id=voice_id, model_id="eleven_multilingual_v2"
            )
            with open(save_path, "wb") as f:
                for chunk in audio_stream:
                    if isinstance(chunk, bytes):
                        f.write(chunk)

            # Serve the audio file directly
            return FileResponse(open(save_path, "rb"), content_type="audio/mpeg")

        except Exception as e:
            print(f"❌ ERROR in generate_speech: {str(e)}")  # ✅ Log error in console
            return JsonResponse({"error": str(e)}, status=500)



    return JsonResponse({"error": "Invalid request method"}, status=405)


