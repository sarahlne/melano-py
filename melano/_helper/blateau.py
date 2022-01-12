import sys
import re
import os
import pathlib
import pandas as pd
import numpy as np
import json


############################################################################################
#
#                                        Blateau class
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


class Blateau():
    from _helper.converter import NpEncoder
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

        print('Parse information from file ', file_path)

        list_patients = []

        # import table
        table = pd.read_excel(file_path, header=0)
        table = table.drop(table.index[53:89],0, inplace=False)
        
        # change values of some table columns
        
        table_sexe = table['sexe']
        table_sexe = table_sexe.replace([0,1], ['male', 'female'])

        table_disease_control_rate = table['Statut (0= stable disease, 1= progression, 2= partial response, 3= complete response)']
        table_disease_control_rate = table_disease_control_rate.replace([0,1,2,3],['SD', 'PD', 'PR', 'CR'])

        table_braf_mut = table['Mut BRAF (0=V600E, 1=V600K)']
        table_braf_mut = table_braf_mut.replace([0,1],['V600E', 'V600K'])

        list_dabrafenib = table.index[table['DABRAFENIB']==True].to_list()
        list_vemurafenib = table.index[table['VEMURAFENIB']==True].to_list()
        list_dabrafenib_trametinib = table.index[table['DABRAFENIB + TRAMETINIB']==True].to_list()
        list_vemurafenib_cobimetinib = table.index[table['VEMURAFENIB + COBIMETINIB']==True].to_list()
        
        table_agent = pd.Series(['nan' for i in range(len(table))])
        table_agent[list_dabrafenib]='dabrafenib'
        table_agent[list_vemurafenib]='vemurafenib'
        table_agent[list_dabrafenib_trametinib]='dabrafenib + trametinib'
        table_agent[list_vemurafenib_cobimetinib] = 'vemurafenib + cobimetinib'
        "Clark level0=II; 1=III; 2=IV; 3=V"


        # create dictionnaries
        for ind in table.index:
            patient_dict=dict(
                sex = table_sexe[ind],
                age = table['age'][ind],
                stage = table['Clark level\n0=II; 1=III; 2=IV; 3=V'][ind],
                LDH = table['LDH (normales = 0, augmentées = 1)'][ind],
                os_statut = table['Statut OS (0 = neg; 1 = death)'][ind],
                os_months = (table['OS'][ind])/12,
                pfs = table['PFS en mois'][ind],
                braf_mut = table_braf_mut[ind],
                disease_control_rate = table_disease_control_rate[ind],
                #prelevement_temporality = 'only before treatment',
                drug = table_agent[ind],
                brain_metastasis = table['Méta cérébrales (0=neg, 1= event)'][ind],
                immunotherapy_treatment = table['Immunothérapie (0=neg, 1=event)'][ind],
                source = dict(
                    title = 'TERT Promoter Mutation as an Independent Prognostic Marker for Poor Prognosis MAPK Inhibitors-Treated Melanoma',
                    author =  'Pauline Blateau, Jerome Solassol',
                    journal =  'Cancers',
                    location = 'Montpellier (France)',
                    date = 2020)
            )
            for (key, value) in patient_dict.items():
                if (pd.isna(value)):
                    patient_dict[key]=None

            convert_dict = json.dumps(patient_dict, cls=NpEncoder)

            list_patients.append(json.loads(convert_dict))

        print('the list of "Blateau" patients has been created')
        return(list_patients)
