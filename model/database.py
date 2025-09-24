from sqlmodel import SQLModel, create_engine
from code_tool_model import *
from header_tool_model import *
from list_tool_models import *
from paragraph_tool_model import *
from quote_tool_model import *
from table_tool_model import *
from tool_model import *

sqlite_url = "sqlite:///testing.db"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)

