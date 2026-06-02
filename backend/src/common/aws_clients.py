import boto3


def sqs_client():
    return boto3.client("sqs")


def dynamodb_resource():
    return boto3.resource("dynamodb")


def cloudwatch_client():
    return boto3.client("cloudwatch")


def lambda_client():
    return boto3.client("lambda")


def apigw_mgmt_client(endpoint_url: str):
    return boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)


def logs_client():
    return boto3.client("logs")
