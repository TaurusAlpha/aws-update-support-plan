from __future__ import annotations
import logging
import boto3
import os
import cfnresponse  # type: ignore[import-untyped]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_support import SupportClient

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s", level=os.getenv("logger_level", "DEBUG")
)
logger = logging.getLogger()

SUPPORT_LEVEL_MAPPING = {
    "low": "basic",
    "normal": "basic",
    "high": "business",
    "urgent": "business",
    "critical": "enterprise",
}


def check_support_plan(support_client: SupportClient) -> str:
    """
    Check the current support plan of the account.
    """
    try:
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
        raise err


def lambda_handler(event, context) -> None:
    """
    Lambda function handler for updating the support plan for a new account.
    """
    logger.info(f"Received event: {event}")
    try:
        # Extract the request type from the event
        request_type = event["RequestType"]
        # Extract the account ID from the Lambda function ARN
        account_id = context.invoked_function_arn.split(":")[4]
        required_support_level = os.environ.get("required_support_level", "basic")

        # Handle creation logic
        if request_type == "Create":
            support_client: SupportClient = boto3.client(
                "support", region_name=os.environ.get("AWS_REGION", "us-east-1")
            )
            if check_support_plan(support_client) == required_support_level:
                logger.info(
                    f"Account {account_id} already has an {required_support_level} support plan."
                )
                # Send a success response to CloudFormation
                cfnresponse.send(
                    event,
                    context,
                    cfnresponse.SUCCESS,
                    {
                        "Message": f"Account {account_id} already has an {required_support_level} support plan."
                    },
                )
                return
            response = support_client.create_case(
                subject="Update Support Plan for New Account",
                serviceCode="account-management",
                severityCode="low",
                categoryCode="other",
                communicationBody=f"Please update the support plan of account {account_id} to {required_support_level}.",
                issueType="customer-service",
            )
            logger.info(f"Create case response: {response}")
            responseData = {"CaseId": response["caseId"]}
            # Send a success response to CloudFormation
            cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)

        elif request_type in ["Update", "Delete"]:
            # For Update and Delete requests, do nothing but signal SUCCESS
            cfnresponse.send(
                event, context, cfnresponse.SUCCESS, {}, event["PhysicalResourceId"]
            )

    except Exception as e:
        # Report any exceptions as a FAILED
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Message": f"{e}"})
