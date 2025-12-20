import pytest
from typing import Literal, Tuple, Generator, Callable
from model import tool_model, code_tool_model
from editorjs_basemodel import Block, EditorJSSessionData
from sqlmodel import Session, select
from dependencies.editorjs_data_store import tool_name_cls_map, store_editorjs_data
import uuid
from sqlalchemy.exc import InvalidRequestError
import json
from conftest import update_func_map, TEST_DATA_FILE, add_tool_md, func_map


@pytest.mark.parametrize("insertion_data_and_func", ["table","code","paragraph","header","quote", "unordered-list", "ordered-list", "checklist"], indirect=True)
def test_insertion_methods(insertion_result: Tuple[tool_model.ToolDataModel, tool_model.ToolDataModel]):
    tool_data_model, td_model = insertion_result
    assert td_model == tool_data_model


@pytest.fixture(name="case1_blocks")
def get_test_block_case1(request) -> list[Block]:
    tool_name = request.param
    with open(TEST_DATA_FILE, 'r') as f:
        data = json.load(f)
        updation_td = data["tests"]["updation-test-data"]["case_1_tests"] # updation test data
        tool_td = updation_td[f"{tool_name}-data"]
    # create a list of blocks and return
    block_list = [ Block.model_validate(block_data) 
                  for block_data in tool_td
                  ]
    return block_list


@pytest.fixture(name="case1_updated_tools")
def updated_tools(case1_blocks: list[Block],
                  ready_session: Session,
                  article_id: uuid.UUID,
                  ) -> Callable[[], 
                                Generator[
                                Tuple[tool_model.ToolDataModel, tool_model.ToolDataModel],
                                None,
                                None
                                ]
                                ]:
    def gen_updated_tools() -> Generator[
                      Tuple[tool_model.ToolDataModel, tool_model.ToolDataModel],
                      None,
                      None
                      ]:
        nonlocal ready_session
        first = case1_blocks[0]
        ready_session, tool_md = add_tool_md(ready_session, first, article_id)
        ready_session, db_obj = func_map[first.type](ready_session, first, tool_md.id)

        for block in case1_blocks[1::]:
            block.id = uuid.uuid4()
            ready_session, update_obj = update_func_map[block.type](ready_session, block, tool_md)
            ready_session.refresh(db_obj)
            yield (update_obj, db_obj) # both of these values should be compared with each other in the test case
    return gen_updated_tools

@pytest.mark.parametrize("case1_blocks", ["table","code","paragraph","header","quote", "unordered-list", "ordered-list", "checklist"], indirect=True)
def test_updation_methods_case1(case1_updated_tools
                                : Callable[[], 
                                Generator[
                                Tuple[tool_model.ToolDataModel, tool_model.ToolDataModel],
                                None,
                                None
                                ]
                                ]):
    try:
        update_tool_gen = case1_updated_tools()
        while True:
            updated_tool, created_tool = next(update_tool_gen)
            assert updated_tool == created_tool
    except StopIteration:
        return


""" 
1. check if the tool_name has been updated in tool_md
2. check the class of the newly created updated_obj
3. check if the object which was created earlier exists.
"""
@pytest.mark.parametrize("case2_blocks", ["table","code","paragraph","header","quote", "unordered-list", "ordered-list", "checklist"], indirect=True)
def test_updation_methods_case2(case2_updated_tools: Callable[[],
              Generator[  
                  Tuple[tool_model.ToolMD, 
                        tool_model.ToolDataModel, 
                        tool_model.ToolDataModel
                        ],  
                        None,  
                        None ]
                ] , ready_session: Session):
    update_tool_gen = case2_updated_tools()

    try:
        while True:
            tool_md, updated_obj, initial_obj = next(update_tool_gen)

            if type(tool_md.id) != uuid.UUID:
                raise ValueError("id for tool_md is not uuid")
            created_tool_name = ready_session.get(tool_model.ToolMD,
                                                  initial_obj.tool_md_id).tool.name
            updated_tool_md = ready_session.exec(
                select(tool_model.ToolMD)
                .where(tool_model.ToolMD.id == updated_obj.tool_md_id)
            ).one()
            created_obj_cls = tool_name_cls_map[created_tool_name]
            created_obj = ready_session.get(created_obj_cls, initial_obj.id)
            tool_data_cls = tool_name_cls_map[updated_tool_md.tool.name]
            assert tool_md == updated_tool_md
            assert type(updated_obj) == tool_data_cls
            with pytest.raises(InvalidRequestError):
                ready_session.refresh(initial_obj)
            assert created_obj == None
    except StopIteration:
        return 


def test_editorjs_data_storage(session: Session):
    # with Session()
    article_id = session.exec(
        select(tool_model.Article)
        .limit(1)
    ).first().id

    data = {"time": 1761490303048,
            "blocks":[
                {"id":"PCdE5q0ExS",
                 "type":"paragraph",
                 "data":{"text":"hii"}
                 },
                 {"id":"g-Cn8w_9fH",
                  "type":"paragraph",
                  "data":{"text":"hello"}
                  },
                  {"id":"638i8uEpJT",
                   "type":"header",
                   "data":{"text":"how are you guys?","level":2}
                   },
                   {"id":"bp1dabjWiY",
                    "type":"paragraph",
                    "data":{"text":"I hope you are fine"}
                    }
                ],
                "version":"2.31.0",
                "logged_in_session_id":"abcdf",
                "browser_session_id":"dbshfg",
                "article_id":f"{article_id}"
                }
    
    store_editorjs_data(EditorJSSessionData.model_validate(data))