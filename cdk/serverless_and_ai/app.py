#!/usr/bin/env python3
import os

from aws_cdk import App, Environment
from boto3 import client, session
from serverless_and_ai.servcerless_and_ai_stack import ServerlessAndAIStack
from serverless_and_ai.utils.utils import get_stack_name

account = client('sts').get_caller_identity()['Account']
region = session.Session().region_name
app = App()
serverless_and_stack = ServerlessAndAIStack(
    app,
    get_stack_name(),
    description='Serverless and AI stack',
    env=Environment(account=os.environ.get('AWS_DEFAULT_ACCOUNT', account), region=os.environ.get('AWS_DEFAULT_REGION', region)),
)
app.synth()
