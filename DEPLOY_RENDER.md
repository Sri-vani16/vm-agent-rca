# Render Deployment Steps

This project deploys as two Render web services:

- `rca-chat-backend`: FastAPI API
- `rca-chat-frontend`: Streamlit UI

## 1. Prepare The Repository

1. Create a Git repo if this folder is not one yet:

   ```bash
   git init
   git add .
   git commit -m "Prepare Render deployment"
   ```

2. Push it to GitHub, GitLab, or Bitbucket.

3. Do not commit `.env`. Use Render environment variables instead.

## 2. Deploy With `render.yaml`

1. Open Render.
2. Choose **New +** -> **Blueprint**.
3. Connect the repository.
4. Render will detect `render.yaml` and create both services.
5. When prompted, enter:

   ```text
   GROQ_API_KEY=<your Groq API key>
   ADMIN_PASSWORD=<strong admin password>
   ```

6. Keep or update:

   ```text
   MODEL_NAME=openai/gpt-oss-20b
   ADMIN_USERNAME=admin
   BACKEND_URL=https://rca-chat-backend.onrender.com
   ```

If Render gives your backend a different URL, update `BACKEND_URL` on the frontend service.

## 3. Manual Service Settings

Backend service:

```text
Runtime: Python
Build Command: pip install -r backend_requirements.txt
Start Command: uvicorn backend_main:app --host 0.0.0.0 --port $PORT
Environment:
  GROQ_API_KEY=<secret>
  MODEL_NAME=openai/gpt-oss-20b
```

Frontend service:

```text
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: streamlit run main.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
Environment:
  BACKEND_URL=<backend Render URL>
  ADMIN_USERNAME=admin
  ADMIN_PASSWORD=<secret>
```

## 4. Verify

After deploy:

```bash
curl https://rca-chat-backend.onrender.com/health
```

Expected response includes:

```json
{
  "status": "healthy",
  "groq_configured": true
}
```

Then open the frontend URL and test:

1. Open **User Chat** and send `hello`.
2. Open **Admin Panel** and log in.
3. Upload a `.txt`, `.log`, or `.md` knowledge-base file.
4. Run a log analysis.

## 5. Persistence Note

Knowledge-base files are stored on the backend service filesystem. On Render, this is not durable unless you attach a persistent disk or move uploads to external storage. For production, add a Render disk to the backend service and mount it at `knowledge_base`, or use object storage.
