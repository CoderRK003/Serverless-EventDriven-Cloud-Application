# How to Run This Project

## Prerequisites

- AWS Account with AWS CLI configured
- AWS SAM CLI installed
- Node.js 18+
- Python 3.11+

---

## Step 1: Deploy Backend to AWS

From the `infrastructure/` folder:

```bash
sam build
sam deploy --guided
```

After deployment, note the output values:
- `HttpApiUrl` - your HTTP API endpoint
- `WebSocketUrl` - your WebSocket endpoint

---

## Step 2: Run Event Simulator (Optional)

Install Python dependencies:
```bash
pip install -r backend/requirements.txt
```

Run the simulator:
```bash
python backend/tools/event_source_simulator.py --url <HttpApiUrl>/events --eps 5 --device device-1
```

---

## Step 3: Run Frontend

1. Navigate to frontend:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file:
   ```
   VITE_HTTP_API_BASE=<HttpApiUrl>
   VITE_WS_URL=<WebSocketUrl>
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

---

## Quick Demo

1. Deploy backend with SAM
2. Run frontend (`npm run dev`)
3. Open `http://localhost:5173` in browser
4. Start simulator at low EPS (e.g., 2) - observe low queue depth
5. Increase EPS (e.g., 30) - observe queue depth grow and auto-scaling kick in
