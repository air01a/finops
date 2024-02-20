import boto3
from datetime import datetime, timedelta
import pandas as pd
# Créer un client pour le service AWS Cost Explorer
client = boto3.client('ce')

# Définir les dates de début et de fin pour l'analyse
start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')
# Create a Savings Plans client
savings_plans_client = boto3.client('ce')

# Call the get_savings_plans_utilization_details method
response = savings_plans_client.get_savings_plans_utilization(
    TimePeriod={
        'Start': '2024-01-18T00:00:00Z',
        'End': '2024-01-28T15:00:00Z'
    },
    Granularity='HOURLY',
)

# Print the response
print(response)