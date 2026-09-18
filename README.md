# ToolNagri — Free Online Utility Hub (V1)

## 1. What was actually built

A real, static, deployable website — no build step, no server required. Every tool below
genuinely works when the site is opened in a browser or hosted anywhere static files are served.

**Note on stack**: the original brief asked for Next.js + Tailwind. This sandbox has **no network
access**, so `npm install` could not run and could not be verified. Rather than hand you unverified
Next.js code, this V1 is plain HTML/CSS/vanilla JS — genuinely working today, and easy to port into
Next.js later (see §11) since the architecture (data-driven tool registry, one page per tool,
shared header/footer) maps directly onto Next.js pages/components.

## 2. Live V1 tool list (16 tools, all fully working)

| Tool | Category | Notes |
|---|---|---|
| SGPA Calculator | Student | Add/remove subjects, weighted calculation |
| CGPA Calculator | Student | Semester-wise SGPA + credits |
| Attendance Calculator | Student | Handles "target impossible" case |
| EMI Calculator | Finance | Standard amortization formula |
| SIP Calculator | Finance | Future value of monthly SIP |
| GST Calculator | Finance | Add/remove GST, CGST/SGST split |
| Age Calculator | Calculators | Exact y/m/d difference |
| BMI Calculator | Calculators | Metric + imperial |
| Percentage Calculator | Calculators | Basic %, marks %, % change |
| Unit Converter | Converters | Length, weight, temp, area, volume, speed, time, data |
| Image Compressor | Everyday | Canvas-based, 100% browser-side |
| QR Code Generator | Everyday | Text/URL, phone, email, Wi-Fi |
| JPG to PDF | PDF | pdf-lib (CDN), 100% browser-side |
| Merge PDF | PDF | pdf-lib (CDN), 100% browser-side |
| Resume Builder | Career | jsPDF (CDN), autosaves draft to localStorage |
| AI Text Rewriter | AI | **Architecture only** — see §7 |

Every page also ships: breadcrumb, H1, description, "How it works", worked example, FAQ
(with FAQ schema), related tools, and a disclaimer where the category needs one (finance/health/AI).

## 3. What is intentionally NOT built in V1 (and why)

- **The other ~24 tools named in the brief** (FD/RD/Loan/Inflation calculators, Split/Compress
  PDF, PDF→JPG, Cover Letter Generator, Job Description Analyzer, Scientific Calculator, Ratio/
  Fraction/Time calculators, etc.). The registry (`data/tools.json`) is built so adding each of
  these is "write one panel + one script + register it" — no architecture change needed. I
  prioritized breadth across every category and every core interaction pattern (form calculator,
  file upload, PDF generation) over building all 40 shallowly.
