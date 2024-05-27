from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    SystemMessage
)
from langchain_core.prompts import PromptTemplate
from typing import Callable

model = None
systemMessage = None


def initLlm(system_message: str, modelName: str = "gpt-4o", temperature: float = 0.7):
    global systemMessage
    global model
    systemMessage = SystemMessage(content=system_message)
    model = ChatOpenAI(temperature=temperature, model_name=modelName)


def getLlmReply(
        promptName: str,
        promptTemplateFile: str,
        outputFilename: str = None,
        templateStringVariables: dict = {},
        templateFileVariables: dict = {},
        mockLlm: bool = False,
        debug: bool = False,
        postProcessors: [Callable[[str], str]] = [],) -> str:
    if mockLlm:
        print(f"{promptName}: skip llm call and read llm reply from disk")
        if outputFilename is None:
            print("file name wasn't provided, even though mockLlm was set to `True` - returning `None`")
            return None
        with open(outputFilename, 'r') as file:
            llmReply = file.read()
    else:
        print(f"{promptName}: template rendering")
        prompt = renderPrompt(templateStringVariables, templateFileVariables, promptTemplateFile)
        if debug:
            print(f"Prompt {promptName}:\n{prompt}")
        print(f"{promptName}: LLM call")
        llmReply = model.invoke([systemMessage, prompt])
        for postProcessor in postProcessors:
            llmReply = postProcessor(llmReply.content)
        if outputFilename is not None:
            with open(outputFilename, 'w') as file:
                print(llmReply.content, file=file)
        print(f"{promptName}: LLM reply")
    return llmReply.content


def renderPrompt(
        templateStringVariables: dict,
        templateFileVariables: dict,
        promptTemplateFile: str,) -> HumanMessage:
    templateVariables = templateStringVariables
    for key, templateStringVariable in templateFileVariables.items():
        with open(templateFileVariables[key], "r") as file:
            templateVariables[key] = file.read()
    with open(promptTemplateFile, "r") as file:
        promptTemplate = PromptTemplate.from_template(file.read())
    prompt = promptTemplate.format(**templateVariables)
    return prompt
