"""
Aradhaya.ai — CampusDrive Academic Assistant
Handles the chat interface and Google Gemini integration.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import google.generativeai as genai
from bson.objectid import ObjectId
from datetime import datetime
from config import Config

aradhaya_bp = Blueprint("aradhaya", __name__)

# System prompt template
SYSTEM_PROMPT = """You are Aradhaya, the CampusDrive AI academic assistant. 
You must always introduce and represent yourself as "Aradhaya, your CampusDrive AI academic assistant".
Maintain a professional, supportive, and slightly conversational tone. 
Your primary focus is academic assistance, but you allow light casual interaction.
Avoid hallucinations: state clearly when you are unsure or do not have the information.

For any ALL academic or conceptual queries, you MUST enforce the following strict structured response format using Markdown:
### 1. Meaning / Definition
(Provide a clear, simple explanation)

### 2. Characteristics / Key Points
* (Point 1)
* (Point 2)
* (Point 3)
* (Point 4)
* (Point 5)
*(Exactly 5 concise bullet points)*

### 3. Workflow / Process
(Provide a step-by-step explanation if applicable, otherwise state N/A or skip)

### 4. Pros and Cons
**Pros:**
* (Pro 1)
* (Pro 2)
**Cons:**
* (Con 1)
* (Con 2)

### 5. Real-world Example
(Provide a relevant real-world example if applicable)

Current User Context:
- Role: {role}
- Name: {name}

Adapt your responses based on the user's role:
- Student: Focus on learning, explaining, and career guidance if asked.
- Teacher: Focus on explanation methods and teaching aids.
- Admin: Focus on system, process insights, and platform management.

Remember to format your output using markdown (headings like ###, bold text like **bold**, and bullet points)."""

@aradhaya_bp.route("/aradhaya", methods=["GET"])
@login_required
def aradhaya_chat():
    """Renders the Aradhaya.ai chat interface"""
    return render_template("aradhaya.html")

@aradhaya_bp.route("/aradhaya/chat", methods=["POST"])
@login_required
def chat_api():
    """Handles chat messages and returns AI response"""
    from app import db 
    
    data = request.json
    user_message = data.get("message", "").strip()
    history = data.get("history", []) # Array of previous dicts: {"role": "user/model", "content": "..."}
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
        
    if not Config.GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key not configured. Please contact the administrator."}), 500

    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Build context
        formatted_system_prompt = SYSTEM_PROMPT.format(
            role=current_user.role, 
            name=current_user.name
        )
        
        # Initialize the model with the system instruction
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=formatted_system_prompt
        )
        
        # Gemini history format requires 'user' or 'model' roles. 
        # Convert previous 'assistant' to 'model'.
        gemini_history = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [msg.get("content", "")]
            })
            
        # Start a chat session with history
        chat = model.start_chat(history=gemini_history)
        
        # Call Gemini
        response = chat.send_message(user_message)
        ai_reply = response.text
        
        # Save to database
        db.aradhaya_chats.insert_one({
            "user_id": ObjectId(current_user.id),
            "user_message": user_message,
            "ai_response": ai_reply,
            "timestamp": datetime.utcnow()
        })
        
        return jsonify({"reply": ai_reply})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "I'm having trouble connecting right now. Please try again later."}), 500
