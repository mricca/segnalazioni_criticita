# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models as gismodels
from django.db import models
from django import forms
from django.utils import timezone
from time import strftime
from django.utils.encoding import smart_str
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.forms.widgets import NullBooleanSelect
from django.utils.translation import ugettext_lazy
from smart_selects.db_fields import ChainedForeignKey 
from smart_selects.db_fields import GroupedForeignKey
from django.contrib.auth.models import User
# Create your models here.

class OggettoSegnalazione(models.Model):
    id = models.CharField(max_length=2, unique=True, blank=False, primary_key=True, editable=False)
    text = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'oggetto_segnalazione'
 
    def __unicode__(self):
        return self.text 

class MotivoSegnalazione(models.Model):
    id = models.CharField(max_length=2, unique=True, blank=False, primary_key=True, editable=False)
    text = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'motivo_segnalazione'
 
    def __unicode__(self):
        return self.text

class InserimentoDODS(models.Model):
    id = models.CharField(max_length=2, unique=True, blank=False, primary_key=True, editable=False)
    text = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'inserimento_dods'
 
    def __unicode__(self):
        return self.text

class SettoreRegComp(models.Model):
    id = models.CharField(max_length=2, unique=True, blank=False, primary_key=True, editable=False)
    text = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'set_reg_comp'
 
    def __unicode__(self):
        return self.text

class Bacini(models.Model):
    id = models.CharField(max_length=2, unique=True, blank=False, primary_key=True, editable=False)
    text = models.CharField(max_length=30)
    email = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'bacini'
 
    def __unicode__(self):
        return self.text

class Province(models.Model):
    cod_prov =  models.CharField(max_length=3, unique=True, blank=False, primary_key=True, editable=False)
    nome_prov = models.CharField(max_length=40)
    sigla_prov = models.CharField(max_length=2)
    
    class Meta:
        db_table = 'province'   
 
    def __unicode__(self):
        return self.sigla_prov

class Comuni(models.Model):
    nom_com = models.CharField(max_length=40)
    cod_com =  models.CharField(max_length=6, unique=True, blank=False, primary_key=True, editable=False)
    nome_prov = models.CharField(max_length=40)
    cod_prov = models.ForeignKey(Province)
    sigla_prov = models.CharField(max_length=2)
    
    class Meta:
        db_table = 'comuni'
        ordering = ['nom_com']
 
    def __unicode__(self):
        return self.nom_com

def nota_segnalazione_user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'documents/utente_{user}/note_segnalazione/{Y}/{m}/{d}/{uploadFile}'.format(Y=strftime('%Y'),m=strftime('%m'),d=strftime('%d'),user=instance.utente, uploadFile=filename)

def relazione_sopralluogo_user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'documents/utente_{user}/relazione_sopralluogo/{Y}/{m}/{d}/{uploadFile}'.format(Y=strftime('%Y'),m=strftime('%m'),d=strftime('%d'),user=instance.utente, uploadFile=filename)

def nota_risposta_user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'documents/utente_{user}/nota_risposta/{Y}/{m}/{d}/{uploadFile}'.format(Y=strftime('%Y'),m=strftime('%m'),d=strftime('%d'),user=instance.utente, uploadFile=filename)

def documento_collegato_user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'documents/utente_{user}/documento_collegato/{Y}/{m}/{d}/{uploadFile}'.format(Y=strftime('%Y'),m=strftime('%m'),d=strftime('%d'),user=User.objects.filter(utente_ds=instance.relate)[0], uploadFile=filename)

