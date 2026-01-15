# SEO Specification
## store.matthewraynor.com

**Goal:** Rank for Hamptons art, aerial photography, and fine art print keywords

---

## 1. Target Keywords

### Primary Keywords (High Intent)
| Keyword | Priority |
|---------|----------|
| hamptons art prints | #1 |
| hamptons photography prints | #1 |
| aerial photography hamptons | #1 |
| hamptons wall art | #2 |
| montauk photography prints | #2 |
| east hampton art | #2 |

### Secondary Keywords
| Keyword | Use In |
|---------|--------|
| hamptons fine art | Homepage, About |
| aluminum photo prints | Product pages |
| drone photography art | Collection pages |
| beach photography prints | Collection pages |
| lighthouse art prints | Collection pages |

### Long-Tail Keywords
- "montauk lighthouse wall art"
- "hamptons beach aerial photography"
- "east end drone photography"
- "long island fine art photography"

---

## 2. On-Page SEO

### Title Tags (60 characters max)
```
Homepage:
Hamptons Fine Art Photography | Aerial Prints by Matthew Raynor

Collection Page:
[Collection Name] | Hamptons Photography Prints

Product Page:
[Image Title] - Hamptons Aerial Print | Matthew Raynor Photography

About Page:
About Matthew Raynor | Hamptons Aerial Photographer
```

### Meta Descriptions (155 characters max)
```
Homepage:
Fine art aerial photography of the Hamptons. Premium aluminum and paper prints by local photographer Matthew Raynor. Free shipping over $500.

Collection Page:
Explore [Collection Name] - stunning views of the Hamptons coastline. Museum-quality aluminum prints. Ships in 14-21 days.

Product Page:
[Image Title] - Available as aluminum or paper print. Sizes from 16x24 to 40x60. Certificate of authenticity included.
```

### Header Structure
```
H1: One per page, includes primary keyword
H2: Section headers
H3: Subsections

Example Product Page:
H1: Montauk Lighthouse at Dawn - Aerial Fine Art Print
H2: About This Photograph
H2: Available Sizes & Materials
H2: Shipping & Returns
```

### URL Structure
```
Good:
/collections/aerial-photography
/photos/montauk-lighthouse-dawn
/about

Bad:
/collections/12345
/photos/IMG_4532
```

---

## 3. Image SEO

### File Naming
```
Good:
montauk-lighthouse-aerial-photography.jpg
hamptons-beach-drone-sunset.jpg

Bad:
IMG_4532.jpg
DSC_0001.jpg
```

### Alt Text
```
Good:
"Aerial photograph of Montauk Lighthouse at sunrise by Matthew Raynor"
"Drone photography of Southampton beach, Hamptons"

Bad:
"lighthouse"
"image1"
```

### Image Optimization
- Format: WebP with JPEG fallback (Next.js handles this)
- Lazy loading: Below-fold images
- Responsive: Next.js Image component handles srcset
- CDN: AWS S3 + CloudFront (or S3 direct)

---

## 4. Technical SEO

### Site Speed
- [x] Compression enabled (Netlify)
- [x] Lazy load images
- [x] CDN for images (S3)
- [x] Next.js optimizations

### Mobile Optimization
- [x] Responsive design
- [x] Touch-friendly buttons
- [x] No horizontal scroll
- [x] Readable text without zoom

### Core Web Vitals Targets
| Metric | Target |
|--------|--------|
| LCP (Largest Contentful Paint) | <2.5s |
| FID (First Input Delay) | <100ms |
| CLS (Cumulative Layout Shift) | <0.1 |

### Sitemap & Robots

**robots.txt:**
```
User-agent: *
Allow: /
Disallow: /cart/
Disallow: /checkout/
Disallow: /api/
Disallow: /admin/

Sitemap: https://store.matthewraynor.com/sitemap.xml
```

### Canonical URLs
- Include on every page to prevent duplicate content

---

## 5. Schema Markup

### Product Schema (Product Pages)
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Montauk Lighthouse at Dawn - Aerial Print",
  "image": "https://s3.../montauk-lighthouse.jpg",
  "description": "Fine art aerial photograph...",
  "brand": {
    "@type": "Brand",
    "name": "Matthew Raynor Photography"
  },
  "offers": {
    "@type": "AggregateOffer",
    "lowPrice": "675",
    "highPrice": "3400",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
```

### Local Business Schema (About Page)
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Matthew Raynor Photography",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Hampton Bays",
    "addressRegion": "NY",
    "addressCountry": "US"
  },
  "url": "https://store.matthewraynor.com",
  "priceRange": "$$$$"
}
```

---

## 6. Local SEO

### Google Business Profile
- [ ] Create/claim profile
- [ ] Add services: Fine art prints, aerial photography
- [ ] Upload portfolio images
- [ ] Add website link
- [ ] Encourage reviews

### Local Directories
- [ ] Southampton Artists Association
- [ ] Hamptons.com business directory
- [ ] East End Arts directory

---

## 7. Content Strategy

### Collection Pages
Each needs:
- 150-300 word description
- Keywords naturally included
- Story behind the collection

### Product Pages
Each needs:
- Unique title
- 100-200 word description
- Location information

### Future: Blog Content Ideas
- "Best Beaches to Photograph in the Hamptons"
- "How Aerial Photography Captures the East End"
- "Decorating with Hamptons Photography"

---

## 8. Implementation Checklist

### Done
- [x] URL structure defined
- [x] Mobile responsive
- [x] Page speed optimized
- [x] Images on S3 CDN

### To Do
- [ ] Review/update title tags
- [ ] Review/update meta descriptions
- [ ] Add image alt text throughout
- [ ] Implement schema markup
- [ ] Generate sitemap
- [ ] Set up Google Search Console
- [ ] Set up Google Analytics 4
- [ ] Create Google Business Profile

---

## 9. Measurement

### Tools
- Google Search Console (free, essential)
- Google Analytics 4 (free, essential)
- PageSpeed Insights (free)

### Key Metrics
| Metric | Track |
|--------|-------|
| Organic sessions | Weekly |
| Keyword rankings | Monthly |
| Page speed | Monthly |
| Core Web Vitals | Monthly |

---

## Quick Reference

### Character Limits
| Element | Limit |
|---------|-------|
| Title tag | 60 chars |
| Meta description | 155 chars |
| URL | 75 chars |
| Alt text | 125 chars |
| H1 | 70 chars |
