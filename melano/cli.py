#imports
import sys
import re
import os
import pathlib
import pandas as pd
import json
import logging

from datetime import datetime
from peewee import Field, IntegerField, DateField, DateTimeField, CharField, ForeignKeyField, Model as PWModel
from peewee import SqliteDatabase

from db.patients import Patients
from db.mutations import Mutations
from db.snp import SNP
from db.patients import db


#import settings data
with open('settings.json') as setting_file:
    settings_data=json.load(setting_file)

#import Timer
from timeit import default_timer
import time

#log initiation
log_file = settings_data['log_file']
user = "MelanoModeler"
if not os.path.exists(log_file):
    os.mkdir(log_file)

fh = logging.FileHandler(log_file, mode='w')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(" %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info(f"Hello {user}")
logger.info(f"Create tables ...")

#connect db
db.connect()

#drop tables 
db.drop_tables([Patients])
db.drop_tables([SNP])

#create tables
db.create_tables([Patients])
db.create_tables([SNP])

p1 = Patients()
snp1 = SNP()

# ----------------- Create Patients ----------------- #
logger.info("Step 1 | Loading patients ...")
start_time = time.time()
p1.fetch_patients_and_create(settings_data['clinical_studies'])
len_patients = Patients.select().count()
elapsed_time = time.time() - start_time
logger.info("... done in {:10.2f} min for #patients = {}".format(elapsed_time/60, len_patients))

 # ----------------- Create SNPs ----------------- #
logger.info("Step 2 | Loading SNPs ...")
start_time = time.time()
snp1.fetch_snps_and_create(settings_data['clinical_studies'])
len_snps = SNP.select().count()
elapsed_time = time.time() - start_time
logger.info("... done in {:10.2f} min for #snps = {}".format(elapsed_time/60, len_snps))

# ----------------- Create CNAs ----------------- #
