from typing import Callable
from transformers.utils import get_json_schema


def get_tool_dict(tool: Callable) -> dict:
    """
    Get a tool's dictionary representation.  This is based on the
    docstring on the passed function, as in
    https://huggingface.co/blog/unified-tool-use
    """
    d = get_json_schema(tool)
    # 'return' is not a standard field for tools even though it can
    # be present in the function docstring, so we remove it
    if "return" in d["function"]:
        del d["function"]["return"]
    return d


class Tool:
    def __init__(self):
        raise NotImplementedError

    def __call__(self, **kwargs) -> str:
        raise NotImplementedError

    def get_tool_dict(self) -> dict:
        raise NotImplementedError
