from typing import List
from pydantic import BaseSettings
from functools import lru_cache
import boto3
import rapidjson
import urllib
from botocore.exceptions import ClientError


class Settings(BaseSettings):
    ALLOWED_HOST: List[str] = []
    POSTGRES_URI: str = ''
    REDIS_URI: str = ''
    DB_NAME: str = ''
    ENV: str = 'local'
    POSTGRES_SECRET_NAME: str = ''
    SENTRY_URI: str = ''

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


def get_postges_uri():
    secret_name = get_settings().POSTGRES_SECRET_NAME
    region_name = "ap-southeast-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
    else:
        print(get_secret_value_response)
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']

            # Your code goes here.
            postgres_data = rapidjson.loads(text_secret_data)
            host = postgres_data.get('host')
            username = postgres_data.get('username')
            password = urllib.parse.quote_plus(postgres_data.get('password'))
            port = postgres_data.get('port')

            uri = "postgres://{}:{}@{}:{}/{}".format(
                username,
                password,
                host,
                port,
                get_settings().DB_NAME
            )
            return uri
    return ''

