import sys
import re
import os
import pathlib
import pandas as pd
import numpy as np
import json


############################################################################################
#
#                                        Yan class
#                                         
############################################################################################

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.nan):
            return None
        else:
            return super(NpEncoder, self).default(obj)

class Yan():
    """
    This module allows to get list of dictionnaries where terms represents patients
    """

    def parse_xlsx_from_file(self, file_path):
        """
        Read the csv file extract from the clinical study (Fichier_melanome_RL.xlsx) and returns a list of dictionnaries
        where terms represent proteins filled with their informations (age, sex, stage, etc...). 

        :returns: list of all patients in the study
        :rtype: list
        """
        list_patients = []

        # import table
        table = pd.read_csv(file_path, header=0)
        
        # change values of some table columns 
        table_sex = table['Sex']
        table_sex = table_sex.replace(['Male','Female'],['male', 'female'])

        table_OS = table['OS Censor']
        table_OS = table_OS.replace([0,1], ['alive', 'dead'])

        table_LDH = table['LDH'].replace(['Normal','Elevated'], ['normal', 'elevated'])


        # create dictionnaries
        for ind in table.index:
            patient_dict=dict(
                patient_ID = table['Patient ID'][ind],
                sex = table_sex[ind],
                age = table['Age'][ind],
                stage = np.NaN,
                M_stage = table['Stage'][ind],
                LDH = table_LDH[ind],
                os_statut = table_OS[ind],
                os_months = table['OS (Months)'][ind],
                pfs = table['PFS (Months)'][ind],
                braf_mut = table['BRAF V600 Mut'][ind],
                disease_control_rate = table['BORR'][ind],
                #prelevement_temporality = table['timing'][ind],
                drug = table['Rx'][ind],
                brain_metastasis = np.NaN,
                immunotherapy_treatment = np.NaN,
                #immunotherapy_mol = table['Immunotherapy'][ind]
                source = dict(
                    title = 'Genomic Features of Exceptional Response in Vemurafenib + Cobimetinib–treated Patients with BRAFV600-mutated Metastatic Melanoma',
                    author =  'Yibing Yan, Antoni Ribas',
                    journal =  'Clinical Cancer Research',
                    location = 'San Francisco, California (United States)',
                    date = 2019)  
            )
            for (key, value) in patient_dict.items():
                if (pd.isna(value)):
                    patient_dict[key]=None
            
            convert_dict = json.dumps(patient_dict, cls=NpEncoder)

            list_patients.append(json.loads(convert_dict))

        print('the list of "Yan" patients has been created')
        return(list_patients)