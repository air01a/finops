import plotly.express as px
import pandas as pd

class graphics:

    def __init__(self,st):
        self.st = st

    def line(self,data,x,y,title,groupby=None):

        if groupby!=None:
            fig = px.line(data, x=x, y=y,color=groupby,title=title)
        else:
            fig = px.line(data, x=x, y=y,title=title)

        self.st.plotly_chart(fig, use_container_width=True)    

    def pie(self, data,name, value,title):
        fig = px.pie(data, values=value, names=name, title=title)
        fig.update_traces(textposition='inside', textinfo='label+percent')
        self.st.plotly_chart(fig, use_container_width=True)

    def bar(self, data, x,y , title, groupby):
        if groupby!=None:
            fig = px.bar(data, x=x, y=y, color=groupby, title=title)
        else:
            fig = px.bar(data, x=x, y=y, title=title)
        #fig.update_traces(width=1000)
        self.st.plotly_chart(fig, use_container_width=True)

