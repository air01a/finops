from queries import get_ec2_hourly_on_demand, get_ec2_hourly_on_demand_group_by_instancetype, cost_by_service
import boto3
import pandas as pd

class AwsCEHelper:

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
                instance = group['Keys'][0]
                
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                result.append([date, instance,amount]) 
        df = pd.DataFrame(result, columns=['Date','Instance', 'Cost'])
        

        all_dates = df['Date'].unique()
        all_instance_types = df['Instance'].unique()
        multi_index = pd.MultiIndex.from_product([all_dates, all_instance_types], names=['Date', 'Instance'])

        # Étape 2: Créer un nouveau DataFrame à partir de cet index multi-niveaux
        df_all_combinations = pd.DataFrame(index=multi_index).reset_index()

        # Étape 3: Fusionner avec le DataFrame original
        df_merged = pd.merge(df_all_combinations, df, on=['Date', 'Instance'], how='left')

        # Étape 4: Remplir les valeurs manquantes dans 'Cost' par 0
        df_merged['Cost'] = df_merged['Cost'].fillna(0)

        df_merged[['Instance_Type', 'Instance_Size']] = df_merged['Instance'].str.split('.', expand=True)

        return df_merged #pd.DataFrame(result, columns=['Date','Instance_Type','Instance_Size', 'Instance', 'Cost'])

    def get_big_instances_cost(self,data):
        filtered_data = data[data['Instance_Size'].isin(self.is_large_instance_type())]
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

    def query_reco(self, type):
        try:
            response = self.client.get_savings_plans_purchase_recommendation(
                LookbackPeriodInDays='SEVEN_DAYS',
                TermInYears='THREE_YEARS',
                PaymentOption='NO_UPFRONT',
                SavingsPlansType=type
            )
            return response
        except Exception as e:
            print("Error",e)

    def get_ec2_recommendation(self):
        response = self.query_reco('EC2_INSTANCE_SP')
        # Traiter la réponse
        result=[]
        for resp in response["SavingsPlansPurchaseRecommendation"]["SavingsPlansPurchaseRecommendationDetails"]:
            instance_family = resp['SavingsPlansDetails']['InstanceFamily']
            hourly_commitment_to_purchase = resp['HourlyCommitmentToPurchase']
            estimated_saving = resp['EstimatedMonthlySavingsAmount']
            estimated_utilization = resp['EstimatedAverageUtilization']
            estimated_percent = resp['EstimatedSavingsPercentage']
            actual_cost = resp['CurrentMaximumHourlyOnDemandSpend']
            result.append([ instance_family,hourly_commitment_to_purchase, estimated_saving, estimated_utilization, estimated_percent,actual_cost])

        result = pd.DataFrame(result, columns=['family','to_purchase', 'saving', 'estimated_utilization','etimated_percent','actual_cost'])
        return result

    def get_compute_sp_reco(self):
        response = self.query_reco('COMPUTE_SP')
        result=[]
        for resp in response["SavingsPlansPurchaseRecommendation"]["SavingsPlansPurchaseRecommendationDetails"]:
            print(resp)
            hourly_commitment_to_purchase = float(resp['HourlyCommitmentToPurchase'])
            estimated_saving = float(resp['EstimatedMonthlySavingsAmount'])
            estimated_utilization = float(resp['EstimatedAverageUtilization'])
            estimated_percent = float(resp['EstimatedSavingsPercentage'])
            result.append([float(hourly_commitment_to_purchase), float(estimated_saving), float(estimated_utilization), float(estimated_percent)])

        result = pd.DataFrame(result, columns=['to_purchase', 'saving', 'estimated_utilization','estimated_percent'])
        return result

    def get_min_total_compute(self, instances, filter=None):
        if filter!=None:
            df = instances[~instances['Instance'].isin(filter)]
        else:
            df = instances
        return df.groupby('Date')['Cost'].sum()
    
    def get_min_cost_by_instance_type(self, instances, filter=None):
        df = instances.groupby('Instance')['Cost'].min().reset_index()
        return df


    def get_instance_sp_reco(self, ec2_sp_purchase, ec2_sp_reco):
        ec2_sp_purchase["Instance_type"]=ec2_sp_purchase["Instance"].str.split('.').str[0]

        ec2_sp_purchase=pd.merge(ec2_sp_purchase, ec2_sp_reco,  left_on='Instance_type', right_on='family')[["Instance","Cost","Instance_type","etimated_percent"]]
        ec2_sp_purchase["To_Purchase"]=(1-ec2_sp_purchase["etimated_percent"].astype(float)/100) * ec2_sp_purchase["Cost"].astype(float)
        ec2_sp_purchase["Monthly_Savings"] = (ec2_sp_purchase["Cost"]-ec2_sp_purchase["To_Purchase"]) * 720
        return ec2_sp_purchase