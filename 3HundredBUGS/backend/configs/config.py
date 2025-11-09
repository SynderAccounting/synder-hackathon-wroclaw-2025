import ast
import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class AppConfig(BaseModel):
    log_level: str = os.getenv('APP_LOG_LEVEL', 'INFO')


class AzureOpenAIConfig(BaseModel):
    api_key: str = os.getenv('AZURE_OPENAI_API_KEY', '')
    endpoint: str = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    deployment_name: str = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4.1-nano')
    api_version: str = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')


class MCPConfig(BaseModel):
    url: str = os.getenv('MCP_B8N_URL')


class N8NConfig(BaseModel):
    url: List[str] = ast.literal_eval(os.getenv('N8N_URL', '[]'))


class AzureCosmosDBConfig(BaseModel):
    uri: str = os.getenv('AZURE_COSMOS_DB_URI')
    key: str = os.getenv('AZURE_COSMOS_DB_KEY')
    database_name: str = os.getenv('AZURE_COSMOS_DB_DATABASE_NAME')
    supplier_container_name: str = os.getenv('AZURE_COSMOS_SUPPLIER_CONTAINER_NAME')
    orders_container_name: str = os.getenv('AZURE_COSMOS_SUPPLIER_ORDERS_NAME')


class PostgreSQLConfig(BaseModel):
    jdbc_url: str = os.getenv('POSTGRES_JDBC')


class SMTPConfig(BaseModel):
    sender_email: str = os.getenv('SMTP_SENDER_EMAIL')
    receiver_email: str = os.getenv('SMTP_RECEIVER_EMAIL')
    password: str = os.getenv('SMTP_PASSWORD')


APP_CONFIG = AppConfig()
AZURE_OPENAI_CONFIG = AzureOpenAIConfig()
MCP_CONFIG = MCPConfig()
N8N_CONFIG = N8NConfig()
AZURE_COSMOS_DB_CONFIG = AzureCosmosDBConfig()
POSTGRESQL_CONFIG = PostgreSQLConfig()
SMTP_CONFIG = SMTPConfig()
