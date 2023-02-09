# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:11:43 2023

@author: mohit
"""

#Importing libraries
import pandas as pd
from pandas_profiling import ProfileReport
import great_expectations as ge
import requests

#Visual libraries
import plotly.express as px
# from dash import Dash, dcc, html, Input, Output
# from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#Dashboard and Report libraries
import streamlit as st
import streamlit.components.v1 as components

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

workbook_url='https://github.com/Negi97Mohit/INFO7374-32925-Algorithmic-Digital-Marketing/blob/main/KPMG_VI_New_raw_data_update_final.xlsx'

#function for EDA
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
    
    transcaction.transaction_date=pd.to_datetime(transcaction.transaction_date)
    transcaction['month']=pd.DatetimeIndex(transcaction.transaction_date).month_name()
    transcaction.list_price=transcaction.list_price.astype('float')
    transcaction.standard_cost=transcaction.standard_cost.astype('float')
    transcaction['profit(K)']=(transcaction.list_price-transcaction.standard_cost)/1000
    
    #merging with customer demographic for further exploration
    cust_expense=pd.merge(transcaction,CustomerDemographic,how='outer',on=['customer_id'])
    
    
    #gouping by each month, customer type and product type
    profits=cust_expense.groupby(['month','wealth_segment','product_size'])['profit(K)'].sum().reset_index()
    profits=profits.round(2)
    
    profits['above_avg']=profits['profit(K)'].apply(lambda x: x if x>profits['profit(K)'].mean() else 0)
    profits['below_avg']=profits['profit(K)'].apply(lambda x: x if x<profits['profit(K)'].mean() else 0)
    

    tab1,tab2,tab3=st.tabs(["Finding the spending cycle","Marketing Effectiveness","Let's talk profits"])
    with tab1:
        st.write('### Finding the spending cycle')

        st.write('-  Since the transactions are only for the year 2017 we will summarize the montly purchases for each month.')
        st.write('-  We will also find the most profitable month for the year 2017.') 
        st.write('-  Since the profits have a wide range we create two section, one for above average and the other for below average profit values')
        st.write('-  We need to find the most profitable and least profitable values per season')
        fig = px.sunburst(profits,
                          path=['month', 'wealth_segment', 'product_size'],values='above_avg',color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(width=800, 
                          height=800,
                         )

        st.plotly_chart(fig)
        st.markdown("<h3 style='text-align: center; color: black;'>Above Averge Monthly Spenders</h3>", unsafe_allow_html=True)
        
        fig = px.sunburst(profits,
                  path=['month', 'wealth_segment', 'product_size'],values='below_avg',color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(width=800, 
                          height=800,
                         )
        st.plotly_chart(fig)
        st.markdown("<h3 style='text-align: center; color: black;'>Below Averge Monthly Spenders</h3>", unsafe_allow_html=True)
    with tab2:
        st.write("### Sector of new customer acquired")
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.new_female_count,orientation='h',marker_color='rgb(115,190,115)',name='New Female Customers'))
        fig1.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.old_female_count,orientation='h',marker_color='crimson',name='Old Female Customers'))
        fig1.update_layout(template='plotly_dark')
        st.plotly_chart(fig1,theme="streamlit")
        
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
        
        st.write('#### How different is our current customer base different from the new acquired customer base, which will help us indicate which category of consumers we can cater the needs to.')
        fig = go.Figure()
        fig.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.new_female_count,orientation='h',marker_color='rgb(144,238,144)',name='New Female Customers'))
        fig.add_trace(go.Bar(y=merged_customer_demo.job_industry_category, x=merged_customer_demo.old_female_count,orientation='h',marker_color='crimson',name='Old Female Customers'))
        st.plotly_chart(fig)
        
    with tab3:
        st.write('#### What are the numbers from on online and offline sales')
        st.write(transcaction.groupby(['online_order'])['profit(K)'].sum())
        st.write('#### What are the numbers for different class of product')
        st.write(transcaction.groupby(['online_order','product_class'])['profit(K)'].sum())
        st.write('#### What are the numbers for different line of product')
        st.write(transcaction.groupby(['online_order','product_class','product_line'])['profit(K)'].sum())

#function for great_expectation computation
def expectation():
    transcaction=ge.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="Transactions")
    CustomerDemographic=ge.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="CustomerDemographic")
    CustomerAddress=ge.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="CustomerAddress")
    NewCustomerList=ge.read_excel(r"C:\gitlab\KPMG_VI_New_raw_data_update_final.xlsx\KPMG_VI_New_raw_data_update_final.xlsx",sheet_name="NewCustomerList")
    
    reset_df_header(transcaction)
    reset_df_header(CustomerAddress)
    reset_df_header(NewCustomerList)    
    NewCustomerList = NewCustomerList.loc[:, NewCustomerList.columns.notna()]
            
    #st.write(transcaction.expect_column_values_to_be_unique(column='brand'))
    validation_result = transcaction.expect_column_values_to_be_in_set(
        column="online_order",
        value_set=[True,False],
        result_format={
            "result_format": "BOOLEAN_ONLY",
            "unexpected_index_column_names": ["online_order"],
            "return_unexpected_index_query": True,
        },
    )
    #st.write(validation_result.success)
    #st.write(validation_result)
    HtmlFile = open("C:/INFO7374-32925-Algorithmic-Digital-Marketing/great_expectations/uncommitted/data_docs/local_site/validations/Assignment1_ge/__none__/20230208T183522.594784Z/eda493f1d25126cede31f768221bf0e2.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, width = 800, height = 800, scrolling = True)


#function for EDA
def profiling():    
    pass

if __name__ == "__main__":
    
    option_selected = st.selectbox(
    'SELECT SECTION',
    ('EDA', 'Pandas Profiling & Data Quality Analysis', 'Great Expectations'))
        
    
    if option_selected=="Pandas Profiling & Data Quality Analysis":
        st.write("Fuck yeah")
            
    if option_selected=="EDA":    
        st.write('#### Question to ask ourself')
        st.write('- How successful was the previous marketing campaign, what typr of clients did we attract most? ')
        st.write('- How different is our current customer base different from the new acquired customer base, which will help us indicate which category of consumers we can cater the needs to.')
        st.write('- Where do we see the bussiness going with new customers acquired. Do we need to make changes, if YES then to what extend.')
        data_cleaning()    
    
    if option_selected=='Great Expectations':
        st.write('### Great Expectations')
        expectation()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    