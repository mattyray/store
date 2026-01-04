# SEO Specification
## store.matthewraynor.com

**Version:** 1.0  
**Date:** January 2026  
**Goal:** Rank for Hamptons art, aerial photography, and fine art print keywords

---

## 1. Target Keywords

### Primary Keywords (High Intent)
| Keyword | Search Volume | Difficulty | Priority |
|---------|---------------|------------|----------|
| hamptons art prints | Medium | Low | #1 |
| hamptons photography prints | Medium | Low | #1 |
| aerial photography hamptons | Low | Low | #1 |
| hamptons wall art | Medium | Medium | #2 |
| montauk photography prints | Low | Low | #2 |
| east hampton art | Low | Low | #2 |

### Secondary Keywords (Discovery)
| Keyword | Intent | Use In |
|---------|--------|--------|
| hamptons fine art | Browse | Homepage, About |
| aluminum photo prints | Product | Product pages |
| chromaluxe prints | Product | Product pages |
| drone photography art | Browse | Collection pages |
| beach photography prints | Browse | Collection pages |
| lighthouse art prints | Browse | Collection pages |
| windmill photography | Browse | Collection pages |

### Long-Tail Keywords (Collection Specific)
- "montauk lighthouse wall art"
- "hamptons beach aerial photography"
- "southampton windmill prints"
- "east end drone photography"
- "hamptons estate aerial photos"
- "long island fine art photography"

---

## 2. On-Page SEO

### Title Tags (60 characters max)
```
Homepage:
Hamptons Fine Art Photography | Aerial Prints by Matthew Raynor

Collection Page:
Above the East End | Aerial Hamptons Photography Prints

Product Page:
[Image Title] - Hamptons Aerial Print | Matthew Raynor Photography

About Page:
About Matthew Raynor | Hamptons Aerial Photographer

Contact Page:
Contact | Custom Hamptons Aerial Photography
```

### Meta Descriptions (155 characters max)
```
Homepage:
Fine art aerial photography of the Hamptons. Limited edition aluminum and paper prints by local photographer Matthew Raynor. Free shipping over $500.

Collection Page:
Explore [Collection Name] - stunning aerial views of the Hamptons coastline. Museum-quality ChromaLuxe aluminum prints. Limited editions available.

Product Page:
[Image Title] - Available as aluminum or paper print. Sizes from 16x24 to 40x60. Certificate of authenticity included. Ships in 14-21 days.
```

### Header Structure (Every Page)
```
H1: One per page, includes primary keyword
H2: Section headers, secondary keywords
H3: Subsections as needed

Example Product Page:
H1: Montauk Lighthouse at Dawn - Aerial Fine Art Print
H2: About This Photograph
H2: Available Sizes & Materials
H2: Shipping & Returns
H2: You May Also Like
```

### URL Structure
```
Good:
/collections/aerial-hamptons
/prints/montauk-lighthouse-dawn
/about

Bad:
/collections/12345
/prints/IMG_4532
/page?id=about
```

---

## 3. Image SEO (Critical for Photography)

### File Naming
```
Good:
montauk-lighthouse-aerial-photography.jpg
hamptons-beach-drone-sunset.jpg
southampton-windmill-fine-art.jpg

Bad:
IMG_4532.jpg
DSC_0001.jpg
final_edit_v3.jpg
```

### Alt Text (Descriptive, Include Keywords)
```
Good:
"Aerial photograph of Montauk Lighthouse at sunrise, fine art print by Matthew Raynor"
"Drone photography of Southampton beach, Hamptons aerial art"

Bad:
"lighthouse"
"image1"
"photo"
```

### Image Optimization
- **Format:** WebP with JPEG fallback
- **Compression:** 80% quality for web display
- **Lazy loading:** Below-fold images
- **Responsive:** srcset for multiple sizes
- **CDN:** Cloudinary for delivery

### Image Sitemap
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://store.matthewraynor.com/prints/montauk-lighthouse</loc>
    <image:image>
      <image:loc>https://res.cloudinary.com/.../montauk-lighthouse.jpg</image:loc>
      <image:title>Montauk Lighthouse Aerial Photography Print</image:title>
      <image:caption>Fine art aerial photograph of Montauk Lighthouse at sunrise</image:caption>
    </image:image>
  </url>
