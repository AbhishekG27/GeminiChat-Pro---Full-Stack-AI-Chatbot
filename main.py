from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot API",
    description="API for interacting with the chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    conversation_id: str

class Message(BaseModel):
    content: str
    role: str
    conversation_id: str
    timestamp: str

# Initialize services
try:
    # Initialize Gemini
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-pro')

    # Initialize Supabase
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_API_KEY')
    )

    # Initialize LangChain
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=os.getenv('GEMINI_API_KEY'),
        temperature=0.7
    )
except Exception as e:
    print(f"Error initializing services: {e}")
    raise

class Chatbot:
    def __init__(self):
        self.history = []
        self.setup_langchain()
        self.setup_langgraph()

    def setup_langchain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{message}")
        ])
        self.chain = prompt | llm

    def setup_langgraph(self):
        def process_message(state: Dict) -> Dict:
            message = state["messages"][-1]["content"]
            history = []
            for msg in self.history:
                if isinstance(msg, HumanMessage):
                    history.append(("human", msg.content))
                elif isinstance(msg, AIMessage):
                    history.append(("assistant", msg.content))
            
            response = self.chain.invoke({
                "message": message,
                "history": history
            })
            
            conversation_id = state.get("conversation_id", datetime.now().strftime("%Y%m%d%H%M%S"))
            self.save_message(message, "user", conversation_id)
            self.save_message(response.content, "assistant", conversation_id)
            
            state["messages"].append({"role": "assistant", "content": response.content})
            state["conversation_id"] = conversation_id
            return state

        workflow = StateGraph(Dict)
        workflow.add_node("process", process_message)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)
        self.graph = workflow.compile()

    def save_message(self, content: str, role: str, conversation_id: str):
        try:
            data = supabase.table('messages').insert({
                "content": content,
                "role": role,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }).execute()
            print(f"Saved {role} message to database")
            return data
        except Exception as e:
            print(f"Error saving message: {e}")
            return None

    def get_response(self, query: str, conversation_id: Optional[str] = None) -> Dict:
        try:
            state = {
                "messages": [{"role": "user", "content": query}],
                "next": "process",
                "conversation_id": conversation_id
            }
            
            final_state = self.graph.invoke(state)
            
            self.history.append(HumanMessage(content=query))
            response = final_state["messages"][-1]["content"]
            self.history.append(AIMessage(content=response))
            
            return {
                "response": response,
                "conversation_id": final_state["conversation_id"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Create chatbot instance
chatbot = Chatbot()

# Test route
@app.get("/")
async def root():
    return {"status": "alive", "message": "Chatbot API is running"}

# Chat endpoint
@app.post("/api/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    try:
        result = chatbot.get_response(request.message, request.conversation_id)
        return MessageResponse(
            response=result["response"],
            conversation_id=result["conversation_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat history endpoint
@app.get("/api/history/{conversation_id}")
async def get_history(conversation_id: str):
    try:
        data = supabase.table('messages')\
            .select('*')\
            .eq('conversation_id', conversation_id)\
            .order('timestamp')\
            .execute()
        return {"messages": data.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)