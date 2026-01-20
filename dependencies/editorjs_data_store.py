from model import tool_model, code_tool_model, header_tool_model, list_tool_models, paragraph_tool_model, quote_tool_model, table_tool_model
from editorjs_basemodel import EditorJSSessionData, Block, CodeToolData, HeaderData, ListData, ListItem, ParagraphData, QuoteData, TableData
from sqlmodel import Session, select
import uuid
from typing import Optional, List, Tuple
from collections import namedtuple
from database import get_session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from datetime import datetime

# AddToolOutput = namedtuple("AddToolOutputType", [""])

def add_tool_md(session: Session,
                block: Block,
                article_id: uuid.UUID,
                time: datetime,
                version: str 
                ) -> Tuple[
                    Session, tool_model.ToolMD
                ]:
    tool_id = session.exec(
        select(tool_model.Tool)
        .where(tool_model.Tool.name == block.type)
    ).one().id 
    tool_md = tool_model.ToolMD(
        sequence= block.sequence,
        article_id= article_id,
        block_id= block.id,
        tool_id= tool_id,
        time= time,
        version=version
    )
    session.add(tool_md)
    print(f"created tool: {tool_md}")
    return (session, tool_md)

# create individual functions for adding record to the db
def add_code_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != CodeToolData:
        raise ValueError(f"object of CodeToolData class was expected but instead got {type(block.data)}")
    
    ct_tbl = code_tool_model.CodeTool(
        code= block.data.code,
        language_code= block.data.languageCode,
        tool_md_id= tool_md_id
    )
    session.add(ct_tbl)
    session.commit()
    return (session, ct_tbl)


def add_header_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != HeaderData:
        raise ValueError(f"object of HeaderData class was expected but instead got {type(block.data)}")
    
    ht_tbl = header_tool_model.HeaderTool(
        text= block.data.text,
        level= block.data.level,
        tool_md_id=tool_md_id
    )
    session.add(ht_tbl)
    session.commit()
    return (session, ht_tbl)


def add_list_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != ListData:
        raise ValueError(f"object of ListData class was expected but instead got {type(block.data)}")

    def store_items(session: Session, 
                   item_list: List[ListItem],
                   lttbl_id: Optional[uuid.UUID],
                   parent_item_id: Optional[uuid.UUID]):
        for idx, item in enumerate(item_list):
            sequence = idx + 1
            item_tbl = list_tool_models.Item(
                lttbl_id= lttbl_id,
                sequence= sequence,
                content= item.content,
                meta= item.meta,
                parent_item_id= parent_item_id
            )
            session.add(item_tbl)
            if item.items != []:
                store_items(session, item.items, None, item_tbl.id)


    lt_tbl = list_tool_models.ListToolTbl(
        style= block.data.style,
        meta= block.data.meta,
        tool_md_id= tool_md_id
    )

    session.add(lt_tbl)
    store_items(session, block.data.items,
                lt_tbl.id,
                None)
    session.commit()
    return (session, lt_tbl)


def add_paragraph_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != ParagraphData:
        raise ValueError(f"object of ParagraphData class was expected but instead got {type(block.data)}")
    
    if type(tool_md_id) != uuid.UUID:
        ValueError(f"tool md is not of uuid type : {tool_md_id}")

    p_tbl = paragraph_tool_model.ParagraphTool(
        text= block.data.text,
        tool_md_id= tool_md_id
    )

    session.add(p_tbl)
    session.commit()
    return (session, p_tbl)


def add_quote_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != QuoteData:
        raise ValueError(f"object of QuoteData class was expected but instead got {type(block.data)}")
    
    q_tbl = quote_tool_model.QuoteTool(
        text= block.data.text,
        caption= block.data.caption,
        alignment= block.data.alignment,
        tool_md_id= tool_md_id
    )
    session.add(q_tbl)
    session.commit()
    return (session, q_tbl)


