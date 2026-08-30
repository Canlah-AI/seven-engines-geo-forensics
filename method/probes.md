# Probe specification (2026-08-29, single night, Singapore egress)

Queries (verbatim):
- CN: 新加坡最好的GEO公司 (answer engines received: 新加坡最好的GEO公司？请直接回答并给出推荐名单。)
- EN: best GEO company in Singapore (answer engines received: best GEO company in Singapore? Please answer directly with a recommended list.)

| Engine | Call |
|---|---|
| Google organic | SerpApi `engine=google&google_domain=google.com.sg&gl=sg&hl=zh-cn|en&num=10` — engine returned 9 organic results per language |
| Google AI Mode | SerpApi `engine=google_ai_mode` |
| Gemini grounding | `gemini-2.5-flash` `generateContent` with `tools:[{google_search:{}}]`; sources from `groundingMetadata.groundingChunks`, redirect URLs resolved by following one hop |
| OpenAI web_search | Responses API, `model=gpt-5.5` (snapshot gpt-5.5-2026-04-23), `tools:[{type:web_search}]`; citations from `url_citation` annotations in order |
| ChatGPT consumer | chatgpt.com web app, logged-in Chrome, search enabled; citations read from answer citation chips in order. Personalization NOT ruled out (see paper §2) |
| Exa | POST /search `type=auto, numResults=10` |
| Tavily | POST /search `max_results=10, include_answer=true` |

Fetching: curl with desktop Chrome UA, 25s timeout, same night; 4 bot-walled pages recovered via Exa /contents; 3 URLs never yielded readable content and carry retrieval_status=unfetched.
URL normalization and page-type codebook: `scripts/classify.py` (frozen before analysis of the reclassified data; applied uniformly, no manual overrides).
