# Azure Deployment Strategy for AtoZ Shop

## Goal
Deploy the Flask fullstack app (`main.py` + `templates/`) to Azure in a way that is easy to start and safe to scale.

## Recommended Strategy (Production)
Use:
1. **Azure App Service (Linux, Python 3.12)** for hosting
2. **Azure Database for PostgreSQL** (or Azure SQL) instead of SQLite for durable multi-instance data
3. **Azure Blob Storage** if you later host product/user media

Why: your current SQLite (`app.db`) is fine for demo/single-instance usage, but not ideal for horizontal scaling.

---

## Path A: Fast Demo Deployment (Keep SQLite)

### When to use
- Quick demo
- Single App Service instance
- Non-critical data

### Steps
1. Create **App Service** (Linux, Python 3.12).
2. Deploy code from GitHub/zip/local.
3. Set startup command:
   ```bash
   gunicorn --bind 0.0.0.0:$PORT main:app
   ```
4. Set App Settings:
   - `WEBSITES_PORT=8000` (if needed by your setup)
   - `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
5. Keep `requirements.txt` in root.
6. Verify `/api/health`.

### Limitation
If scaled to multiple instances, each instance can have different SQLite state.

---

## Path B: Production Deployment (Strongly Recommended)

### 1. Add DB abstraction/config
Introduce:
- `DATABASE_URL` env var
- SQLite fallback only for local dev

Example behavior:
- local: `sqlite:///app.db`
- Azure: `postgresql://...`

### 2. Provision Azure resources
1. Resource Group
2. App Service Plan
3. App Service (Linux)
4. Azure Database for PostgreSQL (Flexible Server)
5. (Optional) Azure Key Vault for secrets

### 3. Configure app settings in App Service
- `DATABASE_URL=<postgres connection string>`
- `FLASK_ENV=production`
- `PYTHONUNBUFFERED=1`
- `WEBSITES_PORT=8000` (if applicable)

### 4. Deploy
Use one:
- GitHub Actions CI/CD
- Azure Web Deploy from local
- Container deployment (Dockerfile) to App Service for Containers

For the included GitHub Actions workflow, create a service principal and save
its JSON credentials as the repository secret `AZURE_CREDENTIALS`:

```bash
az ad sp create-for-rbac \
  --name atoz-shop-github \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP> \
  --sdk-auth
```

Copy the complete JSON output into the GitHub repository secret
`AZURE_CREDENTIALS`. Also add:

- `AZURE_WEBAPP_NAME`: the App Service name

The workflow logs in with `azure/login@v2`, runs smoke tests, and deploys only
after a push to `main`. Pull requests run tests but do not deploy.

### 5. Migrate seed data
Move initial product seed into:
- migration/seed script
- run once during deployment pipeline

### 6. Post-deploy checks
- `/api/health`
- `/api/products`
- add-to-cart and checkout flow
- order persistence after app restart

---

## CI/CD Recommendation (GitHub Actions)
Pipeline stages:
1. Install dependencies
2. Run tests/sanity checks
3. Build artifact (or Docker image)
4. Deploy to Azure App Service
5. Run smoke checks on `/api/health`

---

## Security + Reliability Checklist
- Store secrets in App Settings/Key Vault (never in repo)
- Enable HTTPS only
- Enable App Service logs and Application Insights
- Add custom domain + TLS cert
- Configure autoscale only after moving off SQLite

---

## Cost-aware rollout plan
1. Start with **Path A** for demo validation.
2. Move to **Path B** before real users.
3. Add staging slot and CI/CD once features stabilize.
