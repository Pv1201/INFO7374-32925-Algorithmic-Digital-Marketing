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

st.set_page_config(
    page_title="Home",
)

st.write("# INFO7374-32925-Algorithmic-Digital-Marketing Assignment's")
st.sidebar.success("Select a Assignment above.")

st.markdown(
    """
    INFO7374-32925-Algorithmic-Digital-Marketing Assignment's.
    
    **👈 Select Assignment's from the sidebar** 
    ### Visit the github repository link's?
    - Assignment-1[Github](https://github.com/Negi97Mohit/INFO7374-32925-Algorithmic-Digital-Marketing)

"""
)
