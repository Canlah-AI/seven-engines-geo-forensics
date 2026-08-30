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
def classify(url, dossier):
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
