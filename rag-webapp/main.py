import os

import streamlit as st
from opensearchpy import OpenSearch, RequestsHttpConnection
from dotenv import load_dotenv
from common.bedrock_client import get_bedrock_client
from common.claude3 import process_search_results, query_claude
from common.opensearch_searches import search_by_vector

index_name = 'YOUR_INDEX_HERE'

load_dotenv()

OPENSEARCH_PASSWD = os.getenv("OPENSEARCH_INITIAL_PASSWORD")

opensearch = OpenSearch(
    hosts=[{'host': '127.0.0.1', 'port': 9200}],
    http_auth=('admin', OPENSEARCH_PASSWD),
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)

boto3_bedrock_runtime = get_bedrock_client(assumed_role="IAM_ROLE_STRING")


def response_generator(question):

    documents = search_by_vector(opensearch, boto3_bedrock_runtime, index_name, question)
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


st.title("Legal Document Question Answering")
st.header(index_name)

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


