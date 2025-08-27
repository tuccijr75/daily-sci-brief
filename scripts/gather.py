import os, re, json, hashlib, time, csv, math, textwrap
from datetime import datetime, timedelta, timezone
import feedparser, tldextract
from bs4 import BeautifulSoup

# --- Load config ---
import yaml
with open("config/sources.yaml", "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

FEEDS = CFG.get("feeds", [])
PEER_DOMAINS = set(CFG.get("peer_review_domains", []))
CATEGORIES = CFG.get("categories", {})

TODAY = datetime.now(timezone.utc)
SINCE = TODAY - timedelta(days=2)

WATCH = []
if os.path.exists("config/watchlist.txt"):
    with open("config/watchlist.txt", "r", encoding="utf-8") as f:
        WATCH = [w.strip().lower() for w in f if w.strip()]

SIG_RE = re.compile("|".join([
  r"state[ -]?of[ -]?the[ -]?art|\bSOTA\b", r"benchmark|surpass|exceed",
  r"human[ -]?level", r"RLHF|RAG|agent", r"clinical trial|phase [I|II|III]",
  r"semiconductor|lithograph|EUV|photonic|materials"
]), re.I)

def strip_html(text): 
    return " ".join(BeautifulSoup(text or "", "html.parser").get_text(" ").split())

def norm(entry, feed_url):
    link = entry.get("link") or entry.get("id") or ""
    title = (entry.get("title") or "").strip()
    summary = strip_html(entry.get("summary") or entry.get("description") or "")
    ts = None
    for k in ("published_parsed","updated_parsed"):
        if getattr(entry, k, None):
            ts = time.mktime(getattr(entry, k))
            break
    domain = tldextract.extract(link).registered_domain or tldextract.extract(feed_url).registered_domain
    uid = hashlib.sha1((link or title).encode("utf-8")).hexdigest()
    return {
        "id": uid, "title": title, "link": link, "summary_raw": summary[:3000],
        "source_domain": domain, "published_ts": int(ts) if ts else None
    }

def tag_category(text):
    t = text.lower()
    for cat, rule in CATEGORIES.items():
        if any(substr in t for substr in rule.get("any", [])):
            return cat
    return "General Tech/Science"

def is_peer_reviewed(domain, link):
    d = (domain or "").lower()
    if any(d.endswith(pd) for pd in PEER_DOMAINS): 
        return True
    # DOI sniff
    if re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", link): 
        return True
    return False

def score(it):
    s = 0
    if is_peer_reviewed(it.get("source_domain",""), it.get("link","")): s += 3
    if "arxiv.org" in it.get("source_domain",""): s += 2
    if SIG_RE.search(it.get("title","")) or SIG_RE.search(it.get("summary_raw","")): s += 2
    ts = it.get("published_ts")
    if ts:
        ageh = (TODAY - datetime.fromtimestamp(ts, tz=timezone.utc)).total_seconds()/3600
        s += 2 if ageh <= 24 else (1 if ageh <= 48 else 0)
    # watchlist boost
    t = (it.get("title","") + " " + it.get("summary_raw","")).lower()
    if any(w in t for w in WATCH): s += 3
    return s

def summarize_extractive(text, max_sent=2):
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    if not sents: return ""
    # prefer sentences with signal terms
    keyed = sorted(sents, key=lambda s: -len(re.findall(SIG_RE, s)))
    chosen = keyed[:max_sent] if any(re.findall(SIG_RE, text)) else sents[:max_sent]
    out = " ".join(chosen).strip()
    return out[:480]

def summarize_llm(title, text):
    key = os.getenv("OPENAI_API_KEY")
    if not key: 
        return None
    try:
        import requests
        prompt = f"Summarize in 2 tight sentences for a science/tech brief. Title: {title}\nContent: {text[:3000]}"
        headers = {"Authorization": f"Bearer {key}", "Content-Type":"application/json"}
        # OpenAI responses format vary by model; using /v1/chat/completions with a safe default
        body = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role":"system","content":"You write crisp, factual, non-hype scientific summaries."},
                {"role":"user","content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 140
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

def main():
    items = []
    for f in FEEDS:
        try:
            d = feedparser.parse(f)
            for e in d.entries:
                it = norm(e, f)
                ts = it.get("published_ts")
                if ts and datetime.fromtimestamp(ts, tz=timezone.utc) < SINCE:
                    continue
                items.append(it)
        except Exception:
            pass

    # dedupe by (title_lower, domain) and by SHA if same link/title
    seen, uniq = set(), []
    for it in items:
        key = (it["title"].strip().lower(), it.get("source_domain",""))
        if key in seen: 
            continue
        seen.add(key)
        uniq.append(it)

    # enrich
    for it in uniq:
        text = f'{it["title"]} {it.get("summary_raw","")}'
        it["tag"] = tag_category(text)
        it["peer_reviewed"] = is_peer_reviewed(it.get("source_domain",""), it.get("link",""))
        it["score"] = score(it)

        # summaries
        llm = summarize_llm(it["title"], it.get("summary_raw",""))
        it["summary"] = llm if llm else summarize_extractive(it.get("summary_raw","") or it["title"])

        # bullets
        t = text.lower()
        it["why_new"]      = "New method/benchmark" if re.search(r"benchmark|sota|state[ -]?of", t) else "Fresh results/preprint"
        it["why_matters"]  = "Practical impact likely" if re.search(r"chip|clinical|industry|deployment|production", t) else "Research significance"
        it["caveats"]      = "Peer-reviewed" if it["peer_reviewed"] else ("Preprint — not peer reviewed" if "arxiv" in it.get("source_domain","") or re.search(r"biorxiv|medrxiv", t) else "Check replication/details")

    uniq.sort(key=lambda x: (x["score"], x.get("published_ts") or 0), reverse=True)
    top = uniq[:60]

    # group
    groups = {}
    for it in top:
        groups.setdefault(it["tag"], []).append(it)

    os.makedirs("docs", exist_ok=True)
    out = {
        "generated_at": TODAY.isoformat(),
        "count": sum(len(v) for v in groups.values()),
        "groups": [{"category": k, "items": v} for k, v in groups.items()]
    }
    with open("docs/daily.json","w",encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # CSV export
    csv_path = "docs/daily.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category","title","link","source","published_ts","score","peer_reviewed","summary"])
        for g in out["groups"]:
            for it in g["items"]:
                w.writerow([g["category"], it["title"], it["link"], it["source_domain"], it.get("published_ts",""), it["score"], it["peer_reviewed"], it["summary"]])

    # RSS export
    feed = []
    feed.append('<?xml version="1.0" encoding="UTF-8"?>')
    feed.append('<rss version="2.0"><channel>')
    feed.append(f"<title>Science & AI Brief</title>")
    feed.append(f"<link>https://{os.getenv('GITHUB_REPOSITORY','').split('/')[0]}.github.io/{os.getenv('GITHUB_REPOSITORY','').split('/')[-1]}/</link>")
    feed.append(f"<description>Auto-curated daily brief</description>")
    feed.append(f"<lastBuildDate>{TODAY.strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>")
    for g in out["groups"]:
        for it in g["items"][:12]:
            pub = ""
            if it.get("published_ts"):
                pub = datetime.fromtimestamp(it["published_ts"], tz=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
            desc = BeautifulSoup(it.get("summary",""), "html.parser").get_text(" ")
            feed.append("<item>")
            feed.append(f"<title><![CDATA[{it['title']}]]></title>")
            feed.append(f"<link>{it['link']}</link>")
            feed.append(f"<guid isPermaLink='false'>{it['id']}</guid>")
            if pub: feed.append(f"<pubDate>{pub}</pubDate>")
            feed.append(f"<category>{g['category']}</category>")
            feed.append(f"<description><![CDATA[{desc}]]></description>")
            feed.append("</item>")
    feed.append("</channel></rss>")
    with open("docs/feed.xml","w",encoding="utf-8") as f:
        f.write("\n".join(feed))

    print(f"✅ Collected {out['count']} items in {len(out['groups'])} groups. CSV+RSS exported.")

if __name__ == "__main__":
    main()