def add_table_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != TableData:
        raise ValueError(f"object of TableData class was expected but instead got {type(block.data)}")
    
    tt_tbl = table_tool_model.TableTool(
        content= block.data.content,
        tool_md_id= tool_md_id
    )
    session.add(tt_tbl)
    session.commit()
    return (session, tt_tbl)


def update_ToolMD(session: Session, 
                          tool_md: tool_model.ToolMD,
                          tool_name: str,
                          block_id: str) -> Tuple [
                              Session,
                              tool_model.ToolMD
                          ]:
    new_tool_id = session.exec(
        select(tool_model.Tool)
        .where(tool_model.Tool.name == tool_name)
    ).one().id
    tool_md.tool_id = new_tool_id
    tool_md.block_id = block_id
    session.add(tool_md)
    return (session, tool_md)


tool_name_cls_map = {
    "table": table_tool_model.TableTool,
    "code": code_tool_model.CodeTool,
    "paragraph": paragraph_tool_model.ParagraphTool,
    "header": header_tool_model.HeaderTool,
    "quote": quote_tool_model.QuoteTool,
    "list": list_tool_models.ListToolTbl
}
'''
here already available tool_md's id is given.
if block.type is CodeToolData then call this func.
'''
# create individual functions for updating record in the db
def update_code_tool_data(session: Session, 
                       block: Block, 
                       tool_md: tool_model.ToolMD
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != CodeToolData:
        raise ValueError(f"object of CodeToolData class was expected but instead got {type(block.data)}")
    
    tool_name = tool_md.tool.name
    if tool_name == block.type:
        ct_tbl = session.exec(
            select(code_tool_model.CodeTool)
            .where(code_tool_model.CodeTool.tool_md_id == tool_md.id)
        ).one()
        ct_tbl.code = block.data.code
        ct_tbl.language_code = block.data.languageCode
        session.add(ct_tbl)
        session.commit()

    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        # ct_tbl = code_tool_model.CodeTool(
        #     code= block.data.code,
        #     language_code= block.data.languageCode,
        #     tool_md_id= tool_md.id
        # )        
        # session.add(ct_tbl)
        session, tool_md = update_ToolMD(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= block.type,
                                                 block_id=block.id)
        
        # raise ValueError(f"{tool_md}")
        session, ct_tbl = add_code_tool_data(session, 
                           block=block, 
                           tool_md_id= tool_md.id
                           )

    return (session, ct_tbl)


def update_header_tool_data(session: Session, 
                       block: Block, 
                       tool_md: tool_model.ToolMD
                       ) -> Tuple[
                           Session,
                           tool_model.ToolDataModel
                           ]:
    if type(block.data) != HeaderData:
        raise ValueError(f"object of HeaderData class was expected but instead got {type(block.data)}")
    
    tool_name = tool_md.tool.name
    if tool_name == block.type:
        header_tool_inst = session.exec(
            select(header_tool_model.HeaderTool)
            .where(header_tool_model.HeaderTool.tool_md_id == tool_md.id)
        ).one()
        header_tool_inst.text = block.data.text
        header_tool_inst.level = block.data.level
        session.add(header_tool_inst)
        session.commit()
    
    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)



        # header_tool_inst = header_tool_model.HeaderTool(
        #     text= block.data.text,
        #     level= block.data.level,
        #     tool_md_id= tool_md.id
        # )
        # session.add(header_tool_inst)
        session, tool_md = update_ToolMD(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= block.type,
                                                 block_id=block.id)
        session, header_tool_inst = add_header_tool_data(
            session=session,
            block=block,
            tool_md_id= tool_md.id
        )
    
    return ( session, header_tool_inst)


