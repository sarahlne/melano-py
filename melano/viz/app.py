#imports
import os 
import re
import pathlib
import json
import sqlite3
from unicodedata import name
import pandas as pd
import sklearn as sk
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import logging

from datetime import datetime
from peewee import Field, IntegerField, DateField, DateTimeField, CharField, ForeignKeyField, Model as PWModel
from peewee import SqliteDatabase
from playhouse.reflection import generate_models, print_model, print_table_sql

import patients_viz
import indels_viz

st.set_page_config(page_title = 'Database Visualization', layout="wide")
st.title(''' MelanoModel Database Viewing Page ''')

# Sidebar Navigation
st.sidebar.title('Navigation')
options = st.sidebar.radio('Select a page:', 
    ['Home', 'Patients Information', 'INDELs Information'])

if options == 'Patients Information':
    patients_viz.viz()
elif options == 'INDELs Information':
     indels_viz.viz()



st.write('### Created by Sarah Dandou with Streamlit')
st.write('''This explorer is a tool designed using Python and Streamlit to help you view all data contained in the melano-py database.''')
sm_git = """<a href='https://github.com/sarahlne/melano-py' target="_blank"><img src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png' width="50" height="50"></a>"""
st.write(f'You can donwload the database and related code here: {sm_git}', unsafe_allow_html=True)



st.write('### Descriptions of data')
st.write('#### Table 1: patients')
st.write('**Sex:** refers to the sex of the patient (values: male or female)')
st.write('**Age:** refers to the age of the patient')
st.write('''**AJCC/Stage:** indicator associated to the evolution of a cancer, describe the location, the size, 
how far it has grown into nearby tissues and if it has spread to nearby lymph nodes or other parts of the body . 
To determine it, clinician remove lesions and some surrounding healthy tissues and analyzed them (through microscope). 
Usually they use the Clark level to describe the evolution. Here, Clark level are transpose to integer values: 
{II, III, IV, V} to {0,1,2,3}.''')
st.write('''**LDH (lacatate dehydrogenase, enzyme):** biological marker, LDH is normally present in the blood 
and other tissues in the body. High LDH level may indicates tissue damage or the presence of cancer cell with values: {normal, elevated}''')
st.write('''**OS statut (Overall Survival):** indicator referred to the living statut of a patient. In randomized 
trials, OS is generally measured as the time from randomization to death due to any cause or (if the data are censored) 
to the last time the subject was known to be alive. Values {alive, death}''')
st.write('''**OS month (Overall Survival):** refers to how long patients, who undergo a certain treatment regimen, 
live compared to patients who are in a control group (i.e., taking either another drug or an inactive treatment, 
known as a placebo) (how long someone lives after starting on a treatment)''')
st.write('''**PFS month (Progression-Free Survival):** refers to the effectiveness of cancer drug. 
Time between the first introduction of a drug and the progression of the disease (or death) 
(how long someone is on a treatment before their cancer starts to grow).''')
st.write('''**Drug:** kinase inhibitor drug used to slow / stop the tumor progression 
(ex: dabrafenib, trametinib, vemurafenib, etc..)''')
st.write('''**Disease control rate/Response statut:** refers to the overall response of a patient to therapy. 
Here, response is described with acronyms among(PD: progressive disease, SD: stable disease, PR: partial response, CR: complete response)''')
st.write('''**BRAF mutated :** indicator the mutation of the BRAF gene (especially a substitution of valine at the 600th 
position of the protein) (ex, V600E, V600K, etc...)''')
st.write('''**Brain metastasis (integer):** indicates the presence of metastasis in the patient's brain with  values: {no, yes}''')
st.write('''**Immunotherapy treatment:** indicates if the patient follow an immunotherapy treatment at the same time. Here, the treatment is
 indicated with values: {no, yes}''')



#### Sunburst
st.write('### What does the database contain')
cnx = sqlite3.connect('test_melanodb.db')
df_patients = pd.read_sql_query("SELECT * FROM patients", cnx)
df_indels = pd.read_sql_query("SELECT * FROM snps", cnx)

nb_ids_patients = len(set(list(df_patients['patient_ID'])))
nb_ids_indels = len(set(list(df_indels['patient_id'])))
nb_ids_cnas = 66

sunburst_ids = go.Figure(go.Sunburst(
labels=["Patients", "Clinical data", "INDELs data - 165", "CNAs - 66"],
parents=["", "Patients", "Clinical data", "INDELs data - 165", ],
values=[10, 294, 165, 66],
))
#sunburst_ids.update_traces(hoverinfo='value', textinfo='value+labels')
sunburst_ids.update_layout(font=dict(size = 15), margin = dict(t=0, l=0, r=0, b=0))
st.plotly_chart(sunburst_ids, use_container_width=True)
