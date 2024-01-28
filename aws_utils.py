from queries import get_ec2_hourly_on_demand, get_ec2_hourly_on_demand_group_by_instancetype, cost_by_service
import boto3
import pandas as pd

class AwsHelper:

    def __init__(self):
        self.client = boto3.client('ce')


    def query(self, query):
        response = []
        partial_response = {'nextToken':None}
        while 'nextToken' in partial_response:
            partial_response = self.client.get_cost_and_usage(**query)
            response.extend(partial_response['ResultsByTime'])
            if 'nextToken' in partial_response:
                query['nextToken']=partial_response['nextToken']
        return response

    def get_hourly_cost(self, start_date, end_date):
        query = get_ec2_hourly_on_demand(start_date,end_date)
        result = self.query(query)
        ret = []
        for res in result:
            date = res['TimePeriod']['Start']
            amount = res['Total']['UnblendedCost']['Amount']
            ret.append([date, amount])
        return pd.DataFrame(ret, columns=['Date','Cost'])

    def get_hourly_cost_small_machine(self, start_date, end_date):
        costs = self.get_hourly_cost(start_date, end_date)
        return costs

    def get_hourly_cost_by_instance(self, start_date, end_date):
        query = get_ec2_hourly_on_demand_group_by_instancetype(start_date,end_date)
        response =  self.query(query)
        result = []
        for res in response:
            date = res['TimePeriod']['Start']
            for group in res['Groups']:
                instance = group['Keys'][0].split('.')
                instance_type = instance[0]
                if len(instance)>1:
                    instance_size = instance[1]
                else:
                    instance_size = 'N/A'
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                result.append([date, instance_type, instance_size,amount])
        return pd.DataFrame(result, columns=['Date','Instance_Type','Instance_Size', 'Cost'])

    def get_big_instances_cost(self,data):
        filtered_data = data[data['Instance_Size'].isin(self.is_large_instance_type())]
        """cost_data = {}
        i = 0
        for result in response:
            #period=result['TimePeriod']['Start']
            for group in result['Groups']:
                instance_type = group['Keys'][0]
                if self.is_large_instance_type(instance_type):
                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    # Keep trace of all instances that were previously up
                    #all_instances[instance_type] = all_instances.get(instance_type, 0) + 1

                    if instance_type in cost_data.keys():
                        cost_data[instance_type].append(amount)
                    else:
                        cost_data[instance_type] = [0 for j in range(i-1)]
                        cost_data[instance_type].append(amount)
            i+=1

        for instance in cost_data.keys():
            cost_instance = cost_data[instance]
            if len(cost_instance)<i:
                cost_data[instance] = cost_instance + [0 for j in range(i-len(cost_instance))]"""

        return filtered_data

    def get_residual(self,data):
        filtered_data = data[~data['Instance_Size'].isin(self.is_large_instance_type())]
        filtered_data=filtered_data.groupby('Date')['Cost'].sum().reset_index()
        return filtered_data
                    

    def cost_by_service(self, start_date, end_date, limit=10, granularity='MONTHLY'):
        query = cost_by_service(start_date,end_date, granularity)
        response = self.query(query)
        result = []
        for monthly in response:
            date = monthly['TimePeriod']['Start']
            if granularity=='MONTHLY':
                date = "-".join(date.split('-')[0:2])
            services = []
            for group in monthly['Groups']:
                service = group['Keys'][0]
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                services.append([date, service, amount])
            services = sorted(services, key=lambda item: item[2], reverse=True)
            if len(services)>limit :
                amount = 0
                for i in range(limit, len(services)):
                    amount += services[i][2]
                services = services[0:limit]+[[date,'Other', amount]]
            result+=services
        result = pd.DataFrame(result, columns=['Date','Service','Cost'])
        return result

    def is_large_instance_type(self):
        # Ajoutez d'autres tailles si nécessaire
        large_sizes = ['2xlarge', '4xlarge', '8xlarge', '9xlarge', '12xlarge', '16xlarge', '18xlarge', '24xlarge', '32xlarge']
        return large_sizes

