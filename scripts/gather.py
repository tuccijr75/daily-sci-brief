import json, hashlib, time, re, os
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
  r"benchmark|surpass(es|ed)?",
  r"parameter[-\s]?efficient|distillation|RLHF|RAG|agent",
  r"clinical trial|phase I|phase II|FDA",
  r"semiconductor|chip|wafer|EUV|lithography|materials"
]), re.I)

def strip_html(text):
  return " ".join(BeautifulSoup(text or "", "html.parser").get_text(" ").split())

def score(it):
  s = 0
  src = it.get("source_domain","")
  if any(k in src for k in ["nature.com","science.org","cell.com","ieee.org","technologyreview.com"]): s += 3
  if any(k in src for k in ["arxiv.org","biorxiv.org","medrxiv.org"]): s += 2
  if SIG_RE.search(it["title"]) or SIG_RE.search(it["summary"]): s += 2
  ts = it.get("published_ts")
  if ts:
    ageh = (TODAY - datetime.fromtimestamp(ts, tz=timezone.utc)).total_seconds()/3600
    s += 2 if ageh <= 24 else (1 if ageh <= 48 else 0)
  return s

def norm(entry, feed_url):
  link = entry.get("link") or entry.get("id") or ""
  title = (entry.get("title") or "").strip()
  summary = strip_html(entry.get("summary") or entry.get("description") or "")
  ts = None
  for k in ("published_parsed","updated_parsed"):
    if getattr(entry, k, None): ts = time.mktime(getattr(entry, k)); break
  domain = tldextract.extract(link).registered_domain or tldextract.extract(feed_url).registered_domain
  uid = hashlib.sha1(link.encode("utf-8")).hexdigest() if link else hashlib.sha1(title.encode("utf-8")).hexdigest()
  return {"id": uid,"title": title,"link": link,"summary": summary[:800],
          "source_domain": domain,"published_ts": int(ts) if ts else None}

def tagger(text):
  t = text.lower()
  if any(k in t for k in ["protein","genome","biolog","neuro","drug","medical","clinical"]): return "Bio/Health"
  if any(k in t for k in ["chip","semiconductor","wafer","lithograph","transistor","photonic"]): return "Chips/Materials"
  if any(k in t for k in ["space","astronom","nasa","jwst","telescope"]): return "Space"
  if any(k in t for k in ["robot","autonom","rl ","control","embodied"]): return "Robotics"
  if any(k in t for k in ["ai","machine learning","deep learning","transformer","llm","diffusion","agent"]): return "AI/ML"
  return "General Tech/Science"

def main():
  items = []
  for f in FEEDS:
    try:
      d = feedparser.parse(f)
      for e in d.entries:
        it = norm(e, f)
        ts = it.get("published_ts")
        if ts and datetime.fromtimestamp(ts, tz=timezone.utc) < SINCE: continue
        items.append(it)
    except Exception:
      pass
  seen, uniq = set(), []
  for it in items:
    key = (it["source_domain"], it["title"].lower())
    if key in seen: continue
    seen.add(key)
    it["score"] = score(it)
    it["tag"] = tagger(it["title"] + " " + it["summary"])
    uniq.append(it)
  uniq.sort(key=lambda x: (x["score"], x.get("published_ts") or 0), reverse=True)
  top = uniq[:30]
  os.makedirs("docs", exist_ok=True)
  with open("docs/daily.json","w",encoding="utf-8") as f:
    json.dump({"generated_at": datetime.now(timezone.utc).isoformat(), "count": len(top), "items": top}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
  main()
