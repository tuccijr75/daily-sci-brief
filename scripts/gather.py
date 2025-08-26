import json, hashlib, time, re, os, textwrap
from datetime import datetime, timedelta, timezone
import feedparser, tldextract
from bs4 import BeautifulSoup

TODAY = datetime.now(timezone.utc)
SINCE = TODAY - timedelta(days=2)

FEEDS = [
  "http://export.arxiv.org/rss/cs.AI",
  "http://export.arxiv.org/rss/cs.LG",
  "http://export.arxiv.org/rss/cs.CV",
  "http://export.arxiv.org/rss/stat.ML",
  "https://www.biorxiv.org/rss/latest.xml",
  "https://www.medrxiv.org/rss/latest.xml",
  "https://www.nature.com/subjects/artificial-intelligence.rss",
  "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sci",
  "https://spectrum.ieee.org/feed",
  "https://www.technologyreview.com/feed/",
  "https://ai.googleblog.com/atom.xml",
  "https://openai.com/blog/rss.xml",
  "https://deepmind.google/discover.xml"
]

SIG_RE = re.compile("|".join([
  r"state[-\s]?of[-\s]?the[-\s]?art|\bSOTA\b",
  r"breakthrough|groundbreaking|human[-\s]?level",
  r"benchmark|surpass(?:es|ed)?",
  r"parameter[-\s]?efficient|distillation|RLHF|RAG|agent",
  r"clinical trial|phase I|phase II|FDA",
  r"semiconductor|chip|wafer|EUV|lithography|materials"
]), re.I)

def strip_html(text):
  return " ".join(BeautifulSoup(text or "", "html.parser").get_text(" ").split())

def norm(entry, feed_url):
  link = entry.get("link") or entry.get("id") or ""
  title = (entry.get("title") or "").strip()
  summary = strip_html(entry.get("summary") or entry.get("description") or "")
  ts = None
  for k in ("published_parsed","updated_parsed"):
    if getattr(entry, k, None): ts = time.mktime(getattr(entry, k)); break
  domain = tldextract.extract(link).registered_domain or tldextract.extract(feed_url).registered_domain
  uid = hashlib.sha1((link or title).encode("utf-8")).hexdigest()
  return {
    "id": uid,
    "title": title,
    "link": link,
    "summary_raw": summary[:2000],
    "source_domain": domain,
    "published_ts": int(ts) if ts else None
  }

def score(it):
  s = 0
  src = it.get("source_domain","")
  if any(k in src for k in ["nature.com","science.org","cell.com","ieee.org","technologyreview.com"]): s += 3
  if any(k in src for k in ["arxiv.org","biorxiv.org","medrxiv.org"]): s += 2
  if SIG_RE.search(it["title"]) or SIG_RE.search(it["summary_raw"]): s += 2
  ts = it.get("published_ts")
  if ts:
    ageh = (TODAY - datetime.fromtimestamp(ts, tz=timezone.utc)).total_seconds()/3600
    s += 2 if ageh <= 24 else (1 if ageh <= 48 else 0)
  return s

def tagger(text):
  t = text.lower()
  if any(k in t for k in ["protein","genome","biolog","neuro","drug","medical","clinical"]): return "Bio/Health"
  if any(k in t for k in ["chip","semiconductor","wafer","lithograph","transistor","photonic","materials"]): return "Chips/Materials"
  if any(k in t for k in ["space","astronom","nasa","jwst","telescope","mars"]): return "Space"
  if any(k in t for k in ["robot","autonom","rl ","control","embodied"]): return "Robotics"
  if any(k in t for k in ["ai","machine learning","deep learning","transformer","llm","diffusion","agent"]): return "AI/ML"
  return "General Tech/Science"

# ultra-simple extractive summarizer (no external API required)
def summarize(text, max_sent=2):
  sents = re.split(r'(?<=[.!?])\s+', text.strip())
  if not sents: return ""
  # prefer sentences containing signal words
  keyed = sorted(sents, key=lambda s: -len(re.findall(SIG_RE, s)))
  # fallback: take the first ones
  chosen = (keyed[:max_sent] if any(re.findall(SIG_RE, text)) else sents[:max_sent])
  return " ".join(chosen)[:480]

def bullets(title, text):
  t = (title + " " + text).lower()
  why_new = "New method/benchmark" if re.search(r"benchmark|state[-\s]?of[-\s]?the[-\s]?art|sota|surpass", t) else \
            "Fresh results/preprint"
  why_matters = "Practical impact likely" if re.search(r"chip|clinical|industry|production|deployment", t) else \
                "Research significance"
  caveats = "Preprint — not peer reviewed" if re.search(r"arxiv|biorxiv|medrxiv", t) else "Check replication/details"
  return why_new, why_matters, caveats

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

  # de-dupe by (domain,title)
  seen, uniq = set(), []
  for it in items:
    key = (it["source_domain"], it["title"].lower())
    if key in seen: 
      continue
    seen.add(key)
    it["score"] = score(it)
    it["tag"] = tagger(it["title"] + " " + it["summary_raw"])
    it["summary"] = summarize(it["summary_raw"] or it["title"])
    wnew, wmat, cav = bullets(it["title"], it["summary_raw"])
    it["why_new"], it["why_matters"], it["caveats"] = wnew, wmat, cav
    uniq.append(it)

  uniq.sort(key=lambda x: (x["score"], x.get("published_ts") or 0), reverse=True)
  top = uniq[:30]

  # group by category for easier UI
  groups = {}
  for it in top:
    groups.setdefault(it["tag"], []).append(it)

  os.makedirs("docs", exist_ok=True)
  out = {
    "generated_at": TODAY.isoformat(),
    "count": len(top),
    "groups": [
      {"category": cat, "items": groups[cat]} 
      for cat in sorted(groups.keys(), key=lambda c: {"AI/ML":0,"Chips/Materials":1,"Robotics":2,"Bio/Health":3,"Space":4}.get(c,5))
    ]
  }
  with open("docs/daily.json","w",encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
  main()
