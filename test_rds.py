import boto3
from datetime import datetime, timedelta
"""
# Créer une session avec un profil spécifique
session = boto3.Session(profile_name='PRODUCTION')

# Utiliser cette session pour créer des clients ou des ressources
ec2 = session.client('ec2')
instances = ec2.describe_spot_price_history()
response = []
partial_response = {'NextToken':None}
query={}
while 'NextToken' in partial_response:
    kwargs = {'NextToken': partial_response['NextToken']} if partial_response['NextToken'] is not None else {}
    partial_response = ec2.describe_spot_price_history(**kwargs)
    history = partial_response['SpotPriceHistory']
    for hist in history:
        print(hist)
    if 'NextToken' in partial_response:
        query= {'NextToken':partial_response['NextToken']}"""


def get_spot_instance_costs(start_date, end_date):
    # Créer un client pour AWS Cost Explorer
    session = boto3.Session(profile_name='PRODUCTION')
    client = session.client('rds')
    #client = boto3.client('ce')
    db_instances = client.describe_db_instances()
    for i in range(len(db_instances)):
        j = i - 1
        try:
            print(db_instances['DBInstances'][j])
            DBName = db_instances['DBInstances'][j]['DBName']
            MasterUsername = db_instances['DBInstances'][0]['MasterUsername']
            DBInstanceClass = db_instances['DBInstances'][0]['DBInstanceClass']
            DBInstanceIdentifier = db_instances['DBInstances'][0]['DBInstanceIdentifier']
            Endpoint = db_instances['DBInstances'][0]['Endpoint']
            Address = db_instances['DBInstances'][0]['Endpoint']['Address']
            print("{} {} {} {} {}".format(Address, MasterUsername, DBName, DBInstanceClass,
            DBInstanceIdentifier))
        except KeyError:
            continue


start_date = datetime.today() - timedelta(days=30)
end_date = datetime.today()
print(get_spot_instance_costs(start_date,end_date))