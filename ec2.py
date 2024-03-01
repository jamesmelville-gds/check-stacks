from boto3.session import Session


def describe_network_interfaces(session: Session):
    ec2 = session.client("ec2")

    paginator = ec2.get_paginator("describe_network_interfaces").paginate()

    for page in paginator:
        for interface in page["NetworkInterfaces"]:
            yield interface

def describe_security_group_rules(session: Session, SecurityGroupRuleIds: list):
    ec2 = session.client("ec2")

    paginator = ec2.get_paginator("describe_security_group_rules").paginate(SecurityGroupRuleIds=SecurityGroupRuleIds)

    for page in paginator:
        for rule in page["SecurityGroupRules"]:
            yield rule

def describe_security_groups(session: Session, SecurityGroupIds: list):
    ec2 = session.client("ec2")

    paginator = ec2.get_paginator("describe_security_groups").paginate(SecurityGroupIds=SecurityGroupIds)

    for page in paginator:
        for rule in page["SecurityGroups"]:
            yield rule