from model import tool_model, code_tool_model, header_tool_model, list_tool_models, paragraph_tool_model, quote_tool_model, table_tool_model
from editorjs_basemodel import EditorJSSessionData, Block, CodeToolData, HeaderData, ListData, ListItem, ParagraphData, QuoteData, TableData
from sqlmodel import Session, select
import uuid
from typing import Optional, List, Tuple
from collections import namedtuple


# AddToolOutput = namedtuple("AddToolOutputType", [""])


# create individual functions for adding record to the db
def add_code_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           code_tool_model.CodeTool
                           ]:
    if type(block.data) != CodeToolData:
        raise ValueError(f"object of CodeToolData class was expected but instead got {type(block.data)}")
    
    ct_tbl = code_tool_model.CodeTool(
        code= block.data.code,
        language_code= block.data.languageCode,
        tool_md_id= tool_md_id
    )
    session.add(ct_tbl)
    return (session, ct_tbl)


def add_header_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           header_tool_model.HeaderTool
                           ]:
    if type(block.data) != HeaderData:
        raise ValueError(f"object of HeaderData class was expected but instead got {type(block.data)}")
    
    ht_tbl = header_tool_model.HeaderTool(
        text= block.data.text,
        level= block.data.level,
        tool_md_id=tool_md_id
    )
    session.add(ht_tbl)
    return (session, ht_tbl)


def add_list_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           list_tool_models.ListToolTbl
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
    return (session, lt_tbl)


def add_paragraph_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           paragraph_tool_model.ParagraphTool
                           ]:
    if type(block.data) != ParagraphData:
        raise ValueError(f"object of ParagraphData class was expected but instead got {type(block.data)}")
    
    p_tbl = paragraph_tool_model.ParagraphTool(
        text= block.data.text,
        tool_md_id= tool_md_id
    )

    session.add(p_tbl)
    return (session, p_tbl)


def add_quote_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           quote_tool_model.QuoteTool
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
    return (session, q_tbl)


def add_table_tool_data(session: Session, 
                       block: Block, 
                       tool_md_id: uuid.UUID
                       ) -> Tuple[
                           Session,
                           table_tool_model.TableTool
                           ]:
    if type(block.data) != TableData:
        raise ValueError(f"object of TableData class was expected but instead got {type(block.data)}")
    
    tt_tbl = table_tool_model.TableTool(
        content= block.data.content,
        tool_md_id= tool_md_id
    )
    session.add(tt_tbl)
    return (session, tt_tbl)


def update_ToolMD_tool_id(session: Session, 
                          tool_md: tool_model.ToolMD,
                          tool_name: str) -> Tuple [
                              Session,
                              tool_model.ToolMD
                          ]:
    new_tool_id = session.exec(
        select(tool_model.Tool)
        .where(tool_model.Tool.name == tool_name)
    ).one().id
    tool_md.id = new_tool_id
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
                           code_tool_model.CodeTool
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
        session, tool_md = update_ToolMD_tool_id(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= tool_name)
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
                           header_tool_model.HeaderTool
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
        session, tool_md = update_ToolMD_tool_id(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= tool_name)
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
                          list_tool_models.ListToolTbl
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
        lt_tbl.style = block.data.style
        lt_tbl.meta = block.data.meta
        store_items(session, block.data.items,
                lt_tbl.id,
                None)
    
    else: 
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD_tool_id(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= tool_name)
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
                          paragraph_tool_model.ParagraphTool
                          ]:
    if type(block.data) != ParagraphData:
        raise ValueError(f"object of ParagraphData class was expected but instead got {type(block.data)}")
    
    tool_name = tool_md.tool.name
    if tool_name == block.type:
        p_tbl = session.exec(
            select(paragraph_tool_model.ParagraphTool)
            .where(paragraph_tool_model.ParagraphTool.tool_md_id == tool_md.id)
        ).one()
        p_tbl.text = block.data.text
        session.add(p_tbl)
    
    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD_tool_id(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= tool_name)
        session, p_tbl = add_paragraph_tool_data(session, block, tool_md.id)
    return (session, p_tbl)


def update_quote_tool_data(session: Session,
                           block: Block, 
                          tool_md: tool_model.ToolMD
                          ) -> Tuple[
                            Session,
                          quote_tool_model.QuoteTool
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
    
    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD_tool_id(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= tool_name)
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
                          table_tool_model.TableTool
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

    else:
        tool_cls = tool_name_cls_map[tool_name]
        tool_inst = session.exec(
            select(tool_cls)
            .where(tool_cls.tool_md_id == tool_md.id)
        ).one()
        session.delete(tool_inst)

        session, tool_md = update_ToolMD_tool_id(session=session,
                                                 tool_md= tool_md,
                                                 tool_name= tool_name)
        session, tt_tbl = add_table_tool_data(
            session,
            block,
            tool_md.id
        )
    return (session, tt_tbl)


def store_editorjs_data(editorjs_data: EditorJSSessionData):
    
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
    pass 