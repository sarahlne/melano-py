#imports
import os 
import re
import pathlib
import json
import sqlite3
from tkinter import font
from turtle import width
from unicodedata import name
from matplotlib.pyplot import title
import pandas as pd
import sklearn as sk
import plotly.express as px
import streamlit as st
import logging

from datetime import datetime
from peewee import Field, IntegerField, DateField, DateTimeField, CharField, ForeignKeyField, Model as PWModel
from peewee import SqliteDatabase
from playhouse.reflection import generate_models, print_model, print_table_sql

db = SqliteDatabase('test_melanodb.db')

def viz():
    ############## LOAD DATA ##############
    cnx = sqlite3.connect('test_melanodb.db')
    df_indels = pd.read_sql_query("SELECT * FROM snps", cnx)

    df_indels_unique = df_indels.drop_duplicates(['patient_id','HGNC'])
    df_indels_unique = df_indels_unique['HGNC'].value_counts().reset_index()
    list_freq = []
    for i in range(0,len(df_indels_unique['HGNC'])):
        list_freq.append(df_indels_unique['HGNC'][i]*100/165)
    
    list_freq = [round(list_freq[i],1) for i in range(0,len(list_freq))]
    df_indels_unique['Freq'] = list_freq

    

    df_cat_freq = df_indels.drop_duplicates(['patient_id','HGNC'])
    df_cat_freq = df_cat_freq['HGNC'].value_counts().reset_index()
    df_cat_freq['HGNC'] = pd.cut(df_cat_freq.HGNC, 
                            bins=[0,5,10,50,60,70,80,110], 
                            labels=['-5','[5-10]','[10-50]','[50-60]','[60-70]','[70-80]','80+']
                            )
    df_cat_freq = df_cat_freq['HGNC'].value_counts().reset_index()
    df_cat_freq = df_cat_freq.rename(columns = {'index':'Number of patients w/ this mutated gene', 'HGNC':'Number of genes'})

    bar_cat_freq = px.bar(df_cat_freq,
                            x = 'Number of patients w/ this mutated gene',
                            y = 'Number of genes',
                            log_y=True,
                            text = 'Number of genes',
                            title='Number of genes mutated in same patients')
    bar_cat_freq.update_layout(font=dict(size = 18), legend=dict(font = dict(size = 18)))
    

    top = st.columns((2,1))
    with top[0]:
        st.write(f'SNPs information about 165 patients for 50042')
        st.plotly_chart(bar_cat_freq, use_container_width=True)
    with top[1]:
        st.write('#### Gene mutations frenquencies among patients', font=dict(size = 24))
        st.dataframe(df_indels_unique)

    df_temporality = df_indels
    df_temporality = df_temporality.drop_duplicates(['patient_id','sample_id'])
    df_temporality = df_temporality['patient_id'].value_counts().reset_index()
    df_temporality = df_temporality['patient_id'].value_counts().reset_index()
    df_temporality['index'] = df_temporality['index'].replace([1,2],['pre', 'pre and post'])
    df_temporality = df_temporality.rename(columns = {'index':'samples', 'patient_id':'#patients'})

    pie_chart_temporality = px.pie(df_temporality,
                                    title='Proportions of patients with "pre" or "pre and post" treatment samples',
                                    values = '#patients',
                                    names = 'samples',
                                    )
    pie_chart_temporality.update_traces(hoverinfo='percent', textinfo='value+label')
    pie_chart_temporality.update_layout(font=dict(size = 18),legend=dict(font = dict(size = 20)))

    st.plotly_chart(pie_chart_temporality)

    