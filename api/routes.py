"""
API 路由定义
"""
import re
from fastapi import APIRouter
from .schemas import ArticleRequest, ArticleSuccessResponse, ArticleErrorResponse, ArticleData

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.base_spider import BaseSpider

router = APIRouter(prefix="/api", tags=["article"])

spider = BaseSpider()


def extract_images(html_content: str) -> list[str]:
    """从HTML中提取图片链接"""
    pattern = r'https://mmbiz\.qpic\.cn/[^"\'<>\s\\]+(?:\?wx_fmt=[a-zA-Z]+)?'
    matches = re.findall(pattern, html_content)

    images = []
    for url in matches:
        clean_url = url.split('\\')[0].rstrip('&')
        if clean_url not in images:
            images.append(clean_url)
    return images


@router.post("/article", response_model=ArticleSuccessResponse | ArticleErrorResponse)
def fetch_article(request: ArticleRequest):
    """
    获取单篇微信文章内容

    - **url**: 微信文章链接 (永久链接或短链接)
    """
    result = spider.get_an_article(request.url)

    if result['content_flag'] == 0:
        html_content = result.get('content', '')
        if '当前环境异常' in html_content:
            return ArticleErrorResponse(
                error="human_verification",
                message="触发人机验证，请稍后再试或更换IP"
            )
        elif '操作频繁' in html_content:
            return ArticleErrorResponse(
                error="rate_limit",
                message="请求过于频繁，请稍后再试"
            )
        else:
            return ArticleErrorResponse(
                error="unknown",
                message="获取文章失败，可能是纯图片文章或链接无效"
            )

    article_info = spider.format_content(result['content'])
    images = extract_images(result['content'])

    return ArticleSuccessResponse(
        data=ArticleData(
            title=article_info['article_title'],
            author=article_info['author'],
            nickname=article_info['nickname'],
            create_time=article_info['createTime'],
            content_html=result['content'],
            content_text=article_info['format_texts'],
            images=images,
            article_link=article_info['article_link'],
            public_main_link=spider.public_main_link
        )
    )
