from fastapi import Response, Request, Cookie, Form, HTTPException, status
from model import tool_model, user_model, code_tool_model, list_tool_models, quote_tool_model, table_tool_model, header_tool_model, paragraph_tool_model
from database import get_session
from uuid import UUID
from typing import Annotated
from sqlmodel import select, Session
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound, IntegrityError
from datetime import datetime, timedelta, timezone
from user_basemodel import SigninBaseModel, SignupBaseModel
from editorjs_basemodel import *
from passlib.context import CryptContext
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from TelemetryConfig.telemetry_config import origination_

tracer = trace.get_tracer(__name__)

'''
create a session object and set the session id 
and browser_id as the cookies.
- Also create a new article and set the article id for the session.
- A new article should be created only when an event is triggered in the frontend.
- We create an article now with just the session id. When the user logins we will 
we will change the author id for the user from None to current username.
- A batch job is necessary for clearing the articles which does not have a title, subtitle, and toolmds.
'''
# @tracer.start_as_current_span("editor session creation")
def create_editor_session(request: Request, response: Response ) -> tool_model.EditorSession:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="session_depends",
    #                                func_name="create_editor_session"
    # ))
    with tracer.start_as_current_span("create_editor_session",
                                      attributes={
                                          **origination_(
                                            package="dependencies",
                                            module="session_depends",
                                            func_name="create_editor_session"
                                            )   
                                      }) as current_span: 
        session = next(get_session())
        editor_session = tool_model.EditorSession(expiry_date=datetime.now()+timedelta(days=1))
        session.add(editor_session)
        article = tool_model.Article(editor_session_id=editor_session.id)
        session.add(article)
        # response.set_cookie(
        #     key="editor_session_id",
        #     value=editor_session.id
        # )
        session.commit()
        current_span.add_event("editor session and article has been created")
        with tracer.start_as_current_span("set_session_attrs_and_cookie",
                                          attributes={
                                              "browser_id": str(editor_session.browser_id),
                                              "editor_session_id": str(editor_session.id)
                                          }):
            response.set_cookie(
                key="browser_id",
                value=str(editor_session.browser_id),
                expires=editor_session.expiry_date.astimezone(timezone.utc)
            )
            current_span.add_event("cookie [browser_id] has been set for the browser")
            request.session["editor_session_id"] = str(editor_session.id) 
            request.session["browser_id"] = str(editor_session.browser_id)
            session.expunge(editor_session)
    return editor_session


