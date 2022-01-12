import sys
import re
import os
import pathlib
import pandas as pd
import numpy as np
import json


############################################################################################
#
#                                        Catalanotti class
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


class Catalanotti():
    """
    This module allows to get list of dictionnaries where terms represents patients
    """

    def parse_xlsx_from_file(self, file_path): #file_path2
        """
        Read the csv file extract from the clinical study (Fichier_melanome_RL.xlsx) and returns a list of dictionnaries
        where terms represent proteins filled with their informations (age, sex, stage, etc...). 

        :returns: list of all patients in the study
        :rtype: list
        """
        list_patients = []

        # import table
        table = pd.read_excel(file_path, header=1)
        idx = table[table.isnull().all(1)].index.tolist()
        table = table.drop(idx)
        table=table.reset_index(drop=True)
        #sup_table = pd.read_excel(file_path2, header=1)
        #table = table.drop(table.index[53:89],0, inplace=False)
        
        # change values of some table columns 
        table_sex = table['Sex']
        table_sex = table_sex.replace(['M','F'],['male', 'female'])

        clark_level_dict = {'II': 0, 'III': 1, 'IV': 2, 'V': 3}
        table_stage = table['Stage'].tolist()
        table_stage = [elem[0:3] for elem in table_stage]
        table_stage = [clark_level_dict[elem] for elem in table_stage]


        table_immuno_bool = table['Immunotherapy'].tolist()
        for i in range(len(table_immuno_bool)):
            if(table_immuno_bool[i]=='no'):
                table_immuno_bool[i] = 0
            else:
                table_immuno_bool[i] = 1

        # create dictionnaries
        for ind in table.index:
            patient_dict=dict(
                sex = table_sex[ind],
                age = table['Age'][ind],
                stage = table_stage[ind],
                LDH = table['LDH (1=high, 0=WNL)'][ind],
                os_statut = table['OS NEW Alive (0) Dead (1)'][ind],
                os_months = table['OS (Months)'][ind],
                pfs = table['PFS (months)'][ind],
                braf_mut = table['BRAF Mutation'][ind],
                disease_control_rate = table['Response'][ind],
                prelevement_temporality = table['timing'][ind],
                drug = table['Drug'][ind],
                brain_metastasis = table['Brain mets (Yes=1; no=0)'][ind],
                immunotherapy_treatment = table_immuno_bool[ind],
                immunotherapy_mol = table['Immunotherapy'][ind],
                source = dict(
                    title = 'PTEN Loss-of-Function Alterations Are Associated With Intrinsic Resistance to BRAF Inhibitors in Metastatic Melanoma',
                    author =  'Federica Catalanotti, David B. Solit',
                    journal =  'JCO Precision Oncology',
                    location = 'New York (United States)',
                    date = 2017) 
            )
            for (key, value) in patient_dict.items():
                if (pd.isna(value)):
                    patient_dict[key]=None

            convert_dict = json.dumps(patient_dict, cls=NpEncoder)

            list_patients.append(json.loads(convert_dict))

        print('the list of "Catalanotti" patients has been created')
        return(list_patients)