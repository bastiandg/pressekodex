from typing import Tuple
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    HumanMessage,
    SystemMessage
)
from langchain_core.prompts import PromptTemplate
from typing import Callable


class LLM:
    def __init__(self, outputTokenCost: float, inputTokenCost: float, provider: str, modelName: str, model: BaseChatModel = None):
        self.outputTokenCost = outputTokenCost
        self.inputTokenCost = inputTokenCost
        self.provider = provider
        self.modelName = modelName
        self.model = model

    def calculateCost(self, responseMetadata: dict) -> float:
        inputTokens = responseMetadata["usage"]["input_tokens"] if self.provider == "Anthropic" else responseMetadata["token_usage"]["prompt_tokens"]
        outputTokens = responseMetadata["usage"]["output_tokens"] if self.provider == "Anthropic" else responseMetadata["token_usage"]["completion_tokens"]
        inputCost = (inputTokens * self.inputTokenCost) / 1000000
        outputCost = (outputTokens * self.outputTokenCost) / 1000000
        totalCost = inputCost + outputCost
        return totalCost

    def initLlm(self):
        if self.provider == "Anthropic":
            self.model = ChatAnthropic(model_name=self.modelName)
        elif self.provider == "OpenAI":
            self.model = ChatOpenAI(model_name=self.modelName)


llms = {
    "haiku": LLM(inputTokenCost=0.25, outputTokenCost=1.25, provider="Anthropic", modelName="claude-3-haiku-20240307"),
    "sonnet": LLM(inputTokenCost=3, outputTokenCost=15, provider="Anthropic", modelName="claude-3-sonnet-20240229"),
    "opus": LLM(inputTokenCost=15, outputTokenCost=75, provider="Anthropic", modelName="claude-3-opus-20240229"),
    "gpt4": LLM(inputTokenCost=5, outputTokenCost=15, provider="OpenAI", modelName="gpt-4o")
}


def getLlmReply(
        systemMessage: str,
        promptName: str,
        promptTemplateFile: str,
        outputFilename: str = None,
        templateStringVariables: dict = {},
        templateFileVariables: dict = {},
        mockLlm: bool = False,
        debug: bool = False,
        modelClass: str = "haiku",
        postProcessors: [Callable[[str], str]] = [],) -> Tuple[str, float]:
    if modelClass not in llms.keys():
        raise Exception("Model not supported")
        return None
    if mockLlm:
        print(f"{promptName}: skip llm call and read llm reply from disk")
        if outputFilename is None:
            print("file name wasn't provided, even though mockLlm was set to `True` - returning `None`")
            return None
        with open(outputFilename, 'r') as file:
            storedReply = file.read()
        return storedReply, 0.0
    else:
        print(f"{promptName}: template rendering")
        prompt = renderPrompt(templateStringVariables, templateFileVariables, promptTemplateFile)
        if debug:
            print(f"Prompt {promptName}:\n{prompt}")
        print(f"{promptName}: LLM call")
        if llms[modelClass].model is None:
            llms[modelClass].initLlm()
        llmReply = llms[modelClass].model.invoke([SystemMessage(content=systemMessage), prompt])
        cost = llms[modelClass].calculateCost(llmReply.response_metadata)
        print(f"response_metadata: {llmReply.response_metadata}")
        for postProcessor in postProcessors:
            llmReply = postProcessor(llmReply.content)
        if outputFilename is not None:
            with open(outputFilename, 'w') as file:
                print(llmReply.content, file=file)
        return llmReply.content, cost


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