</urlset>
```

---

## 4. Technical SEO

### Site Speed (Target: <3 seconds)
- [ ] Enable compression (gzip/brotli)
- [ ] Minimize CSS/JS
- [ ] Lazy load images
- [ ] Use CDN for images (Cloudinary)
- [ ] Cache static assets
- [ ] Optimize server response time

### Mobile Optimization
- [ ] Responsive design (all breakpoints)
- [ ] Touch-friendly buttons (min 44px)
- [ ] No horizontal scroll
- [ ] Readable text without zoom
- [ ] Test with Google Mobile-Friendly Tool

### Core Web Vitals
| Metric | Target | How |
|--------|--------|-----|
| LCP (Largest Contentful Paint) | <2.5s | Optimize hero images |
| FID (First Input Delay) | <100ms | Minimize JS |
| CLS (Cumulative Layout Shift) | <0.1 | Set image dimensions |

### XML Sitemap
```
Location: https://store.matthewraynor.com/sitemap.xml

Include:
- All collection pages
- All product pages
- About, Contact, Shipping pages
- Image sitemap

Update: Automatically on new content
Submit: Google Search Console, Bing Webmaster Tools
```

### Robots.txt
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
```html
<!-- On every page -->
<link rel="canonical" href="https://store.matthewraynor.com/prints/montauk-lighthouse" />

<!-- Prevent duplicate content from filters/sorting -->
```

### Schema Markup (Structured Data)

**Product Schema (Every Product Page)**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Montauk Lighthouse at Dawn - Aerial Print",
  "image": "https://res.cloudinary.com/.../montauk-lighthouse.jpg",
  "description": "Fine art aerial photograph of Montauk Lighthouse...",
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
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "5",
    "reviewCount": "12"
  }
}
```

**Local Business Schema (About Page)**
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Matthew Raynor Photography",
  "image": "https://store.matthewraynor.com/logo.jpg",
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

**BreadcrumbList Schema**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://store.matthewraynor.com"},
    {"@type": "ListItem", "position": 2, "name": "Aerial Photography", "item": "https://store.matthewraynor.com/collections/aerial-hamptons"},
    {"@type": "ListItem", "position": 3, "name": "Montauk Lighthouse"}
  ]
}
```

---

## 5. Content SEO

### Collection Page Content
Each collection page needs:
- 150-300 word description
- Include target keywords naturally
- Story behind the collection
- What makes it unique

```
Example - Above the East End Collection:

"Above the East End captures the Hamptons from a perspective few ever see. 
These aerial photographs reveal the geometry of our coastline—the curves of 
Montauk's beaches, the precise rows of Southampton vineyards, the scattered 
sailboats off Sag Harbor.

Shot exclusively by drone over three years, each image in this collection 
represents a unique moment when light, weather, and landscape aligned perfectly. 
From the golden hour glow on Ditch Plains to the abstract patterns of Mecox Bay, 
these prints bring the East End's beauty into your home.

