# AI Chatbot with Gemini 1.5, FastAPI, and Streamlit

A full-stack AI chatbot application that uses Gemini 1.5 Pro for natural language processing, FastAPI for the backend API, Streamlit for the frontend interface, and Supabase for message storage.

## Features

- 🤖 Powered by Google's Gemini 1.5 Pro AI model
- 🚀 FastAPI backend for efficient API handling
- 💻 Streamlit frontend for interactive user interface
- 🗄️ Supabase database for message persistence
- 🔄 Real-time chat functionality
- 📝 Chat history tracking and download
- 🆔 Conversation management with unique IDs
- 🎨 Clean and responsive UI

## Prerequisites

- Python 3.8+
- Google API Key (Gemini access)
- Supabase account and credentials

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your credentials:
```env
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_api_key
```

## Database Setup

Create a new table in Supabase with the following SQL:

```sql
create table messages (
    id bigint primary key generated always as identity,
    content text not null,
    role text not null,
    conversation_id text not null,
    timestamp timestamptz not null,
    created_at timestamptz default now()
);
```

## Project Structure

```
project/
├── main.py              # FastAPI backend
├── streamlit_app.py     # Streamlit frontend
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables
└── README.md           # Project documentation
```

## Running the Application

1. Start the FastAPI backend:
```bash
python main.py
```
The API will be available at `http://127.0.0.1:8000`

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run streamlit_app.py
```
The web interface will automatically open in your browser

## API Endpoints

- `GET /` - Health check endpoint
- `POST /api/chat` - Send a message and get a response
- `GET /api/history/{conversation_id}` - Get chat history for a specific conversation

## Dependencies

```text
fastapi
uvicorn
streamlit
google-generativeai
supabase
python-dotenv
langchain
langchain-google-genai
langgraph
requests
pydantic
```

## Features in Detail

### Backend (FastAPI)
- RESTful API endpoints
- Message processing with Gemini 1.5
- Database integration with Supabase
- Error handling and logging
- CORS middleware for web client support
- Conversation management

### Frontend (Streamlit)
- Real-time chat interface
- Message history display
- New conversation creation
- Chat history download
- Session management
- Loading indicators
- Custom styling
- Error handling

### Database (Supabase)
- Message storage
- Conversation tracking
- Timestamp management
- Role-based message organization

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

1. **API Connection Issues**
   - Ensure the FastAPI backend is running
   - Check if the correct port (8000) is available
   - Verify your API credentials in .env

2. **Database Issues**
   - Confirm Supabase credentials
   - Check table structure
   - Verify network connectivity

3. **Gemini API Issues**
   - Ensure valid API key
   - Check API usage limits
   - Verify model availability

## Acknowledgments

- Google Gemini team for the AI model
- FastAPI team for the backend framework
- Streamlit team for the frontend framework
- Supabase team for the database platform

