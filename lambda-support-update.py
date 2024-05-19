from __future__ import annotations
import logging
import boto3
import os
from typing import TYPE_CHECKING, Optional
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_support import SupportClient
    from mypy_boto3_sts import STSClient

# Configure logging
logger = logging.getLogger()
logging.basicConfig(format="%(asctime)s %(message)s")
logger.setLevel(logging.getLevelName(os.getenv("logger_level", "INFO")))

SUPPORT_LEVEL_MAPPING = {
    "low": "basic",
    "normal": "basic",
    "high": "business",
    "urgent": "business",
    "critical": "enterprise",
}


def check_support_plan(account_id: str) -> Optional[str]:
    """
    Check the current support plan of the account.
    """
    role_arn = os.environ["assume_role_name"].replace("<ACCOUNT_ID>", account_id)

    try:
        sts_client: STSClient = boto3.client("sts")
        stsObject = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName="AssumeRoleSession"
        )
        credentials = stsObject["Credentials"]
    except ClientError as e:
        logger.error(f"Error assuming role: {e}")
        return None

    try:
        support_client: SupportClient = boto3.client(
            "support",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
        response = support_client.describe_severity_levels(language="en")
        return (
            sorted(
                SUPPORT_LEVEL_MAPPING[sv_lvl["code"]]
                for sv_lvl in response["severityLevels"]
            )[-1]
            if response["severityLevels"]
            else SUPPORT_LEVEL_MAPPING["low"]
        )
    except support_client.exceptions.ClientError as err:
        if err.response["Error"]["Code"] == "SubscriptionRequiredException":
            return SUPPORT_LEVEL_MAPPING["low"]
        logger.error(f"ClientError in check_support_plan: {err}")
        return None
    except ClientError as e:
        logger.error(f"Error describing severity levels: {e}")
        return None


def lambda_handler(event, context) -> None:
    """
    Lambda function handler for updating the support plan for a new account.
    """
    logger.info(f"Received event: {event}")
    account_id = event["accountId"]
    required_support_level = os.environ.get("required_support_level", "basic")

    current_support_level = check_support_plan(account_id)
    if current_support_level is None:
        logger.error("Failed to check support plan. Exiting.")
        return

    if current_support_level == required_support_level:
        logger.info(
            f"Account {account_id} already has an {required_support_level} support plan."
        )
        return

    try:
        support_client: SupportClient = boto3.client(
            "support", region_name=os.environ.get("AWS_REGION", "us-east-1")
        )

        response = support_client.create_case(
            subject="Update Support Plan for New Account",
            serviceCode="account-management",
            severityCode="low",
            categoryCode="other",
            communicationBody=f"Please update the support plan of account {account_id} to {required_support_level}.",
            issueType="customer-service",
        )
        logger.info(f"Create case response: {response}")
    except support_client.exceptions.ClientError as err:
        logger.error(f"ClientError in create_case: {err}")
    except ClientError as e:
        logger.error(f"Error creating support case: {e}")
