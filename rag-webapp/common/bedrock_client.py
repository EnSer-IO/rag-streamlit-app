import os
import boto3
from typing import Optional
from botocore.config import Config


def get_bedrock_client(assumed_role: Optional[str] = None, region: Optional[str] = 'us-west-2',
                       runtime: Optional[bool] = True, external_id=None, ep_url=None):
    """Create a boto3 client for Amazon Bedrock, with optional configuration overrides
    """
    target_region = region

    #print(f"Create new client\n  Using region: {target_region}:external_id={external_id}: ")
    session_kwargs = {"region_name": target_region}
    client_kwargs = {**session_kwargs}

    # profile_name = "bedrock-inference-test"

    profile_name = os.environ.get("AWS_PROFILE")
    if profile_name:
        #print(f"  Using profile: {profile_name}")
        session_kwargs["profile_name"] = profile_name

    retry_config = Config(
        region_name=target_region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
    session = boto3.Session(**session_kwargs)

    if assumed_role:
        #print(f"  Using role: {assumed_role}", end='')
        sts = session.client("sts")
        if external_id:
            response = sts.assume_role(
                RoleArn=str(assumed_role),
                RoleSessionName="langchain-llm-1",
                ExternalId=external_id
            )
        else:
            response = sts.assume_role(
                RoleArn=str(assumed_role),
                RoleSessionName="langchain-llm-1",
            )
        #print(f"Using role: {assumed_role} ... sts::successful!")
        client_kwargs["aws_access_key_id"] = response["Credentials"]["AccessKeyId"]
        client_kwargs["aws_secret_access_key"] = response["Credentials"]["SecretAccessKey"]
        client_kwargs["aws_session_token"] = response["Credentials"]["SessionToken"]

    if runtime:
        service_name = "bedrock-runtime"
    else:
        service_name = 'bedrock'

    if ep_url:
        bedrock_client = session.client(service_name=service_name, config=retry_config, endpoint_url=ep_url,
                                        **client_kwargs)
    else:
        bedrock_client = session.client(service_name=service_name, config=retry_config, **client_kwargs)

    #print("boto3 Bedrock client successfully created!")
    #print(bedrock_client._endpoint)
    return bedrock_client
