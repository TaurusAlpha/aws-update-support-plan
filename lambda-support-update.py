from __future__ import annotations
import logging
import boto3
import os
import cfnresponse  # type: ignore[import-untyped]
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_support import SupportClient

# Configure logging
logger = logging.getLogger()
logging.basicConfig(format="%(asctime)s %(message)s")
logger.setLevel(logging.INFO if os.getenv("logger_level") else logging.DEBUG)


def lambda_handler(event, context) -> None:
    try:
        # Extract the request type from the event
        request_type = event["RequestType"]
        # Extract the account ID from the Lambda function ARN
        account_id = context.invoked_function_arn.split(":")[4]

        if request_type == "Create":
            # Handle creation logic here
            # Create a support case to update the support plan for the new account
            # Note: The region is hardcoded to us-east-1 because Support is a global service
            support_client: SupportClient = boto3.client(
                "support", region_name="us-east-1"
            )
            response = support_client.create_case(
                subject="Update Support Plan for New Account",
                serviceCode="account-management",
                severityCode="low",
                categoryCode="other",
                communicationBody=f"Please update the support plan of account {account_id} to Enterprise.",
                issueType="customer-service",
            )
            responseData = {"CaseId": response["caseId"]}
            logger.info(f"Support case created with case ID: {response['caseId']}")
            # Send a success response to CloudFormation
            cfnresponse.send(
                event, context, cfnresponse.SUCCESS, responseData, "CustomResourceId"
            )

        elif request_type in ["Update", "Delete"]:
            # For Update and Delete requests, do nothing but signal SUCCESS
            cfnresponse.send(
                event, context, cfnresponse.SUCCESS, {}, event["PhysicalResourceId"]
            )

    except Exception as e:
        # Report any exceptions as a FAILED
        errorMessage = str(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Message": errorMessage})
