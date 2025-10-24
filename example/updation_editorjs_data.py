# create an 
from dependencies.editorjs_data_store import add_tool_md, add_table_tool_data, update_code_tool_data
from database import get_session
from editorjs_basemodel import Block
import random
from sqlmodel import Session, select
from model import tool_model


def get_random_article_id(session: Session):
    articles = session.exec(
        select(tool_model.Article)
    ).all()
    article = random.choice(articles)
    return article.id 

def main():
    # create a tool in the db of type table
    # update the tool in the db with type code tool
    session = next(get_session())
    add_data = {
        "type" : "table",
        "id": "4dc51dc5-4948-4718-9210-1cb32188d98a",
        "sequence": 1,
        "data" : {
            "content" : [ ["james", "1 pcs", "100$"], ["Pigs", "3 pcs", "200$"], ["Chickens", "12 pcs", "150$"] ]
        }
    }
    add_block_data = Block.model_validate(add_data)
    update_data = {
        "type" : "code",
        "id": "3bb9953d-524a-44f1-bb5e-ce4314daea88",
        "sequence": 1,
        "data" : {
            "code": "div { display: center, background-color: red}",
            "languageCode": "scss"
        }           
    }
    update_block_data = Block.model_validate(update_data)
    article_id = get_random_article_id(session)
    session, tool_md = add_tool_md(session, add_block_data, article_id)
    session, table_tool = add_table_tool_data(session, add_block_data, tool_md.id)    
    session.refresh(tool_md)
    session.refresh(table_tool)
    print(tool_md)
    print(table_tool)
    if tool_md is None:
        print("tool_md is None")
    session, code_tool = update_code_tool_data(session, update_block_data, tool_md)
    session.refresh(code_tool)
    session.refresh(tool_md)
    print(code_tool)
    print(tool_md)
    # session.refresh(table_tool)
    print(table_tool)


if __name__ == "__main__":
    main()