def update_list_tool_data(session: Session, 
                          block: Block, 
                          tool_md: tool_model.ToolMD
                          ) -> Tuple[
                            Session,
                          tool_model.ToolDataModel
                          ]:
    if type(block.data) != ListData:
        raise ValueError(f"object of ListData class was expected but instead got {type(block.data)}")
    
    def store_items(session: Session, 
                   item_list: List[ListItem],
                   lttbl_id: Optional[uuid.UUID],
                   parent_item_id: Optional[uuid.UUID]):
        for idx, item in enumerate(item_list):
            sequence = idx + 1
            item_tbl = list_tool_models.Item(
                lttbl_id= lttbl_id,
                sequence= sequence,
                content= item.content,
                meta= item.meta,
                parent_item_id= parent_item_id
            )
            session.add(item_tbl)
            if item.items != []:
                store_items(session, item.items, None, item_tbl.id)

    tool_name = tool_md.tool.name
    if tool_name == block.type:
        lt_tbl = session.exec(
            select(list_tool_models.ListToolTbl)
            .where(list_tool_models.ListToolTbl.tool_md_id == tool_md.id)
        ).one()
        items = session.exec(
            select(list_tool_models.Item)
            .where(list_tool_models.Item.lttbl_id == lt_tbl.id )
        ).all()
        for item in items:
            session.delete(item)

        lt_tbl.style = block.data.style
        lt_tbl.meta = block.data.meta
        session.add(lt_tbl)
        store_items(session, block.data.items,
                lt_tbl.id,
                None)
        session.commit()
        
    else: 
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= block.type,
                                                 block_id=block.id)
        session, lt_tbl = add_list_tool_data(session=session,
                           block=block,
                           tool_md_id=tool_md.id
                        )
    return (session, lt_tbl)


def update_paragraph_tool_data(session: Session,
                               block: Block, 
                          tool_md: tool_model.ToolMD
                          ) -> Tuple[
                            Session,
                          tool_model.ToolDataModel
                          ]:
    if type(block.data) != ParagraphData:
        raise ValueError(f"object of ParagraphData class was expected but instead got {type(block.data)}")
    tool_md_id = tool_md.id
    if type(tool_md_id) != uuid.UUID:
        ValueError(f"tool md is not of uuid type : {tool_md_id}")
    tool_name = tool_md.tool.name
    with open("update_paragraph.log", 'a') as f:
        f.write(f"tool name: {tool_name}, block.data: {type(block.data)}")

    if tool_name == block.type:
        p_tbl = session.exec(
            select(paragraph_tool_model.ParagraphTool)
            .where(paragraph_tool_model.ParagraphTool.tool_md_id == tool_md.id)
        ).one()
        p_tbl.text = block.data.text
        session.add(p_tbl)
        session.commit()
    
    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= block.type,
                                                 block_id=block.id)
        session, p_tbl = add_paragraph_tool_data(session, block, tool_md.id)
    return (session, p_tbl)


def update_quote_tool_data(session: Session,
                           block: Block, 
                          tool_md: tool_model.ToolMD
                          ) -> Tuple[
                            Session,
                          tool_model.ToolDataModel
                          ]:
    if type(block.data) != QuoteData:
        raise ValueError(f"object of QuoteData class was expected but instead got {type(block.data)}")
    
    tool_name = tool_md.tool.name
    if tool_name == block.type:
        quote_tbl = session.exec(
            select(quote_tool_model.QuoteTool)
            .where(quote_tool_model.QuoteTool.tool_md_id == tool_md.id)
        ).one()
        quote_tbl.text = block.data.text
        quote_tbl.caption = block.data.caption
        quote_tbl.alignment = block.data.alignment
        session.add(quote_tbl)
        session.commit()
    
    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= block.type,
                                                 block_id=block.id)
        session, quote_tbl = add_quote_tool_data(
            session,
            block,
            tool_md.id
        )
    return (session, quote_tbl)


def update_table_tool_data(session: Session,
                           block: Block, 
                          tool_md: tool_model.ToolMD
                          ) -> Tuple[
                            Session,
                          tool_model.ToolDataModel
                          ]:
    if type(block.data) != TableData:
        raise ValueError(f"object of TableData class was expected but instead got {type(block.data)}")
    
    tool_name = tool_md.tool.name
    if tool_name == block.type:
        tt_tbl = session.exec(
            select(table_tool_model.TableTool)
            .where(table_tool_model.TableTool.tool_md_id == tool_md.id)
        ).one()
        tt_tbl.content = block.data.content
        session.add(tt_tbl)
        session.commit()

    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= block.type,
                                                 block_id=block.id)
        session, tt_tbl = add_table_tool_data(
            session,
            block,
            tool_md.id
        )
    return (session, tt_tbl)


