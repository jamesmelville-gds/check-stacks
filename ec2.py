from boto3.session import Session


def describe_network_interfaces(session: Session):
    ec2 = session.client("ec2")

    paginator = ec2.get_paginator("describe_network_interfaces").paginate()

    for page in paginator:
        for interface in page["NetworkInterfaces"]:
            yield interface