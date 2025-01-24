from boto3.session import Session

def describe_vpc_links(session: Session):
    for item in session.client("apigatewayv2").get_vpc_links()['Items']:
        yield(item)