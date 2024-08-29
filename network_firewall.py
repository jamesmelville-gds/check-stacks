from boto3.session import Session

def list_firewalls(session: Session):
    network_firewall = session.client("network-firewall")

    paginator = network_firewall.get_paginator("list_firewalls").paginate()

    for page in paginator:
        for firewall in page["Firewalls"]:
            yield firewall

def describe_firewall(session: Session, firewall_name):
    network_firewall = session.client("network-firewall")

    paginator = network_firewall.get_paginator("describe_firewall").paginate(FirewallName=firewall_name)

    for page in paginator:
        for description in page["Firewall"]:
            yield description