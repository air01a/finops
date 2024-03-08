import streamlit as stm 
from datetime import datetime, timedelta
from aws_cost_explorer import AwsCEHelper
import streamlit as st
import sys, os
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_path+'/utils/')


from pyplot_utils import graphics
from sidebar import show_side_bar

def show_global_usage(st,usage):
    gauge = {'axis': {'range': [None, 100]},
             'steps' : [
                 {'range': [0, 98], 'color': "orange"},
                 {'range': [98, 100], 'color': "lightgreen"}],
             }
    graph = graphics(st)
    graph.indicator(usage['utilization'][0],"RI Usage", gauge)
    

def show_reservation_rate(st,usage):
    gauge = {'axis': {'range': [None, 100]},
             'steps' : [
                 {'range': [0, 80], 'color': "orange"},
                 {'range': [80, 100], 'color': "lightgreen"}],
             }
    graph = graphics(st)
    graph.indicator(usage['reservation_rate'][0],"RI Coverage", gauge)


def show_details(st, details):
    st.table(details)



aws_helper = AwsCEHelper()

start_date = (datetime.today() - timedelta(days=5))
end_date = (datetime.today() - timedelta(days=2))

if end_date<start_date or (end_date - start_date).days>14:
    end_date = start_date + timedelta(days=14)


start_date, end_date = show_side_bar(st,start_date, end_date)

stm.title("RI Usage") 
ri_details, ri_global = aws_helper.get_ri_usage(start_date, end_date)
st.subheader("Ec2 indicators")

show_global_usage(st, ri_global)
show_reservation_rate(st, ri_global)
st.subheader("Savings")
st.metric(label="Net Economy", value=ri_global['savings'][0])
show_details(st, ri_details)