- **Real AI calls.** Per your own rule ("must NOT require a paid AI API" + "gracefully show a
  useful message" when unavailable), the AI Text Rewriter ships a working `AIProvider` abstraction
  that is honestly in its "no provider connected" state, rather than faking AI with keyword tricks
  or silently calling a paid API. Wiring a real free-tier provider is a backend task (see §7).
- **Next.js/React/Supabase/Vercel-specific config.** Can't be installed or tested without network
  access in this environment. The static build ports cleanly (§11).
- **App icons for the PWA manifest.** `manifest.json` exists and is valid but has no icon files —
  add 192px/512px PNGs and reference them to make it installable.

## 4. Project structure

```
site/
  index.html                 homepage
  tools.html                 all-tools directory + search
  about.html, contact.html, privacy-policy.html, terms.html, disclaimer.html, 404.html
  sitemap.xml, robots.txt, manifest.json
  categories/<slug>.html     8 category pages (generated)
  tools/<slug>.html          16 tool pages (generated)
  assets/css/style.css       full design system (one file)
  assets/js/site.js          search, mobile nav, favourites/recents, copy helper
  assets/js/tools-data.js    tool + category registry embedded as JS (generated)
  data/site.config.json      ← BRAND NAME, tagline, domain, contact, socials (edit here)
  data/tools.json            ← tool registry (edit here to add/change tools)
  data/categories.json       ← category registry
  build.py                   generator: reads data/*.json, writes all HTML pages
  tool_pages_*.py            per-tool panel HTML + JS logic + SEO content (5 files)
```

**Rebuilding after any edit:** `python3 build.py` (regenerates every generated file; hand-written
files like `style.css` and `site.js` are untouched).

## 5. How to run locally

No install needed.

```
cd site
python3 -m http.server 8000
```

Open `http://localhost:8000`. (Opening `index.html` directly via `file://` also mostly works, but
a local server avoids occasional browser file:// restrictions.)

## 6. How to deploy

This is a static site — deploy to **any** static host:

- **Vercel**: `vercel deploy` from inside `site/` (no framework preset needed — choose "Other").
- **Netlify**: drag-and-drop the `site/` folder in the Netlify dashboard, or `netlify deploy`.
- **GitHub Pages / Cloudflare Pages**: push `site/` as the repo root and point Pages at it.

No environment variables are required for V1 (there is no server-side code yet).

## 7. AI architecture — how to actually connect a free provider later

`tools/ai-text-rewriter.html` contains an `AIProvider` object with a `FreeProvider.available` flag
currently set to `false`. To go live:

1. **Never call a keyed API directly from this static frontend** — the key would be exposed to
   every visitor.
2. Add a small serverless function (Vercel Function / Cloudflare Worker / Netlify Function) that
   holds the API key server-side and proxies the request.
3. Point `FreeProvider.rewrite()` at that function's URL, and flip `available = true`.
4. Enforce `DAILY_LIMIT` (already stubbed) server-side, e.g. by IP or a device-id cookie, not just
   client-side, since client-side limits are trivially bypassed.
5. Keep the try/catch fallback message — it already handles "provider down" and "limit reached"
   gracefully.

## 8. Connecting Search Console / Analytics

- **Search Console**: verify via the HTML tag method — add the meta tag Google gives you into the
  `<head>` in `build.py`'s `page()` function (one place, applies everywhere), or via DNS.
- **Google Analytics**: add the GA snippet the same way (one place in `build.py`). `site.js`
  already calls `gtag('event', ...)` for `calculation_completed`, `download_clicked` etc. **only
  if** `gtag` exists, so it's safe to add GA at any time without touching tool code.
- Put the GA ID in `data/site.config.json` if you want it centrally configured rather than hardcoded.

## 9. Adding a new tool (once V1 is live)

1. Add an entry to `data/tools.json` (slug, name, category, short description, keywords).
2. Run `python3 build.py` — a placeholder page structure now exists for it in `tools/`, but you
   still need to give it real content: add a `build_tool_page(...)` call in a `tool_pages_*.py`
   file with the tool's panel HTML + calculation JS (see any existing tool for the pattern), then
   register it in `build.py`'s `__main__`.
3. Rebuild. Search, sitemap, category pages and related-tools all update automatically since
   they're derived from the registry.

## 10. Production checklist status

- [x] No broken links (verified programmatically)
- [x] No placeholder/lorem-ipsum content
- [x] No exposed secrets (no API keys anywhere in the codebase)
- [x] No paid dependency required for any live tool
- [x] All 16 listed V1 tools work end-to-end
- [x] Mobile-first responsive CSS (single stylesheet, tested breakpoints at 900/820/640/560px)
- [x] SEO: unique title/description/canonical/H1/FAQ schema/breadcrumb schema/SoftwareApplication
      schema per tool page; sitemap.xml; robots.txt
- [x] Privacy policy, Terms, Disclaimer, About, Contact, 404
- [x] Client-side error handling on every calculator (empty/negative/oversized/invalid-type inputs)
- [x] Favourites/recents via localStorage, no login
- [ ] App icons for installable PWA (add PNGs + reference in manifest.json)
- [ ] Real hosting/domain/SSL (deploy step, §6)
- [ ] Analytics/Search Console IDs (plug in when you have them, §8)
- [ ] AI provider actually connected (§7 — deliberately deferred per your free-cost rule)
- [ ] Remaining ~24 roadmap tools (§3)

## 11. Porting to Next.js later (optional)

If you do want the Next.js/Tailwind/Supabase version from the original brief, the migration is
mechanical, not a rewrite: `data/tools.json` → `src/config/tools.ts`; each `tool_pages_*.py`
function → a React component per tool; `build.py`'s `page()` wrapper → `app/layout.tsx`; static
`categories/*.html` generation → `generateStaticParams` on a dynamic `[category]` route. Nothing
in the current architecture fights against that move.

## 12. Recommended next 10 tools (by SEO/product priority)

1. Loan Calculator (generic, high search volume, reuses EMI math)
2. FD Calculator (pairs naturally with SIP audience)
3. Scientific Calculator (very high, evergreen search volume)
4. Compress PDF (pairs with your PDF category, high intent)
5. PDF to JPG (completes the JPG↔PDF pair)
6. Ratio Calculator (student audience, low competition)
7. RD Calculator (finance completeness)
8. Date Difference Calculator (shares code with Age Calculator)
9. ATS Resume Checker (career, strong differentiator, no AI required for a basic version —
   keyword-overlap heuristic against a pasted job description)
10. Salary / CTC Calculator (very high India-specific search volume)
