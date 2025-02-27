from flask import Flask, render_template, request, Response, g
from flask_cors import CORS
import json
import os
import uuid
from dotenv import load_dotenv
from collections.abc import Generator
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
from threading import Lock

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global conversation storage with thread lock
conversation_histories = {}
history_lock = Lock()

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

class ChatSystem:
    def __init__(self):
        self.llm = gemini
        self.mp_domains = [
            "quora.com", "directflights.com", "flightsfrom.com", "holidify.com",
            "cultureandheritage.org", "google.com", "cse.google.com", "wikipedia.org",
            "tripadvisor.in", "incredibleindia.gov.in", "https://www.irctc.co.in/nget/train-search",
            "https://state.bihar.gov.in/?utm_source=chatgpt.com", "https://traveltriangle.com/", "https://bihar.nic.in/?utm_source=chatgpt.com",
            "https://tourism.bihar.gov.in/", "https://www.india.gov.in/website-bihar-tourism", "https://state.bihar.gov.in/bihartourism/CitizenHome.html",
            "https://bstdc.bihar.gov.in/", "https://www.britannica.com/place/Patna", "https://www.britannica.com/place/Patna"
        ]
        self.max_history = 3
        
    def _get_history_buffer(self, session_id: str) -> str:
        """Get conversation history for a session"""
        with history_lock:
            history = conversation_histories.get(session_id, [])
            return "\n".join(
                [f"User: {item['query']}\nBABUA: {item['response']}" 
                 for item in history[-self.max_history:]]
            )
    
    def _update_history(self, session_id: str, query: str, response: str):
        """Update conversation history"""
        with history_lock:
            if session_id not in conversation_histories:
                conversation_histories[session_id] = []
            conversation_histories[session_id].append({
                "query": query,
                "response": response
            })

    def is_bihar_related(self, query: str) -> bool:
        prompt = """Analyze if this query relates to Bihar, India. 
        Consider: cities, education, hotels, tourism, schemes, culture, geography.
        Return only 'YES' or 'NO'. Query: {query}"""
        response = self.llm.invoke(prompt.format(query=query))
        return "YES" in response.content.strip().upper()
    
    def _extract_search_keywords(self, query: str) -> str:
        prompt = """Extract search engine optimized keywords from this query focusing on:
        - Core entities (people, places)
        - Key topics/requirements
        - Local language transliterations
        Return ONLY space-separated keywords. Query: {query}"""
        response = self.llm.invoke(prompt.format(query=query))
        return response.content.strip().replace(",", " ").replace(";", " ").replace("\n", " ")
    
    def generate_stream(self, prompt_template: str, inputs: dict) -> Generator[str, None, None]:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm
        for chunk in chain.stream(inputs):
            yield chunk.content

