# Email Marketing Specification
## store.matthewraynor.com

**Version:** 1.0  
**Date:** January 2026  
**Goal:** Build email list as primary sales channel (10.3% conversion rate)

---

## 1. Platform Selection

### Recommended: MailerLite
- **Cost:** Free up to 1,000 subscribers, then $10/month
- **Features:** Automation, landing pages, pop-ups, e-commerce integrations
- **Why:** Best value for small art businesses, easy to use, good deliverability

### Alternatives
| Platform | Free Tier | Paid Starting | Best For |
|----------|-----------|---------------|----------|
| MailerLite | 1,000 subs | $10/mo | Small businesses, beginners |
| ConvertKit | 1,000 subs | $15/mo | Creators, more advanced |
| Klaviyo | 250 subs | $20/mo | E-commerce focus, expensive |
| Mailchimp | 500 subs | $13/mo | General, bloated features |

---

## 2. List Building Strategy

### Website Signup Points

**1. Homepage Hero**
- Prominent signup form above the fold
- Value prop: "Get early access to new collections + exclusive offers"

**2. Exit-Intent Popup**
- Triggers when cursor moves toward browser close
- Offer: 10% off first purchase OR free shipping
- Don't show to returning visitors who already signed up

**3. Footer Signup**
- Persistent on every page
- Simple: Email field + "Subscribe" button

**4. Collection Pages**
- "Get notified when new [Collection Name] pieces are added"
- Segment by interest

**5. Checkout Thank You Page**
- "Join our collector list for first access to limited editions"
- Post-purchase capture

### Signup Incentives (Choose One)

| Incentive | Pros | Cons |
|-----------|------|------|
| 10% off first order | High conversion, immediate value | Cuts into margin |
| Free shipping | High perceived value | Cost absorbed |
| Early access to new work | No cost, builds exclusivity | Lower conversion |
| Behind-the-scenes content | No cost, builds connection | Lowest conversion |

**Recommendation:** Start with "Early access to limited editions + 10% off your first purchase"

---

## 3. Email Sequences

### 3.1 Welcome Sequence (Automated)

**Trigger:** New subscriber signup

**Email 1: Immediate**
```
Subject: Welcome to [Store Name] + Your 10% Off Code

- Thank them for joining
- Deliver discount code (if offered)
- Brief intro: Who you are, what you create
- One stunning image
- CTA: Browse the collection

Length: Short (150 words max)
```

**Email 2: Day 2**
```
Subject: The story behind the lens

- Your story (fisherman → photographer → artist)
- Why you photograph the Hamptons
- 2-3 images showing range
- CTA: Explore collections

Length: Medium (250-300 words)
```

**Email 3: Day 4**
```
Subject: How we make your prints

- ChromaLuxe quality explanation
- Why aluminum > paper for longevity
- Behind-the-scenes of production
- CTA: See available sizes

Length: Medium (200-250 words)
```

**Email 4: Day 7**
```
Subject: Ready to bring the Hamptons home?

- Reminder of discount code (if unused)
- Bestsellers or featured pieces
- Social proof (if available)
- Urgency: Code expires in 7 days
- CTA: Shop now

Length: Short (150 words)
```

### 3.2 Abandoned Cart Sequence (Automated)

**Trigger:** Item added to cart, checkout not completed within 1 hour

**Email 1: 1 hour after abandonment**
```
Subject: Still thinking about [Product Name]?

- Image of abandoned product
- "You left something beautiful behind"
- Simple CTA: Complete your purchase
- No discount yet

Length: Very short (50-75 words)
```

**Email 2: 24 hours after abandonment**
```
Subject: Your [Product Name] is waiting

- Image of product
- Address common objections:
  - "Free shipping on orders over $X"
  - "30-day satisfaction guarantee"
  - "Certificate of authenticity included"
- CTA: Return to cart

Length: Short (100 words)
```

**Email 3: 72 hours after abandonment**
```
Subject: Last chance: 10% off your cart

- Final reminder
- Discount code for abandoned items only
- Scarcity: "Limited edition, only X remaining"
- CTA: Complete purchase

Length: Short (100 words)
```

