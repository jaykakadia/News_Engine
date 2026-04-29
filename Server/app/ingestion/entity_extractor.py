"""
Entity Extractor — Uses Gemini to extract companies, people, and topics from article content.
"""
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def extract_entities(title, content):
    """
    Uses Gemini to extract entities (companies, people, topics) from an article.
    
    Returns a dict: {"companies": [...], "people": [...], "topics": [...]}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"companies": [], "people": [], "topics": []}
    
    # Use a small portion of content to save tokens
    text = f"{title}. {content[:1500]}" if content else title
    
    prompt = f"""Extract named entities from this news article. Return ONLY a JSON object with three arrays:
- "companies": company or organization names mentioned
- "people": person names mentioned  
- "topics": key topics or themes (max 5)

Keep each list to max 5 items. If none found, return empty arrays.
Return ONLY valid JSON, nothing else.

Article:
{text}"""
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemma-3-4b-it',
            contents=prompt
        )
        
        # Parse the JSON response
        response_text = response.text.strip()
        # Clean markdown code fences if present
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
            response_text = response_text.rsplit('```', 1)[0]
        
        import json
        entities = json.loads(response_text.strip())
        
        return {
            "companies": entities.get("companies", [])[:5],
            "people": entities.get("people", [])[:5],
            "topics": entities.get("topics", [])[:5]
        }
        
    except Exception as e:
        print(f"    ⚠️ Entity extraction failed: {e}")
        return {"companies": [], "people": [], "topics": []}
