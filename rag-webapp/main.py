import os

import streamlit as st
from opensearchpy import OpenSearch, RequestsHttpConnection
from dotenv import load_dotenv
from common.bedrock_client import get_bedrock_client
from common.claude3 import process_search_results, query_claude
from common.opensearch_searches import search_by_vector

load_dotenv()

OPENSEARCH_PASSWD = os.getenv("OPENSEARCH_PASSWORD")
OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME")
OPENSEARCH_IP = os.getenv("OPENSEARCH_IP")
OPENSEARCH_TARGET_INDEX = os.getenv("OPENSEARCH_TARGET_INDEX")

IAM_ROLE_STRING = os.getenv("IAM_ROLE_STRING")


opensearch = OpenSearch(
    hosts=[{'host': OPENSEARCH_IP, 'port': 9200}],
    http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWD),
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)

boto3_bedrock_runtime = get_bedrock_client(assumed_role=IAM_ROLE_STRING)


def response_generator(question):

    documents = search_by_vector(opensearch, boto3_bedrock_runtime, OPENSEARCH_TARGET_INDEX, question)
    context = process_search_results(documents)

    prompt = f"""
    Human: You are a legal advisor AI system, and provides answers to questions by using fact based information when possible.
    Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    <context>
    {context}
    </context>
    
    <question>
    {question}
    </question>
    
    Assistant:"""

    model_response = query_claude(boto3_bedrock_runtime, prompt)
    yield model_response


st.title("Document Question Answering")
st.header(OPENSEARCH_TARGET_INDEX)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("waiting"):
            response = st.write_stream(response_generator(prompt))

    st.session_state.messages.append({"role": "assistant", "content": response})


