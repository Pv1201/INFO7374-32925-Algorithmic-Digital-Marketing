# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:11:43 2023

@author: mohit
"""

#Importing libraries
import pandas as pd
import numpy as np
import datetime

#Visual libraries
import plotly.express as px
# from dash import Dash, dcc, html, Input, Output
# from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#Dashboard and Report libraries
import streamlit as st

st.markdown("# Assignment-1")
st.sidebar.header("Assignment-1")

#reset the customer row names to proper values
def reset_df_header(df):
    df.columns=df.loc[0]
    df=df.drop(index=0,inplace=True)

def get_female_marketing_effectiveness(new,old):
    if new==0 and old==0:
        return 0
    else:
        sum=new+old
        return round(100*float(new/sum),2)    

global transcaction
global CustomerDemographic
global CustomerAddress
global NewCustomerList

def filter_plot(df):
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(y=df.job_industry_category, x=df.new_female_count,orientation='h',marker_color='rgb(115,190,115)',name='New Female Customers'))
    fig1.add_trace(go.Bar(y=df.job_industry_category, x=df.old_female_count,orientation='h',marker_color='crimson',name='Old Female Customers'))
    fig1.update_layout(template='plotly_dark')
    st.plotly_chart(fig1)
    

def data_cleaning():
    transcaction=pd.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="Transactions")
    CustomerDemographic=pd.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="CustomerDemographic")
    CustomerAddress=pd.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="CustomerAddress")
    NewCustomerList=pd.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="NewCustomerList")
    
    
    reset_df_header(transcaction)
    reset_df_header(CustomerAddress)
    reset_df_header(NewCustomerList)    
    NewCustomerList = NewCustomerList.loc[:, NewCustomerList.columns.notna()]
    
    
    #Finding gender demograph industry wise for new acquired customers
    NewCustGender=NewCustomerList[['first_name','gender','job_industry_category']].groupby(['gender','job_industry_category']).count().reset_index()
    NewCustGender.rename(columns={"first_name":"Count"},inplace=True)
    NewCustGender['new_female_count']=NewCustGender['Count'][NewCustGender['gender']=='Female']
    NewCustGender['new_male_count']=NewCustGender['Count'][NewCustGender['gender']=='Male']
    NewCustGender['new_unknown_count']=NewCustGender['Count'][NewCustGender['gender']=='U']
    NewCustGender.drop(columns=['gender','Count'],inplace=True)
    NewCustGender=NewCustGender.groupby('job_industry_category').sum().reset_index()
    
    #Finding gender demograph industry wise for new acquired customers
    OldCustomerDemographic=CustomerDemographic[['name','gender','job_industry_category']].groupby(['gender','job_industry_category']).count().reset_index()
    OldCustomerDemographic.rename(columns={"name":"Count"},inplace=True)
    OldCustomerDemographic['old_female_count']=OldCustomerDemographic['Count'][OldCustomerDemographic['gender']=='Female']
    OldCustomerDemographic['old_male_count']=OldCustomerDemographic['Count'][OldCustomerDemographic['gender']=='Male']
    OldCustomerDemographic['old_unknown_count']=OldCustomerDemographic['Count'][OldCustomerDemographic['gender']=='U']
    OldCustomerDemographic.drop(columns=['gender','Count'],inplace=True)
    OldCustomerDemographic=OldCustomerDemographic.groupby('job_industry_category').sum().reset_index()
    OldCustomerDemographic.rename(columns={"job_industry_category":"old_job_industry_category"},inplace=True)
    
    #Merged File
    merged_customer_demo=pd.concat([NewCustGender,OldCustomerDemographic],axis='columns') #,how='inner',on=['job_industry_category'])
    merged_customer_demo.drop(columns=['old_job_industry_category'],inplace=True)
    
    merged_customer_demo['f_effective%']=merged_customer_demo.apply(lambda x: get_female_marketing_effectiveness(x['new_female_count'],x['old_female_count']),axis=1)
    merged_customer_demo['m_effective%']=merged_customer_demo.apply(lambda x: get_female_marketing_effectiveness(x['new_male_count'],x['old_male_count']),axis=1)
    merged_customer_demo['u_effective%']=merged_customer_demo.apply(lambda x: get_female_marketing_effectiveness(x['new_unknown_count'],x['old_unknown_count']),axis=1)

    filter_plot(merged_customer_demo)
    
    fig2=go.Figure()
    fig2.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.new_male_count,orientation='h',marker_color='rgb(27,79,114)',name='New Male Customers'))
    fig2.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.old_male_count,orientation='h',marker_color='crimson',name='Old Male Customers'))
    fig2.update_layout(template='plotly_dark')
    st.plotly_chart(fig2)
    
    fig3=go.Figure()
    fig3.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.new_unknown_count,orientation='h',marker_color='rgb(255, 220, 172)',name='New Unknow Customers'))
    fig3.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.old_unknown_count,orientation='h',marker_color='crimson',name='Old Unknow Customers'))
    fig3.update_layout(template='plotly_dark')
    st.plotly_chart(fig3)
    
    fig4=go.Figure()
    fig4.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo['f_effective%'],orientation='h',name='Female'))
    fig4.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo['m_effective%'],orientation='h',name='Male'))
    fig4.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo['u_effective%'],orientation='h',name='Unknown'))
    fig4.update_layout(template='plotly_dark')
    st.plotly_chart(fig4)
    
    

def plot():
    pass


if __name__ == "__main__":
    data_cleaning()
    plot()
    
    

    






















