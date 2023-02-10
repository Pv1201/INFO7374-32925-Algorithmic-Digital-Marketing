# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:11:43 2023

@author: mohit
"""

#Importing libraries
import pandas as pd
from pandas_profiling import ProfileReport

#Visual libraries
import plotly.express as px
# from dash import Dash, dcc, html, Input, Output
# from plotly.offline import plot
import plotly.graph_objects as go

#Dashboard and Report libraries
import streamlit as st
import streamlit.components.v1 as components
from streamlit_pandas_profiling import st_profile_report


st.markdown("# Assignment-1")
st.sidebar.header("Assignment-1")

def get_data():
    global transaction
    global CustomerDemographic
    global CustomerAddress
    global NewCustomerList

    tran_url=('https://docs.google.com/spreadsheets/d/1i1K42EZurcdozq0wc2JgR0RbqM470dLQ/edit#gid=1362789858')
    newcust_url='https://docs.google.com/spreadsheets/d/1i1K42EZurcdozq0wc2JgR0RbqM470dLQ/edit#gid=1123351247'
    cust_demo_url='https://docs.google.com/spreadsheets/d/1i1K42EZurcdozq0wc2JgR0RbqM470dLQ/edit#gid=2032610074'
    cust_Addr_url='https://docs.google.com/spreadsheets/d/1i1K42EZurcdozq0wc2JgR0RbqM470dLQ/edit#gid=1901353749'

    tran_xlsx_export_url = tran_url.replace('/edit#gid=', '/export?format=xlsx&gid=')
    newcust_xlsx_export_url = newcust_url.replace('/edit#gid=', '/export?format=xlsx&gid=')
    custdemo_xlsx_export_url = cust_demo_url.replace('/edit#gid=', '/export?format=xlsx&gid=')
    custaddr_xlsx_export_url = cust_Addr_url.replace('/edit#gid=', '/export?format=xlsx&gid=')

    transaction=pd.read_excel(tran_xlsx_export_url)
    CustomerDemographic=pd.read_excel(custdemo_xlsx_export_url)
    CustomerAddress=pd.read_excel(custaddr_xlsx_export_url)
    NewCustomerList=pd.read_excel(newcust_xlsx_export_url)


def get_female_marketing_effectiveness(new,old):
    if new==0 and old==0:
        return 0
    else:
        sum=new+old
        return round(100*float(new/sum),2)    


workbook_url='https://github.com/Negi97Mohit/INFO7374-32925-Algorithmic-Digital-Marketing/blob/main/KPMG_VI_New_raw_data_update_final.xlsx'

#function for EDA
def data_cleaning():
  
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
    
    transaction.transaction_date=pd.to_datetime(transaction.transaction_date)
    transaction['month']=pd.DatetimeIndex(transaction.transaction_date).month_name()
    transaction.list_price=transaction.list_price.astype('float')
    transaction.standard_cost=transaction.standard_cost.astype('float')
    transaction['profit(K)']=(transaction.list_price-transaction.standard_cost)/1000
    
    #merging with customer demographic for further exploration
    cust_expense=pd.merge(transaction,CustomerDemographic,how='outer',on=['customer_id'])
    
    
    #gouping by each month, customer type and product type
    profits=cust_expense.groupby(['month','wealth_segment','product_size'])['profit(K)'].sum().reset_index()
    profits=profits.round(2)
    
    profits['above_avg']=profits['profit(K)'].apply(lambda x: x if x>profits['profit(K)'].mean() else 0)
    profits['below_avg']=profits['profit(K)'].apply(lambda x: x if x<profits['profit(K)'].mean() else 0)
    

    tab1,tab2,tab3,tab4=st.tabs(["Finding the spending cycle","Marketing Effectiveness","Lets talk profits","Our Inference"])
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
        st.write(transaction.groupby(['online_order'])['profit(K)'].sum())
        st.write('#### What are the numbers for different class of product')
        st.write(transaction.groupby(['online_order','product_class'])['profit(K)'].sum())
        st.write('#### What are the numbers for different line of product')
        st.write(transaction.groupby(['online_order','product_class','product_line'])['profit(K)'].sum())

#function for great_expectation computation
def expectation():     
# =============================================================================
#     validation_result = transaction.expect_column_values_to_be_in_set(
#         column="online_order",
#         value_set=[True,False],
#         result_format={
#             "result_format": "BOOLEAN_ONLY",
#             "unexpected_index_column_names": ["online_order"],
#             "return_unexpected_index_query": True,
#         },
#     )
#     #st.write(validation_result.success)
# =============================================================================
    #st.write(validation_result)
    
    #HtmlFile = open("https://raw.githubusercontent.com/Negi97Mohit/INFO7374-32925-Algorithmic-Digital-Marketing/main/Assignment-1/Assignment1_ge.html", 'r', encoding='utf-8')
    #source_code = HtmlFile.read()
    components.html("https://raw.githubusercontent.com/Negi97Mohit/INFO7374-32925-Algorithmic-Digital-Marketing/main/Assignment-1/Assignment1_ge.html", width = 800, height = 800, scrolling = True)


#function for EDA
def profiling():    

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
    
    transaction.transaction_date=pd.to_datetime(transaction.transaction_date)
    transaction['month']=pd.DatetimeIndex(transaction.transaction_date).month_name()
    transaction.list_price=transaction.list_price.astype('float')
    transaction.standard_cost=transaction.standard_cost.astype('float')
    transaction['profit(K)']=(transaction.list_price-transaction.standard_cost)/1000
    
    #merging with customer demographic for further exploration
    cust_expense=pd.merge(transaction,CustomerDemographic,how='outer',on=['customer_id'])
    
    
    #gouping by each month, customer type and product type
    profits=cust_expense.groupby(['month','wealth_segment','product_size'])['profit(K)'].sum().reset_index()
    profits=profits.round(2)
    
    profits['above_avg']=profits['profit(K)'].apply(lambda x: x if x>profits['profit(K)'].mean() else 0)
    profits['below_avg']=profits['profit(K)'].apply(lambda x: x if x<profits['profit(K)'].mean() else 0)
    
    tab1,tab2=st.tabs(['Profile Reports','Our Inference'])

    with tab1:
        profit_expander = st.expander(label='Profit Report')
        with profit_expander:
            'Profits Profile Report'
            profit_report=ProfileReport((profits))
            st_profile_report(profit_report)
        merged_expander = st.expander(label='Customers Report')
        with merged_expander:
            'Customers Profile Report'
            merged_customer_demo=ProfileReport((merged_customer_demo))
            st_profile_report(merged_customer_demo)

        tran_expander = st.expander(label='Transaction Report')
        with tran_expander:
            'Transaction Profile Report'
            tran_repo_demo=ProfileReport((cust_expense))
            st_profile_report(tran_repo_demo)            


if __name__ == "__main__":
    get_data()
    option_selected = st.selectbox(
    'SELECT SECTION',
    ('EDA', 'Pandas Profiling & Data Quality Analysis', 'Great Expectations'))
    
    if option_selected=="Pandas Profiling & Data Quality Analysis":
        profiling()
        
    if option_selected=="EDA":    
        st.write('#### Question to ask ourself')
        st.write('- How successful was the previous marketing campaign, what typr of clients did we attract most? ')
        st.write('- How different is our current customer base different from the new acquired customer base, which will help us indicate which category of consumers we can cater the needs to.')
        st.write('- Where do we see the bussiness going with new customers acquired. Do we need to make changes, if YES then to what extend.')
        data_cleaning()    
    
    if option_selected=='Great Expectations':
        st.write('### Great Expectations')
        expectation()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
