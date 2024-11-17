import json


def process_search_results(results):

    documents = [hit['_source'] for hit in results['hits']['hits']]
    context = "\n".join([doc['contents'] for doc in documents])

    return context


def query_claude(boto3_bedrock_runtime, prompt):

    messages = [{"role": 'user', "content": [{'type': 'text', 'text': prompt}]}]

    sonnet_payload = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8192,
        "messages": messages,
        "temperature": 0.5,
        "top_p": 1
    })

    response = boto3_bedrock_runtime.invoke_model(
        body=sonnet_payload,
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        accept='application/json',
        contentType='application/json'
    )

    response_body = json.loads(response['body'].read())

    return response_body.get('content')[0]['text']