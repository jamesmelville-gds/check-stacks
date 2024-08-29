#!/usr/bin/env python3
from boto3.session import Session
from sso import get_account_roles, get_accounts, get_oidc_token
from network_firewall import list_firewalls,describe_firewall

import csv


def main():
    session = Session(region_name="eu-west-2")
    token = get_oidc_token(session)
    access_token = token["accessToken"]
    accounts = get_accounts(session, access_token)

    with open("firewalls.csv", "w+") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                        "accountName",
                        "accountId",
                        "firewallName",
                        ],
        )
        writer.writeheader()

        for account in accounts:
            role_name = "ReadOnlyAccess"
            account_name = account["accountName"]
            account_id = account["accountId"]
            sso = session.client("sso")
            try:
                role_creds = sso.get_role_credentials(
                            roleName=role_name,
                            accountId=account_id,
                            accessToken=access_token,
                            )["roleCredentials"]
                session = Session(region_name="eu-west-2",
                                    aws_access_key_id=role_creds["accessKeyId"],
                                    aws_secret_access_key=role_creds["secretAccessKey"],
                                    aws_session_token=role_creds["sessionToken"],
                                    )
                
                firewalls = list_firewalls(session)
                for firewall in firewalls:
                    firewall_name = firewall["FirewallName"]
                    

                    writer.writerow({
                                    "accountName": account_name,
                                    "accountId": account_id,
                                    "firewallName": firewall_name,
                                })
            except:
                print(f'Unable to get role {role_name} in account with name {account_name}, id {account_id}')

if __name__ == "__main__":
    main()