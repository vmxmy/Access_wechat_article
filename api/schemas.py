"""
Pydantic 请求/响应模型
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional


class ArticleRequest(BaseModel):
    """文章获取请求"""
    url: str


class ArticleData(BaseModel):
    """文章数据"""
    title: str
    author: str
    nickname: str
    create_time: str
    content_html: str
    content_text: list[str]
    images: list[str]
    article_link: str
    public_main_link: str


class ArticleSuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    data: ArticleData


class ArticleErrorResponse(BaseModel):
    """失败响应"""
    success: bool = False
    error: str
    message: str