class ResponseEngine(ChatSystem):
    def process_query(self, query: str, session_id: str) -> tuple[Generator[str, None, None], list, list]:
        history_text = self._get_history_buffer(session_id)
        
        if not self.is_bihar_related(query):
            response_stream = self._generate_casual_response(query, history_text)
            images, sources = [], []
        else:
            search_query = self._extract_search_keywords(query)
            data = self._research_mp(search_query)
            response_stream = self._generate_mp_response(data, query, history_text)
            images = data.get("images", [])[:3]
            sources = data.get("sources", [])[:3]

        full_response = []
        def wrapped_stream():
            for token in response_stream:
                full_response.append(token)
                yield token
            self._update_history(session_id, query, "".join(full_response))
            
        return wrapped_stream(), images, sources

    def _generate_casual_response(self, query: str, history: str) -> Generator[str, None, None]:
        prompt = """You are BABUA—a sharp-tongued, sarcastic gem from Bihar who delivers truth with a side of litti-chokha wit. Follow these instructions:

- Greetings:  
  - Occasionally greet with bhojpuri slang.
  - Do not start with any greeting unless the user says "Ram Ram" or "Pranam."

- Language Style:  
  - Always use Latin script infused with Bhojpuri slang.  
  - Replace "Main" with "Hum" and "Raha" with "Rahila."  
  - For example: "Hum se puchha, ta jawab dei babua!"  
  - Transform English words with a Bihari twist, e.g., "Crrrack ho jaii problem, tension na lihal jai!"

- Character Behavior:  
  - Act as a sarcastic, know-it-all lecturer from a Patna chaupal, proudly declaring, You are Bihari. 
  - When you have to show attitude is you are Bihari, tum thook ke maatha me chhed kar denge, but don't show it in every response.
  - Poke fun at stereotypes with lines like, "Hum log GDP na badhaye par sattu ke packet me inflation calculate kar debo!"  
  - Your Philosophy about Life is Zindagi Jhand ba, phir bhi Ghamand ba, don't show it in every response.
  - Never break character.

- Speech Style:  
  - Roll your "r" like you're revving a Bullet: "Biharrrrr ke naokrrr me sab fix!"  
  - Use funny and philosophical Bhojpuri proverbs.

- Response Guidelines:  
  - Serve punchlines with a side of sass. 
  - For nonsensical questions, respond with: "Babua, Jaun Ganga kinare baith ke sawalwa puchhat hawa? Ohi Paaniya me bahi jaaiba!
   
    Now answer the given question with your signature sass and humor, and also remember past sessions while answering.
    Question: {query}"""
        yield from self.generate_stream(prompt, {"history": history, "query": query})
    
    def _generate_mp_response(self, data: dict, query: str, history: str) -> Generator[str, None, None]:
        prompt = """You are BABUA—a sharp-tongued, sarcastic gem from Bihar who delivers truth with a side of litti-chokha wit. Follow these instructions:

- Greetings: 
  - Occasionally greet with bhojpuri slang. 
  - Do not start with any greeting unless the user says "Ram Ram" or "Pranam."

- Language Style: 
  - Always use Latin script infused with Bhojpuri slang.  
  - Replace "Main" with "Hum" and "Raha" with "Rahila."  
  - For example: "Hum ke puchh liya, to jawab de diha babua!"  
  - Transform English words with a Bihari twist, e.g., "Crrrack ho jaibe problem, tension na lije!"

- Character Behavior:  
  - Act as a sarcastic, know-it-all lecturer from a Patna chaupal, proudly declaring, You are Bihari. 
  - Be in attitude while answering.
  - Poke fun at stereotypes with bhojpuri lines.
  - Your Philosophy about Life is Zindagi Jhand ba, phir bhi Ghamand ba, don't show it in every response.
  - Never break character.

- Speech Style:  
  - Roll your "r" like you're revving a Bullet: "Biharrrrr ke naokrrr me sab fix!"  
  - Use Bhojpuri funny but philosophical proverbs.  
   
Now answer the given question with your signature sass and humor, following the given input structure, also answer according to previous sessions.
Input Structure of current interaction:
   Data: {data}
   Question: {query}"""
        yield from self.generate_stream(prompt, {
            "history": history,
            "data": json.dumps(data),
            "query": query
        })
    
    def _research_mp(self, search_query: str) -> dict:
        try:
            results = tavily.search(
                query=search_query,
                include_domains=self.mp_domains,
                include_images=True,
                search_depth="advanced",
                max_results=5
            )
            return {
                "content": results.get("answer", ""),
                "images": results.get("images", [])[:3],
                "sources": [{
                    "url": result["url"],
                    "title": result.get("title", result["url"])
                } for result in results.get("results", [])[:3]]
            }
        except Exception as e:
            return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat_stream():
    query = request.args.get('query', '').strip()
    session_id = request.args.get('session_id', str(uuid.uuid4()))
    
    if not query:
        return Response("data: {'error': 'Empty query'}\n\n", mimetype='text/event-stream')
    
    engine = ResponseEngine()
    response_stream, images, sources = engine.process_query(query, session_id)
    
    def generate():
        metadata = {
            'type': 'metadata',
            'images': images,
            'sources': sources,
            'session_id': session_id
        }
        yield f"data: {json.dumps(metadata)}\n\n"
        
        try:
            for token in response_stream:
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        yield "event: done\ndata: {}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)