Available as museum-quality ChromaLuxe aluminum prints in sizes up to 40x60 inches."
```

### Product Page Content
Each product needs:
- Unique title (not just filename)
- 100-200 word description
- Location information
- Story/context
- Technical details

### Blog/Journal (Future)
Content ideas for organic traffic:
- "Best Beaches to Photograph in the Hamptons"
- "How Aerial Photography Captures the East End"
- "The Story Behind [Image Name]"
- "Decorating with Hamptons Photography"
- "Limited Edition vs Open Edition: What's the Difference?"

---

## 6. Local SEO

### Google Business Profile
- [ ] Create/claim profile for "Matthew Raynor Photography"
- [ ] Add all services: Fine art prints, aerial photography, custom commissions
- [ ] Upload portfolio images
- [ ] Add website link
- [ ] Encourage reviews from buyers
- [ ] Post updates (new work, events, shows)

### Local Keywords to Target
- "hamptons photographer"
- "east hampton art gallery"
- "montauk fine art"
- "southampton wall art"
- "sag harbor photography"
- "long island aerial photography"

### Local Directories
- [ ] Yelp (Photography category)
- [ ] Southampton Artists Association
- [ ] Hamptons.com business directory
- [ ] East End Arts directory

---

## 7. Link Building

### Internal Linking
- Link between related products
- Link collections to individual products
- Link About page to featured work
- Use descriptive anchor text

### External Link Opportunities
| Source | Type | How to Get |
|--------|------|------------|
| Local publications | Editorial | PR outreach, features |
| Interior design blogs | Guest post | Offer expert content |
| Photography blogs | Feature | Submit to roundups |
| Artist directories | Listing | Submit profile |
| Local business directories | Citation | Claim listings |

### Backlink Priorities
1. Local Hamptons publications (James Lane Post, etc.)
2. Photography/art publications
3. Interior design resources
4. Local business directories

---

## 8. E-commerce SEO Specifics

### Product Variants
- Use canonical tags to main product
- Don't create separate URLs for each size
- Handle with JavaScript, single URL

### Out of Stock / Limited Editions
- Keep page live (don't 404)
- Show "Sold Out" status
- Offer "Notify me" option
- Maintain SEO value

### Reviews
- Implement review schema
- Display ratings on product pages
- Encourage customer reviews
- Reviews appear in search results

### Faceted Navigation (Filters)
- Use JavaScript for filtering (no new URLs)
- Or use canonical tags to main page
- Prevent Google from indexing filter combinations

---

## 9. Measurement & Tools

### Google Search Console
- [ ] Verify domain
- [ ] Submit sitemap
- [ ] Monitor indexing status
- [ ] Track search queries
- [ ] Fix crawl errors
- [ ] Monitor Core Web Vitals

### Google Analytics 4
- [ ] Install tracking
- [ ] Set up e-commerce tracking
- [ ] Track conversions by source
- [ ] Monitor organic traffic growth

### Key Metrics to Track
| Metric | Target | Frequency |
|--------|--------|-----------|
| Organic sessions | Growing | Weekly |
| Keyword rankings | Top 10 | Monthly |
| Indexed pages | All products | Monthly |
| Page speed | <3s | Monthly |
| Backlinks | Growing | Monthly |

### SEO Tools
- **Google Search Console:** Free, essential
- **Google Analytics 4:** Free, essential
- **Ubersuggest:** Free tier for keyword research
- **PageSpeed Insights:** Free, speed testing
- **Schema Markup Validator:** Free, test structured data

---

## 10. SEO Launch Checklist

### Pre-Launch
- [ ] Keyword research complete
- [ ] URL structure defined
- [ ] Title tags written
- [ ] Meta descriptions written
- [ ] Image alt text added
- [ ] Schema markup implemented
- [ ] Sitemap generated
- [ ] Robots.txt configured
- [ ] Canonical tags in place
- [ ] Mobile responsive verified
- [ ] Page speed optimized

### Launch
- [ ] Submit sitemap to Google Search Console
- [ ] Submit sitemap to Bing Webmaster Tools
- [ ] Verify all pages indexed
- [ ] Set up Google Analytics 4
- [ ] Create Google Business Profile
- [ ] Test all schema with validator

### Post-Launch (Ongoing)
- [ ] Monitor Search Console weekly
- [ ] Track keyword rankings monthly
- [ ] Add new content quarterly
- [ ] Build backlinks ongoing
- [ ] Update stale content annually
- [ ] Technical audit quarterly

---

## Appendix: Quick Reference

### Character Limits
| Element | Limit | Display |
|---------|-------|---------|
| Title tag | 60 chars | Full in search |
| Meta description | 155 chars | Full in search |
| URL | 75 chars | Clean, readable |
| Alt text | 125 chars | Screen readers |
| H1 | 70 chars | One per page |

### Page Speed Targets
| Metric | Mobile | Desktop |
|--------|--------|---------|
| Time to First Byte | <600ms | <200ms |
| First Contentful Paint | <1.8s | <1s |
| Largest Contentful Paint | <2.5s | <1.5s |
| Time to Interactive | <3.8s | <2s |

### Priority by Page Type
| Page | SEO Priority | Focus |
|------|--------------|-------|
| Homepage | High | Brand + primary keywords |
| Collections | High | Category keywords |
| Products | High | Long-tail keywords |
| About | Medium | Local + brand |
| Contact | Low | Local citations |
| Shipping | Low | Trust signals |
