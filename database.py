from sqlmodel import SQLModel, create_engine, Session, select
from model import code_tool_model, header_tool_model, list_tool_models, paragraph_tool_model, quote_tool_model, table_tool_model, tool_model, user_model
from sqlalchemy.exc import IntegrityError
from  fastapi import Depends
from datetime import datetime
from typing import Annotated


sqlite_url = "sqlite:///development.db"

engine = create_engine(sqlite_url, echo= True)

def create_db_tables():
   SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def user_tbl_setup():
    user1 = user_model.User(username="joe pesci", email="joe@gmail.com", hashed_password="hudyejshen", last_login=datetime.now())
    user2 = user_model.User(username="John Doe", email="john@gmail.com", hashed_password="hudyejshen", last_login=datetime.now())
    user3 = user_model.User(username="james", email="james@gmail.com",hashed_password="hudyejshen", last_login=datetime.now())

    with Session(engine) as session:
            try:
                with session.begin_nested():
                    session.add(user1)
                    session.add(user2)
                    session.add(user3)
                    session.commit()
            except IntegrityError:
                pass 
            except Exception as err:
                print(err)

def tool_tbl_setup():
    tool_dict = [
        { "name": "table", "class_name": "Table"},
        { "name": "code", "class_name": "CodeTool"},
        { "name": "paragraph", "class_name": "Paragraph"},
        { "name": "header", "class_name": "Header"},
        { "name": "quote", "class_name": "Quote"},
        { "name": "list", "class_name": "EditorjsList"},
    ]

    for t in tool_dict:
        with Session(engine) as session:
            try: 
                with session.begin_nested():
                    tool = tool_model.Tool(name= t.get("name", None), class_name= t.get("class_name", None))
                    session.add(tool)
                    session.commit()
            except IntegrityError:
                pass

def article_tbl_setup():
    
    with Session(engine) as session:
        
        with session.begin_nested():
            user1, user2 = session.exec(
                select(user_model.User).limit(2)
                ).all()
            article_dicts = [
                {
                    "title": "My first article", 
                    "subtitle": "My experience of writing first article",
                    "author_id": user1.id
                },
                {
                    "title": "Welcome to my publication", 
                    "subtitle": "Welcomming everyone to my publication to make you understand it better",
                    "author_id": user2.id
                }
            ]
        for a in article_dicts:
            article = tool_model.Article(
                title=a.get("title", None), 
                subtitle=a.get("subtitle", None), 
                author_id=a.get("author_id", None)
                )
            try:
                with session.begin_nested():
                    session.add(article)
                    session.commit()
            except IntegrityError:
                pass

def init_db_setup():
    # create all the db tables
    # populate tool tbl
    # populate user tbl
    # populate article tbl
    create_db_tables()
    user_tbl_setup()
    tool_tbl_setup()
    article_tbl_setup()

if __name__ == "__main__":
    init_db_setup()