#!/usr/bin/env python3
from boto3.session import Session
from sso import get_account_roles, get_accounts, get_oidc_token
from ec2 import describe_network_interfaces

import csv
import os
import sys


def main():
    session = Session(region_name="eu-west-2")
    token = get_oidc_token(session)
    access_token = token["accessToken"]
    accounts = get_accounts(session, access_token)
    try: # TODO: move to .get('ROLE_FILTER', 'readonly')
        role_filter = os.environ['ROLE_FILTER']
    except KeyError:
        role_filter = 'readonly'

    
    with open("defaultSecurityGroups.csv", "w+") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                        "accountName",
                        "accountId",
                        "securityGroupId",
                        "NetworkInterfaceId",
                        "interfaceType",
                        "description",
            ],
        )
        writer.writeheader()

        for account in accounts:
            account_name = account["accountName"]
            account_id = account["accountId"]
            for role in get_account_roles(session, access_token, account_id):
                role_name = role["roleName"]
                if role_filter in role_name:
                    sso = session.client("sso")
                    role_creds = sso.get_role_credentials(
                        roleName=role["roleName"],
                        accountId=account_id,
                        accessToken=access_token,
                    )["roleCredentials"]
                    session = Session(
                        region_name="eu-west-2",
                        aws_access_key_id=role_creds["accessKeyId"],
                        aws_secret_access_key=role_creds["secretAccessKey"],
                        aws_session_token=role_creds["sessionToken"],
                    )

                    enis = describe_network_interfaces(session)
                    for eni in enis:
                        for group in eni["Groups"]:
                            if group["GroupName"] == 'default':
                                writer.writerow({
                                                "accountName": account_name,
                                                "accountId": account_id,
                                                "securityGroupId": group["GroupId"],
                                                "NetworkInterfaceId": eni["NetworkInterfaceId"],
                                                "interfaceType": eni["InterfaceType"],
                                                "description": eni["Description"]
                                            })

if __name__ == "__main__":
    main()