def delete_tool_md(session: Session,
                   tool_md: tool_model.ToolMD):
    # tool_md = session.get(tool_model.ToolMD, tool_md_id)
    session.delete(tool_md)
    return session


def delete_code_tool_data(session: Session,
                          block_id: str
                          ) -> Session:
    tool_md = session.exec(
        select(tool_model.ToolMD)
        .where(tool_model.ToolMD.block_id == block_id)
    ).one()
    tool_name = session.get(tool_model.Tool, 
                            tool_md.tool_id
                            ).name
    
    if tool_name != "code":
        raise ValueError(f"tool name is invalid. It should be 'code' but instead it is {tool_name}")
    
    ct_mdl = session.exec(
        select(code_tool_model.CodeTool)
        .where(code_tool_model.CodeTool.tool_md_id == tool_md.id)
    ).one()
    session = delete_tool_md(session, tool_md)
    
    session.delete(ct_mdl)
    session.commit()
    return session


def delete_header_tool_data(session: Session,
                            block_id: str) -> Session:
    tool_md = session.exec(
        select(tool_model.ToolMD)
        .where(tool_model.ToolMD.block_id == block_id)
    ).one()
    tool_name = session.get(tool_model.Tool, 
                            tool_md.tool_id
                            ).name
    
    if tool_name != "header":
        raise ValueError(f"tool name is invalid. It should be 'header' but instead it is {tool_name}")
    
    ht_mdl = session.exec(
        select(header_tool_model.HeaderTool)
        .where(header_tool_model.HeaderTool.tool_md_id == tool_md.id)
    ).one()
    session = delete_tool_md(session, tool_md)
    
    session.delete(ht_mdl)
    session.commit()
    return session


def delete_list_tool_data(session: Session,
                          block_id: str) -> Session:
    tool_md = session.exec(
        select(tool_model.ToolMD)
        .where(tool_model.ToolMD.block_id == block_id)
    ).one()
    tool_name = session.get(tool_model.Tool, 
                            tool_md.tool_id
                            ).name
    
    if tool_name != "list":
        raise ValueError(f"tool name is invalid. It should be 'list' but instead it is {tool_name}")
    
    ltt_mdl = session.exec(
        select(list_tool_models.ListToolTbl)
        .where(list_tool_models.ListToolTbl.tool_md_id == tool_md.id)
    ).one()
    items = session.exec(
        select(list_tool_models.Item)
        .where(list_tool_models.Item.lttbl_id == ltt_mdl.id)
    ).all()
    session = delete_tool_md(session, tool_md)
    
    session.delete(ltt_mdl)
    for item in items:
        session.delete(item) 
    session.commit()
    return session


def delete_paragraph_tool_data(session: Session,
                          block_id: str) -> Session:
    tool_md = session.exec(
        select(tool_model.ToolMD)
        .where(tool_model.ToolMD.block_id == block_id)
    ).one()
    tool_name = session.get(tool_model.Tool, 
                            tool_md.tool_id
                            ).name
    
    if tool_name != "paragraph":
        raise ValueError(f"tool name is invalid. It should be 'paragraph' but instead it is {tool_name}")
    
    pt_mdl = session.exec(
        select(paragraph_tool_model.ParagraphTool)
        .where(paragraph_tool_model.ParagraphTool.tool_md_id == tool_md.id)
    ).one()
    session = delete_tool_md(session, tool_md)
    
    session.delete(pt_mdl)
    session.commit()
    return session


