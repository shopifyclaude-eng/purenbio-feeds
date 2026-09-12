#!/usr/bin/env python3
"""
Pure n' Bio — Meta supplemental feed generator.
Reads Shopify (products, Arabic translations, market prices, stock per warehouse)
and writes CSVs that Meta fetches as supplemental feeds:
  docs/ar.csv  language feed (Arabic titles/descriptions, /ar-ae/ links)
  docs/ae.csv  country feed UAE  (AED price, Abu Dhabi stock, /en-ae/ links)
  docs/sa.csv  country feed Saudi (SAR price, Riyadh stock, root links) — only if ENABLE_SA=1
Run hourly by GitHub Actions. No manual steps.
"""
import csv, html, os, re, sys, time
import urllib.request, json

STORE   = os.environ["SHOPIFY_STORE"]          # e.g. lily-n-coco.myshopify.com
TOKEN   = os.environ["SHOPIFY_TOKEN"]          # Admin API access token (custom app)
API_VER = os.environ.get("SHOPIFY_API_VERSION", "2025-07")
DOMAIN  = "https://purenbio.com"
OUT     = "docs"

COUNTRIES = {
    # code: (currency, location gid, link prefix, enabled)
    "AE": ("AED", "gid://shopify/Location/114713854299", "/en-ae", True),
    "SA": ("SAR", "gid://shopify/Location/65014661259",  "",       os.environ.get("ENABLE_SA") == "1"),
}
AR_LINK_PREFIX = "/ar-ae"   # Arabic landing page for the UAE market

QUERY = """
query($after: String) {
  products(first: 50, after: $after, query: "status:active") {
    pageInfo { hasNextPage endCursor }
    nodes {
      handle
      translations(locale: "ar") { key value }
      variants(first: 100) {
        nodes {
          legacyResourceId
          title
          priceAE: contextualPricing(context: {country: AE}) { price { amount currencyCode } }
          priceSA: contextualPricing(context: {country: SA}) { price { amount currencyCode } }
          inventoryItem {
            invAE: inventoryLevel(locationId: "%s") { quantities(names: ["available"]) { quantity } }
            invSA: inventoryLevel(locationId: "%s") { quantities(names: ["available"]) { quantity } }
          }
        }
      }
    }
  }
}
""" % (COUNTRIES["AE"][1], COUNTRIES["SA"][1])

def gql(query, variables):
    req = urllib.request.Request(
        f"https://{STORE}/admin/api/{API_VER}/graphql.json",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Content-Type": "application/json", "X-Shopify-Access-Token": TOKEN},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            if "errors" in data and not data.get("data"):
                raise RuntimeError(data["errors"])
            return data["data"]
        except Exception as e:
            if attempt == 4: raise
            time.sleep(2 ** attempt)

def strip_html(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s or "", flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()[:5000]

def qty(level):
    try:
        return level["quantities"][0]["quantity"]
    except (TypeError, KeyError, IndexError):
        return 0   # not stocked at this location => out of stock there

def main():
    ar_rows, country_rows = [], {c: [] for c, v in COUNTRIES.items() if v[3]}
    after, n_products = None, 0
    while True:
        d = gql(QUERY, {"after": after})
        page = d["products"]
        for p in page["nodes"]:
            n_products += 1
            tr = {t["key"]: t["value"] for t in p["translations"]}
            ar_title, ar_desc = tr.get("title"), strip_html(tr.get("body_html"))
            for v in p["variants"]["nodes"]:
                vid = v["legacyResourceId"]
                shade = "" if v["title"] in ("Default Title", None) else f" – {v['title']}"
                if ar_title:
                    ar_rows.append({
                        "id": vid, "override": "ar",
                        "title": (ar_title.strip() + shade)[:150],
                        "description": ar_desc,
                        "link": f"{DOMAIN}{AR_LINK_PREFIX}/products/{p['handle']}?variant={vid}",
                    })
                for code, (cur, _loc, prefix, enabled) in COUNTRIES.items():
                    if not enabled: continue
                    price = v[f"price{code}"]["price"]
                    q = qty(v["inventoryItem"][f"inv{code}"])
                    country_rows[code].append({
                        "id": vid, "override": code,
                        "price": f"{float(price['amount']):.2f} {price['currencyCode']}",
                        "availability": "in stock" if q > 0 else "out of stock",
                        "link": f"{DOMAIN}{prefix}/products/{p['handle']}?variant={vid}",
                    })
        if not page["pageInfo"]["hasNextPage"]: break
        after = page["pageInfo"]["endCursor"]

    os.makedirs(OUT, exist_ok=True)
    def write(name, rows, cols):
        with open(f"{OUT}/{name}", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL)
            w.writeheader(); w.writerows(rows)
        print(f"{name}: {len(rows)} rows")
    write("ar.csv", ar_rows, ["id", "override", "title", "description", "link"])
    for code, rows in country_rows.items():
        write(f"{code.lower()}.csv", rows, ["id", "override", "price", "availability", "link"])
    print(f"products scanned: {n_products}")
    if not ar_rows: sys.exit("No Arabic rows produced — check translations/scopes")

if __name__ == "__main__":
    main()
