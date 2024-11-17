import json


def search_by_keyword(opensearch, index_name, keyword):

    query = {
        "size": 30,
        "query": {
            "match": {
                "contents": keyword
            }
        }
    }
    response = opensearch.search(body=query, index=index_name, )

    print("hits=" + str(response['hits']['total']) + " for keyword " + keyword)
    for hit in response['hits']['hits']:
        print("\t" + str(hit['_source']['title']))
    return response


def search_by_vector(opensearch, bedrock_client, index_name, question):

    #print("Search OpenSearch using the vector representation of the search")

    sample_model_input = {
        "inputText": question,
        "dimensions": 1024,
        "normalize": True
    }

    body = json.dumps(sample_model_input)
    response = bedrock_client.invoke_model(body=body, modelId="amazon.titan-embed-text-v2:0", accept="application/json", contentType="application/json")
    response_body = json.loads(response.get('body').read())
    search_vector = response_body.get("embedding")

    query = {
        "size": 2,
        "query": {
            "knn": {
                "contents_embedding": {
                    "vector": search_vector,
                    "k": 1
                }
            }
        }
    }
    response = opensearch.search(body=query, index=index_name, )

    #print("hits=" + str(response['hits']['total']) + " for question " + question)
    #for hit in response['hits']['hits']:
    #    print("\t" + str(hit['_source']['title']))
    return response