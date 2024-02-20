from datetime import datetime, timedelta
from aws_cost_explorer import AwsCEHelper
import streamlit as st
from pyplot_utils import graphics
import pandas as pd
#Example https://github.com/aws-samples/aws-cost-explorer-report/blob/master/src/lambda.py



def show_cost_by_service(costs,st):
    
    graph = graphics(st)
    graph.pie(costs,'Service','Cost','Cost by service')
    st.table(costs)

def show_monthly_cost_by_service(costs,st):
    graph = graphics(st)
    graph.bar(costs,"Date", "Cost",groupby="Service", title="Monthly cost")

    st.table(costs.groupby('Date')['Cost'].sum().reset_index())

aws_helper = AwsCEHelper()

# Définir la période de temps pour laquelle récupérer les coûts
end_date = datetime.today()- timedelta(days=1)
last_month = end_date - timedelta(weeks=4)
last_six_month = end_date - timedelta(days=180)
# Obtenir et afficher les coûts EC2
cost_by_service = aws_helper.cost_by_service(last_month, end_date)
monthly_cost_by_service = aws_helper.cost_by_service(last_six_month, end_date)

st.title('# Damart finops')
st.sidebar.header("Input Parameters")

st.header("Services")
show_cost_by_service(cost_by_service,st)
show_monthly_cost_by_service(monthly_cost_by_service,st)

