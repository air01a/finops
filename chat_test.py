#pip install st-chat-message
import streamlit as st
from st_chat_message import message

message("Hello world!", is_user=True)
message("Hi $$\int x dx$$")