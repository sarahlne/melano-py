import sys
import re
import os
import pathlib
import pandas as pd
import numpy as np


############################################################################################
#
#                                        Van Allen class
#                                         
############################################################################################

class VanAllen():
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
        table = pd.read_csv(file_path, sep = '\t', header=4)
        table = table.drop([2])
        table=table.reset_index(drop=True)

        table['MEDICATION']=table['MEDICATION'].replace(np.nan, 'unknow')
        #sup_table = pd.read_excel(file_path2, header=1)
        #table = table.drop(table.index[53:89],0, inplace=False)
        
        # change values of some table columns 
        table_sex = table['SEX']
        table_sex = table_sex.replace(['Male','Female'],['male', 'female'])

        # create dictionnaries
        for ind in table.index:
            patient_dict=dict(
                sex = table_sex[ind],
                age = table['AGE'][ind],
                stage = np.NaN,
                LDH = np.NaN,
                os_statut = np.NaN,
                os_months = (table['DURATION_OF_THERAPY_WEEKS'][ind])/4,
                pfs = np.NaN,
                braf_mut = np.NaN,
                disease_control_rate = table['TREATMENT_BEST_RESPONSE'][ind],
                prelevement_temporality = np.NaN,
                drug = table['MEDICATION'][ind],
                brain_metastasis = np.NaN,
                immunotherapy_treatment = np.NaN,
                immunotherapy_mol = np.NaN,
                source = dict(
                    title = 'The Genetic Landscape of Clinical Resistance to RAF Inhibition in Metastatic Melanoma',
                    author =  'Eliezer M. Van Allen, Dirk Schadendorf',
                    journal =  'Cancer Discovery',
                    location = 'United States, Germany',
                    date = 2019)  
            )
            for (key, value) in patient_dict.items():
                if (pd.isna(value)):
                    patient_dict[key]=None

            list_patients.append(patient_dict)

        print('the list of "Van Allen" patients has been created')
        return(list_patients)