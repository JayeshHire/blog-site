import datetime
from zoneinfo import ZoneInfo
from typing import Annotated, Optional
from sqlmodel import Session, select
from database import get_session
from model import code_tool_model, header_tool_model, list_tool_models, paragraph_tool_model, quote_tool_model, table_tool_model, tool_model
from editorjs_basemodel import EditorJSSessionData, Depends
from fastapi import Body
import uuid
from database import engine
from sqlalchemy.exc import IntegrityError

def convert_to_IST(unix_timestamp: int) -> datetime.datetime:
    unix_timestamp = unix_timestamp / 1000 # convert from ms to sec
    utc = datetime.datetime.fromtimestamp(unix_timestamp, tz=datetime.timezone.utc)
    ist = utc.astimezone(ZoneInfo("Asia/Kolkata"))
    return ist

def save_editorjs_data(editorjs_data: Annotated[EditorJSSessionData, Body()], session: Annotated[Session, Depends(get_session)]):
    def get_tool_id(session: Session, tool_type: str):
        tool_id = session.exec(
            select(tool_model.Tool)
            .where(tool_model.Tool.name == tool_type)
        ).first().id
        return tool_id

    def get_article_id(session: Session):
        article_id = session.exec(
            select(tool_model.Article).limit(1)
        ).first().id
        return article_id

    def get_tool_md_mdl_inst(session: Session, data: dict):
        # data = get_data()
        article_id = get_article_id(session)
        tool_id = get_tool_id(session, block["type"])
        tool_md = tool_model.ToolMD(
            sequence= data.get("sequence", None),
            block_id = data.get("id", None),
            article_id=article_id,
            tool_id= tool_id
        )
        session.add(tool_md)
        session.commit()
        return tool_md 
    
    def create__table_tool__(session: Session, data: dict):
        tool_md = get_tool_md_mdl_inst()
        tbl_tool = table_tool_model.TableTool(
            content= data["data"]["content"],
            tool_md_id= tool_md.id
        )
        session.add(tbl_tool)
        session.commit()
        return tbl_tool
    
    def create__code_tool__(session: Session, data: dict):
        tool_md = get_tool_md_mdl_inst()
        code_tool = code_tool_model.CodeTool(
            code= data["data"]["code"],
            language_code= data["data"].get("languageCode", None),
            tool_md_id= tool_md.id
        )
        session.add(code_tool)
        session.commit()
        return code_tool

    def create__paragraph_tool__(session: Session, data: dict):
        tool_md = get_tool_md_mdl_inst()
        paragraph_tool = paragraph_tool_model.ParagraphTool(
            text= data["data"].get("text", None),
            tool_md_id = tool_md.id
        )
        session.add(paragraph_tool)
        session.commit()
        return paragraph_tool

    def create__header_tool__(session: Session, data: dict):
        tool_md = get_tool_md_mdl_inst()
        header_tool = header_tool_model.HeaderTool(
            text= data["data"].get("text", None),
            level= data["data"].get("level", None),
            tool_md_id= tool_md.id
        )
        session.add(header_tool)
        session.commit()
        return header_tool

    def create__quote_tool__(session: Session, data: dict):
        tool_md = get_tool_md_mdl_inst()
        quote_tool = quote_tool_model.QuoteTool(
            text= data["data"].get("text", None),
            caption= data["data"].get("caption", None),
            alignment= data["data"].get("alignment", None),
            tool_md_id= tool_md.id 
        )
        session.add(quote_tool)
        session.commit()
        return quote_tool

    def create__list_tool__(session: Session, data: dict):
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
            session.add(item_obj)
            session.commit()
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

        session.add(list_tool)
        session.commit()

        for idx, item in enumerate(data["data"]["items"]):
            store_item(item, 
                       lttbl_id= list_tool.id,
                       parent_item_id= None,
                       sequence= idx + 1
                       )

        return list_tool


    # this implementation won't work for list tool 
    # hence the older way used in the test file needs 
    # to be used here.
    def create__tool_tbl__inst(block: dict, mode: str): # mode u-update, c-create
        tool_tbl_lst = {
            "table": create__table_tool__,
            "code": create__code_tool__,
            "paragraph": create__paragraph_tool__,
            "header": create__header_tool__,
            "quote": create__quote_tool__,
            "list": create__list_tool__
        }
        tool_type = block["type"]
        data = block["data"]
        block_id = block["id"]

        if mode == 'u':
            """ 
            get the tool_md using the block_id
            compare the tool associated with the 
            tool_md and the tool in the block data.
            if both are same delete the record of tool

            """
            
            with Session(engine) as session:

                with session.begin_nested():
                    tool_md = session.exec(
                        select(tool_model.ToolMD)
                        .where(tool_model.ToolMD.block_id == block_id)
                    ).first()
                    tool_name = tool_md.tool.name
                    block_tool_class = tools_model_map[tool_type]

                    tool_class = tools_model_map[tool_name]
                    tool_data = session.exec(
                        select(tool_class)
                        .where(tool_class.tool_md_id == tool_md.id)
                    ).first()
                    if tool_data is not None:
                        session.delete(tool_data)

                    attrs = list(
                        block_tool_class.model_fields.keys()
                        )
                    attrs_with_val = {
                        key: data[key]
                        for key in attrs if key != "id" and key != "tool_md_id"
                    }
                    attrs_with_val["tool_md_id"] = tool_md.id
                    new_tool_data = block_tool_class(
                        **attrs_with_val
                    )
                    session.add(new_tool_data)
                    session.commit()
        
        elif mode == 'c':
            with Session(engine) as session:
                with session.begin_nested():
                    article_id = get_article_id(session)
                    tool_id = get_tool_id(session, tool_type)
                
                    tool_md = tool_model.ToolMD(
                        sequence = block["sequence"],
                        block_id= block["id"],
                        article_id= article_id,
                        tool_id= tool_id
                    )

                    session.add(tool_md)

                    block_tool_class = tools_model_map[tool_type]
                    attrs = list(
                        block_tool_class.model_fields.keys()
                        )
                    attrs_with_val = {
                        key: data[key]
                        for key in attrs if key != "id" and key != "tool_md_id"
                    }
                    attrs_with_val["tool_md_id"] = tool_md.id
                    new_tool_data = block_tool_class(
                        **attrs_with_val
                    )
                    session.add(new_tool_data)
                    session.commit()





        # data = get_data()
        func = tool_tbl_lst.get(tool_type, None)
        if func is None:
            raise ValueError(f"tool of type {tool_type} is not supported")
        return func(data)
    
    print("inside the save_editorjs_data function")
    time = convert_to_IST(editorjs_data.time)
    print(f"time: {time}")
    print(f"blocks: {editorjs_data.blocks}")

    tools_model_map = {
        "table": table_tool_model.TableTool,
        "code": code_tool_model.CodeTool,
        "paragraph": paragraph_tool_model.ParagraphTool,
        "header": header_tool_model.HeaderTool,
        "quote": quote_tool_model.QuoteTool,
        "list": list_tool_models.ListToolTbl
    }
    data_blocks = editorjs_data.blocks
    data_lst = [ block.model_dump().update(sequence=(idx + 1)) for idx, block in enumerate(data_blocks)]

    with Session(engine) as session:
        
        for block in data_lst:
            try:
                with session.begin_nested():
                    with session.begin_nested():
                        tool_md = session.exec(
                            select(tool_model.ToolMD)
                            .where(tool_model.ToolMD.block_id == block.get("id", None))
                        ).first()

                        if tool_md is not None:
                            # populate data in update mode
                            article_id = get_article_id(session)
                            if tool_md.article_id == article_id:
                                # perform updation
                                create__tool_tbl__inst(block["data"], block["type"])
                                continue 
                                pass
                            else:
                                # perform insertion

                                continue
                                pass
                        else: 
                            # populate data in create mode
                            pass
                        
                    with session.begin_nested():
                        # perform insertion
                        pass


                    # if tool_md is not None:
                    #     # ***perform updation operation
                    #     with session.begin_nested():
                    #         model_class = tools_model_map[tool_md.tool.name]

                    #     continue
                
                with session.begin_nested():
                    tool_id = get_tool_id(session, block["type"])
                    article_id = get_article_id(session)
                    tool_md = get_tool_md_mdl_inst(session, block)
                    create__tool_tbl__inst(block["data"], block["type"])

            except IntegrityError:
                print(f"block with block id {block["id"]} already exists")

    return True
