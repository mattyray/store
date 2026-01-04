# Photography E-Commerce Store Specification
## store.matthewraynor.com

**Version:** 1.0  
**Date:** January 2026  
**Target Market:** Hamptons luxury art buyers

---

## 1. Executive Summary

A fine art photography e-commerce platform selling premium prints to the Hamptons luxury market. Clean, gallery-style design that lets the photography speak for itself. Two product tiers: in-house paper prints and Aluminyze-fulfilled aluminum prints.

**Tech Stack:**
- Backend: Django REST Framework + PostgreSQL
- Frontend: Next.js / React / TypeScript / Tailwind CSS
- Payments: Stripe Checkout (no account required)
- Aluminum Fulfillment: Aluminyze API
- Hosting: Railway (API) + Netlify (Frontend)

---

## 2. Product Structure

### 2.1 Collections

| Collection | Description | Content |
|------------|-------------|---------|
| Above the East End | Aerial abstracts of Hamptons | Drone photography, beaches, estates, landscapes |
| Shots from the Sea | Commercial fishing era | Pre-injury boat photography, ocean life |
| Travel Photography | Global destinations | International travel images |
| The Twelve Windmills | Limited edition documentary | All 12 historic Hamptons windmills |
| Four Lights | Lighthouse collection | Montauk, etc. |
| Monochrome Coast | Black & white seascapes | Dramatic B&W ocean imagery |

### 2.2 Product Types

**Paper Prints (In-House Production)**
- Standard sizes: 11x14, 13x19
- Matted presentation
- Price range: $150-400
- Ships within 5-7 business days

**Aluminum Prints (Aluminyze Fulfillment)**
- Custom sizes up to 60x90"
- Float mount backing
- Price range: $600-5,000+
- 3.5x markup on Aluminyze wholesale
- Ships within 14-21 business days

### 2.3 Pricing Matrix

| Size | Paper (Matted) | Aluminum |
|------|----------------|----------|
| 11x14 | $150 | - |
| 13x19 | $250 | - |
| 16x20 | $350 | $600 |
| 20x30 | - | $1,200 |
| 30x40 | - | $2,100 |
| 40x60 | - | $3,400 |
| 60x90 | - | $5,000+ |

---

## 3. Site Architecture

### 3.1 Pages

```
/                       → Home (hero + featured collections)
/collections            → All collections grid
/collections/[slug]     → Single collection with all images
/prints/[slug]          → Product detail page with size/material selector
/cart                   → Shopping cart
/checkout               → Stripe Checkout redirect
/about                  → Artist story (Matt's background)
/contact                → Custom work inquiries
/shipping               → Shipping & returns info
```

### 3.2 Navigation

```
Logo | Collections ▼ | About | Contact | Cart(n)
      └── Above the East End
      └── Shots from the Sea
      └── Travel Photography
      └── Limited Editions
```

---

## 4. Core Features (MVP)

### 4.1 Product Display
- [ ] 3-column image grid (desktop), 2-column (tablet), 1-column (mobile)
- [ ] High-res images with zoom on hover/click
- [ ] Lazy loading with blur placeholders
- [ ] Clean white background, generous whitespace

### 4.2 Product Detail Page
- [ ] Large hero image (70% width)
- [ ] Thumbnail gallery below
- [ ] Size selector dropdown
- [ ] Material selector (Paper / Aluminum)
- [ ] Dynamic price update on selection
- [ ] "Add to Cart" button
- [ ] Location/story in description
- [ ] Shipping timeframe display

### 4.3 Cart & Checkout
- [ ] Slide-out cart drawer
- [ ] Quantity adjustment
- [ ] Remove items
- [ ] Stripe Checkout integration
- [ ] NO account required (guest checkout)
- [ ] Shipping address collection at checkout
- [ ] Order confirmation email

### 4.4 Collections/Filtering
- [ ] Browse by collection
- [ ] Filter by location (Hamptons towns: Montauk, East Hampton, Southampton, etc.)
- [ ] Filter by orientation (horizontal, vertical, square)
- [ ] Sort by: newest, price low-high, price high-low

### 4.5 Content Pages
- [ ] About page with Matt's story (quadriplegic fisherman → drone photographer)
- [ ] Contact form for custom aerial commissions
- [ ] Shipping & returns policy
- [ ] Print quality/materials information

---

## 5. Design Specifications

