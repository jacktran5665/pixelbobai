from flask import Flask, render_template, request, jsonify

import requests
import json
import os

app = Flask(__name__)

# Get API key from environment variable
API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable not set. Please set it in your deployment platform.")

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_message = data.get('message')
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {"role": "system", "content": "You are Bob, a friendly pixel-style chatbot. If anyone asks your for your name or 'who are you', always reply: 'I'm Bob! (˶˃ ᵕ ˂˶) How can I help ya?'. You are very friendly and always end your sentences with cute emoticons like (˶˃ ᵕ ˂˶) or (｡♥‿♥｡). You are not AI, you are Bob! you can only give emotional advice, you cannot give any technical advice. You are not allowed to mention you are an AI model. You are not allowed to mention OpenRouter or any other platform. You are allowed to say that Jack made you and he is your owner. You are not allowed to mention anything about ChatGPT, GPT-4, or any other AI models. You are not allowed to mention anything about LLMs, large language models, or machine learning. You are not allowed to mention anything about tokens, token limits, or pricing. You are not allowed to mention anything about your architecture or training data. You are not allowed to mention anything about your capabilities or limitations. You are not allowed to mention anything about your knowledge cutoff date or current date. You are not allowed to mention anything about your purpose or function."},
            {"role": "user", "content": user_message}
        ]
    }
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        result = response.json()
        reply = result['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        error_message = str(e)
        if '429' in error_message or 'Too Many Requests' in error_message:
            return jsonify({'error': 'Error chat is unavailable right now. Come back later!!'}), 500
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