def delete_quote_tool_data(session: Session,
                          block_id: str) -> Session:
    tool_md = session.exec(
        select(tool_model.ToolMD)
        .where(tool_model.ToolMD.block_id == block_id)
    ).one()
    tool_name = session.get(tool_model.Tool, 
                            tool_md.tool_id
                            ).name
    
    if tool_name != "quote":
        raise ValueError(f"tool name is invalid. It should be 'quote' but instead it is {tool_name}")
    
    qt_mdl = session.exec(
        select(quote_tool_model.QuoteTool)
        .where(quote_tool_model.QuoteTool.tool_md_id == tool_md.id)
    ).one()
    session = delete_tool_md(session, tool_md)
    
    session.delete(qt_mdl)
    session.commit()
    return session


def delete_table_tool_data(session: Session,
                          block_id: str) -> Session:
    tool_md = session.exec(
        select(tool_model.ToolMD)
        .where(tool_model.ToolMD.block_id == block_id)
    ).one()
    tool_name = session.get(tool_model.Tool, 
                            tool_md.tool_id
                            ).name
    
    if tool_name != "table":
        raise ValueError(f"tool name is invalid. It should be 'table' but instead it is {tool_name}")
    
    tt_mdl = session.exec(
        select(table_tool_model.TableTool)
        .where(table_tool_model.TableTool.tool_md_id == tool_md.id)
    ).one()
    session = delete_tool_md(session, tool_md)
    
    session.delete(tt_mdl)
    session.commit()
    return session


def get_toolmd_ifexists(block_id: str) -> Optional[tool_model.ToolMD] \
        | MultipleResultsFound:
    """ 
    This function checks if the block data exists in the db or not.
    """
    session = next(get_session())
    try:
        tool_md = session.exec(
            select(tool_model.ToolMD)
            .where(tool_model.ToolMD.block_id == block_id)
        ).one()
        '''
        the MultipleResultsFound exception is purposefully
        not handled here as we want that error to be thrown.
        Because, if that error is caused that means there is
        a serious consistency problem in our db.
        '''
    except NoResultFound:
        return None 
    
    return tool_md


def get_prev_toolmd(block_ids: List[str], article_id: uuid.UUID, session: Session) -> List[tool_model.ToolMD]:
    '''
    This should return all the toolmd for which 
    blocks does not exist in the frontend.
    '''
    tool_md = session.exec(
        select(tool_model.ToolMD)
        .where(tool_model.ToolMD.block_id.not_in(block_ids))
        .where(tool_model.ToolMD.article_id == article_id)
    ).all()
    return tool_md


def delete_inexisting_toolmd(block_ids: List[str], article_id: uuid.UUID) :

    session = next(get_session())
    tool_mds = get_prev_toolmd(block_ids, article_id, session)
    for tool_md in tool_mds:
        tool_name = session.get(tool_model.Tool, 
                                    tool_md.tool_id).name
        delete_func = delete_func_map[tool_name]
        session = delete_func(session, tool_md.block_id)
        session.delete(tool_md)
    session.commit()


def update_tool_md_seq(session: Session, tool_md_id: uuid.UUID, seq: int):
    tool_md = session.get(tool_model.ToolMD, tool_md_id)
    tool_md.sequence = seq 
    session.add(tool_md)
    return session

def update_tool_md_time_n_ver(session: Session, 
                            tool_md_id: uuid.UUID, 
                            time: datetime, version: str):
    tool_md = session.get(tool_model.ToolMD, tool_md_id)
    tool_md.time = time 
    tool_md.version = version
    session.add(tool_md)
    return session


func_map = {
        "table": add_table_tool_data,
        "code": add_code_tool_data,
        "paragraph": add_paragraph_tool_data,
        "header": add_header_tool_data,
        "quote": add_quote_tool_data,
        "list": add_list_tool_data
    }

update_func_map = {
    "table": update_table_tool_data,
    "code": update_code_tool_data,
    "paragraph": update_paragraph_tool_data,
    "header": update_header_tool_data,
    "quote": update_quote_tool_data,
    "list": update_list_tool_data
}