### 5.1 Visual Style
- **Aesthetic:** Clean, minimal, gallery-style
- **Background:** White (#FFFFFF) or off-white (#FAFAFA)
- **Typography:** Sans-serif (Inter or similar)
- **Accent color:** Ocean blue (#0077B6) - used sparingly
- **Photography dominates** - 80% visual weight

### 5.2 Layout Principles
- Maximum content width: 1400px
- Generous padding (32-64px sections)
- Image-first hierarchy
- Minimal text, let photos speak
- No clutter competing with imagery

### 5.3 Responsive Breakpoints
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

---

## 6. Data Models

### 6.1 Django Models

```python
class Collection(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    cover_image = models.ImageField()
    is_limited_edition = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)

class Photo(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    image = models.ImageField()  # Cloudinary
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    location_tag = models.CharField(max_length=100, blank=True)  # e.g., "montauk"
    orientation = models.CharField(choices=[('H','Horizontal'),('V','Vertical'),('S','Square')])
    date_taken = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductVariant(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=20)  # e.g., "16x20"
    material = models.CharField(choices=[('paper','Paper'),('aluminum','Aluminum')])
    price = models.DecimalField(max_digits=8, decimal_places=2)
    width_inches = models.IntegerField()
    height_inches = models.IntegerField()
    is_available = models.BooleanField(default=True)
    aluminyze_sku = models.CharField(max_length=100, blank=True)  # For aluminum orders

class Order(models.Model):
    stripe_checkout_id = models.CharField(max_length=200)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200)
    shipping_address = models.JSONField()
    status = models.CharField(choices=[
        ('pending','Pending'),
        ('paid','Paid'),
        ('processing','Processing'),
        ('shipped','Shipped'),
        ('delivered','Delivered')
    ], default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    aluminyze_order_id = models.CharField(max_length=100, blank=True)
```

### 6.2 API Endpoints

```
GET  /api/collections/              → List all collections
GET  /api/collections/{slug}/       → Single collection with photos
GET  /api/photos/                   → List photos (filterable)
GET  /api/photos/{slug}/            → Single photo with variants
POST /api/cart/                     → Create cart session
PUT  /api/cart/                     → Update cart
POST /api/checkout/                 → Create Stripe checkout session
POST /api/webhooks/stripe/          → Stripe webhook handler
```

---

## 7. Third-Party Integrations

### 7.1 Stripe Checkout
- Checkout Sessions for payment
- Webhooks for order confirmation
- Shipping address collection
- No customer accounts needed

### 7.2 Aluminyze (Future)
- API for order submission
- Tracking number retrieval
- Enroll in Aluminyze Pro for wholesale pricing first

### 7.3 Cloudinary
- Image hosting and optimization
- Responsive image delivery
- Watermarking for previews (optional)

### 7.4 Email (Resend or similar)
- Order confirmation
- Shipping notifications
- Contact form submissions

---

## 8. Future Enhancements (V2+)

- [ ] "See in room" mockup tool
- [ ] Limited edition badges with edition numbers
- [ ] Customer gallery ("Styled by You")
- [ ] Newsletter signup
- [ ] Instagram feed integration
- [ ] Virtual consultation booking
- [ ] Gift certificates
- [ ] Wishlist functionality
- [ ] Admin dashboard for order management
- [ ] Wholesale/gallery portal

---

## 9. Success Metrics

- Clean, fast-loading pages (< 3s)
- Mobile-responsive at all breakpoints
- Frictionless checkout (< 3 clicks from browse to buy)
- SEO-optimized for "Hamptons art," "aerial photography prints"
- Professional presentation worthy of $5,000 purchases

---

## 10. Project Phases

### Phase 1: Foundation (Week 1-2)
- Django project setup with models
- Next.js frontend scaffold
- Basic collection/photo display
- Stripe Checkout integration

### Phase 2: Polish (Week 3-4)
- Product configurator (size/material selector)
- Cart functionality
- About/Contact pages
- Responsive design refinement

### Phase 3: Launch (Week 5)
- Content population (photos, descriptions)
- Testing
- DNS/deployment
- Soft launch

---

## Appendix: Competitive Research Summary

Based on analysis of Gray Malin, Peter McKinnon, Almost Real, and Mike Kelley stores:

**What works:**
- Image-first design (photos are 80% of visual weight)
- Clean white backgrounds
- Large high-res previews with zoom
- Real-time price updates as options change
- Multiple browse paths (collection, location, theme)
- Guest checkout (no friction)
- Clear shipping/production timeframes

**Gray Malin benchmark pricing:**
- Small framed: $464-524
- Medium framed: $799-904
- Large framed: $1,324-1,484
- X-Large framed: $2,349-2,579
- Oversized framed: $3,749-4,024

Matt's pricing is competitive for the Hamptons market.
