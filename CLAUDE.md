# Matthew Raynor Photography Store - Project Context

## Overview
E-commerce website for fine art photography prints targeting the Hamptons luxury art market. Sells photo prints (paper and aluminum), a photography book, and gift cards.

**Live Site:** https://store.matthewraynor.com

**Active Code Review:** See [CODE_REVIEW.md](CODE_REVIEW.md) for tracked findings and implementation status.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15+ (App Router), TypeScript, Tailwind CSS |
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL 16 with pgvector |
| Payments | Stripe Checkout |
| Email | Resend SMTP |
| Newsletter | MailerLite |
| Media Storage | AWS S3 |
| Frontend Hosting | Netlify (with `@netlify/plugin-nextjs`) |
| Backend Hosting | Railway (web + Celery worker + Redis) |
| AI | Claude (chat agent), OpenAI (embeddings) |

---

## Project Structure

```
store/
├── backend/                 # Django API
│   ├── apps/
│   │   ├── catalog/         # Collections, Photos, ProductVariants, Products
│   │   ├── orders/          # Cart, CartItem, Order, OrderItem
│   │   ├── core/            # Contact form, Newsletter, Gift Cards
│   │   ├── payments/        # Stripe webhooks, checkout, gift card redemption
│   │   ├── chat/            # AI shopping agent (LangChain + Claude)
│   │   └── mockup/          # "See in room" ML wall detection
│   ├── config/
│   │   └── settings/
│   │       ├── base.py      # Shared settings
│   │       ├── development.py
│   │       └── production.py
│   ├── start.sh             # Production startup script
│   ├── Dockerfile
│   └── Procfile
├── frontend/                # Next.js App
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Shared React components
│   │   └── lib/
│   │       └── api.ts       # API client functions
│   ├── netlify.toml
│   └── Dockerfile
└── docker-compose.yml
```

---

## Collections

| Collection | Description |
|------------|-------------|
| Shots from the Sea | Commercial fishing era photography |
| Travel Photography | Global destinations |
| Aerial Photography | Drone perspectives of the East End |

---

## Pricing

### Paper Prints (Matted, Open Edition)
*Printed in-house on archival paper with acid-free matting*

| Size | Mat Size | Price |
|------|----------|-------|
| 11x14 | 16x20 | $175 |
| 13x19 | 18x24 | $250 |

Ships within 5-7 business days.

### Aluminum Prints (Open Edition)
*Dye-sublimated on premium aluminum. Scratch-resistant, UV-resistant, ready to hang.*

| Size | Price |
|------|-------|
| 16x24 | $675 |
| 20x30 | $995 |
| 24x36 | $1,350 |
| 30x40 | $1,850 |
| 30x45 | $2,150 |
| 40x60 | $3,400 |

Ships within 14-21 business days (lab fulfilled).

**Pricing Formula:** Retail = (Wholesale + Tax + Shipping) × 3.5

---

## Database Models

### Catalog App
- **Collection** - Photo series/collections
- **Photo** - Photographs with title, description, location, orientation, dimensions, embedding (pgvector)
- **ProductVariant** - Purchasable options: size + material (paper/aluminum) + price
- **Product** - Standalone products like books

### Orders App
- **Cart** - Session-based cart (UUID primary key)
- **CartItem** - Links to either ProductVariant or Product
- **Order** - Completed orders with status tracking
- **OrderItem** - Order line items

### Core App
- **Subscriber** - Newsletter subscribers
- **GiftCard** - Gift card codes, balances, expiration
- **GiftCardRedemption** - Audit trail for gift card usage

### Chat App
- **Conversation** - Chat sessions with the AI agent
- **Message** - Individual messages in conversations

---

## Gift Cards & Promotion Codes

### Gift Cards
- **Purchase**: Fixed amounts ($100, $250, $500, $1000, $2500)
- **Check Balance**: `POST /api/gift-cards/check/`
- **Redemption**: Applied at checkout as a Stripe coupon
- Gift card balance is deducted after successful payment
- Partial redemption supported (remaining balance stays on card)

### Stripe Promotion Codes
- Enabled at checkout when no gift card is applied
- Promo codes created in Stripe Dashboard → Products → Coupons
- **Note**: Stripe doesn't allow both gift card (coupon) and promo codes in the same session

### Product Discounts
- `Product.compare_at_price` - For showing "was $X, now $Y" (display only)

---

## Environment Variables

