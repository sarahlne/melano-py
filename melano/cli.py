import sys
import re
import os
import pathlib
import pandas as pd

from datetime import datetime
from peewee import Field, IntegerField, DateField, DateTimeField, CharField, ForeignKeyField, Model as PWModel
from peewee import SqliteDatabase

from db.patients import Patients
from db.patients import db

db.connect()
db.drop_tables([Patients])
db.create_tables([Patients])

p1 = Patients()

data_dir = '../clinical-studies'
files = dict(
    blateau_file= '/blateau&solassol_Cancers-2020/blateau&solassol_Cancers-2020/Fichier_melanome_RL.xlsx',
    catalanotti_file= '/catalanotti&solit_jcopo_2017/ds_16.00054-3.xlsx',
    catalanotti_sup_file = '/catalanotti&solit_jcopo_2017/catalanotti&solit_jcopo_2017/skcm_vanderbilt_mskcc_2015/data_clinical_patient.txt', 
    van_allen_file= '/van-allen&schadendorf_cancer-discovery_2014/van-allen&schadendorf_cancer-discovery_2014/skcm_broad_brafresist_2012/data_clinical_patient.txt',
    yan_ribas_file= '/yan&ribas_Clin-Can-Res_2019/yan&ribas_Clin-Can-Res_2019/198021_2_supp_5455023_ppszzf.csv'
)
p1.fetch_patients_and_create(data_dir, files)


# #Create database
# db = SqliteDatabase('test_db.db')

# # Connect to our database.
# db.connect()

# # Create the tables.
# db.create_tables([User, Tweet])
