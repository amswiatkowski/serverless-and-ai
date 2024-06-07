from aws_cdk import Stack
from constructs import Construct
from serverless_and_ai.chatbot_api_construct import ChatBotApiConstruct
from serverless_and_ai.chatbot_api_network_construct import \
    ChatBotNetworkConstruct
from serverless_and_ai.chatbot_cache_construct import ChatBotCacheConstruct


class ServerlessAndAIStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.chatbot_network_construct = ChatBotNetworkConstruct(
            self, 'ChatbotNetworkConstruct')
        self.chatbot_cache_construct = ChatBotCacheConstruct(
            self, 'ChatbotCacheConstruct')
        self.chatbot_api_construct = ChatBotApiConstruct(
            self, 'ChatbotApiConstruct')
