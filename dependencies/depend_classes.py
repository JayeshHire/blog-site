from database import get_session
from sqlmodel import select
from model.tool_model import EditorSession
from fastapi import Request, Response
import uuid
from datetime import datetime
from enum import Enum


def get_editor_session(user_id: uuid.UUID, browser_id):
    session = next(get_session())
    editor_session = session.exec(
        select(EditorSession)
        .where(EditorSession.browser_id == browser_id)
        .where(EditorSession.user_id == user_id)
    ).first()
    session.expunge(editor_session)
    
    # editor session should not be expired
    if editor_session.expiry_date > datetime.now():
        return editor_session
    
    return None 


def create_editor_session(user_id: uuid.UUID | None = None):
    # user_id of the current logged in user should be passed here
    session = next(get_session())
    editor_session = EditorSession(logged_in=True, 
                                   user_id=user_id, 
                                   expiry_date= datetime.now())
    session.add(editor_session)
    session.commit()
    session.expunge(editor_session)
    return editor_session


def close_editor_session(response: Response, editor_session: EditorSession):
    session = next(get_session())
    editor_session.expiry_date = datetime.now()
    editor_session.isopen = False
    editor_session.logged_in = False 
    session.merge(editor_session)
    session.commit()
    response.delete_cookie(key="browser_id")
    

# def set_editor_session_cookie(browser_id: uuid.UUID | None = None):

class ModelSessMgr():
    pass 

class EditorSesMgr(ModelSessMgr):
    class ESessionUIDEum(Enum):
        USER_ID = 'user_id'
        EDITOR_SESSION_ID = 'editor_session_id'
        BROWSER_ID = 'browser_id'

    '''
    editor_session object should be refreshed if any update
    operation is performed on the session.
    '''

    def __init__(self, user_id: uuid.UUID, browser_id = None):
        self.browser_id = browser_id
        editor_session = get_editor_session(user_id, browser_id) if browser_id is not None else create_editor_session(user_id)
        
        if editor_session is None:
            editor_session = create_editor_session(browser_id, user_id)
    
        # setting the cookie is remaining here

    def close(self):
        # close the editor session
        pass 
    
    def open(self):
        # open the editor session
        # by default the editor session is open
        pass 

    def get_editor_session(uid: uuid.UUID, 
                           field: ESessionUIDEum = ESessionUIDEum.BROWSER_ID
                        #    by default it will search for editor_session by the browser_id
                        # if the field type is not given.
                           ):
        pass 

    def create_editor_session(user_id: uuid.UUID): # provide user id if user is logged in
        pass 

    def user_logged_in(self): 
        # this function does not make the exact check about the user login
        # but it just executes and updates the state of user in the session table

        pass 

    def user_logged_out(self):
        # changes the state of the editor_session user login status
        # to logged out.
        pass 

    def get_logged_in_user(func, request: Request, response: Response):

        def wrapper():
            session = next(get_session())
       
    def perf_op_checker(func):
        ''' 
        This function sees whether the operation should 
        be performed or not for the editor session.
        '''
        def wrapper(esession_mgr: EditorSesMgr):

    pass 

def driver(request: Request, 
           response: Response,
           session_mgr: ModelSessMgr
           ):
    


class UserSesMgr(ModelSessMgr):

    pass 

class EditorSesDataMgr(ModelSessMgr):

    pass 

