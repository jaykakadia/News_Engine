from flask import Blueprint, render_template, jsonify, request, session
import os
import uuid
from datetime import datetime
from google import genai
from app.utils.embeddings import get_embeddings
from app.utils.vector_db import news_collection
from app.models.chat import ChatHistory
from app.schemas.models import ChatHistorySchema

# No url_prefix so we can define both /chat/ and /api/chat exactly as they were
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/', methods=['GET'])
def chat_view():
    return render_template("chat.html")

@chat_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Returns saved chat history for the logged-in user."""
    user_id = session.get('user_id') or session.get('tenant_id', '')
    if not user_id:
        return jsonify({"history": []})
    
    chats = ChatHistory.get_by_user(user_id)
    history = []
    for chat in chats:
        history.append({"role": "user", "content": chat.query})
        history.append({"role": "model", "content": chat.response})
    
    return jsonify({"history": history})

@chat_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    query = data.get('query')
    history = data.get('history', [])
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"response": "Error: GEMINI_API_KEY is not set in the environment variables. Please add it to your .env file."}), 500
        
    try:
        # Initialize Gemini Client
        client = genai.Client(api_key=api_key)
        
        # Format history string (keep last 6 messages to save tokens but retain context)
        history_text = ""
        for msg in history[-6:]:
            role = "User" if msg['role'] == 'user' else "AI"
            history_text += f"{role}: {msg['content']}\n"
            
        # --- QUERY REFORMULATION ---
        # If there is history, we use the LLM to quickly rewrite the query to resolve pronouns (e.g., "her" -> "Taylor Swift")
        search_query = query
        if history_text:
            reformulate_prompt = f"""Given the following conversation history, rewrite the latest user question into a standalone search query. 
For example, if the user asks "what about her?", rewrite it to "what about Taylor Swift?".
If the question is already clear, just output the exact same question.
Do NOT output anything else except the rewritten query.

Chat History:
{history_text}
Latest Question: {query}
Rewritten Query:"""
            
            rewrite_response = client.models.generate_content(
                model='gemma-3-4b-it',
                contents=reformulate_prompt
            )
            search_query = rewrite_response.text.strip()
            print(f"Original Query: '{query}' -> Reformulated: '{search_query}'")
        
        # 1. Embed the standalone search query
        query_embedding = get_embeddings(search_query)
        
        # 2. Retrieve relevant context from ChromaDB
        results = news_collection.query(
            query_embeddings=[query_embedding],
            n_results=15
        )
        
        # Combine the retrieved documents into a single context string
        context_chunks = []
        if results and results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                source = meta.get('source', 'Unknown Source')
                title = meta.get('title', 'Unknown Title')
                context_chunks.append(f"[{source}] {title}: {doc}")
                
        context = "\n\n".join(context_chunks)
        
        if not context:
            return jsonify({"response": "I couldn't find any relevant news in my database to answer your question."})
            
        # 3. Construct the prompt
        prompt = f"""You are an intelligent News AI Assistant. 
Use ONLY the following retrieved news context to answer the user's question. 
Take the Chat History into consideration so you can naturally converse with the user.
If the answer is not contained in the context, say "I don't have enough information in my news database to answer that." 
Cite your sources by mentioning the source name from the context.

Retrieved Context:
{context}

Chat History:
{history_text}

User Question: {query}
Answer:"""

        # 4. Generate response using Gemini
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt
        )
        
        response_text = response.text
        
        # 5. Save chat history to DynamoDB
        user_id = session.get('user_id') or session.get('tenant_id', '')
        if user_id:
            chat_record = ChatHistorySchema(
                chat_id=str(uuid.uuid4()),
                user_id=user_id,
                query=query,
                response=response_text,
                created_at=datetime.utcnow()
            )
            ChatHistory.save(chat_record)
        
        return jsonify({
            "response": response_text,
            "search_query": search_query if search_query != query else None
        })
        
    except Exception as e:
        print(f"Error in chat API: {e}")
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500