### Backend
```
# Django
SECRET_KEY=               # Django secret key
DEBUG=False               # Must be False in production
DJANGO_SETTINGS_MODULE=config.settings.production

# Database (Railway provides DATABASE_URL automatically)
DATABASE_URL=             # postgres://user:pass@host:port/dbname

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=       # Default: us-east-1

# Stripe
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=

# Email (Resend SMTP)
EMAIL_HOST=               # Default: smtp.resend.com
EMAIL_PORT=               # Default: 587
EMAIL_HOST_USER=          # Default: resend
EMAIL_HOST_PASSWORD=      # Resend API key
DEFAULT_FROM_EMAIL=
ADMIN_EMAIL=

# Newsletter
MAILERLITE_API_KEY=

# CORS/Security
ALLOWED_HOSTS=            # Comma-separated: your-app.railway.app,store-api.matthewraynor.com
CORS_ALLOWED_ORIGINS=     # Comma-separated frontend URLs
FRONTEND_URL=             # For Stripe redirects

# Redis (for Celery)
REDIS_URL=                # Railway Redis addon provides this

# AI APIs
ANTHROPIC_API_KEY=        # For Claude chat agent
OPENAI_API_KEY=           # For embeddings (text-embedding-ada-002)
```

### Frontend (Netlify)
```
NEXT_PUBLIC_API_URL=      # Public API URL (browser requests)
INTERNAL_API_URL=         # Internal URL (server-side, Docker: http://backend:7974/api)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

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
1. **db** - PostgreSQL 16 Alpine with pgvector
2. **backend** - Runs migrations on startup, then `runserver`
3. **frontend** - Runs `npm run dev` with hot reload
4. **redis** - For Celery task queue (optional locally)

---

## Important Technical Details

### Cross-Origin Cookies (Cart Persistence)
- Backend sets `SameSite=None; Secure` cookies
- Frontend must include `credentials: 'include'` on all API calls
- CORS must allow the frontend origin with credentials

### Next.js Image Optimization
```js
// next.config.js
images: {
  remotePatterns: [
    { protocol: 'https', hostname: '*.s3.*.amazonaws.com' },
  ],
}
```

### Dark Mode
Uses Tailwind's `dark:` variants with `prefers-color-scheme` media query (no toggle).

### Server vs Client Data Fetching
- **Server Components**: Use `INTERNAL_API_URL` (service-to-service)
- **Client Components**: Use `NEXT_PUBLIC_API_URL` (browser requests)

### Honeypot Spam Protection
Contact form has hidden honeypot field. If filled by bots, form silently "succeeds" without sending.

### Semantic Photo Search (pgvector)
- Photos have embeddings generated via OpenAI `text-embedding-ada-002`
- Chat agent uses cosine similarity to find photos matching user descriptions
- Embeddings auto-generated on deploy via `start.sh`

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
| `/api/checkout/create-session/` | POST | Create Stripe checkout (accepts `gift_card_code`) |
| `/api/contact/` | POST | Submit contact form |
| `/api/newsletter/subscribe/` | POST | Subscribe to newsletter |
| `/api/gift-cards/purchase/` | POST | Purchase gift card |
| `/api/gift-cards/check/` | POST | Check gift card balance |
| `/api/chat/` | POST | AI chat agent (SSE streaming) |
| `/api/mockup/analyze/` | POST | Upload wall image for ML analysis |
| `/api/health/` | GET | Health check |

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
| Embeddings not generating | Check `OPENAI_API_KEY` is set |

---

## Django Admin Actions

### Photo Admin Actions
- **Create paper/aluminum/all variants** - Bulk create variants with default pricing
- **Remove paper/aluminum/all variants** - Bulk delete variants
- **Refresh image dimensions** - Re-save photos to update aspect ratio
- **Delete photos and variants** - Bulk delete photos with their variants

### Default Variant Pricing
Defined in `ProductVariant.DEFAULT_PRICING` - used by bulk create actions.

---

## Feature Status

### Completed
- Stripe checkout integration
- Gift card purchase and redemption at checkout
- Stripe promotion codes (when no gift card applied)
- Newsletter subscription (MailerLite)
- Contact form with honeypot spam protection
- Dark mode support
- Image aspect ratio handling for crop previews
- All collections and product pages
- Cart functionality
- Order confirmation emails
- AI chat shopping agent
- "See in room" wall mockup tool (ML-powered)
- Semantic photo search (pgvector)

### Pre-Launch TODO
- [ ] Configure sales tax (TaxJar/Avalara or manual NY collection)
- [ ] Switch Stripe to live mode
- [ ] Final content review

### Future Enhancements
- Customer reviews/testimonials
- Filter by location/orientation

---

## Git Workflow
User prefers to run git commands manually. Provide commit commands but don't execute push automatically.
