# Railway Production Notes

## Accessing the Container Shell

Railway uses `railway ssh` (not `railway shell`) to access the running container:

```bash
railway login
railway link        # link to your project if not already
railway ssh         # SSH into the container
```

Or get the full command from the Railway dashboard: **right-click on your service** → **"Copy SSH Command"**

**Important distinction:**
- `railway ssh` - connects to the actual running container on Railway
- `railway shell` / `railway run` - runs commands LOCALLY with Railway env vars (doesn't connect to the container)

## Running Django Management Commands

Since `railway ssh` works, you can run commands directly:

```bash
railway ssh
# then inside the container:
python manage.py generate_photo_embeddings
python manage.py generate_photo_descriptions
```

Or use start.sh for one-time commands by adding them before gunicorn starts.

## Start Script (start.sh)

The backend uses `start.sh` instead of `Procfile` for the web process. Current startup sequence:

1. Run migrations
2. Run Django checks
3. Generate embeddings for any new photos (skips existing)
4. Log embedding count
5. Start gunicorn

To run a one-time command in production, add it to start.sh before the gunicorn line, push, then remove it after it runs.

## Environment Variables

Required in Railway dashboard:

```
# Django
SECRET_KEY
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# Database (Railway provides DATABASE_URL automatically)
DATABASE_URL

# AWS S3
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME
AWS_S3_REGION_NAME

# Stripe
STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET

# AI APIs
ANTHROPIC_API_KEY      # For Claude (chat agent, photo descriptions)
OPENAI_API_KEY         # For embeddings (text-embedding-ada-002)

# Email
EMAIL_HOST_PASSWORD    # Resend API key
DEFAULT_FROM_EMAIL
ADMIN_EMAIL

# CORS
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
FRONTEND_URL

# Redis (if using Celery)
REDIS_URL
```

## Checking Embeddings

The startup script logs embedding count:
```
Photos with embeddings: 31/31
```

If this shows 0/31, embeddings need to be generated. The `generate_photo_embeddings` command runs automatically on startup for any photos missing embeddings.

## pgvector

Railway PostgreSQL supports pgvector. The extension is enabled via migration:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `railway shell` doesn't connect | Use `railway ssh` instead |
| Django AppRegistryNotReady | Need `DJANGO_SETTINGS_MODULE` set before `django.setup()` |
| Embeddings not generating | Check `OPENAI_API_KEY` is set in Railway |
| Container restart loop | Check logs - usually a startup script error |

## AI Agent Stack

- **LangChain** - Agent framework with tool calling
- **Claude API** - Chat responses (via langchain-anthropic)
- **OpenAI** - Embeddings for semantic search (text-embedding-ada-002)
- **pgvector** - Vector similarity search in PostgreSQL
- **MiDaS ONNX** - Depth estimation for room mockups

## Useful Commands

```bash
# Update Railway CLI
npm update -g @railway/cli

# Check current linked project
railway status

# View logs
railway logs

# SSH into container
railway ssh
```
