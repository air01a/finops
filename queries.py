def format_date(date, granularity):
    if granularity=='HOURLY':
          return date.strftime('%Y-%m-%dT00:00:00Z')
    else:
         return date.strftime('%Y-%m-%d')

def get_ec2_hourly_on_demand(start_date,end_date, granularity='HOURLY'):
    return {
        'TimePeriod': {
            'Start': format_date(start_date, granularity),
            'End': format_date(end_date, granularity)
        },
        'Granularity': granularity,
        'Filter': {
            'And': [
                {
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Elastic Compute Cloud - Compute']
                    }
                },
                {
                    'Dimensions': {
                    'Key': 'PURCHASE_TYPE',
                    'Values': ['On Demand Instances']
                    }
                    
                },
                {
                    'Not': {
                        'Tags': {
                            'Key': 'aws:createdBy',
                            'Values': ['Taxes', 'Credits']
                        }
                    }
                }
            ]
        },
        'Metrics': ['UnblendedCost']
    }


def get_ec2_hourly_on_demand_group_by_instancetype(start_date, end_date, granularity='HOURLY'):
        query = get_ec2_hourly_on_demand(start_date,end_date, granularity)
        query['GroupBy'] = [
            {
                'Type': 'DIMENSION',
                'Key': 'INSTANCE_TYPE'
            }
        ]

        return query


def cost_by_service(start_date,end_date, granularity='MONTHLY'):
    return {
        'TimePeriod': {
            'Start': format_date(start_date, granularity),
            'End': format_date(end_date, granularity)
        },
        'Granularity': granularity,
        'Filter': {
             'Not': {
                        'Dimensions': {
                            'Key': 'SERVICE',
                            'Values': ['Tax', 'Credit']
                        }
                    }
        },
        'GroupBy': [{
             'Type': 'DIMENSION',
             'Key': 'SERVICE'
        }],
        'Metrics': ['UnblendedCost']
    }
