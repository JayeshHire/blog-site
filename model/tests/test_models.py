import code_tool_model, header_tool_model, list_tool_models, paragraph_tool_model, quote_tool_model, table_tool_model, tool_model
from sqlmodel import SQLModel, create_engine, Session, select
import pytest
from sqlalchemy.exc import IntegrityError, PendingRollbackError
import uuid
from typing import Optional


@pytest.fixture(name="session", scope="session")
def create_session():
    sqlite_url = "sqlite:///testing_temp.db"
    # sqlite_url = "sqlite://" # in memory database
    engine = create_engine(sqlite_url)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        

@pytest.fixture(scope="session")
def user_tbl_setup(session: Session):
    user1 = tool_model.User(username="joe pesci", email="joe@gmail.com")
    user2 = tool_model.User(username="John Doe", email="john@gmail.com")
    user3 = tool_model.User(username="james", email="james@gmail.com")

    try:
        session.add(user1)
        session.add(user2)
        session.add(user3)
        session.commit()
    except IntegrityError:
        session.rollback()
        return session
    return session


@pytest.fixture(scope="session")
def tool_tbl_setup(user_tbl_setup: Session):
    tool_dict = [
        { "name": "table", "class_name": "Table"},
        { "name": "code", "class_name": "CodeTool"},
        { "name": "paragraph", "class_name": "Paragraph"},
        { "name": "header", "class_name": "Header"},
        { "name": "quote", "class_name": "Quote"},
        { "name": "List", "class_name": "EditorjsList"},
    ]

    try:
        for t in tool_dict:
            tool = tool_model.Tool(name= t.get("name", None), class_name= t.get("class_name", None))
            user_tbl_setup.add(tool)
            user_tbl_setup.commit()
    except IntegrityError:
        user_tbl_setup.rollback()
        return user_tbl_setup
    return user_tbl_setup


