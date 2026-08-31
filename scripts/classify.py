#!/usr/bin/env python3
r"""Deterministic page-type classifier + URL normalization used in this study.

Frozen codebook (applied uniformly to every page, no manual overrides):
  listicle          := page title matches /(top|best|\d+\s*(best|top)|推荐|十强|排名)/i
                       AND page mentions >= 3 distinct entities from LEXICON
  self_listicle     := listicle AND alnum(publisher domain stem) is a substring of
                       alnum(any mentioned entity) or vice versa
  third_party_listicle := listicle, not self
  directory_or_media   := registrable domain in DIRECTORY_DOMAINS
  vendor_service_page  := everything else fetched
  (retrieval_status is reported separately; unfetched pages get no page_type)

Known limitation: LEXICON covers GEO-marketing entities observed in this case;
pages from the geospatial/GIS semantic cluster (e.g. flypix.ai's self-ranked
geospatial list) are typed vendor_service_page because their entities are out
of lexicon. Stated in the paper.

URL tiers: raw string -> minus utm_* params (T1) -> minus trailing slash (T2).
All uniqueness/overlap stats in the paper use T2 ("page") unless stated.
"""
import re, json, sys, hashlib, os
LEXICON=["OOm","First Page","Impossible Marketing","Hashmeta","Performance Marketing Lab","Stridec",
"MediaPlus","AI Studio","2Stallions","MediaOne","Canlah","CANLAH","GenOptima","OC Digital","PurpleClick",
"Digitrio","Brew Interactive","Construct Digital","Single Grain","Tenten","Esri","MediaTropy","Awebstar",
"Synscribe","Best Marketing","Kaliber","NEO360","Salween","Digital Business Lab"]
DIRECTORY_DOMAINS={"facebook.com","instagram.com","finance.ifeng.com","agencies.semrush.com",
"designrush.com","ensun.io","tracxn.com","digitalagencynetwork.com","resource.geospatialworld.net"}
alnum=lambda s: re.sub(r"[^a-z0-9]","",s.lower())
def t1(url): return re.sub(r"\?utm_[^#]*","",url)
def t2(url): return t1(url).rstrip("/")
def classify(url, dossier, retrieval_status="fetched"):
    # The codebook says unfetched pages get no page_type. In this dataset that already
    # holds without this line — all 3 unfetched rows happen to have ok=false dossiers —
    # so the guard changes no published value (verified: 116/116 either way). It is here
    # because the coincidence is not a guarantee: page_dossiers.json is keyed by URL, and
    # a URL one engine failed to fetch can carry ok=true from another engine that did.
    # Stating the rule in code rather than only in the docstring keeps the codebook true
    # for anyone who extends this data.
    if retrieval_status != "fetched": return None
    if not dossier.get("ok"): return None
    dom=url.split("/")[2].replace("www.","")
    title=dossier.get("title","")
    mentions=dossier.get("mentions",[])
    lex=[m for m in mentions if any(alnum(x) in alnum(m) or alnum(m) in alnum(x) for x in LEXICON)]
    listicle=bool(re.search(r"(top|best|\d+\s*(best|top)|推荐|十强|排名)",title,re.I)) and len(lex)>=3
    if listicle:
        stem=alnum(dom.split(".")[0])
        selfr=any(stem in alnum(m) or alnum(m) in stem for m in mentions if alnum(m))
        return "self_listicle" if selfr else "third_party_listicle"
    if dom in DIRECTORY_DOMAINS or dom.lstrip("www.") in DIRECTORY_DOMAINS: return "directory_or_media"
    return "vendor_service_page"


def _reproduce(base):
    """Re-derive every page_type in sources.csv from page_dossiers.json and diff.

    Offline and deterministic: no keys, no network, no cost. This is the half of the
    study that MUST come out bit-identical for everyone. (The capture half cannot —
    engines change their answers; that instability is the finding, not a defect.)
    """
    src=os.path.join(base,"data","sources.csv")
    dos=os.path.join(base,"data","page_dossiers.json")
    with open(dos,encoding="utf-8") as fh: dossiers=json.load(fh)
    import csv
    agree=disagree=0; misses=[]
    with open(src,encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            # page_dossiers.json is keyed by the RAW url (trailing slash intact),
            # while sources.csv also carries the T2-normalized form. Try raw first,
            # then the normalized key, then T2 of either — matching on the wrong one
            # silently yields an empty dossier and a fake "disagreement".
            raw=row["url_raw"]; norm=row["url_page_normalized"] or raw
            dossier=next((dossiers[k] for k in (raw,norm,t2(raw),t2(norm)) if k in dossiers),{})
            got=classify(norm,dossier,row.get("retrieval_status","fetched")) or ""
            if got==(row.get("page_type") or ""): agree+=1
            else:
                disagree+=1
                misses.append((row["engine"],url,row.get("page_type",""),got))
    print(f"page_type reproduced: {agree} agree / {disagree} disagree  (expected 116 / 0)")
    for m in misses: print("  MISMATCH engine=%s url=%s published=%r recomputed=%r"%m)
    return 0 if disagree==0 else 1


if __name__=="__main__":
    sys.exit(_reproduce(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
