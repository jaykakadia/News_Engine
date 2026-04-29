from flask import Blueprint, render_template, jsonify, request
import os
from google import genai
from app.models.news import NewsItem
from app.utils.embeddings import get_embeddings
from app.utils.vector_db import news_collection
from config.config import RSS_FEEDS

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def index():
    # Fetch real news from DynamoDB
    news_items = NewsItem.list_all(limit=15)
    return render_template("index.html", news=news_items)

@dashboard_bp.route('/article/<news_id>', methods=['GET'])
def article_detail(news_id):
    item = NewsItem.get_by_id(news_id)
    if not item:
        return "Article not found", 404
    return render_template("article.html", item=item)

@dashboard_bp.route('/dashboard/', methods=['GET'])
def get_dashboard():
    # Calculate basic stats
    news_items = NewsItem.list_all(limit=100)
    
    stats = {
        "total_news": len(news_items),
        "total_sources": len(RSS_FEEDS),
        "total_categories": len(set([f[1] for f in RSS_FEEDS]))
    }
    
    return render_template("dashboard.html", stats=stats)

@dashboard_bp.route('/chat/', methods=['GET'])
def chat_view():
    return render_template("chat.html")

@dashboard_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"response": "Error: GEMINI_API_KEY is not set in the environment variables. Please add it to your .env file."}), 500
        
    try:
        # Initialize Gemini Client
        client = genai.Client(api_key=api_key)
        
        # 1. Embed the query
        query_embedding = get_embeddings(query)
        
        # 2. Retrieve relevant context from ChromaDB
        results = news_collection.query(
            query_embeddings=[query_embedding],
            n_results=5
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
If the answer is not contained in the context, say "I don't have enough information in my news database to answer that." 
Cite your sources by mentioning the source name from the context.

Context:
{context}

User Question: {query}
Answer:"""

        # 4. Generate response using Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return jsonify({"response": response.text})
        
    except Exception as e:
        print(f"Error in chat API: {e}")
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500
