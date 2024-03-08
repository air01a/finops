import streamlit as stm 
from datetime import datetime, timedelta
from aws_cost_explorer import AwsCEHelper
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

def filter_instances_without_zero_cost(group):
    return (group['Cost'] != 0).all()


stm.title("EC2 Costs") 

aws_helper = AwsCEHelper()

# Définir la période de temps pour laquelle récupérer les coûts
start_date = datetime.today() - timedelta(days=13)
end_date = datetime.today() - timedelta(days=2)
last_month = end_date - timedelta(weeks=4)
# Obtenir et afficher les coûts EC2
ec2_costs = aws_helper.get_hourly_cost(start_date, end_date)
ec2_instances = aws_helper.get_hourly_cost_by_instance(start_date, end_date)
ec2_big_instances = aws_helper.get_big_instances_cost(ec2_instances)

ec2_sp_reco = aws_helper.get_ec2_recommendation()
sp_reco = aws_helper.get_compute_sp_reco()
discount = sp_reco['estimated_percent'][0]/100

residuals = aws_helper.get_residual(ec2_instances)
with st.expander("Graphics", expanded=False):
    st.header("Compute on demand")
    show_ec2_cost(ec2_costs)
    st.header("Big instance on demand")
    show_big_instance(ec2_big_instances)
    st.header("Residuals")
    show_residuals(residuals)
st.header("Recommendation")

with st.expander("AWS Recommendation", expanded=False):
    st.subheader("AWS Recommendation for EC2 Instances")
    st.table(ec2_sp_reco)
    st.subheader("AWS Recommendation for compute")
    st.table(sp_reco)

st.subheader("Current Big instance")
st.caption("Select big instance that you want to reserve")

# Calculate and show big instance that are never at 0 during the current period
filtered_df = ec2_big_instances.groupby('Instance').filter(filter_instances_without_zero_cost).groupby("Instance")["Cost"].min().reset_index()
filtered_df["Selected"] = False
filtered_df.insert(0, 'Selected', filtered_df.pop('Selected'))
selected_big_instance=st.data_editor(filtered_df)


# Substract selected instance cost from global compute cost
compute_cost =aws_helper.get_min_total_compute(ec2_big_instances)
filter_on_selected = selected_big_instance[selected_big_instance['Selected']==True]['Instance'].tolist()
residuals_cost = aws_helper.get_min_total_compute(ec2_instances, filter_on_selected)
st.header(residuals_cost.min())
st.table(residuals_cost)
#Calculate amount to purchase for aws compute
min_cost = residuals_cost.min() *(1-discount)
savings = (residuals_cost.min() - min_cost)*720

st.divider()

st.subheader(f"Savings plan to purchase : {min_cost:.2f}", divider='red')
st.subheader(f"EC2 Saving plans to purchase :", divider='red')
ec2_sp_purchase = selected_big_instance[selected_big_instance['Selected']==True].drop('Selected',axis=1)

saving_instance = 0
if len(ec2_sp_purchase)>0:
    ec2_sp_purchase = aws_helper.get_instance_sp_reco(ec2_sp_purchase, ec2_sp_reco)
    st.table(ec2_sp_purchase)
    saving_instance= ec2_sp_purchase["Monthly_Savings"].sum()

st.subheader(f"Global Saving : {int(saving_instance + savings) }/m, {int((saving_instance + savings)*12) }/y", divider='red')
