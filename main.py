#!/usr/bin/env python3
from boto3.session import Session
import re
from sso import get_account_roles, get_accounts, get_oidc_token
from cloudformation import list_stacks

import csv, os, sys

class Version:
    def __init__(self, version):
        self.major = self.version.split('.')[0]
        self.minor = self.version.split('.')[1]
        self.patch = self.version.split('.')[2]
    
    def __gt__(self, other):
        other.major = self.version.split('.')[0]
        other.minor = self.version.split('.')[1]
        other.patch = self.version.split('.')[2]

        if self.major > other.major:
            return True
        
        if self.major < other.major:
            return False
        
        if self.minor > other.minor:
            return True
        
        if self.minor < other.minor:
            return False
        
        if self.patch > other.patch:
            return True
        
        if self.patch < other.patch:
            return False
        
        return False

    def __lt__(self, other):
        other.major = self.version.split('.')[0]
        other.minor = self.version.split('.')[1]
        other.patch = self.version.split('.')[2]

        if self.major < other.major:
            return True
        
        if self.major > other.major:
            return False
        
        if self.minor < other.minor:
            return True
        
        if self.minor > other.minor:
            return False
        
        if self.patch < other.patch:
            return True
        
        if self.patch > other.patch:
            return False
        
        return False
    
    def __eq__(self, other):
        other.major = self.version.split('.')[0]
        other.minor = self.version.split('.')[1]
        other.patch = self.version.split('.')[2]
        return self.major == other.major and self.minor == other.minor and self.patch == other.patch
    
def match_type(required_type, type):
    if not required_type:
        return True
    if required_type:
        return required_type == type


def match_version(after_version, before_version, version):
    if not before_version and not after_version:
        return True
    if before_version and after_version:
        if version > after_version and version < before_version:
            return True
    if before_version and not after_version:
        if version < before_version:
            return True
    if after_version and not before_version:
        if version > after_version:
            return True
    return False

class Stack():
    def __init__(self, accountId,accountName,stackName,stackType,stackVersion):
        self.accountId = accountId
        self.accountName = accountName
        self.stackName = stackName
        self.stackType = stackType
        self.stackVersion = stackVersion
    
    def __str__(self):
        return {
            "accountId": self.accountId,
            "accountName": self.accountName,
            "stackName": self.stackName,
            "stackType": self.stackType,
            "stackVersion": self.stackVersion
        }

def main():
    session = Session()
    token = get_oidc_token(session)
    access_token = token["accessToken"]
    accounts = get_accounts(session, access_token)
    role_filter = os.environ.get('ROLE_FILTER', 'readonly')
    before_version = os.environ.get('BEFORE_VERSION')
    after_version = os.environ.get('AFTER_VERSION')
    stack_type = os.environ.get('STACK_TYPE')

    if before_version > after_version:
        print(f'Version $before_version is later than $after_version')
        sys.exit(1)
    
    if before_version == after_version:
        print(f'Version $before_version is the same as $after_version')
        sys.exit(1)
    
    with open("stacks.csv", "w+") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "accountName",
                "accountId",
                "stackName",
                "stackType",
                "stackVersion",
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

                    stacks = list_stacks(session)
                    found_stacks = []

                    for stack in stacks:
                        name = stack["StackName"]
                        description = stack.get("Description", "")
                        m = re.match(
                            "^(di-)?devplatform-deploy ([a-z\-]+) template version: v([\d\.]+)",
                            description,
                        )
                        if m:
                            found_stacks.append(Stack(account_id,account_name,name,m.group(2),m.group(3)))

                    stacks_filtered_by_type = [stack for stack in found_stacks if match_type(stack_type,stack.stackType)]
                    stacks_filtered_by_versions = [stack for stack in stacks_filtered_by_type if match_version(after_version,before_version,stack.stackVersion)]
                    for stack in stacks_filtered_by_versions:
                        writer.writerow(str(stack))


if __name__ == "__main__":
    main()
