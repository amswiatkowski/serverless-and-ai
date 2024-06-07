# pylint: disable=redefined-outer-name

import os
import time

import requests
import streamlit as st
from requests import Response


def get_api_gateway_url():
    try:
        api_gateway_url = os.environ["CHATBOT_API_URL"]
        return api_gateway_url
    except Exception as e:
        raise ValueError(
            "API_GATEWAY_URL environment variable can't be found! Make sure CDK stack was deployed initially with `./deploy.sh` command."
        ) from e


def response_generator(prompt: str):
    api_url = f'{get_api_gateway_url()}chat/prompt'
    print(f'calling {api_url}. With prompt: {prompt}')
    response: Response = requests.post(api_url,
                                       json={'question': prompt},
                                       timeout=120)

    answer = f'{response.text} (Response took: {response.elapsed.total_seconds()}s)'
    for word in answer.split():
        yield word + " "
        time.sleep(0.05)


st.title("Simple chat with Bedrock using Lambda and API Gateway")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt))
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
