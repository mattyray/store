# Photography E-Commerce Store Specification
## store.matthewraynor.com

**Version:** 2.0 (Updated January 2026)
**Status:** Development complete, pre-launch
**Target Market:** Hamptons luxury art buyers

---

## 1. Executive Summary

A fine art photography e-commerce platform selling premium prints to the Hamptons luxury market. Clean, gallery-style design that lets the photography speak for itself. Two product tiers: in-house paper prints and lab-fulfilled aluminum prints.

**Tech Stack:**
- Backend: Django 5, Django REST Framework, PostgreSQL 16
- Frontend: Next.js 15+ (App Router), TypeScript, Tailwind CSS
- Payments: Stripe Checkout (guest checkout, no account required)
- Email: Resend SMTP
- Newsletter: MailerLite
- Media Storage: AWS S3
- Hosting: Railway (backend) + Netlify (frontend)

---

## 2. Product Structure

### 2.1 Collections

| Collection | Description |
|------------|-------------|
| Shots from the Sea | Commercial fishing era photography |
| Travel Photography | Global destinations |
| Aerial Photography | Drone perspectives of the East End |

### 2.2 Product Types

**Paper Prints (In-House Production)**
- Sizes: 11x14, 13x19
- Matted presentation
- Price: $175-$250
- Ships within 5-7 business days

**Aluminum Prints (Lab Fulfilled)**
- Sizes: 16x24 to 40x60
- Float mount backing, ready to hang
- Price: $675-$3,400
- Ships within 14-21 business days

### 2.3 Pricing

| Size | Paper (Matted) | Aluminum |
|------|----------------|----------|
| 11x14 | $175 | - |
| 13x19 | $250 | - |
| 16x24 | - | $675 |
| 20x30 | - | $995 |
| 24x36 | - | $1,350 |
| 30x40 | - | $1,850 |
| 30x45 | - | $2,150 |
| 40x60 | - | $3,400 |

---

## 3. Site Architecture

### 3.1 Pages

```
/                       → Home (hero + featured collections)
/collections            → All collections grid
/collections/[slug]     → Single collection with all images
/photos/[slug]          → Product detail page with size/material selector
/cart                   → Shopping cart
/checkout               → Stripe Checkout redirect
/about                  → Artist story
/contact                → Contact form
/shipping               → Shipping & returns info
/book                   → Photography book
/gift-cards             → Gift card purchase
/order/[id]             → Order confirmation
/track-order            → Order tracking
```

---

## 4. Feature Status

### 4.1 Product Display ✅
- [x] Responsive image grid (3-col desktop, 2-col tablet, 1-col mobile)
- [x] High-res images with lazy loading
- [x] Clean white background, generous whitespace
- [x] Dark mode support

### 4.2 Product Detail Page ✅
- [x] Large hero image
- [x] Size selector dropdown
- [x] Material selector (Paper / Aluminum)
- [x] Dynamic price update on selection
- [x] "Add to Cart" button
- [x] Crop preview overlay showing what gets cropped per size
- [x] Location/description display

### 4.3 Cart & Checkout ✅
- [x] Cart page with quantity adjustment
- [x] Remove items
- [x] Stripe Checkout integration
- [x] Guest checkout (no account required)
- [x] Shipping address collection at checkout
- [x] Order confirmation email

### 4.4 Collections/Filtering ✅
- [x] Browse by collection
- [x] Photo detail pages

### 4.5 Content Pages ✅
- [x] About page
- [x] Contact form with honeypot spam protection
- [x] Shipping & returns page

### 4.6 Additional Features ✅
- [x] Gift card purchase
- [x] Newsletter signup (MailerLite)
- [x] Photography book product

### 4.7 Not Yet Implemented
- [ ] Gift card redemption at checkout
- [ ] Stripe promotion codes
- [ ] Customer reviews
- [ ] Filter by location/orientation

---

## 5. Design Specifications

### 5.1 Visual Style
- **Aesthetic:** Clean, minimal, gallery-style
- **Background:** White / off-white
- **Dark mode:** Automatic via `prefers-color-scheme`
- **Typography:** Sans-serif
- **Photography dominates** - 80% visual weight

### 5.2 Responsive Breakpoints
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

---

## 6. Integrations

### Active
- **Stripe Checkout** - Payment processing (currently sandbox mode)
- **AWS S3** - Image storage
- **Resend** - Transactional email
- **MailerLite** - Newsletter

### Not Implemented
- Aluminyze API (orders placed manually)

---

## 7. Pre-Launch Checklist

- [ ] Switch Stripe to live mode
- [ ] Configure sales tax collection
- [ ] Final content review
- [ ] Test order flow end-to-end

---

## Appendix: Competitive Reference

**Gray Malin benchmark pricing:**
- Small framed: $464-524
- Medium framed: $799-904
- Large framed: $1,324-1,484
- X-Large framed: $2,349-2,579
- Oversized framed: $3,749-4,024

Your pricing is competitive for the Hamptons market.
