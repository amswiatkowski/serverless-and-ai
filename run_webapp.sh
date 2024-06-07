#!/bin/bash
CHATBOT_API_URL=$(./utils/set_env_vars_for_webapp.py) streamlit run ./chat_webapp/chat_webapp.py