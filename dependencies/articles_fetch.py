from fastapi import Request, HTTPException, status
from sqlmodel import select
from uuid import UUID
from database import get_session
from model.tool_model import Article, DraftArticle, PublishedArticle, CommunityArticle

'''
Drafts - get all the articles which are written but not published yet.

Published articles - get all the published articles by the current user

Community articles - get all the articles published by all the users which are made public.
'''

''' 
First get the meta data of the article.
get the below fields for every article:
    title, subtitle, 
    get these fields for published articles: author, published date()
'''

def get_drafted_articles_meta(request: Request) -> list[DraftArticle]:
    user_id = request.get("user_id", None)
    user_id = None if user_id is None else UUID(user_id) 
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="user should be logged in to be able to access their drafts")
    session = next(get_session())
    articles = session.exec(
        select(Article)
        .where(Article.author_id == user_id)
        .where(Article.is_public == False)
    ).all()
    drafts = [DraftArticle.model_validate(article) for article in articles]
    return drafts

def get_published_articles_meta(request: Request) -> list[PublishedArticle]:
    user_id = request.get("user_id", None)
    user_id = None if user_id is None else UUID(user_id) 
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="user should be logged in to be able to access their drafts")
    session = next(get_session())
    articles = session.exec(
        select(Article)
        .where(Article.author_id == user_id)
        .where(Article.is_public == True)
    ).all()
    published_articles = [PublishedArticle.model_validate(article) for article in articles]
    return published_articles

def get_community_articles_meta(request: Request) -> list[CommunityArticle]:
    session = next(get_session())
    articles = session.exec(
        select(Article)
        .where(Article.is_public == True)
    ).all()
    community_articles = [CommunityArticle.model_validate(article) for article in articles]
    return community_articles 

