# purenbio-feeds — Meta supplemental feeds (auto)

Hourly: Shopify → `docs/ar.csv` (Arabic), `docs/ae.csv` (UAE / AED), `docs/sa.csv` (Saudi, when enabled) → GitHub Pages → Meta fetches.

## One-time setup
1. Shopify app — Shopify admin → Settings → Apps and sales channels → Develop apps (opens the Dev Dashboard) → Create app → Start from Dev Dashboard →
   Create version: scopes read_products, read_inventory, read_locations, read_translations, read_markets, read_locales, "Embed app in Shopify admin" unticked → Release →
   Home → Install app on the store. Then Settings → Credentials: copy the Client ID and the Client secret.
   (Shopify no longer issues a permanent Admin API token; the workflow exchanges these credentials for a 24 h token on every run.)
2. GitHub — Settings → Secrets and variables → Actions:
   Secret SHOPIFY_STORE = lily-n-coco.myshopify.com · Secret SHOPIFY_CLIENT_ID · Secret SHOPIFY_CLIENT_SECRET (both from step 1) · Variable ENABLE_SA = 0
   (set ENABLE_SA=1 the day the Riyadh warehouse fulfils online orders)
3. GitHub Pages — Settings → Pages → Deploy from a branch → main / /docs.
   Feed URLs: https://<owner>.github.io/purenbio-feeds/ar.csv and .../ae.csv
4. Run once — Actions → Build Meta feeds → Run workflow. Check docs/ar.csv has ~370 rows.
5. Meta — catalog 1314599092656927. Commerce Manager's "Add → Country or language data" redirects Shopify-managed
   catalogs to Shopify Markets, so the feeds were set up like this (done 2026-09-13/14):
   - Language feed "Arabic language feed (ar.csv, hourly)": an existing empty language feed was reused → Settings →
     Language fields: Title, Description, Link → Replace schedule: hourly, URL .../ar.csv.
     The override value must be the Facebook locale `ar_AR` (`ar` and `ar_XX` are rejected as "Override value isn't supported").
     The catalog's default language (Settings → Localization → Global) must be English, not Arabic, or every Arabic row is rejected.
   - Country feed "UAE country feed (ae.csv, hourly)": created via Graph API with a system-user token
     (Business Settings → System users → hanadi → app purenbio-feeds → catalog_management + business_management):
     POST /v23.0/1314599092656927/product_feeds  name=…  override_type=COUNTRY  schedule={"interval":"HOURLY","url":".../ae.csv"}
     Meta auto-detected the country fields (ID, Price, Availability, Link). Revoke the token afterwards; the schedule keeps running.
   - (later) Saudi country feed → same API call with .../sa.csv. Caveat: Saudi Arabia is the catalog's default country;
     check that Meta accepts an override for the default country before relying on sa.csv.

## Do NOT
- Turn off the Shopify "Facebook & Instagram" channel — it is the primary feed these files sit on top of.
- Put the token in the code. Secrets only.
