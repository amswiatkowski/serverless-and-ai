# pylint: disable=broad-exception-caught,unused-argument
import json
import os
from http import HTTPStatus
from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import (APIGatewayRestResolver,
                                                 Response, content_types)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_typing import events
from aws_lambda_typing.context import Context
from langchain.globals import set_llm_cache
from langchain_aws import ChatBedrock
from langchain_community.cache import RedisCache
from langchain_core.prompts import ChatPromptTemplate
from redis import Redis, RedisError

tracer = Tracer()
logger: Logger = Logger()
app = APIGatewayRestResolver()


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def handler(event: events.APIGatewayProxyEventV1, context: Context) -> Response:
    logger.debug('Received prompt', extra={'event': event})
    try:
        response = _prepare_response(json.loads(event['body']), context)
        logger.debug('Sending response', extra={'response': response})
        return response
    except Exception as exc:
        logger.exception('Got fatal error', extra={'Exception': str(exc)})
        return Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content_type=content_types.TEXT_PLAIN,
            body="Internal Server Error",
        )


def _prepare_response(request: dict[str, Any], context: Context) -> dict[str, Any]:
    user_id = request.get('user_id')
    question = request.get('question')
    logger.info('Asking AI...', extra={'user_id': user_id, 'question': question})

    llm = __get_llm()
    logger.debug('Enabling caching for LLM responses', extra={'user_id': user_id})
    redis_client = Redis.from_url(url=f"rediss://{os.getenv('ELASTICACHE_ENDPOINT')}:6379", decode_responses=True)
    logger.debug('Pinging redis...', extra={'ping': redis_client.ping()})
    set_llm_cache(RedisCache(redis_=redis_client))

    conversation_history = __get_conversation_history(user_id, redis_client)
    if not conversation_history:
        logger.info(f'This is the beginning of the conversation with User {user_id}', extra={'user_id': user_id})
        conversation_history.append({"role": "system", "content": "You are a helpful, respectful and honest assistant. Your name is Tony."})
    else:
        logger.info(f'Continuing conversation with User {user_id}', extra={'user_id': user_id})
    conversation_history.append({"role": "human", "content": question})
    response_content = _get_response_from_llm(llm, conversation_history)
    conversation_history.append({"role": "assistant", "content": response_content})

    __save_conversation_history(user_id, conversation_history, redis_client)

    return {"body": response_content}


def __get_conversation_history(user_id: str, redis_client: Redis) -> list[dict[str, str]]:
    try:
        history = redis_client.get(user_id)
        logger.debug(f'Getting conversation with the User {user_id}', extra={'user_id': user_id, 'history': history})
        if history:
            return json.loads(history)
    except RedisError as e:
        logger.error('Failed to get conversation history from Redis', extra={'error': str(e)})
    logger.debug(f'Could not get the conversation history for the User {user_id}', extra={'user_id': user_id})
    return []


def __save_conversation_history(user_id: str, conversation_history: list[dict[str, str]], redis_client: Redis) -> None:
    try:
        logger.debug(f'Setting conversation with the User {user_id}', extra={'user_id': user_id, 'history': conversation_history})
        result = redis_client.set(user_id, json.dumps(conversation_history))
        logger.debug(f'Set the conversation with the User {user_id}', extra={
            'user_id': user_id,
            'history': conversation_history,
            'result': result
        })
    except RedisError as e:
        logger.error('Failed to save conversation history to Redis', extra={'error': str(e)})


def __get_llm() -> ChatBedrock:
    logger.debug('Setting model for LLM')
    llm = ChatBedrock(
        model_id=os.getenv('BEDROCK_MODEL_ID'),
        model_kwargs={"max_gen_len": 512},
    )
    return llm


def _get_response_from_llm(llm: ChatBedrock, conversation_history: list[dict[str, str]]) -> str:
    logger.debug('Getting response from Bedrock', extra={'conversation_history': conversation_history})

    prompt = ChatPromptTemplate.from_messages(conversation_history)
    chain = prompt | llm

    response = chain.invoke(input={})
    logger.debug('Got the response from Bedrock', extra={'response': response})
    return response.content
