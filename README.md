# Harness FastAPI POC — End-to-End CI/CD Guide

A complete proof-of-concept for building and deploying a **FastAPI (Python)** app on **Harness CI/CD**.

---

## Project Structure

```
harness-fastapi-poc/
├── app/
│   └── main.py             # FastAPI application
├── tests/
│   └── test_main.py        # Pytest test suite
├── k8s/
│   └── deployment.yaml     # Kubernetes manifests
├── .harness/
│   └── pipeline.yaml       # Harness pipeline definition
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Local dev environment
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Step 1 — Prerequisites

| Tool | Purpose |
|------|---------|
| Python 3.12+ | Local development |
| Docker Desktop | Build & run containers locally |
| Git + GitHub account | Source control |
| Harness account (free) | CI/CD platform |
| DockerHub account | Container registry |

Sign up for free Harness at: https://app.harness.io/auth/#/signup

---

## Step 2 — Run Locally

```bash
# Clone or create the project
cd harness-fastapi-poc

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn app.main:app --reload --port 8000

# Open API docs at:
# http://localhost:8000/docs

# Run tests
pytest tests/ -v
```

---

## Step 3 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial FastAPI POC"
git remote add origin https://github.com/YOUR_USERNAME/harness-fastapi-poc.git
git push -u origin main
```

---

## Step 4 — Set Up Harness

### 4.1 Create a Project
1. Log in to https://app.harness.io
2. Click **Projects** → **+ New Project**
3. Name it: `fastapi-poc`
4. Enable modules: **CI** and **CD**

### 4.2 Create GitHub Connector
1. Go to **Project Settings** → **Connectors** → **+ New Connector**
2. Select **GitHub**
3. Connection type: **Account** (or Repository)
4. Authentication: **Personal Access Token**
   - GitHub token needs: `repo`, `admin:repo_hook` scopes
5. Test the connection ✅
6. Note the **Connector ID** — paste it in `pipeline.yaml` → `connectorRef`

### 4.3 Create DockerHub Connector
1. Go to **Project Settings** → **Connectors** → **+ New Connector**
2. Select **Docker Registry**
3. Docker Registry URL: `https://index.docker.io/v2/`
4. Auth: your DockerHub username + Access Token
5. Note the **Connector ID** — paste it in `pipeline.yaml` → `BuildAndPushDockerRegistry.connectorRef`

---

## Step 5 — Fix the Delegate Error (your current issue)

The error `Failed to connect to /127.0.0.1:3000` means the runner isn't reachable.

**Easiest fix: Switch to Harness Cloud (no delegate needed)**

In your pipeline's Build stage, set infrastructure to:
```yaml
platform:
  os: Linux
  arch: Amd64
runtime:
  type: Cloud
  spec: {}
```

This uses Harness's free hosted runners — no delegate, no runner setup needed.

---

## Step 6 — Import the Pipeline

### Option A: Via UI
1. In Harness, go to your project → **Pipelines** → **+ Create Pipeline**
2. Select **Import from Git**
3. Point to your repo → `.harness/pipeline.yaml`

### Option B: Inline YAML
1. Create a new pipeline → **YAML editor**
2. Paste the contents of `.harness/pipeline.yaml`
3. Replace placeholder values:
   - `YOUR_PROJECT_ID` → your Harness project ID
   - `YOUR_GITHUB_CONNECTOR` → GitHub connector ID
   - `YOUR_DOCKERHUB_CONNECTOR` → DockerHub connector ID
   - `YOUR_DOCKERHUB_USERNAME` → your DockerHub username

---

## Step 7 — Run the Pipeline

1. Click **Run Pipeline**
2. Select branch: `main`
3. Watch the stages execute:

```
build-and-test
  ├── Install Dependencies   ✅
  ├── Lint (flake8)          ✅
  ├── Run Tests              ✅  (JUnit report generated)
  └── Build & Push Docker    ✅

deploy-dev
  └── K8s Rolling Deploy     ✅
```

---

## Step 8 — Add a Git Trigger (Auto-run on push)

1. In your pipeline → **Triggers** → **+ New Trigger**
2. Type: **GitHub** → **Push**
3. Branch: `main`
4. Harness auto-creates a webhook in your GitHub repo

Now every `git push` to `main` triggers the full pipeline automatically!

---

## Step 9 — View Test Results

After the pipeline runs:
1. Click the **Tests** tab in the pipeline execution
2. See all 11 test results with pass/fail status
3. Failed tests block the Docker build automatically

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health message |
| GET | `/health` | Health check |
| GET | `/items` | List all items |
| GET | `/items/{id}` | Get item by ID |
| POST | `/items` | Create new item |
| PUT | `/items/{id}` | Update item |
| DELETE | `/items/{id}` | Delete item |

Full interactive docs: `http://localhost:8000/docs`

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Failed to connect to /127.0.0.1:3000` | Switch to Harness Cloud infrastructure |
| `Bitbucket App Passwords deprecated` | Migrate to API tokens before June 9, 2026 |
| Docker push fails | Check DockerHub connector credentials |
| Tests fail in CI but pass locally | Check Python version mismatch — use python:3.12 image |
