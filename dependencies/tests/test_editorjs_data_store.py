# from dependencies.editorjs_data_store import add_code_tool_data, add_header_tool_data, add_list_tool_data, add_paragraph_tool_data, add_quote_tool_data, add_table_tool_data, add_tool_md, tool_name_cls_map
# from sqlmodel import SQLModel, create_engine, Session, select
# from model import code_tool_model, header_tool_model, list_tool_models, paragraph_tool_model, quote_tool_model, table_tool_model, tool_model
import pytest
# import json
# from dotenv import load_dotenv
# import os
# from sqlalchemy.exc import IntegrityError
# import random
# from editorjs_basemodel import Block
from typing import Tuple
from model import tool_model
# import uuid



# def db_setup():



@pytest.mark.parametrize("insertion_data_and_func", ["table","code","paragraph","header","quote", "unordered-list", "ordered-list", "checklist"], indirect=True)
def test_insertion_methods(insertion_result: Tuple[tool_model.ToolDataModel, tool_model.ToolDataModel]):
    tool_data_model, td_model = insertion_result
    assert td_model == tool_data_model


