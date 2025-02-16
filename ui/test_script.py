import requests
import json

url = "http://127.0.0.1:8000/api/generate-speech/"
data = {
    "text": "What is your question again?",
    "language": "fr-FR"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(data), headers=headers)

if response.status_code == 200:
    response_data = response.json()
    print("Speech generated successfully!")
    print("Audio File URL:", response_data["audio_url"])
else:
    print(f" Error {response.status_code}: {response.text}")
