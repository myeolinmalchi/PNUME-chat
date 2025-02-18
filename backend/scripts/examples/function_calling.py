from time import time

from dependency_injector.wiring import Provide, inject
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat_model import ChatModel
from containers.app import AppContainer
from typing import List

from openai import OpenAI
from config.logger import _logger
from services.app import prompt
from services.app.app import ApplicationService
from services.app.tools import TOOLS

logger = _logger(__name__)

client = OpenAI()

context_dump = """
<ContextDump>
    <SearchHistory>
{}
    </SearchHistory>
</ContextDump>
"""

model: ChatModel = "o3-mini-2025-01-31"


def init_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", dest="query", required=True)
    parser.add_argument("-d", "--department", dest="department", required=True)
    parser.add_argument("-g", "--grade", dest="grade", required=True)
    parser.add_argument("-v", "--verbose", dest="verbose", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    query = str(args.query)
    department = str(args.department)
    grade = int(args.grade)

    return query, department, grade


@inject
def main(app: ApplicationService = Provide[AppContainer.app]):

    st = time()
    contexts: str = ""
    query, deps, grade = init_args()

    while True:
        prompt_ = prompt(query, deps, grade, contexts)

        messages: List[ChatCompletionMessageParam] = [{"role": "user", "content": prompt_}]
        completion = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS, tool_choice="auto", reasoning_effort="low"
        )
        result = app.parse_chat_completion(completion)

        if not result:
            break

        if isinstance(result, str):
            print(f"답변({time() - st:.2f}sec): \n\n{result}")
            break

        history = "\n".join(result)
        contexts += "\n" + history


if __name__ == "__main__":

    app = AppContainer()
    app.init_resources()
    app.wire(modules=[__name__])

    main()