'''
get the session object using the browser_id from the browser.

- get the browser id from the browser.
- get the session object for the browser id from the db table editor_session
    which is not expired.
- return the session object. [article id is more important here.]
'''
# @tracer.start_as_current_span("editor session fetch")
def get_editor_session(request: Request, 
                       browser_id: UUID | None = None):
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="session_depends",
    #                                func_name="get_editor_session"
    # ))
    with tracer.start_as_current_span("get_editor_session", 
                                      attributes={
                                          **origination_(
                                            package="dependencies",
                                            module="session_depends",
                                            func_name="get_editor_session"
                                            ),
                                            "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        if browser_id:
            session = next(get_session())
            user_id = request.session.get("user_id")
            user_id = UUID(user_id) if user_id is not None else None
            current_span.set_attribute("user_id", user_id)
            editor_session = session.exec(
                select(tool_model.EditorSession)
                .where(tool_model.EditorSession.browser_id == browser_id)
                .where(tool_model.EditorSession.expiry_date > datetime.now())
                .where(tool_model.EditorSession.user_id == user_id)
            ).first()
            current_span.add_event("editor session has been fetched")
            print(f"editor session: {editor_session}")
            if editor_session is None:
                return None
            else:
                session.expunge(editor_session)
                current_span.set_attribute("editor_session.id", editor_session.id)

            if editor_session.logged_in:
                request.session['editor_session_id'] = str(editor_session.id)
                return editor_session
            elif user_id is None:
                print("inside get_editor_session func")
                print(f"editor session: {editor_session.id}")
                request.session['editor_session_id'] = str(editor_session.id)
                return editor_session
            else: 
                return None
        else:
            return None
    

''' 
initialize the editor session
'''
# @tracer.start_as_current_span("editor session initialization")
def init_editor_session(request: Request, 
                        response: Response,
                        browser_id: Annotated[UUID | None, Cookie()] = None
                        ):
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="session_depends",
    #                                func_name="init_editor_session"
    # ))
    with tracer.start_as_current_span("init_editor_session",
                                      attributes={
                                          **origination_(
                                            package="dependencies",
                                            module="session_depends",
                                            func_name="init_editor_session"
                                            ),
                                            "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        if browser_id is not None:
            current_span.set_attribute("browser_id", str(browser_id))
        if browser_id:
            print(f"----- browser id: {browser_id}")
            editor_session = get_editor_session(request, browser_id)
            if editor_session is None:
                print("editor session is none")
                editor_session = create_editor_session(request, response)
            session = next(get_session())
            # session.add(editor_session)
            try:
                article = session.exec(
                    select(tool_model.Article)
                    .where(tool_model.Article.editor_session_id == editor_session.id)
                    .order_by(tool_model.Article.last_updated_at.desc())
                ).first()
                current_span.set_attribute("article_id", article.id)
            except NoResultFound as e:
                current_span.record_exception(e)
                article = create_new_article(request)
                current_span.set_attribute("article_id", article.id)
        else:
            editor_session = create_editor_session(request, response)
            current_span.add_event("New editor session created")
            article = create_new_article(request)
            current_span.add_event("New article created")

    return True # session info tup


''' 
get the article for the current editor session.
'''
# @tracer.start_as_current_span("article fetch")
def get_article(request: Request,
                browser_id: UUID | None = None
                ):
    ''' 
    I am assuming that during the initialization
    process an editor session is created for the browser if
    one does not exists and an article is associated with the
    editor session.
    '''
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="session_depends",
    #                                func_name="get_article"
    # ))
    with tracer.start_as_current_span("get_article",
                                      attributes={
                                        **origination_(
                                          package="dependencies",
                                          module="session_depends",
                                          func_name="init_editor_session"
                                          ),
                                          "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        print(f"Entering get_article: ")
        # print(f"editor_session_id: {request.session.get("editor_session_id")}")
        # editor_session_id = UUID(request.session.get("editor_session_id"))

        # editor_session_id = None if editor_session_id is None else UUID(editor_session_id)
        print("browser_id: ", str(browser_id) )
        session = next(get_session())
        editor_session_id = session.exec(
            select(tool_model.EditorSession)
            .where(tool_model.EditorSession.browser_id == browser_id)
            .order_by(tool_model.EditorSession.created_at.desc())
        ).first().id
        current_span.set_attribute("editor_session_id", editor_session_id)
        article = session.exec(
            select(tool_model.Article)
            .where(tool_model.Article.editor_session_id == editor_session_id)
            .where(tool_model.EditorSession.browser_id == browser_id)
            .order_by(tool_model.Article.last_updated_at.desc())
        ).first()
        current_span.set_attribute("article_id", article.id)
        request.session['article_id'] = str(article.id) #if article is not None else None
        if article is not None:
            session.expunge(article)
    return article


'''

'''
# @tracer.start_as_current_span("article creation")
def create_new_article(request: Request):
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="session_depends",
    #                                func_name="create_new_article"
    # ))

    editor_session_id = request.session.get("editor_session_id")
    # current_span.set_attribute("editor_session_id", editor_session_id)
    author_id = request.session.get("user_id")
    # current_span.set_attribute("author_id", author_id)
    author_id = UUID(author_id) if author_id is not None else None
    article = tool_model.Article(editor_session_id=UUID(editor_session_id),
                                 author_id=author_id)
    with tracer.start_as_current_span("create_new_article",
                                      attributes={
                                          **origination_(
                                            package="dependencies",
                                            module="session_depends",
                                            func_name="create_new_article"
                                          ),
                                        "editor_session.id": editor_session_id,
                                        "user.id": author_id
                                      }) as current_span:
        session = next(get_session())
        session.add(article)
        session.commit()
        current_span.add_event("New article has been created")
        current_span.set_attribute("article_id", article.id)
        request.session['article_id'] = str(article.id)
        current_span.add_event("added article_id to the session")
    return article


# @tracer.start_as_current_span("store article data")
def store_article_data(request: Request, 
                       article_data: ArticleHead,
                       browser_id: Annotated[UUID | None, Cookie()] = None):
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="store_article_data"
    # ))
    with tracer.start_as_current_span("store_article_data",
                                      attributes={
                                          **origination_(
                                            package="dependencies",
                                            module="editorjs_data_store",
                                            func_name="store_article_data"
                                          ),
                                          "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        session = next(get_session())
        # article = session.get(tool_model.Article,
                            #   UUID(request.session.get("article_id")))
        article = get_article(request, browser_id)
        current_span.set_attribute("article.id", article.id)
        user_id = request.session.get("user_id")
        current_span.set_attribute("user.id", user_id)
        article.author_id = UUID(user_id) if user_id is not None else None
        title = None
        subtitle = None
        for block in article_data.blocks:
            if block.type == 'title':
                title = block.data.text
            elif block.type == 'subtitle':
                subtitle = block.data.text

        article.title = title
        article.subtitle = subtitle
        article.last_updated_at = datetime.fromtimestamp(article_data.time / 1000)
        session.add(article)
        session.commit()
        current_span.add_event("Article data has been stored inside the article")
        session.expunge(article)
    return article


''' 
this function is for getting the data of article head
from the database and then sending it to the frontend.
'''
# @tracer.start_as_current_span("load article head data", 
#                               attributes={"func_name": "load_article_head_data"})
def load_article_head_data(request: Request, 
                           browser_id: Annotated[UUID| None, Cookie()] 
                           ) -> ArticleHeadPublic:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="load_article_head_data"
    # ))
    with tracer.start_as_current_span("load_article_head_data",
                                      attributes={
                                          **origination_(
                                            package="dependencies",
                                            module="editorjs_data_store",
                                            func_name="load_article_head_data"
                                            ),
                                            "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        print("inside load_article_head_data")
        print(f"browser_id: {browser_id}")
        article = get_article(request, browser_id)
        current_span.add_event("article has been fetched successfully")
        current_span.set_attribute("article.id", article.id)

        article_pub = ArticleHeadPublic()
        title_block = TitleBlockPub(data=TitleHeaderDataPub(
            text=article.title
        ))
        subtitle_block = SubtitleBlockPub(data=SubtitleHeaderDataPub(
            text=article.subtitle
        ))
        article_pub.blocks = (title_block, subtitle_block)
        current_span.add_event("article data has been populated in ArticleHeadPublic BaseModel")
    return article_pub
    

@tracer.start_as_current_span("populate table data")
def populate_table_data(session: Session, 
                        tool_md_id: UUID) -> TableData:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_table_data"
    # ))
    # current_span.set_attribute("tool_md.id", str(tool_md_id))
    with tracer.start_as_current_span("populate_table_data",
                                      attributes={
                                          **origination_(
                                           package="dependencies",
                                           module="editorjs_data_store",
                                           func_name="populate_table_data"
                                            ),
                                            "tool_md.id": str(tool_md_id)
                                      }) as current_span:
        table_tool = session.exec(
            select(table_tool_model.TableTool)
            .where(table_tool_model.TableTool.tool_md_id == tool_md_id)
        ).one()
        current_span.add_event("table_tool data fetched")
        current_span.set_attribute("table_tool.id", table_tool.id)
        table_data = TableData.model_validate(table_tool)
    return table_data 

# @tracer.start_as_current_span("populate_codetool_data")
def populate_codetool_data(session: Session, 
                        tool_md_id: UUID) -> CodeToolData:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_codetool_data"
    # ))
    # current_span.set_attribute("tool_md.id", str(tool_md_id))
    with tracer.start_as_current_span("populate_codetool_data",
                                      attributes={
                                          **origination_(
                                           package="dependencies",
                                           module="editorjs_data_store",
                                           func_name="populate_codetool_data"
                                            ),
                                            "tool_md.id": str(tool_md_id)
                                      }) as current_span:
        code_tool = session.exec(
            select(code_tool_model.CodeTool)
            .where(code_tool_model.CodeTool.tool_md_id == tool_md_id)
        ).one()
        current_span.add_event("code tool data fetched")
        current_span.set_attribute("code_tool.id", code_tool.id)
        code_data = CodeToolData.model_validate(code_tool)
    return code_data

# @tracer.start_as_current_span("populate_paragraph_data")
def populate_paragraph_data(session: Session, 
                        tool_md_id: UUID) -> ParagraphData:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_paragraph_data"
    # ))
    # current_span.set_attribute("tool_md.id", str(tool_md_id))
    with tracer.start_as_current_span("populate_paragraph_data",
                                      attributes={
                                          **origination_(
                                           package="dependencies",
                                           module="editorjs_data_store",
                                           func_name="populate_paragraph_data"
                                            ),
                                            "tool_md.id": str(tool_md_id)
                                      }) as current_span:
        paragraph_tool = session.exec(
            select(paragraph_tool_model.ParagraphTool)
            .where(paragraph_tool_model.ParagraphTool.tool_md_id == tool_md_id)
        ).one()
        current_span.add_event("paragraph tool data fetched")
        current_span.set_attribute("paragraph_tool.id", paragraph_tool.id)
        paragraph_data = ParagraphData.model_validate(paragraph_tool) 
    return paragraph_data

# @tracer.start_as_current_span("populate_header_data")
def populate_header_data(session: Session, 
                        tool_md_id: UUID) -> HeaderData:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_header_data"
    # ))
    # current_span.set_attribute("tool_md.id", str(tool_md_id))
    with tracer.start_as_current_span("populate_header_data",
                                      attributes={
                                          **origination_(
                                           package="dependencies",
                                           module="editorjs_data_store",
                                           func_name="populate_header_data"
                                            ),
                                            "tool_md.id": str(tool_md_id)
                                      }) as current_span:
        header_tool = session.exec(
            select(header_tool_model.HeaderTool)
            .where(header_tool_model.HeaderTool.tool_md_id == tool_md_id)
        ).one()
        current_span.add_event("header tool data fetched")
        current_span.set_attribute("header_tool.id", header_tool.id)
        header_data = HeaderData.model_validate(header_tool) 
    return header_data

# @tracer.start_as_current_span("populate_quote_data")
def populate_quote_data(session: Session, 
                        tool_md_id: UUID) -> QuoteData:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_quote_data"
    # ))
    # current_span.set_attribute("tool_md.id", str(tool_md_id))
    with tracer.start_as_current_span("populate_quote_data",
                                      attributes={
                                          **origination_(
                                           package="dependencies",
                                           module="editorjs_data_store",
                                           func_name="populate_quote_data"
                                            ),
                                            "tool_md.id": str(tool_md_id)
                                      }) as current_span:
        quote_tool = session.exec(
            select(quote_tool_model.QuoteTool)
            .where(quote_tool_model.QuoteTool.tool_md_id == tool_md_id)
        ).one()
        current_span.add_event("quote tool data fetched")
        current_span.set_attribute("quote_tool.id", quote_tool.id)
        quote_data = QuoteData.model_validate(quote_tool) 
    return quote_data

@tracer.start_as_current_span("populate_list_item")
def populate_list_item(session: Session,
                       list_item: ListItem,
                       parent_item_id: UUID,
                       lttbl_id: UUID):
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_list_item"
    # ))
    # current_span.set_attribute("parent_id.id", str(parent_item_id))
    # current_span.set_attribute("list_tool_tbl.id", str(lttbl_id))
    with tracer.start_as_current_span("populate_list_item",
                                      attributes={
                                          **origination_(
                                           package="dependencies",
                                           module="editorjs_data_store",
                                           func_name="populate_list_item"
                                            ),
                                            "parent_id.id": str(parent_item_id),
                                            "list_tool_tbl.id": str(lttbl_id)
                                      }) as current_span:
        list_items_db = session.exec(
            select(list_tool_models.Item)
            # .where(list_tool_models.Item.lttbl_id == lttbl_id)
            .where(list_tool_models.Item.parent_item_id == parent_item_id)
            .order_by(list_tool_models.Item.sequence)
        ).all()
        current_span.add_event("list tool items from the db have been fetched")
        print(f"parent_item: {list_item}")
        if list_items_db == []:
            return 
        list_item_bmodel: List[ListItem] = []
        for item in list_items_db:
            parent_item_id = item.id
            if parent_item_id is None:
                continue
            tmp_list_item = ListItem(content=item.content, meta=item.meta, items=[])
            populate_list_item(session, 
                               list_item, 
                               parent_item_id,
                               lttbl_id)
            list_item_bmodel.append(tmp_list_item)
        list_item.items = list_item_bmodel


# @tracer.start_as_current_span("populate_list_data")
def populate_list_data(session: Session, 
                        tool_md_id: UUID) -> ListData:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_list_data"
    # ))
    # current_span.set_attribute("tool_md.id", str(tool_md_id))
    with tracer.start_as_current_span("populate_list_data",
                                      attributes={
                                          **origination_(
                                           package="dependencies",
                                           module="editorjs_data_store",
                                           func_name="populate_list_data"
                                            ),
                                            "tool_md.id": str(tool_md_id)
                                      }) as current_span:
        list_tool = session.exec(
            select(list_tool_models.ListToolTbl)
            .where(list_tool_models.ListToolTbl.tool_md_id == tool_md_id)
        ).one() 
        current_span.add_event("list tool tbl for tool_md has been fetched")
        list_items_db = session.exec(
            select(list_tool_models.Item)
            .where(list_tool_models.Item.lttbl_id == list_tool.id)
            .where(list_tool_models.Item.parent_item_id == None)
            .order_by(list_tool_models.Item.sequence)
        ).all()

        list_items: List[ListItem] = []
        for list_item_db in list_items_db:
            parent_item_id = list_item_db.id 
            list_item = ListItem(content=list_item_db.content, meta=list_item_db.meta, items=[])
            populate_list_item(session, list_item, parent_item_id, list_tool.id)
            list_items.append(list_item)

        print(list_items)
        list_data = ListData(style=list_tool.style, 
                             meta=list_tool.meta,
                             items=list_items
                            )
    return list_data


population_funcs = {
    "table": populate_table_data,
    "code": populate_codetool_data,
    "paragraph": populate_paragraph_data,
    "header": populate_header_data,
    "quote": populate_quote_data,
    "list": populate_list_data
}


''' 
populating data from the db tables in the
EditorJSSessionData object.
'''
# @tracer.start_as_current_span("populate_editorjs_session")
def populate_editorjs_session(article_id: UUID) -> EditorJSSessionData:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="populate_editorjs_session"
    # ))
    # current_span.set_attribute("article.id", str(article_id))
    with tracer.start_as_current_span("populate_editorjs_session",
                                      attributes={
                                        **origination_(
                                            package="dependencies",
                                            module="editorjs_data_store",
                                            func_name="populate_editorjs_session"
                                        ),
                                        "article.id": str(article_id)
                                      }) as current_span:
        session = next(get_session())
        tool_mds = session.exec(
            select(tool_model.ToolMD)
            .where(tool_model.ToolMD.article_id == article_id)
            .order_by(tool_model.ToolMD.sequence)
        ).all()
        current_span.add_event("all the tool_mds have been fetched")
        if tool_mds == []:
            return EditorJSSessionDataPub(
                time=int(datetime.now().timestamp()),
                blocks=[],
                version="0.0"
            )
        time = tool_mds[0].time
        version = tool_mds[0].version
        blocks = []
        for tool_md in tool_mds:
            populate_data_func = population_funcs.get(tool_md.tool.name, None)
            data = populate_data_func(session, tool_md.id)
            current_span.add_event("got the data for the tool_md from the tool_tbl")
            block = Block(
                id = tool_md.block_id,
                type= tool_md.tool.name,
                sequence= tool_md.sequence,
                data=data
            )
            blocks.append(block)

        editorjs_session_data = EditorJSSessionData(time=int(time.timestamp()),
                                                    blocks=blocks,
                                                    version=version,
                                                    article_id=str(article_id)
                                                    )
    return editorjs_session_data

''' 
this function is for fetching the previous saved
data for the article body from the database.
'''
# @tracer.start_as_current_span("load_article_body_data")
def load_article_body_data(request: Request,
                           browser_id: Annotated[UUID | None, Cookie()]
                           ) -> EditorJSSessionDataPub:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="load_article_body_data"
    # ))
    with tracer.start_as_current_span("load_article_body_data",
                                      attributes={
                                        **origination_(
                                            package="dependencies",
                                            module="editorjs_data_store",
                                            func_name="load_article_body_data"
                                        ),
                                        "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
    # if browser_id is not None:
    #     current_span.set_attribute("browser_id", str(browser_id))
        article = get_article(request, browser_id)
        editorjs_session_data = populate_editorjs_session(article.id)
    return EditorJSSessionDataPub.model_validate(editorjs_session_data)


''' 
orchestrating the sessions.
'''
# @tracer.start_as_current_span("editor_session_orchestrator")
def editor_session_orchestrator(request: Request,
                                response: Response,
                                browser_id: Annotated[UUID | None, Cookie()] = None) -> tool_model.EditorSession:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="editor_session_orchestrator"
    # ))
    with tracer.start_as_current_span("editor_session_orchestrator",
                                      attributes={
                                        **origination_(
                                        package="dependencies",
                                        module="editorjs_data_store",
                                        func_name="editor_session_orchestrator"
                                        ),
                                        "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        editor_session = get_editor_session(request, response, browser_id=browser_id) 
        if editor_session is None:
            editor_session = create_editor_session(request, response)
            return editor_session
    return editor_session

# @tracer.start_as_current_span("get_curr_article_or_make_new")
def get_curr_article_or_make_new(request: Request, 
                    response: Response,
                    browser_id: Annotated[UUID | None, Cookie()] = None):
    ''' 
        This should get the last article which was present on the editor.
    '''
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="get_curr_article_or_make_new"
    # ))
    with tracer.start_as_current_span("get_curr_article_or_make_new",
                                      attributes={
                                        **origination_(
                                        package="dependencies",
                                        module="editorjs_data_store",
                                        func_name="get_curr_article_or_make_new"
                                        ),
                                        "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        user_id = UUID(request.session.get("user_id"))
        session = next(get_session())
        if user_id:
            current_span.add_event("if block: user_id is not none. Processing records for logged in user")
            current_span.set_attribute("user_id", user_id)
            curr_user = session.exec(
                select(user_model.User)
                .where(user_model.User.id == user_id)
            )

            editor_session = session.exec(
                select(tool_model.EditorSession)
                .where(tool_model.EditorSession.browser_id == browser_id)
                .where(or_(
                    tool_model.EditorSession.user_id == curr_user.id,
                    tool_model.EditorSession.user_id == None) )
                .order_by(
                    tool_model.EditorSession.created_at.desc()
                )
            ).first() 

            # if the editor session does not exists for that browser
            # create a new editor session with new article
            if editor_session is None:
                current_span.add_event("if block: creating editor session as editor session does not exists")
                editor_session = create_editor_session(request, response)
                article = tool_model.Article(editor_session_id= editor_session.id)
                session.add(article)
                session.commit(article)
            else:
                current_span.add_event("else block: editor session exists")
                current_span.add_event("getting the article for the current session")
                article = session.exec(
                    select(tool_model.Article)
                    .where(tool_model.Article.editor_session_id == editor_session.id)
                )
        else: 
            current_span.add_event("else block: user_id is None")
            editor_session = session.exec(
                select(tool_model.EditorSession)
                .where(tool_model.EditorSession.browser_id == browser_id)
                .order_by(tool_model.EditorSession.created_at.desc())
            ).first()

            if editor_session is None:
                current_span.add_event("if block: creating editor session as editor session does not exists")
                editor_session = create_editor_session(request, response)
                article = tool_model.Article(editor_session_id= editor_session.id)
                session.add(article)
                session.commit(article)
            else:
                current_span.add_event("else block: editor session exists")
                article = session.exec(
                    select(tool_model.Article)
                    .where(tool_model.Article.editor_session_id == editor_session.id)
                )
    return article

'''
- delete those editor sessions which are expired.
'''

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str :
    hash = pwd_context.hash(password.encode("utf-8"))
    return hash

def verify_password(password: str, hashed_password: str)->bool:
    return pwd_context.verify(password, hashed_password)

'''
Following functions will do the login for a user.

Adding the tracing by creating a span on the function
'''
# @tracer.start_as_current_span("user_login")
def user_login(request: Request, 
               response: Response, 
               user: Annotated[SigninBaseModel, Form()], 
               browser_id: Annotated[UUID | None, Cookie()] = None) -> dict:
    ''' 
    This function will login an already existing user.
    '''
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="user_login"
    # ))
    with tracer.start_as_current_span("user_login",
                                      attributes={
                                        **origination_(
                                        package="dependencies",
                                        module="editorjs_data_store",
                                        func_name="user_login"
                                        ),
                                        "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
    
        if browser_id is None:
            editor_session = create_editor_session(request, response)
        else:
            editor_session = get_editor_session(request, browser_id)
            # if the editor session has expired, create a new session
            if editor_session is None:
                editor_session = create_editor_session(request, response)

        session = next(get_session())

        # get the existing user
        existing_user_dict = None 
        try: 
            if '@' in user.username_or_email:
                # print("inside @")
                email = user.username_or_email
                # print("email: ", email)
                existing_user = session.exec(
                    select(user_model.User)
                    .where(user_model.User.email == email)
                ).one()
            else:
                username = user.username_or_email
                existing_user = session.exec(
                    select(user_model.User)
                    .where(user_model.User.username == username)
                ).one()
            existing_user_pub = user_model.UserPublic.model_validate(existing_user)
        except NoResultFound:
            e = HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail="User not found")
            current_span.set_status(Status(StatusCode.ERROR))
            current_span.record_exception(e)
            raise e


        # check if the password is correct with the hash present in the db
        is_correct = verify_password(user.password, existing_user.hashed_password)
        current_span.add_event("user entered password has been verified")
        if is_correct:
            request.session["user_id"] = str(existing_user.id)
            request.session["username"] = existing_user.username
            request.session["email"] = existing_user.email
            existing_user.is_logged_in = True 
            existing_user.last_login = datetime.now()
            editor_session.user_id = existing_user.id  
            editor_session.logged_in = True 
            # print("Existing user 1")
            # print(existing_user)
            session.add(existing_user)
            session.add(editor_session)
            session.commit() 
            # print("Existing user")
            # print(existing_user)
        else:
            e = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Password is incorrect")
            current_span.set_status(Status(StatusCode.ERROR))
            current_span.record_exception(e)
            raise e 
        # pass 
        # print("hello world")
        # print(existing_user)
        current_span.add_event("user has been logged in")
    return existing_user_pub


# @tracer.start_as_current_span("user_signup")
def user_signup(request: Request,
                response: Response,
                user_create: Annotated[user_model.UserCreate, Form()] ,
                browser_id: Annotated[UUID | None, Cookie()] = None
                ) -> user_model.UserPublic:
    ''' 
    This function will register a new user and logs in the user.
    '''
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="user_signup"
    # ))
    with tracer.start_as_current_span("user_signup",
                                      attributes={
                                        **origination_(
                                        package="dependencies",
                                        module="editorjs_data_store",
                                        func_name="user_signup"
                                        ),
                                        "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
    # create a user.
        session = next(get_session())
        hashed_password = hash_password(user_create.password)
        try:
            new_user = user_model.User.model_validate(user_create, update={
                "hashed_password": hashed_password,
                "last_login": datetime.now()
                })
        except ValidationError as e:
            # print(user_model.User.model_validate(user_create, update={"hashed_password": hashed_password}))
            # print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="username field should not contain '@' symbol"
            )
        new_user.is_logged_in = True
        new_user.last_login = datetime.now()
        try:
            session.add(new_user)
            # session.commit()
        except IntegrityError as e:
            # session.rollback()
            current_span.set_status(Status(StatusCode.ERROR))
            current_span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with the same email or username already exists"
            )
        request.session["user_id"] = str(new_user.id)
        request.session["username"] = new_user.username
        request.session["email"] = new_user.email

        # using the browser id check if an editor session
        # exists for that device.
            # If it doesn't exists then create new session and 
            # add the user id to that session
            # else add user id to the existing session.
        if browser_id is None:
            editor_session = create_editor_session(request, response)
        else: 
            editor_session = get_editor_session(request, browser_id)
            if editor_session is None:
                editor_session = create_editor_session(request, response)
        editor_session.user_id = new_user.id
        editor_session.logged_in = True 
        session.add(editor_session)
        pub_user = user_model.UserPublic.model_validate(new_user)
        # pub_user_dict = pub_user.model_dump(mode="json")
        session.commit()
    return pub_user


# @tracer.start_as_current_span("user_logout")
def user_logout(request: Request,
                response: Response,
                browser_id: Annotated[UUID | None, Cookie()] = None) -> bool:
    # current_span = trace.get_current_span()
    # current_span.set_attributes(origination_(
    #                                package="dependencies",
    #                                module="editorjs_data_store",
    #                                func_name="user_logout"
    # ))
    # if browser_id is not None:
    #     current_span.set_attribute("browser_id", browser_id)
    with tracer.start_as_current_span("user_logout",
                                      attributes={
                                        **origination_(
                                        package="dependencies",
                                        module="editorjs_data_store",
                                        func_name="user_logout"
                                        ),
                                        "browser_id": "-" if browser_id is None else str(browser_id)
                                      }) as current_span:
        session = next(get_session())
        user_id = UUID(request.session.get("user_id"))
        current_span.set_attribute("user_id")
        editor_session = get_editor_session(request, browser_id) if browser_id is not None else None 
        if editor_session:
            editor_session.logged_in = False
            session.add(editor_session)

        if user_id:
            user = session.get(user_model.User, user_id)
            if user is None:
                # this is a big error in the system.
                # application should crash in development here if this occurs
                pass 
            request.session["user_id"] = None 
            request.session["username"] = None 
            request.session["email"] = None 
            user.is_logged_in = False 
            user.last_login = datetime.now()
            session.add(user)
        session.commit()
        # We are giving here browser id as
        # None because we want it to create a new 
        # editor session, browser_id and article.
        res = init_editor_session(request, response, browser_id=None)
        current_span.add_event("initialized the editor session after logout")
    return res 



def persist_editor_data():

    '''
    - condition: does 

    '''

    # create a editor session in the db 
    # whenever data is sent, store it in the db
    # 