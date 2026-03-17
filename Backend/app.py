from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
import requests
import base64

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key="AIzaSyAckzFj5uN4CWwXMjbPfsumLgIBHOOxOhA")



PROMPTS = {
    "Summary": """
You are a professional tourist guide.
Provide a high-level overview of "{place}" in {language}.

Focus on:
- The historical significance
- Why the place is famous
- Key architectural or cultural highlights

Keep the explanation concise, engaging, and easy to follow.
Avoid excessive details and dates.
Limit the response to around 200 words.

Respond ONLY in {language}.
""",

    "Detailed": """
You are a professional tourist guide.
Provide a detailed and immersive explanation of "{place}" in {language}.

Cover:
- Historical background and timeline
- Architectural design and unique features
- Cultural importance and notable events
- Interesting facts and visitor insights

Explain concepts clearly and in a storytelling manner.
Include relevant details and examples to create a rich experience.
Limit the response to around 400 words.

Respond ONLY in {language}.
"""
}

def generate_description(place, answer_type, language):
    prompt = PROMPTS[answer_type].format(place=place, language=language)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    print(response)
    return response.text
def generate_audio(voice_id,locale,description):
    url = "https://global.api.murf.ai/v1/speech/stream"
    headers = {
        "api-key": "ap2_d4436a80-fbcc-41a8-9394-5c4a4f77f3c5",
        "Content-Type": "application/json"
    }
    data = {
    "voice_id": voice_id,
    "text": description,
    "locale": locale,
    "model": "FALCON",
    "format": "MP3",
    "sampleRate": 24000,
    "channelType": "MONO"
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    if response.status_code == 200:
        audio_bytes = b''

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                audio_bytes += chunk

        print("Audio received successfully")

        # Convert to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return audio_base64

    else:
        print(f"Error: {response.status_code}")
        return None



    
@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():
    data = request.json
    print(data)
    place = data["place"]
    answer_type = data["answerType"]
    language = data["language"]
    voice_id=data["voiceId"]
    locale=data["locale"]
    
    text_description = generate_description(place, answer_type, language)
    audio=generate_audio(voice_id,locale,text_description)
    return jsonify({
        "description": text_description,
        "audioBase64":audio
    })

app.run(debug=True)