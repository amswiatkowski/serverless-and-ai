from aws_cdk import CfnOutput, Duration, RemovalPolicy, aws_apigateway, aws_ec2, aws_iam, aws_lambda, aws_lambda_python_alpha
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from serverless_and_ai.constants import (
    API_HANDLER_LAMBDA_MEMORY_SIZE,
    API_HANDLER_LAMBDA_TIMEOUT,
    BEDROCK_MODEL_ID,
    BUILD_FOLDER,
    LAMBDA_ARCHITECTURE,
    LAMBDA_RUNTIME,
    POWER_TOOLS_LOG_LEVEL,
    POWERTOOLS_SERVICE_NAME,
    SERVICE_NAME,
)


class ChatBotApiConstruct(Construct):

    def __init__(self, scope: Construct, stack_id: str) -> None:
        super().__init__(scope, stack_id)
        self._scope = scope

        self.chatbot_api = self._build_apigw()
        self.chatbot_lambda_layer = self._build_lambda_layer()
        self.chatbot_lambda_role = self._build_lambda_role()
        self.chatbot_lambda_function = self._build_lambda_function()
        root_resource = self.chatbot_api.root.add_resource('chat')
        prompt_resource = root_resource.add_resource('prompt')
        prompt_resource.add_method('POST', integration=aws_apigateway.LambdaIntegration(handler=self.chatbot_lambda_function))

    def _build_lambda_layer(self) -> aws_lambda_python_alpha.PythonLayerVersion:
        layer = aws_lambda_python_alpha.PythonLayerVersion(scope=self, id='ChatbotLambdaLayer', entry='.build/common_layer',
                                                           compatible_architectures=[LAMBDA_ARCHITECTURE],
                                                           compatible_runtimes=[LAMBDA_RUNTIME], removal_policy=RemovalPolicy.DESTROY)
        return layer

    def _build_lambda_role(self) -> aws_iam.Role:
        lambda_role = aws_iam.Role(
            scope=self, id='chatbot-lambda-role', assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com'),
            role_name='chatbot-lambda-role', managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaVPCAccessExecutionRole')
            ], inline_policies={
                'bedrock_policies':
                    aws_iam.PolicyDocument(statements=[
                        aws_iam.PolicyStatement(
                            actions=['bedrock:InvokeModel'],
                            resources=[f'arn:aws:bedrock:{self._scope.region}::foundation-model/{BEDROCK_MODEL_ID}'],
                            effect=aws_iam.Effect.ALLOW,
                        )
                    ]),
                'vpc_policies':
                    aws_iam.PolicyDocument(statements=[
                        aws_iam.PolicyStatement(
                            actions=["elasticache:Connect"],
                            resources=[self._scope.chatbot_cache_construct.elasticache_cluster.attr_arn],
                            effect=aws_iam.Effect.ALLOW,
                        )
                    ])
            })
        return lambda_role

    def _build_lambda_function(self) -> aws_lambda.Function:

        lambda_function = aws_lambda.Function(
            self,
            'ChatbotLambdaFunction',
            function_name='ChatbotLambdaFunction',
            description='Chatbot Lambda Function',
            runtime=LAMBDA_RUNTIME,
            architecture=aws_lambda.Architecture.ARM_64,
            code=aws_lambda.Code.from_asset(BUILD_FOLDER),
            handler='lambda_handlers.chatbot_handler.handler',
            environment={
                POWERTOOLS_SERVICE_NAME: SERVICE_NAME,  # for logger, tracer and metrics
                POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                'ELASTICACHE_ENDPOINT': self._scope.chatbot_cache_construct.elasticache_cluster.attr_endpoint_address,
                'BEDROCK_MODEL_ID': BEDROCK_MODEL_ID
            },
            tracing=aws_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.chatbot_lambda_layer],
            role=self.chatbot_lambda_role,
            log_retention=RetentionDays.ONE_DAY,
            vpc=self._scope.chatbot_network_construct.vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self._scope.chatbot_network_construct.vpc_sg])
        aws_lambda.Alias(self, id='ChatbotLambdaAlias', alias_name='chatbot-lambda', version=lambda_function.current_version)
        return lambda_function

    def _build_apigw(self) -> aws_apigateway.RestApi:
        rest_api: aws_apigateway.RestApi = aws_apigateway.RestApi(
            self,
            'chatbot-rest-api',
            rest_api_name='Chatbot Rest API',
            description='This service handles chatbot prompts',
            deploy_options=aws_apigateway.StageOptions(throttling_rate_limit=2, throttling_burst_limit=10),
            cloud_watch_role=False,
        )

        CfnOutput(self, id='CHATBOT_API_URL', value=rest_api.url).override_logical_id('APIURL')

        return rest_api
