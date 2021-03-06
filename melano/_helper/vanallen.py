import sys
import re
import os
import pathlib
import pandas as pd
import numpy as np
import json


############################################################################################
#
#                                        Van Allen class
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
        table = table.drop([1])
        table=table.reset_index(drop=True)

        table['MEDICATION']=table['MEDICATION'].replace(np.nan, 'unknow')
        #sup_table = pd.read_excel(file_path2, header=1)
        #table = table.drop(table.index[53:89],0, inplace=False)
        
        # change values of some table columns 
        table_sex = table['SEX']
        table_sex = table_sex.replace(['Male','Female'],['male', 'female'])

        table_pfs_statut = table['EARLY_RESISTANCE'].replace(['No', 'Yes'],['0','1'])

        # create dictionnaries
        for ind in table.index:
            patient_dict=dict(
                patient_ID = table['PATIENT_ID'][ind],
                sex = table_sex[ind],
                age = table['AGE'][ind],
                stage = np.NaN,
                LDH = np.NaN,
                os_statut = np.NaN,
                os_months = np.NaN,
                pfs_statut = str(table_pfs_statut[ind]),
                pfs = (table['DURATION_OF_THERAPY_WEEKS'][ind])/4,
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

    def parse_mutation_from_file(self, file_mutation_path):
        list_van_allen_mutations = []

        table_mutations_extended = pd.read_csv(file_mutation_path, header=0, sep='\t')

        table_IDs = table_mutations_extended[['Tumor_Sample_Barcode']]
        list_patients = []
        list_treatment = []
        for ind in table_IDs.index:
            list_patients.append(re.match('Pat_\d{2}', table_IDs['Tumor_Sample_Barcode'][ind]).group(0))
            if(re.match('Pat_\d{2}_Pre', table_IDs['Tumor_Sample_Barcode'][ind])):
                list_treatment.append('pre treatment')
            elif(re.match('Pat_\d{2}_Post', table_IDs['Tumor_Sample_Barcode'][ind])):
                list_treatment.append('post treatment')


        table_IDs.insert(loc=0, column='Patient_ID', value=list_patients)
        table_IDs.insert(loc=0, column='Treatment', value=list_treatment)

        #create mutations dictionaries
        for ind in table_mutations_extended.index:
            snp_dict = dict(
                sample_ID = table_mutations_extended['Tumor_Sample_Barcode'][ind],
                patient_ID = table_IDs['Patient_ID'][ind],
                HGNC = table_mutations_extended['Hugo_Symbol'][ind],
                Consequence = table_mutations_extended['Consequence'][ind],
                Variant_Classification = table_mutations_extended['Variant_Classification'][ind],
                Chromosome = table_mutations_extended['Chromosome'][ind],
                mutated = 'yes',
                temporality = table_IDs['Treatment'][ind],
                source = dict(
                    title = 'The Genetic Landscape of Clinical Resistance to RAF Inhibition in Metastatic Melanoma',
                    author =  'Eliezer M. Van Allen, Dirk Schadendorf',
                    journal =  'Cancer Discovery',
                    location = 'United States, Germany',
                    date = 2019)
            )

            for (key, value) in snp_dict.items():
                if (pd.isna(value)):
                    snp_dict[key]=None

            convert_dict = json.dumps(snp_dict, cls=NpEncoder)
            list_van_allen_mutations.append(json.loads(convert_dict))

        print('the list of "Van Allen" mutations has been created')
        return(list_van_allen_mutations)