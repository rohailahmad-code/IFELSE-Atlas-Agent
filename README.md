# if/else Atlas Agent

A skeleton project demonstrating a connection between a React (Vite) frontend and a FastAPI backend orchestrated with LangGraph (running a single node calling the Google Gemini SDK).

## Structure
- `/backend` - FastAPI app, LangGraph, python-dotenv, Google GenAI SDK integration.
- `/frontend` - React app (Vite) with a chat interface.

---

## Setup & Running the Project

### 1. Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
   - **Windows (Command Prompt)**: `.venv\Scripts\activate.bat`
   - **macOS/Linux**: `source .venv/bin/activate`

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure your environment variables. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and set your `GEMINI_API_KEY`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   ```
   *(You can obtain a free API key from [Google AI Studio](https://aistudio.google.com/))*

6. Start the FastAPI backend server using Uvicorn:
   - **Using activated environment**:
     ```bash
     uvicorn main:app --reload
     ```
   - **Directly (Recommended on Windows)**:
     ```bash
     .venv\Scripts\python -m uvicorn main:app --reload
     ```
   The backend will be running at `http://localhost:8000`.

---

### 2. Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install the node modules:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173` (or check console output for the port).

---

## Development Info

- **Backend API**: The endpoint is `POST http://localhost:8000/chat`, which accepts `{"message": "string"}` and returns `{"response": "string"}`.
- **LangGraph Orchestration**: The `/chat` endpoint invokes a compiled LangGraph workflow with a state mapping `{message, response}` passing through a single node that queries the Google Gemini API.
- **Fallback**: If `GEMINI_API_KEY` is not present in your `.env` file, the backend returns a mock helper message instead of crashing, allowing you to test client-server connectivity immediately.
