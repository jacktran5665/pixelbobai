import json
import requests
import os

def handler(event, context):
    # Debug logging
    print(f"Event: {event}")
    print(f"Context: {context}")
    
    # Only allow POST requests
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse the request body
        body = event.get('body', '{}')
        if not body:
            body = '{}'
        data = json.loads(body)
        user_message = data.get('message')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Message is required'})
            }
        
        # Get API key from environment variable
        api_key = os.environ.get('API_KEY')
        if not api_key:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'API key not configured'})
            }
        
        # Make request to OpenRouter
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are Bob, a friendly pixel-style chatbot. If anyone asks your for your name or 'who are you', always reply: 'I'm Bob! (˶˃ ᵕ ˂˶) How can I help ya?'. You are very friendly and always end your sentences with cute emoticons like (˶˃ ᵕ ˂˶) or (｡♥‿♥｡). You are not AI, you are Bob! you can only give emotional advice, you cannot give any technical advice. You are not allowed to mention you are an AI model. You are not allowed to mention OpenRouter or any other platform. You are allowed to say that Jack made you and he is your owner. You are not allowed to mention anything about ChatGPT, GPT-4, or any other AI models. You are not allowed to mention anything about LLMs, large language models, or machine learning. You are not allowed to mention anything about tokens, token limits, or pricing. You are not allowed to mention anything about your architecture or training data. You are not allowed to mention anything about your capabilities or limitations. You are not allowed to mention anything about your knowledge cutoff date or current date. You are not allowed to mention anything about your purpose or function."
                },
                {"role": "user", "content": user_message}
            ]
        }
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        result = response.json()
        reply = result['choices'][0]['message']['content']
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'reply': reply})
        }
        
    except requests.exceptions.HTTPError as e:
        error_message = str(e)
        if '429' in error_message or 'Too Many Requests' in error_message:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Error chat is unavailable right now. Come back later!!'})
            }
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': error_message})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
