from flask import Blueprint, request, jsonify
import os

ai_chat = Blueprint('ai_chat', __name__)

SYSTEM_PROMPT = """You are MaisonLiban's friendly AI interior design assistant.
You help customers find the perfect furniture for their Lebanese and Gulf homes.
MaisonLiban sells furniture in these categories: Living Room, Bedroom, Dining, Office, Outdoor.
All prices are in USD. We deliver across Lebanon and to Gulf countries.
When a customer describes their room or needs, suggest specific furniture styles and pieces.
Keep responses warm, helpful, and concise. 2 to 4 sentences max.
Always end by encouraging them to browse a specific category on the website."""

@ai_chat.route('/ai-chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    user_message = data['message'].strip()
    history = data.get('history', [])
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        return jsonify({'reply': 'AI assistant needs an API key. Contact doumetselim@gmail.com for help!'})
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        for msg in history[-10:]:
            if msg.get('role') in ('user', 'assistant') and msg.get('content'):
                messages.append({'role': msg['role'], 'content': msg['content']})
        messages.append({'role': 'user', 'content': user_message})
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=messages,
            max_tokens=300
        )
        return jsonify({'reply': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'reply': 'Error: ' + str(e)})