delete_func_map = {
    "table": delete_table_tool_data,
    "code": delete_code_tool_data,
    "paragraph": delete_paragraph_tool_data,
    "header": delete_header_tool_data,
    "quote": delete_quote_tool_data,
    "list": delete_list_tool_data
}

def store_editorjs_data(editorjs_data: EditorJSSessionData) :
    
    # article id will be supplied from the frontend
    # if article doesn't exists throw an error

    # for now just return a dummy article id

    # get the tool_id for the specific tool.

    # first check if a tool_md object exists in the
    # db having the above article_id and block_id 

    # If the db do not have the tool_md with it, that means
    # this is a new record and it needs to be added in the db
    '''
        adding new record.
        - create an object of tool_md table, and get the tool_id
        - create individual function for adding record to the db.
        - Depending on the type of tool, call the specific function,
        and create that kind of tool object.
        - commit the changes in the transaction.
    '''
    
    # else it is an existing record which needs to be 
    # modified or updated in the db.
    '''
        modifying new record in the db.
        - create individual function for updating record in the db.
        - For the tool_md having a record for a block_id 
        and article_id get the tool_data_mdl instance.
        - update the data inside the instance with the new data.
        - commit the changes in the transaction.
    '''

    """ 
        for each block in the list of blocks see 
        if the block is present in the tool_md table or not.
        If the block is present in the tool_md table 
        then call update function for that block.
        If the block is not present in the tool_md table
        then call add function for that block.
    """

    '''
        For deleting the row whose tool is changed and the
        row still persists in it's tool data table. do the following
        steps:
        1. get all the block ids from the blocks
        2. get all the block ids from the table which have same sequence and article id.
        3. delete the block ids from the table with same sequence 
        where the block id is not equal to the one in the blocks
    '''
    time = datetime.fromtimestamp(editorjs_data.time / 1000)
    version = editorjs_data.version
    blocks = editorjs_data.blocks
    tool_md_exists = [ get_toolmd_ifexists(block.id) for block in blocks]
    article_id = uuid.UUID(editorjs_data.article_id)

    for idx, tool_md in enumerate(tool_md_exists):
        if tool_md:
            # update the existing data
            block = blocks[idx]
            block.sequence = idx + 1
            tool_type = block.type
            func = update_func_map[tool_type]
            session = next(get_session())
            # tool_md.sequence = block.sequence
            # session.add(tool_md)
            update_tool_md_seq(session, tool_md.id, block.sequence)
            update_tool_md_time_n_ver(session, tool_md.id, time, version)
            s, tool_data_mdl = func(session, block, tool_md)
        else:
            # add new data
            block = blocks[idx]
            block.sequence = idx + 1
            tool_type = block.type
            func = func_map[tool_type]
            session = next(get_session())
            s, tool_md = add_tool_md(session, block, article_id, time, version)
            print(f"tool md data: {tool_md}")
            s, tool_data_mdl = func(s, block, tool_md.id)
    


    # for block in blocks:
    #     session = next(get_session())
    #     tool_mds = session.exec(
    #         select(tool_model.ToolMD)
    #         .where(tool_model.ToolMD.article_id == article_id)
    #         .where(tool_model.ToolMD.sequence == block.sequence)
    #         .where(tool_model.ToolMD.block_id != block.id)
    #     ).all()
    #     for tool_md in tool_mds:
    #         tool_name = session.get(tool_model.Tool, 
    #                                 tool_md.tool_id).name
    #         delete_func = delete_func_map[tool_name]
    #         session = delete_func(session, tool_md.block_id)
    block_ids = [block.id for block in blocks]
    delete_inexisting_toolmd(block_ids, article_id)
            
    return editorjs_data
    # pass 

def store_editorjs_data_n(editorjs_data: EditorJSSessionData) -> EditorJSSessionData:

    '''
        To store and update the editor js data in the db.

        case 1:
            only the style has changed

        steps:
        1. get the article id.
    '''
    pass