@pytest.fixture(scope="session")
def article_tbl_setup(tool_tbl_setup: Session):
    user1, user2 = tool_tbl_setup.exec(
        select(tool_model.User).limit(2)
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
    try:
        for a in article_dicts:
            article = tool_model.Article(
                title=a.get("title", None), 
                subtitle=a.get("subtitle", None), 
                author_id=a.get("author_id", None)
                )
            tool_tbl_setup.add(article)
            tool_tbl_setup.commit()
    except IntegrityError:
        tool_tbl_setup.rollback()
        return tool_tbl_setup
    return tool_tbl_setup


@pytest.fixture(scope="session", name="init_db_session")
def initialize_db_setup(article_tbl_setup: Session):
    return article_tbl_setup


def test_tool(init_db_session: Session):
    from tool_model import Tool
    tool = init_db_session.get(Tool, 1)
    assert tool.name == "table"
    assert tool.class_name == "Table"


""" 
Creating tests to check if it is possible to
store data inside the db tables as it is received 
from the frontend for every tool.
"""
# for every test tool_id and article_id is required
# hence a fixture for there creation is required
# tool_md object creation

@pytest.fixture(name="created_tool")
def create_tool_in_db(request, init_db_session):
    tool_type = request.param
    # tool_id = init_db_session.exec(
    #     select(tool_model.Tool)
    #     .where(tool_model.Tool.name == data.get("type", None))
    # ).first().id
    def get_data():
        output_data_lst = [
            {
                "type" : "table",
                "id": str(uuid.uuid4()),
                "sequence": 1,
                "data" : {
                    "content" : [ ["Kine", "1 pcs", "100$"], ["Pigs", "3 pcs", "200$"], ["Chickens", "12 pcs", "150$"] ]
                }
            },
            {
                "type" : "code",
                "id": str(uuid.uuid4()),
                "sequence": 1,
                "data" : {
                    "code": "body {\n font-size: 14px;\n line-height: 16px;\n}",
                    "languageCode": "css"
                }
            },
            {
            	"type": "paragraph",
                "id": str(uuid.uuid4()),
                "sequence": 1,
            	"data": {
            		"text": "This is my paragraph. It has some knowledgeable info"
            	}
            },
            {
            	"type": "header",
                "id": str(uuid.uuid4()),
                "sequence": 1,
            	"data": {
            		"text": "I am beginner level programmer",
            		"level": 2
            	}
            },
            {
                "type" : "quote",
                "id": str(uuid.uuid4()),
                "sequence": 1,
                "data" : {
                    "text" : "The unexamined life is not worth living.",
                    "caption" : "Socrates",
                    "alignment" : "left"
                }
            },
            {
            	"type": "list",
                "id": str(uuid.uuid4()),
                "sequence": 1,
            	"data": {
            		"style": "unordered",
            			"items": [
            				{
            					"content": "Apple",
            					"meta": {},
            					"items": [
            						{
            							"content": "red",
            							"meta": {},
            							"items": {}
            						}
            					]
            				}
            			]
            	}
            },
            {
            	"type": "list",
                "id": str(uuid.uuid4()),
                "sequence": 1,
            	"data": {
            		"style": "ordered",
            		"meta": {
            			"start": 2,
            			"counterType": "upper-roman"
            		},
            		"items": [
            			{
            				"content": "Apple",
            				"meta": {},
            				"items": [
            					{
            						"content": "Red",
            						"meta": {},
            						"items": []
            					}
            				]
            			}
            		]
            	}
            },
            {
              "type" : "list",
              "id": str(uuid.uuid4()),
              "sequence": 1,
              "data" : {
                "style": "checklist",
                "items" : [
                  {
                    "content": "Apples",
                    "meta": {
                      "checked": False
                    },
                    "items": [
                      {
                        "content": "Red",
                        "meta": {
                          "checked": True
                        },
                        "items": []
                      },
                    ]
                  },
                ]
              }
            },
        ]
        available_tool_types = (
            "table",
            "code",
            "paragraph",
            "header",
            "quote",
            "list"
        )
        for index, tt in enumerate(available_tool_types):
            if tool_type.lower() == tt:
                return output_data_lst[index]
    
    def get_tool_id():
        tool_id = init_db_session.exec(
            select(tool_model.Tool)
            .where(tool_model.Tool.name == tool_type)
        ).first().id
        return tool_id
    
    def get_article_id():
        article_id = init_db_session.exec(
            select(tool_model.Article).limit(1)
        ).first().id
        return article_id
    
    def get_tool_md_mdl_inst():
        data = get_data()
        article_id = get_article_id()
        tool_id = get_tool_id()
        tool_md = tool_model.ToolMD(
            sequence= data.get("sequence", None),
            block_id = data.get("id", None),
            article_id=article_id,
            tool_id= tool_id
        )
        init_db_session.add(tool_md)
        init_db_session.commit()
        return tool_md 

    def create__table_tool__(data):
        tool_md = get_tool_md_mdl_inst()
        tbl_tool = table_tool_model.TableTool(
            content= data["data"]["content"],
            tool_md_id= tool_md.id
        )
        init_db_session.add(tbl_tool)
        init_db_session.commit()
        return tbl_tool
    
    def create__code_tool__(data):
        tool_md = get_tool_md_mdl_inst()
        code_tool = code_tool_model.CodeTool(
            code= data["data"]["code"],
            language_code= data["data"].get("languageCode", None),
            tool_md_id= tool_md.id
        )
        init_db_session.add(code_tool)
        init_db_session.commit()
        return code_tool

    def create__paragraph_tool__(data):
        tool_md = get_tool_md_mdl_inst()
        paragraph_tool = paragraph_tool_model.ParagraphTool(
            text= data["data"].get("text", None),
            tool_md_id = tool_md.id
        )
        init_db_session.add(paragraph_tool)
        init_db_session.commit()
        return paragraph_tool

    def create__header_tool__(data):
        tool_md = get_tool_md_mdl_inst()
        header_tool = header_tool_model.HeaderTool(
            text= data["data"].get("text", None),
            level= data["data"].get("level", None),
            tool_md_id= tool_md.id
        )
        init_db_session.add(header_tool)
        init_db_session.commit()
        return header_tool

    def create__quote_tool__(data):
        tool_md = get_tool_md_mdl_inst()
        quote_tool = quote_tool_model.QuoteTool(
            text= data["data"].get("text", None),
            caption= data["data"].get("caption", None),
            alignment= data["data"].get("alignment", None),
            tool_md_id= tool_md.id 
        )
        init_db_session.add(quote_tool)
        init_db_session.commit()
        return quote_tool

    def create__list_tool__(data):
        def store_item(item, 
                       lttbl_id: Optional[uuid.UUID] = None, 
                       parent_item_id: Optional[uuid.UUID] = None,
                       sequence: int = 1):
            item_obj = list_tool_models.Item(
                lttbl_id= lttbl_id,
                parent_item_id= parent_item_id,
                sequence= sequence,
                content= item.get("content"),
                meta= item.get("meta")
            )
            init_db_session.add(item_obj)
            init_db_session.commit()
            if item["items"] != []:
                for idx, inner_item in enumerate(item["items"]):
                    store_item(inner_item,
                               lttbl_id= None,
                               parent_item_id= item_obj.id,
                               sequence= idx + 1
                               )

        tool_md = get_tool_md_mdl_inst()
        list_tool = list_tool_models.ListToolTbl(
            style= data["data"].get("style", None),
            meta= data["data"].get("meta", None),
            sequence= data["data"].get("sequence", None),
            tool_md_id= tool_md.id
        )

        init_db_session.add(list_tool)
        init_db_session.commit()

        for idx, item in enumerate(data["data"]["items"]):
            store_item(item, 
                       lttbl_id= list_tool.id,
                       parent_item_id= None,
                       sequence= idx + 1
                       )

        return list_tool

    def create__tool_tbl__inst():
        tool_tbl_lst = {
            "table": create__table_tool__,
            "code": create__code_tool__,
            "paragraph": create__paragraph_tool__,
            "header": create__header_tool__,
            "quote": create__quote_tool__,
            "List": create__list_tool__
        }
        data = get_data()
        func = tool_tbl_lst.get(tool_type, None)
        if func is None:
            raise ValueError(f"tool of type {tool_type} is not supported")
        return func(data)
    
    return (create__tool_tbl__inst(), tool_type)

@pytest.mark.parametrize("created_tool", ["table", "code", "paragraph", "header", "quote", "List"], indirect=True)
def test__table_tool__(request, init_db_session: Session, created_tool):
    tool, tool_type = created_tool
    if tool_type == "table":
        isinstance(created_tool, table_tool_model.TableTool)