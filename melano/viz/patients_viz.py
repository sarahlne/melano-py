#imports
import os 
import re
import pathlib
import json
import sqlite3
from unicodedata import name
import pandas as pd
import plotly.graph_objects as go
import numpy as np
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
    df_patients = pd.read_sql_query("SELECT * FROM patients", cnx)

    ############## CREATE CHARTS ##############
    ### Sex pie chart
    pie_chart_sex = px.pie(df_patients,
                                    title = 'Sex',
                                    values = 'patient_ID',
                                    names = 'sex',
                                    color = 'sex',
                                    color_discrete_map={"male":"#3366CC", "female":"#DD4477"}
                                    )
    pie_chart_sex.update_traces(hoverinfo='percent', textinfo='percent+label')
    pie_chart_sex.update_layout(font=dict(size = 18),legend=dict(
                                                font = dict(
                                                    size = 20
                                                    )
                                                )
                                )

    ### Patients per studies pie chart
    df_patient_per_studies = df_patients.copy()
    df_patient_per_studies = df_patient_per_studies['source'].value_counts().reset_index(name='values')
    for i in range(0, len(df_patient_per_studies['index'])):
        df_patient_per_studies['index'][i] = json.loads(df_patient_per_studies['index'][i])['author']

    pie_chart_patient_per_studies = px.pie(df_patient_per_studies,
                            #title = 'Number of patient per studies (Total number of patients=294)',
                            values = 'values',
                            names = 'index'
                            )
    pie_chart_patient_per_studies.update_traces(hoverinfo='percent', textinfo='value+percent')
    pie_chart_patient_per_studies.update_layout(font=dict(size = 18), legend=dict(font = dict(size = 16)))
    
    ### Age diagnosis bar charts
    df_age_cat = df_patients.copy()
    df_age_cat['age'] = pd.cut(df_age_cat.age, 
                            bins=[0,30,40,45,50,55,60,65,70,75,90], 
                            labels=['-30','[30-40]','[40-45]','[45-50]','[50-55]','[55-60]','[60-65]', '[65-70]', '[70-75]', '75+']
                            )
    df_age_cat = df_age_cat[['age', 'sex']].value_counts(sort=False).reset_index(name = 'values')
    df_age_cat = df_age_cat.rename(columns = {'age':'age (years)', 'values':'number of patients'})
    bar_age_level = px.bar(df_age_cat,
                            x = 'age (years)',
                            y = 'number of patients',
                            color="sex",
                            color_discrete_map={"male":"#3366CC", "female":"#DD4477"},
                            title='Diagnosis Age')
    bar_age_level.update_layout(font=dict(size = 18), legend=dict(font = dict(size = 18)))

    ############## DISPLAY FIRST CHARTS ##############
    top = st.columns((1,1))
    middle_top = st.columns(1)
    middle_down = st.columns((1,1))
    bottom = st.columns((2,1))
    down = st.columns((2,1))
    sup = st.columns((2,1))

    with top[0]:
        st.write(f'Number of patient per studies (Total number of patients={df_patients.shape[0]})')
        st.plotly_chart(pie_chart_patient_per_studies)

    with top[1]:
        st.plotly_chart(pie_chart_sex)

    with middle_top[0]:
        st.plotly_chart(bar_age_level, use_container_width=True)
    
    ### Treatment Drugs
    with middle_down[0]:
        st.markdown("### Treatment Drugs ")
        option_drug_info = st.selectbox('' , ['Drug','Mono-/Bi-therapy'])

        if (option_drug_info == 'Drug'):
            df_drug = df_patients.copy()
            df_drug=df_drug['drug'].value_counts(dropna=False).reset_index()
            pie_chart_drug = px.pie(df_drug,
                                    values='drug',
                                    names='index',
                                    color = 'drug',
                                    color_discrete_map={"male":"#3366CC", "female":"#DD4477"})
            pie_chart_drug.update_traces(hoverinfo='percent', textinfo='value+percent')
            pie_chart_drug.update_layout(font=dict(size = 13), legend=dict(font = dict(size = 14)))
            st.plotly_chart(pie_chart_drug)

        elif(option_drug_info=='Mono-/Bi-therapy'):
            df_drug = df_patients.copy()
            type_drug_list = []
            for i in range(0, len(df_drug['drug'])):
                if("+" in df_drug['drug'][i]):
                    type_drug_list.append("Bitherapy")
                elif(df_drug['drug'][i]=='unknow' or df_drug['drug'][i]=='unknow'):
                    type_drug_list.append("nan")
                else:
                    type_drug_list.append("Monotherapy")
            type_drug_dict = dict((i, type_drug_list.count(i)) for i in type_drug_list)
            type_drug_dict = {"Drug type": list(type_drug_dict.keys()), "count": list(type_drug_dict.values())}
            df_drug2 = pd.DataFrame.from_dict(type_drug_dict)
            pie_chart_drug = px.pie(df_drug2,
                                values='count',
                                names='Drug type',
                                color = 'Drug type',
                                color_discrete_sequence=px.colors.qualitative.Set3)
            pie_chart_drug.update_traces(hoverinfo='percent', textinfo='value+label+percent')
            st.plotly_chart(pie_chart_drug)

    ### Disease Stage
    with middle_down[1]:
        st.markdown("### Disease Stages ")
        option_stage_info = st.selectbox('', ['AJCC/Stage','M-Stage'])

        if(option_stage_info=='AJCC/Stage'):
            df_stage = df_patients.copy()
            df_stage = df_stage['AJCC_stage'].value_counts(dropna=False).reset_index()
            pie_chart_AJCC_stage = px.pie(df_stage,
                                        values = 'AJCC_stage',
                                        names  = 'index',
                                        color = 'index',
                                        color_discrete_sequence=px.colors.qualitative.Pastel[::-1])
            pie_chart_AJCC_stage.update_layout(font=dict(size = 15), legend=dict(font = dict(size = 15)))
            pie_chart_AJCC_stage.update_traces(hoverinfo='value', textinfo='label+percent')
            st.plotly_chart(pie_chart_AJCC_stage)

        elif(option_stage_info=='M-Stage'):
            df_Mstage = df_patients.copy()
            df_Mstage = df_Mstage['M_stage'].value_counts(dropna=False).reset_index()
            list_col = px.colors.qualitative.Pastel[::-1]
            list_col[0], list_col [1] = list_col[1], list_col [0]
            pie_chart_M_stage = px.pie(df_Mstage,
                                        values = 'M_stage',
                                        names  = 'index',
                                        color = 'index',
                                        color_discrete_sequence=list_col)
            pie_chart_M_stage.update_layout(font=dict(size = 15), legend=dict(font = dict(size = 15)))
            pie_chart_M_stage.update_traces(hoverinfo='value', textinfo='label+percent')
            st.plotly_chart(pie_chart_M_stage)

    ### PFS & OS month
    with bottom[0]:
        st.markdown("### OS & PFS in month ")
        option_stage_info = st.selectbox('', ['OS_month','PFS_month'])
        
        if(option_stage_info=='OS_month'):
                df_OS = df_patients.copy()
                df_OS['OS_month'] = pd.cut(df_OS.OS_month, 
                                bins=[1,3,5,10,15,20,25,30,35,135], 
                                labels=['-3','[3-5]','[5-10]','[10-15]','[15-20]','[20-25]','[25-30]', '[30-35]', '35+']
                                )
                df_OS['immunotherapy_treatment'] = df_OS['immunotherapy_treatment'].replace(np.nan, 'unknow')
                df_OS = df_OS[['OS_month', 'immunotherapy_treatment']].value_counts(sort=False, dropna=False).reset_index(name = 'values')
                bar_OS_month = px.bar(df_OS,
                                x = 'OS_month',
                                y = 'values',
                                color = 'immunotherapy_treatment',
                                color_discrete_sequence=px.colors.qualitative.Pastel[::-1])
                st.plotly_chart(bar_OS_month, use_container_width=True)

        if(option_stage_info=='PFS_month'):
                df_PFS = df_patients.copy()
                df_PFS['PFS_month'] = pd.cut(df_PFS.PFS_month, 
                                bins=[0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30,35,40,45,50,60], 
                                labels=['-2','[2-3]','[3-4]','[4-5]','[5-6]','[6-7]', '[7-8]', '[8-9]', '[9-10]', 
                                '[10-11]', '[11-12]', '[12-13]', '[13-14]', '[14-15]', '[15-20]', '[20-30]', '[30-35]',
                                '[35-40]', '[40-45]', '[45-50]', '50+']
                                )
                df_PFS['immunotherapy_treatment'] = df_PFS['immunotherapy_treatment'].replace(np.nan, 'unknow')
                df_PFS = df_PFS[['PFS_month', 'immunotherapy_treatment']].value_counts(sort=False, dropna=False).reset_index(name = 'values')
                bar_PFS_month = px.bar(df_PFS,
                                x = 'PFS_month',
                                y = 'values',
                                color = 'immunotherapy_treatment',
                                color_discrete_sequence=px.colors.qualitative.Pastel[::-1])
                st.plotly_chart(bar_PFS_month, use_container_width=True)
    
    with bottom[1]:
        st.markdown("## Disease Control Rate ")
        df_treatment_response = df_patients.copy()
        df_treatment_response['disease_control_rate'] = df_treatment_response['disease_control_rate'].replace(['SD ', ' SD ', 'PD ', ' PD ', 'CR ', ' CR ', 'PR ', ' PR ', ' SD/PR '],['SD', 'SD', 'PD', 'PD', 'CR', 'CR', 'PR', 'PR', ' PR/SD '])
        df_treatment_response = df_treatment_response['disease_control_rate'].value_counts(dropna=True).reset_index(name='values')

        pie_chart_disease_control_rate = px.pie(df_treatment_response,
                                values = 'values',
                                labels={"PD":"Progressive Disease", "CR":"Complete Response", "PR": "Partial Response", "SD": "Stable Response", "N.E.": "Non Evaluated", "PR/SD": "PR/SD"},
                                names = "index",
                                color = 'index',
                                color_discrete_sequence=px.colors.qualitative.Safe
                                )
        pie_chart_disease_control_rate.update_traces(hoverinfo='percent', textinfo='label+percent')

        st.plotly_chart(pie_chart_disease_control_rate, use_container_width=True)

    with down[0]:
        st.markdown("### Other informations ")
        option_stage_info = st.selectbox('',['LDH', 'Brain metastasis', 'Immunotherapy treatment', 'BRAF mutation'])
        if(option_stage_info=='LDH'):
            pie_chart_LDH = px.pie(df_patients,
                                 values = 'patient_ID',
                                 names = 'LDH',
                                 color_discrete_sequence=px.colors.sequential.RdBu
                                 )
            pie_chart_LDH.update_layout(font=dict(size = 16), legend=dict(font = dict(size = 16)))
            pie_chart_LDH.update_traces(hoverinfo='percent', textinfo='label+percent')
            st.plotly_chart(pie_chart_LDH)

        elif(option_stage_info=='Brain metastasis'):
            df_brain = df_patients.copy()
            df_brain = df_brain['brain_metastasis'].value_counts(dropna=False).reset_index()
            pie_chart_brain = px.pie(df_brain,
                                 values = 'brain_metastasis',
                                 names = 'index',
                                 color = 'index',
                                 color_discrete_sequence=[px.colors.qualitative.Pastel[10],px.colors.qualitative.Pastel[1],px.colors.qualitative.Pastel[2]]
                                 )
            pie_chart_brain.update_layout(font=dict(size = 16), legend=dict(font = dict(size = 16)))
            pie_chart_brain.update_traces(hoverinfo='percent', textinfo='label+percent')
            st.plotly_chart(pie_chart_brain)

        elif(option_stage_info=='Immunotherapy treatment'):
            df_immuno = df_patients.copy()
            df_immuno = df_immuno['immunotherapy_treatment'].value_counts(dropna=False).reset_index()
            list_col1 = px.colors.qualitative.Pastel
            list_col1[0], list_col1[10] = list_col1[10], list_col1[0]
            pie_chart_immuno = px.pie(df_immuno,
                                 values = 'immunotherapy_treatment',
                                 names = 'index',
                                 color = 'index',
                                 color_discrete_sequence=list_col1
                                 )
            pie_chart_immuno.update_layout(font=dict(size = 16), legend=dict(font = dict(size = 16)))
            pie_chart_immuno.update_traces(hoverinfo='percent', textinfo='label+percent')
            st.plotly_chart(pie_chart_immuno)
        
        elif(option_stage_info=='BRAF mutation'):
            df_braf_mut = df_patients.copy()
            df_braf_mut = df_braf_mut['BRAF_mut'].value_counts(dropna=False).reset_index()
            list_col2 = px.colors.qualitative.Set2[::-1]
            list_col2[0], list_col2[1] = list_col2[1], list_col2[0]
            pie_chart_braf_mut = px.pie(df_braf_mut,
                                 values = 'BRAF_mut',
                                 names = 'index',
                                 color = 'index',
                                 color_discrete_sequence=list_col2
                                 )
            pie_chart_braf_mut.update_layout(font=dict(size = 16), legend=dict(font = dict(size = 16)))
            pie_chart_braf_mut.update_traces(hoverinfo='percent', textinfo='label+percent')
            st.plotly_chart(pie_chart_braf_mut)

    #### OS and PFS repartition on studies
    with sup[0]:
        st.markdown("### OS & PFS in month by study ")
        option_stage_info = st.selectbox('', ['OS_month repartition by study','PFS_month repartition by study'])

        if(option_stage_info=='OS_month repartition by study'):
            df_OS_sup = df_patients.copy()
            df_OS_sup['OS_month'] = pd.cut(df_OS_sup.OS_month, 
                                    bins=[1,3,5,10,15,20,25,30,35,135], 
                                    labels=['-3','[3-5]','[5-10]','[10-15]','[15-20]','[20-25]','[25-30]', '[30-35]', '35+']
                                    )
            df_OS_sup = df_OS_sup[['OS_month', 'source']].value_counts(sort=False, dropna=False).reset_index(name = 'values')
            for i in range(0, len(df_OS_sup['source'])):
                df_OS_sup['source'][i] = json.loads(df_OS_sup['source'][i])['author']
            bar_OS_sup_month = px.bar(df_OS_sup,
                            x = 'OS_month',
                            y = 'values',
                            color = 'source',
                            color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(bar_OS_sup_month, use_container_width=True)
        
        elif(option_stage_info=='PFS_month repartition by study'):
            df_PFS_sup = df_patients.copy()
            df_PFS_sup['PFS_month'] = pd.cut(df_PFS_sup.PFS_month, 
                            bins=[0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30,35,40,45,50,60], 
                            labels=['-2','[2-3]','[3-4]','[4-5]','[5-6]','[6-7]', '[7-8]', '[8-9]', '[9-10]', 
                            '[10-11]', '[11-12]', '[12-13]', '[13-14]', '[14-15]', '[15-20]', '[20-30]', '[30-35]',
                            '[35-40]', '[40-45]', '[45-50]', '50+']
                            )
            df_PFS_sup = df_PFS_sup[['PFS_month', 'source']].value_counts(sort=False, dropna=False).reset_index(name = 'values')
            for i in range(0, len(df_PFS_sup['source'])):
                df_PFS_sup['source'][i] = json.loads(df_PFS_sup['source'][i])['author']
            bar_PFS_sup = px.bar(df_PFS_sup,
                            x = 'PFS_month',
                            y = 'values',
                            color = 'source',
                            color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(bar_PFS_sup, use_container_width=True)

    
    sunburst_ids = go.Figure(go.Sunburst(
    labels=["III", "IV", "Unknown", "IIIC","US IIIC","NAN","M1A", "M1B", "M1C","NaN"],
    parents=["", "", "", "III", "III", "III", "IV", "IV", "IV", "IV"],
    values=[19,230,45,7,4,8,31,25,127,47],
    ))
    #sunburst_ids.update_traces(hoverinfo='value', textinfo='value+labels')
    sunburst_ids.update_layout(font=dict(size = 15), margin = dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(sunburst_ids, use_container_width=True)

