from langchain_openai import AzureChatOpenAI

from configs.config import AZURE_OPENAI_CONFIG

AGENT_LLM = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_CONFIG.endpoint,
    api_version=AZURE_OPENAI_CONFIG.api_version,
    api_key=AZURE_OPENAI_CONFIG.api_key,
    model=AZURE_OPENAI_CONFIG.deployment_name
)
