from fastapi import Response, Request, Cookie, Form, HTTPException, status
from model import tool_model, user_model
from database import get_session
from uuid import UUID
from typing import Annotated
from sqlmodel import select
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound, IntegrityError
from datetime import datetime, timedelta
from user_basemodel import SigninBaseModel, SignupBaseModel
from passlib.context import CryptContext


'''
create a session object and set the session id 
and browser_id as the cookies.
- Also create a new article and set the article id for the session.
- A new article should be created only when an event is triggered in the frontend.
- We create an article now with just the session id. When the user logins we will 
we will change the author id for the user from None to current username.
- A batch job is necessary for clearing the articles which does not have a title, subtitle, and toolmds.
'''
def create_editor_session(request: Request, response: Response ) -> tool_model.EditorSession:
    session = next(get_session())
    editor_session = tool_model.EditorSession(expiry_date=datetime.now()+timedelta(days=1))
    session.add(editor_session)
    article = tool_model.Article(editor_session_id=editor_session.id)
    session.add(article)
    session.commit()
    # response.set_cookie(
    #     key="editor_session_id",
    #     value=editor_session.id
    # )
    response.set_cookie(
        key="browser_id",
        value=str(editor_session.browser_id)
    )
    # whenever we will need to fetch the data for 
    # previous application state. We'll fetch it through 
    # the browser_id key stored as a cookie on the browser.
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
def get_editor_session(request, response, browser_id: UUID | None = None):
    # print(f"browser id: {browser_id}")
    session = next(get_session())
    if browser_id:
        try:
            editor_session = session.exec(
                select(tool_model.EditorSession)
                .where(tool_model.EditorSession.browser_id == browser_id)
            ).one()
            session.expunge(editor_session)
        except NoResultFound:
            editor_session = create_editor_session(request, response)
        if editor_session.expiry_date > datetime.now():
            return editor_session
        return None 
    return None 

''' 
orachestrating the sessions.
'''
def editor_session_orchestrator(request: Request,
                                response: Response,
                                browser_id: Annotated[UUID | None, Cookie()] = None) -> tool_model.EditorSession:
    editor_session = get_editor_session(request, response, browser_id=browser_id) 
    if editor_session is None:
        editor_session = create_editor_session(request, response)
        return editor_session
    return editor_session

def get_curr_article_or_make_new(request: Request, 
                    response: Response,
                    browser_id: Annotated[UUID | None, Cookie()] = None):
    ''' 
        This should get the last article which was present on the editor.
    '''
    user_id = request.session.get("user_id")
    session = next(get_session())
    if user_id:
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
            editor_session = create_editor_session(request, response)
            article = tool_model.Article(editor_session_id= editor_session.id)
            session.add(article)
            session.commit(article)
        else:
            article = session.exec(
                select(tool_model.Article)
                .where(tool_model.Article.editor_session_id == editor_session.id)
            )
    else: 
        editor_session = session.exec(
            select(tool_model.EditorSession)
            .where(tool_model.EditorSession.browser_id == browser_id)
            .order_by(tool_model.EditorSession.created_at.desc())
        ).first()

        if editor_session is None:
            editor_session = create_editor_session(request, response)
            article = tool_model.Article(editor_session_id= editor_session.id)
            session.add(article)
            session.commit(article)
        else:
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
'''
def user_login(request: Request, 
               response: Response, 
               user: Annotated[SigninBaseModel, Form()], 
               browser_id: Annotated[UUID | None, Cookie()] = None) -> dict:
    ''' 
    This function will login an already existing user.
    '''
    if browser_id is None:
        editor_session = create_editor_session(request, response)
    else:
        editor_session = get_editor_session(request, response, browser_id)
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
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail="User not found")


    # check if the password is correct with the hash present in the db
    is_correct = verify_password(user.password, existing_user.hashed_password)
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Password is incorrect")
    # pass 
    # print("hello world")
    # print(existing_user)
    return existing_user_pub


def user_signup(request: Request,
                response: Response,
                user_create: Annotated[user_model.UserCreate, Form()] ,
                browser_id: Annotated[UUID | None, Cookie()] = None
                ) -> user_model.UserPublic:
    ''' 
    This function will register a new user and logs in the user.
    '''

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
    except IntegrityError:
        # session.rollback()
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
        editor_session = get_editor_session(request, response, browser_id)
        if editor_session is None:
            editor_session = create_editor_session(request, response)
    editor_session.user_id = new_user.id
    editor_session.logged_in = True 
    session.add(editor_session)
    pub_user = user_model.UserPublic.model_validate(new_user)
    # pub_user_dict = pub_user.model_dump(mode="json")
    session.commit()
    return pub_user


def user_logout(request: Request,
                response: Response,
                browser_id: Annotated[UUID | None, Cookie()] = None) -> bool:
    session = next(get_session())
    user_id = request.session.get("user_id")

    editor_session = get_editor_session(request, response, browser_id) if browser_id is not None else None 
    if editor_session:
        editor_session.logged_in = False
        session.add(editor_session)

    if user_id:
        user = session.get(user_model.User, UUID(user_id))
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
    return True 



def persist_editor_data():

    '''
    - condition: does 

    '''

    # create a editor session in the db 
    # whenever data is sent, store it in the db
    # 