### 3.3 Post-Purchase Sequence (Automated)

**Trigger:** Order completed

**Email 1: Immediate (Order Confirmation)**
```
Subject: Order confirmed! Here's what happens next

- Order details
- Production timeline (14-21 days for aluminum)
- What to expect (tracking email coming)
- Contact info for questions

Length: Short, transactional
```

**Email 2: Day 3 (Production Update)**
```
Subject: Your artwork is being created

- Behind-the-scenes of printing process
- Build anticipation
- "Your piece is being carefully crafted..."

Length: Short (100 words)
```

**Email 3: Shipping (Automated via Stripe/fulfillment)**
```
Subject: Your artwork is on its way!

- Tracking number
- Expected delivery date
- Handling/unpacking tips

Length: Short, transactional
```

**Email 4: Day 30 (Follow-up)**
```
Subject: How's your new piece looking?

- Check in on satisfaction
- Ask for photo of artwork installed
- Request review/testimonial
- Invite to share on social (tag for repost)

Length: Short (100 words)
```

### 3.4 Browse Abandonment (Automated)

**Trigger:** Viewed product page 2+ times, no purchase, has email

**Email 1: 24 hours after browse**
```
Subject: Caught your eye?

- Image of viewed product
- Brief description
- CTA: Take another look

Length: Very short (50 words)
```

---

## 4. Ongoing Email Calendar

### Frequency
- **Minimum:** 2 emails per month
- **Recommended:** 3-4 emails per month
- **Maximum:** Weekly (risk of fatigue)

### Monthly Template

**Week 1: New Work / Collection Spotlight**
```
Subject lines:
- "New: [Collection Name] just dropped"
- "Fresh off the drone: [Location]"
- "First look: [Season] in the Hamptons"

Content:
- 3-5 new images
- Story behind the shoot
- CTA: View collection
```

**Week 2: Behind-the-Scenes / Story**
```
Subject lines:
- "The shot that almost didn't happen"
- "Why I photograph [Subject]"
- "5am on [Location]: Worth it"

Content:
- Personal narrative
- Process insights
- Connection building (no hard sell)
```

**Week 3: Social Proof / Featured Piece**
```
Subject lines:
- "This piece found a home in [Town]"
- "Our collectors' favorite this month"
- "Why [Piece Name] keeps selling out"

Content:
- Customer testimonial or installation photo
- Featured piece with story
- CTA: Shop similar pieces
```

**Week 4: Promotion / Limited Time (Optional)**
```
Subject lines:
- "48 hours: Free shipping on aluminum prints"
- "Last call for holiday delivery"
- "Collector's weekend: 15% off everything"

Content:
- Clear offer with deadline
- Urgency/scarcity
- Strong CTA
```

### Seasonal Content Calendar

| Month | Theme | Content Ideas |
|-------|-------|---------------|
| January | New Year | "New work for a new year," winter landscapes |
| February | Valentine's | Gift guide, "Art as a gift" |
| March | Spring | Early spring shots, renewal themes |
| April | Easter/Spring | Gardens, fresh starts |
| May | Mother's Day | Gift guide, home decor |
| June | Summer kickoff | Beach season begins, new aerial shots |
| July | Peak summer | Hamptons Fine Art Fair, beach content |
| August | Late summer | Golden hour content, limited editions |
| September | Fall | Back to routines, "bring summer home" |
| October | Halloween | Moody shots, autumn colors |
| November | Thanksgiving | Gratitude, holiday gift guide preview |
| December | Holidays | Gift guide, year in review, shipping deadlines |

---

## 5. Segmentation Strategy

### Basic Segments

**By Purchase History**
- Never purchased
- Purchased once
- Purchased 2+ times (VIP)

