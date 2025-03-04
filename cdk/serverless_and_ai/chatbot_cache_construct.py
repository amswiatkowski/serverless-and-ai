from aws_cdk import CfnOutput, aws_elasticache
from constructs import Construct


class ChatBotCacheConstruct(Construct):

    def __init__(self, scope: Construct, stack_id: str) -> None:
        super().__init__(scope, stack_id)
        self._scope = scope

        self.elasticache_cluster = self._build_elasticache()

    def _build_elasticache(self) -> aws_elasticache.CfnServerlessCache:
        subnet_ids = [subnet.subnet_id for subnet in self._scope.chatbot_network_construct.vpc.private_subnets]

        elasticache = aws_elasticache.CfnServerlessCache(
            self, "ChatBotCache", engine="redis", serverless_cache_name="ChatBotCache",
            security_group_ids=[self._scope.chatbot_network_construct.vpc_sg.security_group_id], subnet_ids=subnet_ids)
        CfnOutput(self, id='CHATBOT_ELASTICACHE_URI', value=elasticache.attr_endpoint_address).override_logical_id('ELASTICACHEURI')
        return elasticache