class Segnalazione(gismodels.Model):
    
    # OBBLIGATORIO DI DEFAULT
    codice_segnalazione = gismodels.CharField(max_length=20, unique=True, blank=False, null=False, editable=False, db_column='codsegn')
    
    # OBBLIGATORIO DI DEFAULT
    data_prot_arrivo = gismodels.DateField(blank=True, null=True, db_column='data_prot_arr',db_index=True, verbose_name="Data protocollo di arrivo")
    
    # OBBLIGATORIO DI DEFAULT
    prot_arrivo = gismodels.CharField(blank=True, null=True, verbose_name="Protocollo di arrivo", max_length=100,db_column='prot_arrivo',db_index=True, help_text='Max 100 caratteri')
    
    # GEOMETRIA PUNTUALE
    segnalazione_aggiunta = gismodels.PointField(srid=3003,db_index=True,db_column='geom',blank=True, null=True)
    objects = gismodels.GeoManager()
    
    # OBBLIGATORIO DI DEFAULT
    oggetto_segnalazione = gismodels.ForeignKey(OggettoSegnalazione, blank=False, null=True, related_name='oggetto_segnalazione_ds',db_index=True, db_column='ogg_segn')
    
    # OBBLIGATORIO DI DEFAULT
    nota_segnalazione = gismodels.FileField(upload_to=nota_segnalazione_user_directory_path,blank=False, null=True, db_column='nota_segn')
    
    # OBBLIGATORIO DI DEFAULT
    nominativo_segnalazione = gismodels.CharField(blank=False, null=True, verbose_name="Nominativo Segnalazione",db_index=True, max_length=100,db_column='nominativo_s', help_text='Max 100 caratteri')
    
    # OBBLIGATORIO DI DEFAULT
    corso_viabilita = gismodels.CharField(blank=True, null=True, verbose_name="Corso d'acqua / Viabilità / Versante",db_index=True, max_length=100,db_column='corso_via', help_text='Max 100 caratteri')
    
    # OBBLIGATORIO DI DEFAULT
    bacino_idrografico = gismodels.ForeignKey(Bacini, blank=True, null=True, related_name='bacini_ds', db_column='bacidro',db_index=True, help_text='Bacino idrografico L 183/1989')
    
    # OBBLIGATORIO DI DEFAULT
    provincia = gismodels.ForeignKey(Province, blank=True, null=True,db_index=True, related_name='provincia_ds')
    
    # OBBLIGATORIO DI DEFAULT
    #comune = gismodels.ForeignKey(Comuni, blank=False, null=True, related_name='comune_ds')
    comune = ChainedForeignKey(Comuni, chained_field="provincia", chained_model_field="cod_prov",show_all=False, auto_choose=True, blank=True, null=True,db_index=True, related_name='comune_ds')
    
    # OBBLIGATORIO DI DEFAULT
    localita = gismodels.CharField(blank=True, null=True, verbose_name="Località", max_length=100,db_column='localita',db_index=True, help_text='Max 100 caratteri')
    
    # OBBLIGATORIO DI DEFAULT
    motivo_segnalazione = gismodels.ForeignKey(MotivoSegnalazione, blank=False, null=True, related_name='motivo_segnalazione_ds', db_column='mot_segn')
    
    # OBBLIGATORIO DI DEFAULT
    inserimento_dods = gismodels.ForeignKey(InserimentoDODS, blank=True, null=True, related_name='inserimento_dods_ds', db_column='ins_dods', verbose_name="Inserimento nel Documento Operativo")
    
    # OBBLIGATORIO IN CHIUSURA
    relazione_sopralluogo = gismodels.FileField(upload_to=relazione_sopralluogo_user_directory_path,blank=True, null=True, db_column='rel_sopr')
    
    # OBBLIGATORIO IN CHIUSURA
    nota_risposta = gismodels.FileField(upload_to=nota_risposta_user_directory_path,blank=True, null=True, db_column='nota_risp')
    
    # OBBLIGATORIO DI DEFAULT
    desc_sint_crit = gismodels.TextField(blank=False, null=True, db_column='desc_sint_crit', verbose_name='Descrizione sintetica della criticità')
    
    # OPZIONALE DI DEFAULT
    liv_prog_lav = gismodels.TextField(blank=True, null=True, db_column='liv_prog_lav', verbose_name='Livello Progettazione o Lavori realizzati')
    
    # OPZIONALE DI DEFAULT
    desc_sint_int = gismodels.TextField(blank=True, null=True, db_column='desc_sint_int', verbose_name='Descrizione sintetica dell\'intervento necessario')
    
    # OPZIONALE DI DEFAULT
    importo_globale = gismodels.DecimalField(blank=True, null=True, verbose_name="Importo globale stimato dell'intervento (EURO)", max_digits=11, decimal_places=2, db_column='imp_glob')
    
    # OPZIONALE DI DEFAULT
    importo_richiesto = gismodels.DecimalField(blank=True, null=True, verbose_name="Importo richiesto (EURO)", max_digits=11, decimal_places=2, db_column='imp_ric')
    
    # OBBLIGATORIO DI DEFAULT
    set_reg_comp = gismodels.ForeignKey(SettoreRegComp, blank=False, null=True, related_name='set_reg_comp_ds', db_column='set_reg_comp', verbose_name="Settore regionale competente")
    
    # OBBLIGATORIO DI DEFAULT
    referente_documentazione = gismodels.CharField(blank=False, null=True, verbose_name="referente che detiene la documentazione", max_length=100,db_column='ref_doc', help_text='Max 100 caratteri')
    
    # OPZIONALE DI DEFAULT
    note = gismodels.TextField(blank=True, null=True)
    
    stato_istruttoria = gismodels.NullBooleanField(blank=True, db_column='istruttoria')
    
    data_inizio_istruttoria = gismodels.DateTimeField(null=True, blank=True, db_column='data_inizio_istr', verbose_name="Data inserimento segnalazione")
    
    data_fine_istruttoria = gismodels.DateTimeField(null=True, blank=True, db_column='data_fine_istr', verbose_name="Data chiusura istruttoria")

    # OBBLIGATORIO DI DEFAULT
    email_task_id = gismodels.CharField(blank=False, null=True,max_length=40,db_column='email_task_id')
    
    email_sent = gismodels.BooleanField(default=False, db_column='email_sent', verbose_name="Sollecito inviato")
    
    utente = models.ForeignKey(User,null=True, blank=True, related_name='utente_ds')
    
    class Meta:
        verbose_name_plural = "Segnalazioni Criticità"
        
    def __unicode__(self):
        return u"%s" % (self.codice_segnalazione)

class DocumentazioneCollegata(models.Model):
    tipo_doc = gismodels.CharField(blank=True, null=True, verbose_name="Tipologia Documento", max_length=100,db_column='tipo_doc', help_text='Max 100 caratteri')
    documento_collegato = gismodels.FileField(upload_to=documento_collegato_user_directory_path,blank=True, null=True, db_column='doc_coll')
    relate = gismodels.ForeignKey(Segnalazione, db_column='segn_fk', blank=False, null=True, to_field='codice_segnalazione')
    
    class Meta:
        db_table = 'documentazione'   
        verbose_name_plural = "Documentazione Collegata"
 
    def __unicode__(self):
        return self.tipo_doc