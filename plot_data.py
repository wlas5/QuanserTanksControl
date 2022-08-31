#coding=utf8
import io
import pandas as pd  
from datetime import datetime
import plotly.graph_objects as go
headers = ['Menor','3xMenor','Soma','DataHora','PotInstInv1','PotInstInv2']
df = pd.read_csv('data.csv',delimiter=";",names=["Data", "Ref", "Nivel", "Erro", "U","corrente"])

x = df['Data']
y = df['Ref']
z = df['Nivel']

inicio = 1
fim =  330

fig = go.Figure()
fig.add_trace(go.Scatter(y=y, name='Ref'))
fig.add_trace(go.Scatter(y=z, name='Ref'))

#fig.add_trace(go.Scatter(y=z, use_index=True, name='Nivel'))
#fig.add_trace(go.Scatter(x=x ,y=z, name='Potência Total'))
fig.update_layout(xaxis_range=[inicio,fim],yaxis_range=[0,20])
fig.show()
