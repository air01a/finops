import streamlit as stm 
from datetime import datetime, timedelta
from aws_utils import AwsHelper
import streamlit as st
from pyplot_utils import graphics

def average(lst): 
    return sum(lst) / len(lst) 


def show_big_instance(ec2_big_instances):
    ec2_big_instances['Instance']=ec2_big_instances['Instance_Type']+'.'+ec2_big_instances['Instance_Size']
    graph = graphics(st)
    graph.line(ec2_big_instances, 'Date','Cost',groupby='Instance',title='Aws big instance')

def show_residuals(residuals):
     
    graph = graphics(st)

    graph.line(residuals,'Date','Cost',title="Residuals")
    
def show_ec2_cost(cost):
    graph = graphics(st)    
    #data = [[i,cost[i]] for i in range(len(cost))]
    #print(data)
    graph.line(cost, 'Date','Cost', title="EC2 Cost")


stm.title("EC2 Costs") 

aws_helper = AwsHelper()

# Définir la période de temps pour laquelle récupérer les coûts
start_date = datetime.today() - timedelta(days=13)
end_date = datetime.today()- timedelta(days=1)
last_month = end_date - timedelta(weeks=4)
# Obtenir et afficher les coûts EC2
ec2_costs = aws_helper.get_hourly_cost(start_date, end_date)
ec2_instances = aws_helper.get_hourly_cost_by_instance(start_date, end_date)
ec2_big_instances = aws_helper.get_big_instances_cost(ec2_instances)

residuals = aws_helper.get_residual(ec2_instances)
st.header("Compute on demand")
show_ec2_cost(ec2_costs)
st.header("Big instance on demand")
show_big_instance(ec2_big_instances)
st.header("Residuals")
show_residuals(residuals)
st.header("Recommendation")
ec2_big_instances_to_reserve = ec2_big_instances.groupby('Instance_Type').agg({'Date': 'count', 'Cost': 'sum'})
st.table(ec2_big_instances_to_reserve[ec2_big_instances_to_reserve['Date'] == 288]['Cost'])
st.subheader(f"Savings plan residual : {residuals['Cost'].min():.2f}", divider='red')
