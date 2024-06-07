# pylint: disable=broad-exception-caught,unused-argument
import json
import os
from typing import Any, Final

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_typing import events
from aws_lambda_typing.context import Context
from langchain.chains.llm import LLMChain
from langchain.globals import set_llm_cache
from langchain.prompts import PromptTemplate
from langchain_community.cache import RedisCache
from langchain_community.llms.bedrock import Bedrock
from mypy_boto3_bedrock import BedrockClient
from redis import Redis

DEFAULT_RESPONSE: Final[dict] = {
    "statusCode": 500,
    "headers": {
        "Content-Type": "application/json"
    },
    "body": "Internal Server Error"
}

bedrock_client: BedrockClient = boto3.client(service_name="bedrock-runtime",
                                             region_name="us-east-1")


# POST chatbot
def handler(event: events.APIGatewayProxyEventV1,
            context: Context) -> dict[str, Any]:
    logger: Logger = Logger()
    logger.info('Received prompt: ', extra={'event': event})
    try:
        response = _prepare_response(json.loads(event['body']), logger,
                                     context)
        logger.info('Sending response', extra={'response': response})
        return response
    except Exception as exc:
        logger.exception('Got fatal error', extra={'Exception': str(exc)})
        return DEFAULT_RESPONSE


def _prepare_response(request: dict[str, Any], logger: Logger,
                      context: Context) -> dict[str, Any]:
    llm = __get_llama2_llm(logger)
    logger.debug('Enabling caching for LLM responses')
    set_llm_cache(RedisCache(redis_=_get_redis_client(logger)))
    response = _get_response_llm(llm, request.get('question'), logger)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response
    }


# Bedrock Client Setup
def __get_llama2_llm(logger: Logger) -> Bedrock:
    logger.debug('Setting model for LLM')
    llm = Bedrock(
        model_id="meta.llama2-13b-chat-v1",
        client=bedrock_client,
        model_kwargs={"max_gen_len": 512},
    )

    return llm


def _get_response_llm(llm: Bedrock, query: str, logger: Logger):
    logger.debug('Getting response from Bedrock')
    prompt_template = """<s>[INST] You are a helpful, respectful and honest assistant.
    {question} [/INST] </s>
    """
    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["question"])
    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.predict(question=query)
    logger.debug('Got the response from Bedrock', extra={'response': response})
    return response


def _get_redis_client(logger: Logger) -> Redis:
    try:
        logger.debug('Setting redis client')
        return Redis.from_url(
            url=f"rediss://{os.getenv('ELASTICACHE_ENDPOINT')}:6379")
    except ValueError as e:
        raise ValueError(f"Redis failed to connect: {e}") from e
