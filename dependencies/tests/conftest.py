import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from dotenv import load_dotenv
import os
import json
from sqlalchemy.exc import IntegrityError
import random
import uuid
from typing import Callable, Tuple
from editorjs_basemodel import Block
from dependencies.editorjs_data_store import add_code_tool_data, add_header_tool_data, add_list_tool_data, add_paragraph_tool_data, add_quote_tool_data, add_table_tool_data, add_tool_md, tool_name_cls_map
from model import tool_model, table_tool_model


load_dotenv()

TEST_DATA_FILE = os.getenv("TEST_DATA_FILE")

@pytest.fixture(name="session", scope="session")
def get_session():
    sqlite_url = "sqlite:///testing.db"
    engine = create_engine(sqlite_url)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session", name="usr_tbl")
def create_user_tbl_ifnexists(session: Session):
    from model.tool_model import User
    print(f"test data file: {TEST_DATA_FILE}")
    with open(TEST_DATA_FILE, 'r') as f:
        test_data = json.load(f)
        users = test_data["users"]

    for user in users:
        try:
            u = User(
                username= user["username"],
                email= user["email"]
            )
            session.add(u)
            session.commit()
        except IntegrityError:
            session.rollback()
    return session


@pytest.fixture(scope="session", name= "tool_tbl")
def create_tool_tbl_ifnexists(usr_tbl: Session):
    from model.tool_model import Tool
    with open(TEST_DATA_FILE, 'r') as f:
        test_data = json.load(f)
        tools = test_data["tools"]
    
    for tool in tools:
        try:
            t = Tool(
                name= tool["name"],
                class_name= tool["class_name"]
            )
            usr_tbl.add(t)
            usr_tbl.commit()
        except IntegrityError:
            usr_tbl.rollback()
    return usr_tbl

    
@pytest.fixture(scope="session", name="article_tbl")
def create_article_tbl_ifnexists(tool_tbl: Session):
    from model.tool_model import Article
    from model.tool_model import User
    authors = tool_tbl.exec(
        select(User)
    ).all()
    with open(TEST_DATA_FILE, 'r') as f:
        test_data = json.load(f)
        articles = test_data["articles"]
    
    for article in articles:
        author = random.choice(authors)
        try:
            a = Article(
                title= article["title"],
                subtitle= article["subtitle"],
                author_id= author.id
            )
            tool_tbl.add(a)
            tool_tbl.commit()
        except IntegrityError:
            tool_tbl.rollback()
    return tool_tbl


@pytest.fixture(scope="session", name="ready_session")
def run_tbl_setup(article_tbl: Session):
    return article_tbl


@pytest.fixture(name="insertion_data_and_func")
def get_insertion_data(request) -> Tuple[Block, 
                                           Callable[
                                               [Session, Block, uuid.UUID], 
                                               Tuple[Session,table_tool_model.TableTool]
                                               ]
]:
    tool_name = request.param
    with open(TEST_DATA_FILE, "r") as f:
        data = json.load(f)
        test_data = data["tests"]["insertion-test-data"]
        tool_data = test_data[f"{tool_name}-data"]
    # del tool_data["id"]

    # print(tool_data)
    block = Block.model_validate(tool_data)
    # with open("test_log", "a+") as f:
    #     f.write(f"BLOCK TYPE: {type(block)}\nBLOCK DATA: {block}\n\n")
    func_map = {
        "table": add_table_tool_data,
        "code": add_code_tool_data,
        "paragraph": add_paragraph_tool_data,
        "header": add_header_tool_data,
        "quote": add_quote_tool_data,
        "list": add_list_tool_data
    }
    if "list" in tool_name:
        return (block, func_map["list"])
    return (block, func_map[tool_name])


@pytest.fixture(name="article_id")
def get_random_article_id(ready_session: Session) -> uuid.UUID:
    # since the article creation and user management logic
    # has not been implemented yet. We will just return 
    # a random article id from the db for testing purpose.
    articles = ready_session.exec(
        select(
            tool_model.Article
        )
    ).all()
    rand_article = random.choice(articles)
    return rand_article.id


@pytest.fixture(name="insertion_result")
def call_insertion_funcs(ready_session: Session, 
                        insertion_data_and_func: Tuple[Block, 
                                           Callable[
                                               [Session, Block, uuid.UUID], 
                                               Tuple[Session,table_tool_model.TableTool]
                                               ]
                                ],
                                article_id: uuid.UUID):
    # this function returns the saved 
    block = insertion_data_and_func[0]
    add_func = insertion_data_and_func[1]
    # article_id = get_random_article_id(ready_session)
    session, tool_md = add_tool_md(
        session=ready_session,
        block= block,
        article_id= article_id
    )
    session, tool_data_model = add_func(ready_session, block, tool_md.id)
    tool_cls = tool_name_cls_map[block.type]
    td_model = session.exec(
        select(tool_cls)
        .where(tool_cls.tool_md_id == tool_md.id)
    ).one()
    return (tool_data_model, td_model)
    # assert td_model == tool_data_model, f"The model of class {str(tool_cls)} has not been created"
