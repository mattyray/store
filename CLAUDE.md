# Matthew Raynor Photography Store - Project Context

## Overview
E-commerce website for fine art photography prints. Sells photo prints (paper and aluminum), a photography book, and gift cards.

**Live Site:** https://store.matthewraynor.com

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15+ (App Router), TypeScript, Tailwind CSS |
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL 16 |
| Payments | Stripe Checkout |
| Email | Resend SMTP |
| Newsletter | MailerLite |
| Media Storage | AWS S3 |
| Frontend Hosting | Netlify (with `@netlify/plugin-nextjs`) |
| Backend Hosting | Railway |

---

## Project Structure

```
store/
├── backend/                 # Django API
│   ├── apps/
│   │   ├── catalog/         # Collections, Photos, ProductVariants, Products
│   │   ├── orders/          # Cart, CartItem, Order, OrderItem
│   │   ├── core/            # Contact form, Newsletter, Gift Cards
│   │   └── payments/        # Stripe webhooks, checkout
│   ├── config/
│   │   └── settings/
│   │       ├── base.py      # Shared settings
│   │       ├── development.py
│   │       └── production.py
│   └── Dockerfile.bak
├── frontend/                # Next.js App
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── about/
│   │   │   ├── book/
│   │   │   ├── cart/
│   │   │   ├── collections/
│   │   │   ├── contact/
│   │   │   ├── gift-cards/
│   │   │   ├── order/
│   │   │   ├── photos/
│   │   │   ├── shipping/
│   │   │   └── track-order/
│   │   ├── components/      # Shared React components
│   │   └── lib/
│   │       └── api.ts       # API client functions
│   └── Dockerfile
└── docker-compose.yml
```

---

## Database Models

### Catalog App
- **Collection** - Photo series/collections (e.g., "Montauk Sunsets")
- **Photo** - Individual photographs with title, description, location, orientation
- **ProductVariant** - Purchasable options: size + material (paper/aluminum) + price
- **Product** - Standalone products like books or merchandise

### Orders App
- **Cart** - Session-based cart (UUID primary key)
- **CartItem** - Links to either ProductVariant or Product
- **Order** - Completed orders with status tracking
- **OrderItem** - Order line items

### Core App
- **Subscriber** - Newsletter subscribers
- **GiftCard** - Gift card codes and balances

---

## Docker Development Setup

**Ports:**
- Frontend: `3000`
- Backend: `7974`
- PostgreSQL: `7975`

**Start development:**
```bash
docker compose up
```

**Services:**
1. **db** - PostgreSQL 16 Alpine, auto-creates `photography_store` database
2. **backend** - Runs migrations on startup, then `runserver` on port 7974
3. **frontend** - Runs `npm run dev` with hot reload

**Volumes:**
- `postgres_data` - Database persistence
- `static_volume` / `media_volume` - Django static/media files
- Source code mounted for hot reload

**Environment Variables in Docker:**
- Backend reads from shell environment or defaults
- Pass Stripe keys via: `STRIPE_SECRET_KEY=xxx docker compose up`

---

## Environment Variables

### Backend (.env)
```
# Django
SECRET_KEY=               # Django secret key
DEBUG=                    # True/False

# Database
DATABASE_URL=             # Full connection string (Railway provides this)
# OR individual:
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Stripe
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# Email (Resend)
EMAIL_HOST_PASSWORD=      # Resend API key
DEFAULT_FROM_EMAIL=
ADMIN_EMAIL=

# Newsletter
MAILERLITE_API_KEY=

# CORS/Security
ALLOWED_HOSTS=
CORS_ALLOWED_ORIGINS=
FRONTEND_URL=
```

### Frontend
```
NEXT_PUBLIC_API_URL=      # Public API URL (browser requests)
INTERNAL_API_URL=         # Internal URL (server-side requests, Docker: http://backend:7974/api)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

---

## Important Technical Details

### Cross-Origin Cookies (Cart Persistence)
The cart uses session-based cookies across domains:
- Backend sets `SameSite=None; Secure` cookies
- Frontend must include `credentials: 'include'` on all API calls
- CORS must allow the frontend origin with credentials

### Next.js Image Optimization
Images from S3 require `remotePatterns` in `next.config.js`:
```js
images: {
  remotePatterns: [
    { protocol: 'https', hostname: '*.s3.*.amazonaws.com' },
  ],
}
```

### Dark Mode
Uses Tailwind's `dark:` variants with `prefers-color-scheme` media query (no toggle). All components should include dark mode classes.

### Server vs Client Data Fetching
- **Server Components** (default): Use `INTERNAL_API_URL` - direct service-to-service in Docker/Railway
- **Client Components** (`'use client'`): Use `NEXT_PUBLIC_API_URL` - browser makes request

### Honeypot Spam Protection
Contact form has a hidden honeypot field. If filled (by bots), form silently "succeeds" without sending.

---

## Deployment

### Backend (Railway)
- Deploys from `backend/` directory
- Uses `Procfile` or Railway auto-detect
- PostgreSQL addon for database
- Set all environment variables in Railway dashboard

### Frontend (Netlify)
- Deploys from `frontend/` directory
- Uses `@netlify/plugin-nextjs` for App Router support
- Set environment variables in Netlify dashboard
- Build command: `npm run build`

### Manual Deploy Steps
1. Push to GitHub
2. Railway auto-deploys backend from main branch
3. Netlify auto-deploys frontend from main branch

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Cart not persisting | Check CORS config, ensure `credentials: 'include'`, verify `SameSite=None` cookie |
| S3 images 403 | Check bucket policy, CORS config on bucket, IAM permissions |
| Next.js images broken | Add S3 domain to `remotePatterns` in `next.config.js` |
| Dark mode text invisible | Add `dark:text-gray-100` (or similar) Tailwind classes |
| Stripe webhook fails | Verify `STRIPE_WEBHOOK_SECRET`, check Railway logs |
| CORS errors | Update `CORS_ALLOWED_ORIGINS` in backend settings |
| 404 on page refresh (Netlify) | Netlify plugin should handle this; check `netlify.toml` |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/collections/` | GET | List all collections |
| `/api/collections/{slug}/` | GET | Collection detail |
| `/api/photos/` | GET | List photos (supports filtering) |
| `/api/photos/{slug}/` | GET | Photo detail with variants |
| `/api/products/` | GET | List products (books, etc.) |
| `/api/cart/` | GET | Get current cart |
| `/api/cart/add/` | POST | Add item to cart |
| `/api/cart/update/` | POST | Update item quantity |
| `/api/cart/remove/` | POST | Remove item |
| `/api/checkout/create-session/` | POST | Create Stripe checkout |
| `/api/contact/` | POST | Submit contact form |
| `/api/newsletter/subscribe/` | POST | Subscribe to newsletter |
| `/api/gift-cards/purchase/` | POST | Purchase gift card |
| `/api/gift-cards/check/` | POST | Check gift card balance |
| `/api/health/` | GET | Health check |

---

## Git Workflow
- User prefers to run git commands manually
- Provide commit commands but don't execute push automatically

---

## Current Status / TODO
- Stripe checkout integration complete
- Gift card system implemented
- Newsletter subscription (MailerLite) working
- Contact form with honeypot spam protection
- Dark mode fully supported across all pages
