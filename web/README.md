# Web UI

Static HTML client that calls the FastAPI runtime. Dropdowns are populated from `/v1/registry`, and selections are passed into `/v1/chat` on each request.

## Usage
- Open `index.html` in a browser (or host via GitHub Pages).
- Choose channel, providers, and optional RAG/ServiceDesk usage.
- Send a message to see the response plus debug drawer showing routing details and simulated costs.

Update `apiBase` in localStorage if pointing to a remote backend.
