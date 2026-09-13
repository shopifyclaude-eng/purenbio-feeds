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
5. Meta — Commerce Manager → Catalog 1314599092656927 → Data sources → Add → Supplemental feed:
   Language feed → Arabic → URL .../ar.csv → hourly
   Country feed → United Arab Emirates → URL .../ae.csv → hourly
   (later) Country feed → Saudi Arabia → .../sa.csv

## Do NOT
- Turn off the Shopify "Facebook & Instagram" channel — it is the primary feed these files sit on top of.
- Put the token in the code. Secrets only.
