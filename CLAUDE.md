# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

WeChat Official Account article scraper (微信公众号文章爬虫). Extracts article lists, content, and engagement metrics (reads, likes, shares, comments) from WeChat Official Accounts using Fiddler to capture authentication tokens.

## Commands

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
# .\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the interactive CLI
python main.py

# Run the API server
uvicorn api.main:app --reload --port 8000
```

## Architecture

```
api/
├── main.py           # FastAPI application entry
├── routes.py         # POST /api/article endpoint
└── schemas.py        # Pydantic request/response models

src/
├── all_process.py    # AccessWechatArticle - main orchestrator class
├── base_spider.py    # BaseSpider - HTTP requests, article parsing, image download
├── wechat_funcs.py   # ArticleDetail(BaseSpider) - token-based API calls for lists/metrics
├── save_to_excel.py  # SaveToExcel - pandas-based Excel I/O
└── tools.py          # Debug utilities (save_cache)
```

### Data Flow

1. **Token Capture**: User captures WeChat token URL via Fiddler from `mp.weixin.qq.com/mp/profile_ext`
2. **Article List**: `ArticleDetail.whole_article_list()` paginates through `getmsg` API (10 articles/page)
3. **Content Extraction**: `BaseSpider.get_an_article()` fetches HTML, `format_content()` parses with BeautifulSoup
4. **Metrics (optional)**: `ArticleDetail.get_detail_content()` calls `getappmsgext` and `appmsg_comment` APIs

### Key Token Parameters

Extracted from Fiddler-captured URL via `urllib.parse`:
- `__biz` - Official account identifier
- `uin` - User identifier
- `key` - Session key
- `pass_ticket` - Authentication ticket

### Output Files

All saved to `./all_data/公众号----{nickname}/`:
- `文章列表 (article_list).xlsx` - Article metadata
- `文章内容 (article_contents).xlsx` - Full text content
- `文章详情 (article_detiles).xlsx` - Engagement metrics
- `问题链接 (error_links).xlsx` - Failed URLs

### Anti-Ban Mechanisms

- `delay_time()`: 3-7 second random delay between paginated requests
- `delay_short_time()`: 0.1-1.5 second delay between article fetches
- Random User-Agent via `fake_useragent`
- SSL verification disabled for proxy compatibility

## API Endpoint

**POST /api/article**
```json
// Request
{ "url": "https://mp.weixin.qq.com/s/xxx" }

// Success Response
{
  "success": true,
  "data": {
    "title": "文章标题",
    "author": "作者",
    "nickname": "公众号名称",
    "create_time": "2025-01-01 10:30",
    "content_html": "完整HTML",
    "content_text": ["段落1", "段落2"],
    "images": ["https://mmbiz.qpic.cn/..."],
    "article_link": "永久链接",
    "public_main_link": "公众号主页链接"
  }
}

// Error Response
{ "success": false, "error": "human_verification|rate_limit|unknown", "message": "..." }
```

## Dependencies

Core: `requests`, `beautifulsoup4`, `lxml`, `pandas`, `openpyxl`, `jsonpath`, `fake-useragent`
API: `fastapi`, `uvicorn`
