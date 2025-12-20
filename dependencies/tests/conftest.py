import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from dotenv import load_dotenv
import os
import json
from sqlalchemy.exc import IntegrityError
import random
import uuid
from typing import Callable, Tuple, Generator
from editorjs_basemodel import Block
from dependencies.editorjs_data_store import add_tool_md, tool_name_cls_map, func_map, update_func_map
from model import tool_model, table_tool_model


load_dotenv()

TEST_DATA_FILE = os.getenv("TEST_DATA_FILE")

# func_map = {
#         "table": add_table_tool_data,
#         "code": add_code_tool_data,
#         "paragraph": add_paragraph_tool_data,
#         "header": add_header_tool_data,
#         "quote": add_quote_tool_data,
#         "list": add_list_tool_data
#     }

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


# create a fixture to accept a block, 
# 

# case 1: a function to read the json test data and create block items



# update_func_map = {
#     "table": update_table_tool_data,
#     "code": update_code_tool_data,
#     "paragraph": update_paragraph_tool_data,
#     "header": update_header_tool_data,
#     "quote": update_quote_tool_data,
#     "list": update_list_tool_data
# }

""" 
using the blocks from the above function
first save the first block's data in db
now update the tool data in the db 
using the other block's data and return the newly
created ToolDataModel object.
"""




# case 2: a function to read the json test data and create block items

# perform the same steps as above for case 2
# @pytest.fixture(name="case2_block")
# def get_test_blocks_case2(request) -> Block:
#     tool_name = request.param
#     with open(TEST_DATA_FILE, 'r') as f:
#         data = json.load(f)
#         updation_td = data["tests"]["updation-test-data"]["case_2_tests"] # updation test data
#         tool_td = updation_td[f"{tool_name}-data"]
#     return Block.model_validate(tool_td)


@pytest.fixture(name="case2_blocks")
def get_test_blocks_case2(request) -> list[Block]:
    tn = request.param
    tool_names = ["table","code","paragraph","header","quote", "unordered-list", "ordered-list", "checklist"]
    tool_td_ls = [] # tool test data list
    with open(TEST_DATA_FILE, 'r') as f:
        data = json.load(f)
        updation_td = data["tests"]["updation-test-data"]["case_2_tests"] # updation test data

    tool_td = updation_td[f"{tn}-data"]
    block = Block.model_validate(tool_td)
    block.id = str(uuid.uuid4())
    tool_td_ls.append(block)

    tool_names = [tname for tname in tool_names  if tname != tn]

    for tool_name in tool_names:
        tool_td = updation_td[f"{tool_name}-data"]
        block = Block.model_validate(tool_td)
        block.id = str(uuid.uuid4())
        tool_td_ls.append(block)
    
    # first element in the list is the passed tool name 
    # block data and the other data is except the first one.
    # create the db obj for first one, and update the db using the other records
    return tool_td_ls 


@pytest.fixture(name="case2_updated_tools")
def updated_tools(case2_blocks: list[Block],
                  ready_session: Session,
                  article_id: uuid.UUID
                  ) -> Callable [
                      [],
                      Generator[
                        Tuple[tool_model.ToolMD, tool_model.ToolDataModel, tool_model.ToolDataModel],
                        None,
                        None
                        ]
                  ]:
    # insert the first record in the list
    first = case2_blocks[0]
    ready_session, tool_md = add_tool_md(ready_session, first, article_id)
    ready_session, db_obj = func_map[first.type](ready_session, first, tool_md.id)
    
    # call the update func on the other records

    def update_tool_gen() -> Generator[
        Tuple[tool_model.ToolMD, tool_model.ToolDataModel, tool_model.ToolDataModel],
        None,
        None
    ]:
        nonlocal ready_session
    
        for block in case2_blocks[1::]:
            ready_session, updated_obj = update_func_map[block.type](ready_session, block, tool_md)
            yield (tool_md, updated_obj, db_obj)

    return update_tool_gen