**By Engagement**
- Highly engaged (opens 50%+ emails)
- Moderately engaged (opens 20-50%)
- Disengaged (hasn't opened in 90 days)

**By Interest (Based on clicks/views)**
- Aerial photography
- Shots from the Sea
- Travel photography
- Limited editions

### Segment-Specific Content

| Segment | Content Strategy |
|---------|------------------|
| Never purchased | Welcome sequence, education, trust-building |
| Purchased once | Cross-sell, new collections, loyalty building |
| VIP (2+ purchases) | Early access, exclusive previews, special offers |
| Disengaged | Re-engagement campaign, then remove |

---

## 6. Re-engagement Campaign

**Trigger:** No email opens in 90 days

**Email 1:**
```
Subject: We miss you (and we have something new)

- Acknowledge absence
- Show 2-3 best new pieces
- CTA: "See what's new"
```

**Email 2 (7 days later if no open):**
```
Subject: Should we part ways?

- "We noticed you haven't opened our emails"
- Offer to stay or unsubscribe
- CTA: "Keep me on the list" button
```

**Email 3 (7 days later if no open):**
```
Subject: Goodbye (for now)

- "We're removing you from our list"
- "Click here if you'd like to stay"
- Clean list of non-responders
```

---

## 7. Email Design Guidelines

### Visual Style
- **Layout:** Single column, mobile-first
- **Width:** 600px max
- **Background:** White
- **Font:** System fonts (Arial, Helvetica) for deliverability
- **Images:** High quality, compressed (<200KB each)

### Structure Template
```
[Logo]

[Hero Image - Full Width]

[Headline - 6-10 words]

[Body Copy - 2-3 short paragraphs]

[CTA Button - Contrasting color]

[Secondary content/images if needed]

[Footer: Social links, unsubscribe, address]
```

### Best Practices
- **Subject lines:** 40 characters or less, no spam words
- **Preview text:** Use it! Continues the subject line
- **Images:** Always include alt text
- **CTAs:** One primary CTA per email, button style
- **Mobile:** 50%+ opens are mobile, test everything
- **Personalization:** Use first name in greeting when available

---

## 8. Key Metrics & Benchmarks

### Industry Benchmarks (Art/E-commerce)

| Metric | Good | Great | Action if Below |
|--------|------|-------|-----------------|
| Open Rate | 20% | 30%+ | Improve subject lines |
| Click Rate | 2% | 4%+ | Better CTAs, content |
| Unsubscribe | <0.5% | <0.2% | Reduce frequency, better targeting |
| Conversion | 2% | 5%+ | Improve offers, landing pages |
| List Growth | 5%/mo | 10%/mo | More signup points, better incentive |

### What to Track Weekly
- Total subscribers
- New subscribers this week
- Unsubscribes
- Open rate by email
- Click rate by email
- Revenue attributed to email

---

## 9. Technical Setup Checklist

### Platform Setup
- [ ] Create MailerLite account
- [ ] Verify sending domain (DNS records)
- [ ] Set up custom email: hello@store.matthewraynor.com
- [ ] Import any existing contacts (with consent)
- [ ] Create signup forms (embedded, popup, landing page)

### Integrations
- [ ] Connect to Stripe (purchase triggers)
- [ ] Connect to website (signup forms)
- [ ] Set up abandoned cart tracking
- [ ] Configure e-commerce revenue tracking

### Automations
- [ ] Welcome sequence (4 emails)
- [ ] Abandoned cart sequence (3 emails)
- [ ] Post-purchase sequence (4 emails)
- [ ] Browse abandonment (1 email)
- [ ] Re-engagement campaign (3 emails)

### Compliance
- [ ] Add physical mailing address to footer
- [ ] Include unsubscribe link in every email
- [ ] Double opt-in enabled (recommended)
- [ ] Privacy policy link in signup forms
- [ ] Honor unsubscribes within 10 days (legal requirement)

---

## 10. Launch Plan

### Week 1: Setup
- Create MailerLite account
- Design email template
- Write welcome sequence (4 emails)
- Create signup forms

### Week 2: Integration
- Add forms to website
- Connect Stripe
- Set up abandoned cart tracking
- Test all automations

### Week 3: Pre-Launch List Building
- Announce coming soon on social
- Personal outreach to contacts
- Goal: 50-100 subscribers before store launch

### Week 4: Launch
- Send "We're live" email to list
- Monitor metrics daily for first week
- Adjust based on performance

### Ongoing
- Send 2-4 emails per month
- Review metrics weekly
- A/B test subject lines monthly
- Clean list quarterly (remove disengaged)
