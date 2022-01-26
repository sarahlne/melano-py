import json

from datetime import datetime
from peewee import CharField, FloatField, ForeignKeyField
from peewee import Field, IntegerField, DateField, DateTimeField, CharField, ForeignKeyField, Model as PWModel
from peewee import SqliteDatabase
from playhouse.sqlite_ext import JSONField

from db.mutations import Mutations

db = SqliteDatabase('test_melanodb.db')

class SNP(Mutations):
    """
    This class represents SNPs (Single Nucleotide Polymorphism).

    :property patienr_id: id of the patients
    :type pt_id: CharField 
    :property sample_id: id of the biological sample
    """

    id = IntegerField(primary_key=True)
    data = JSONField(null=True)
    creation_datetime = DateTimeField(default=datetime.now)
    #save_datetime = DateTimeField()
    #type = CharField(null=True, index=True)

    patient_id = CharField(null=True, index=True)
    sample_id = CharField(null=True, index=True)
    HGNC = CharField(null=True, index=True)
    mutated = CharField(null=True, index=True)
    consequence = CharField(null=True, index=True)
    variant_classification = CharField(null=True, index=True)
    temporality = CharField(null=True, index=True)
    other_prelevements = CharField(null=True, index=True)
    source = CharField(null=True, index=True)

    def fetch_snps_and_create(cls, settings_data):
        from _helper.blateau import Blateau
        from _helper.catalanotti import Catalanotti
        from _helper.vanallen import VanAllen
        from _helper.yan import Yan

        b = Blateau()
        list_snp_blateau = b.parse_xlsx_from_file(settings_data['blateau_file'], 'mutations')

        c = Catalanotti()
        list_snp_catalanotti = c.parse_mutations_from_file(settings_data['catalanotti_mutations_extended'], settings_data['catalanotti_clinical_sample'])
        
        v = VanAllen()
        list_snp_vanallen = v.parse_mutation_from_file(settings_data['van_allen_mutations_file'])
        

        cls.create_snp_table_from_list(list_snp_blateau)
        cls.create_snp_table_from_list(list_snp_catalanotti)
        cls.create_snp_table_from_list(list_snp_vanallen)

    @classmethod
    def create_snp_table_from_list(cls, list_mut):
        snps = [cls(data = dict_) for dict_ in list_mut]
        for snp in snps:
            snp.set_sample_ID(snp.data["sample_ID"])
            snp.set_patient_ID(snp.data["patient_ID"])
            snp.set_hgnc(snp.data["HGNC"])
            snp.set_mutated(snp.data["mutated"])
            snp.set_temporality(snp.data["temporality"])
            snp.set_source(snp.data["source"])
            if ('Consequence' in snp.data.keys()):
                snp.set_consequence(snp.data['Consequence'])
            if ('Variant_Classification' in snp.data.keys()):
                snp.set_variant_class(snp.data['Variant_Classification'])    
        
        with db.atomic():
            for snp in snps:
                snp.save()
    
    def set_sample_ID(self, sample_ID):
        if(sample_ID):
            self.sample_id = sample_ID
    
    def set_patient_ID(self, patient_ID):
        if(patient_ID):
            self.patient_id = patient_ID
    def set_hgnc(self, hgnc):
        if(hgnc):
            self.HGNC = hgnc
    def set_mutated(self, mutated):
        if(mutated):
            self.mutated = mutated
    def set_consequence(self, consequence):
        if(consequence):
            self.consequence = consequence
    def set_variant_class(self, variant_class):
            self.variant_classification = variant_class
    def set_temporality(self, temporality):
        if(temporality):
            self.temporality = temporality
    def set_other_prelev(self, other_prelev):
        if(other_prelev):
            self.other_prelevements = other_prelev
    def set_source(self, source):
        if(source):
            self.source = source


    class Meta():
        database = db
        table_name = 'snps'