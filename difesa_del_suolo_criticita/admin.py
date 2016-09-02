# -*- coding: utf-8 -*-
import sys, traceback
from django.core.mail import EmailMessage
#FOR REPORT PDF OUTPUT
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, BaseDocTemplate
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import styles, colors
from reportlab.pdfgen import canvas

from django.utils.encoding import smart_str

from django.contrib.gis.geos import GEOSGeometry

from django.http import HttpResponse
from django import forms
from datetime import datetime, timedelta
from django.utils import timezone
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.contrib.gis import admin
from olwidget.admin import GeoModelAdmin
#from leaflet.admin import LeafletGeoAdmin
from tabbed_admin import TabbedModelAdmin
from reversion.admin import VersionAdmin
from django.contrib.gis.gdal import *
from django.contrib.gis.geos import GEOSGeometry, Point
#from ajax_select import make_ajax_form
#from ajax_select.admin import AjaxSelectAdmin

from models import Segnalazione, DocumentazioneCollegata
#from models import Segnalazione

from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from django import template
from django.contrib import messages
from django.utils.encoding import force_text
register = template.Library()
from django.http import QueryDict

#from prova_lamma.tasks import send_feedback_email_task
from celery import uuid
from celery.task.control import revoke
import uuid as uuidp
from easy_select2 import select2_modelform, apply_select2

# Register your models here.

class DocumentazioneCollegataAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
            self.request = kwargs.pop('request', None)
            super(DocumentazioneCollegataAdminForm, self).__init__(*args, **kwargs)
            
    class Meta:
        model = DocumentazioneCollegata
        fields = '__all__'
        widgets = {
          'relate': apply_select2(forms.Select),
          #'documenti_collegati': apply_select2(forms.SelectMultiple),
          #'documenti_collegati': forms.ClearableFileInput(attrs={'multiple': True}),
        }
            
class CronoprogrammaAdminForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CronoprogrammaAdminForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Segnalazione
        fields = '__all__'
        widgets = {
          'desc_sint_crit': forms.Textarea(attrs={'rows':2, 'cols':80}),
          'liv_prog_lav': forms.Textarea(attrs={'rows':2, 'cols':80}),
          'desc_sint_int': forms.Textarea(attrs={'rows':2, 'cols':80}),
          'note': forms.Textarea(attrs={'rows':2, 'cols':80}),
          'oggetto_segnalazione': apply_select2(forms.Select),
          'bacino_idrografico': apply_select2(forms.Select),
          #'provincia': apply_select2(forms.Select),
          #'comune': apply_select2(forms.Select),
          'motivo_segnalazione': apply_select2(forms.Select),
          'inserimento_dods': apply_select2(forms.Select),
          'set_reg_comp': apply_select2(forms.Select),
          #'documenti_collegati': apply_select2(forms.SelectMultiple),
          #'documenti_collegati': forms.ClearableFileInput(attrs={'multiple': True}),
        }

    def clean_data_prot_arrivo(self):
        data_prot_arrivo = self.cleaned_data['data_prot_arrivo']
        oggetto_segnalazione = self.data.get('oggetto_segnalazione')
        #oggetto_segnalazione = self.cleaned_data['oggetto_segnalazione'].text
        if data_prot_arrivo is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        elif data_prot_arrivo is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_not_completed'):
            raise forms.ValidationError(_('Non puoi aprire l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return data_prot_arrivo
        
    def clean_prot_arrivo(self):
        prot_arrivo = self.cleaned_data['prot_arrivo'].strip()
        oggetto_segnalazione = self.data.get('oggetto_segnalazione')
        #oggetto_segnalazione = self.cleaned_data['oggetto_segnalazione'].text
        if prot_arrivo == '' and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        elif prot_arrivo == '' and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_not_completed'):
            raise forms.ValidationError(_('Non puoi aprire l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return prot_arrivo
        
    def clean_nota_segnalazione(self):
        nota_segnalazione = self.cleaned_data['nota_segnalazione']
        if nota_segnalazione is None and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return nota_segnalazione
        
    def clean_nominativo_segnalazione(self):
        nominativo_segnalazione = self.cleaned_data['nominativo_segnalazione'].strip()
        if nominativo_segnalazione == '' and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return nominativo_segnalazione

    def clean_bacino_idrografico(self):
        bacino_idrografico = self.cleaned_data['bacino_idrografico']
        oggetto_segnalazione = self.data.get('oggetto_segnalazione')
        #oggetto_segnalazione = self.cleaned_data['oggetto_segnalazione'].text
        if bacino_idrografico is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        elif bacino_idrografico is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_not_completed'):
            raise forms.ValidationError(_('Non puoi aprire l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return bacino_idrografico

    def clean_provincia(self):
        provincia = self.cleaned_data['provincia']
        oggetto_segnalazione = self.data.get('oggetto_segnalazione')
        #oggetto_segnalazione = self.cleaned_data['oggetto_segnalazione'].text
        if provincia is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        elif provincia is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_not_completed'):
            raise forms.ValidationError(_('Non puoi aprire l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return provincia

    def clean_comune(self):
        comune = self.cleaned_data['comune']
        oggetto_segnalazione = self.data.get('oggetto_segnalazione')
        #oggetto_segnalazione = self.cleaned_data['oggetto_segnalazione'].text
        if comune is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        elif comune is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_not_completed'):
            raise forms.ValidationError(_('Non puoi aprire l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return comune

    def clean_corso_viabilita(self):
        corso_viabilita = self.cleaned_data['corso_viabilita'].strip()
        oggetto_segnalazione = self.data.get('oggetto_segnalazione')
        #oggetto_segnalazione = self.cleaned_data['oggetto_segnalazione'].text
        if corso_viabilita == '' and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        elif corso_viabilita == '' and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_not_completed'):
            raise forms.ValidationError(_('Non puoi aprire l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return corso_viabilita

    def clean_segnalazione_aggiunta(self):
        segnalazione_aggiunta = self.cleaned_data['segnalazione_aggiunta']
        oggetto_segnalazione = self.data.get('oggetto_segnalazione')
        #oggetto_segnalazione = self.cleaned_data['oggetto_segnalazione'].text
        if segnalazione_aggiunta[0] is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        elif segnalazione_aggiunta[0] is None and oggetto_segnalazione != "04" and self.request.POST.__contains__(u'_save_and_investigation_not_completed'):
            raise forms.ValidationError(_('Non puoi aprire l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return segnalazione_aggiunta

    #def clean_localita(self):
    #    localita = self.cleaned_data['localita'].strip()
    #    if localita == '' and self.request.POST.__contains__(u'_save_and_investigation_completed'):
    #        raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
    #    return localita
        
    #def clean_inserimento_dods(self):
    #    inserimento_dods = self.cleaned_data['inserimento_dods']
    #    if inserimento_dods is None and self.request.POST.__contains__(u'_save_and_investigation_completed'):
    #        raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
    #    return inserimento_dods
        
    #def clean_relazione_sopralluogo(self):
    #    relazione_sopralluogo = self.cleaned_data['relazione_sopralluogo']
    #    if relazione_sopralluogo is None and self.request.POST.__contains__(u'_save_and_investigation_completed'):
    #        raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
    #    return relazione_sopralluogo
        
    #def clean_nota_risposta(self):
    #    nota_risposta = self.cleaned_data['nota_risposta']
    #    if nota_risposta is None and self.request.POST.__contains__(u'_save_and_investigation_completed'):
    #        raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
    #    return nota_risposta
        
    def clean_desc_sint_crit(self):
        desc_sint_crit = self.cleaned_data['desc_sint_crit'].strip()
        if desc_sint_crit == '' and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return desc_sint_crit
        
    def clean_set_reg_comp(self):
        set_reg_comp = self.cleaned_data['set_reg_comp']
        if set_reg_comp is None and self.request.POST.__contains__(u'_save_and_investigation_completed'):
            raise forms.ValidationError(_('Non puoi chiudere l\'istruttoria se non hai compilato questo campo'), code='invalid')
        return set_reg_comp
    
    def clean(self):
        cleaned_data = super(CronoprogrammaAdminForm, self).clean()
        relazione_sopralluogo = cleaned_data.get("relazione_sopralluogo")
        nota_risposta = cleaned_data.get("nota_risposta")

        if relazione_sopralluogo is None and nota_risposta is None and self.request.POST.__contains__(u'_save_and_investigation_completed'):            
            msg = 'Non puoi chiudere l\'istruttoria se non hai compilato almeno un campo tra Relazione Sopralluogo e Nota Risposta'
            self.add_error('relazione_sopralluogo', msg)
            self.add_error('nota_risposta', msg)

def export_pdf_single(modeladmin, request, queryset, cod = None):
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Segnalazione_criticita_LaMMA.pdf"'

    buffer = BytesIO()
    
    #p = canvas.Canvas(buffer)
    p = SimpleDocTemplate(buffer,pagesize=A4)
    styles = getSampleStyleSheet()
    Catalog = []
    #I = Image('http://172.16.1.141:8081/static/admin/images/logoregione.png')
    I = Image('http://159.213.57.81/static/admin/images/logoregione.png')
    Catalog.append(I)
    style = styles["BodyText"]
    style.alignment = TA_LEFT      

    header = Paragraph('''<para align=center spaceb=3><b><font color=red >Segnalazione Criticità LaMMA</font></b></para>''', style)
    Catalog.append(header)
    
    headings = ('Attributo', 'Valore')
    allproducts = []

    for obj in queryset:
        if obj.codice_segnalazione == cod:
            allproducts.append([smart_str(u"codice_segnalazione"),Paragraph(smart_str(obj.codice_segnalazione),style)])
            allproducts.append([smart_str(u"data_prot_arrivo"),Paragraph(smart_str(obj.data_prot_arrivo),style)])
            allproducts.append([smart_str(u"prot_arrivo"),Paragraph(smart_str(obj.prot_arrivo),style)])
            allproducts.append([smart_str(u"bacino_idrografico"),Paragraph(smart_str(obj.bacino_idrografico),style)])
            allproducts.append([smart_str(u"provincia"),Paragraph(smart_str(obj.provincia),style)])
            allproducts.append([smart_str(u"comune"),Paragraph(smart_str(obj.comune),style)])
            allproducts.append([smart_str(u"localita"),Paragraph(smart_str(obj.localita),style)])
            allproducts.append([smart_str(u"corso_viabilita"),Paragraph(smart_str(obj.corso_viabilita),style)])
            allproducts.append([smart_str(u"segnalazione_aggiunta"),Paragraph(smart_str(obj.segnalazione_aggiunta),style)])
            allproducts.append([smart_str(u"oggetto_segnalazione"),Paragraph(smart_str(obj.oggetto_segnalazione),style)])
            allproducts.append([smart_str(u"nota_segnalazione"),Paragraph(smart_str(obj.nota_segnalazione),style)])
            allproducts.append([smart_str(u"nominativo_segnalazione"),Paragraph(smart_str(obj.nominativo_segnalazione),style)])
            allproducts.append([smart_str(u"motivo_segnalazione"),Paragraph(smart_str(obj.motivo_segnalazione),style)])
            allproducts.append([smart_str(u"inserimento_dods"),Paragraph(smart_str(obj.inserimento_dods),style)])
            allproducts.append([smart_str(u"desc_sint_crit"),Paragraph(smart_str(obj.desc_sint_crit),style)])
            allproducts.append([smart_str(u"referente_documentazione"),Paragraph(smart_str(obj.referente_documentazione),style)])
            allproducts.append([smart_str(u"set_reg_comp"),Paragraph(smart_str(obj.set_reg_comp),style)])
            allproducts.append([smart_str(u"liv_prog_lav"),Paragraph(smart_str(obj.liv_prog_lav),style)])
            allproducts.append([smart_str(u"desc_sint_int"),Paragraph(smart_str(obj.desc_sint_int),style)])
            allproducts.append([smart_str(u"importo_globale"),Paragraph(smart_str(obj.importo_globale),style)])
            allproducts.append([smart_str(u"importo_richiesto"),Paragraph(smart_str(obj.importo_richiesto),style)])
            allproducts.append([smart_str(u"note"),Paragraph(smart_str(obj.note),style)])
            allproducts.append([smart_str(u"relazione_sopralluogo"),Paragraph(smart_str(obj.relazione_sopralluogo),style)])
            allproducts.append([smart_str(u"nota_risposta"),Paragraph(smart_str(obj.nota_risposta),style)])
            #allproducts.append([smart_str(u"documenti_collegati"),Paragraph(smart_str(obj.documenti_collegati),style)])
            allproducts.append([smart_str(u"stato_istruttoria"),Paragraph(smart_str(obj.stato_istruttoria),style)])
            allproducts.append([smart_str(u"data_inizio_istruttoria"),Paragraph(smart_str(obj.data_inizio_istruttoria),style)])
            allproducts.append([smart_str(u"data_fine_istruttoria"),Paragraph(smart_str(obj.data_fine_istruttoria),style)])

    t = Table([headings] + allproducts,[230,250])
    t.setStyle(TableStyle([('GRID', (0,0), (1,-1), 2, colors.black),('LINEBELOW', (0,0), (-1,0), 2, colors.red),('BACKGROUND', (0, 0), (-1, 0), colors.pink)]))
    Catalog.append(t)
    p.build(Catalog)

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return pdf
    
def export_pdf(modeladmin, request, queryset):
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Segnalazione_criticita_LaMMA.pdf"'

    buffer = BytesIO()
    
    #p = canvas.Canvas(buffer)
    p = SimpleDocTemplate(buffer,pagesize=A4)
    styles = getSampleStyleSheet()

    Catalog = []
    #I = Image('http://172.16.1.141:8081/static/admin/images/logoregione.png')
    I = Image('http://159.213.57.81/static/admin/images/logoregione.png')

    Catalog.append(I)
    style = styles["BodyText"]
    style.alignment = TA_LEFT   

    header = Paragraph('''<para align=center spaceb=3><b><font color=red >Segnalazione Criticità LaMMA</font></b></para>''', style)
    Catalog.append(header)
    
    headings = ('Attributo', 'Valore')
    allproducts = []

    for obj in queryset:
        allproducts.append([smart_str(u"codice_segnalazione"),Paragraph(smart_str(obj.codice_segnalazione),style)])
        allproducts.append([smart_str(u"data_prot_arrivo"),Paragraph(smart_str(obj.data_prot_arrivo),style)])
        allproducts.append([smart_str(u"prot_arrivo"),Paragraph(smart_str(obj.prot_arrivo),style)])
        allproducts.append([smart_str(u"bacino_idrografico"),Paragraph(smart_str(obj.bacino_idrografico),style)])
        allproducts.append([smart_str(u"provincia"),Paragraph(smart_str(obj.provincia),style)])
        allproducts.append([smart_str(u"comune"),Paragraph(smart_str(obj.comune),style)])
        allproducts.append([smart_str(u"localita"),Paragraph(smart_str(obj.localita),style)])
        allproducts.append([smart_str(u"corso_viabilita"),Paragraph(smart_str(obj.corso_viabilita),style)])
        allproducts.append([smart_str(u"segnalazione_aggiunta"),Paragraph(smart_str(obj.segnalazione_aggiunta),style)])
        allproducts.append([smart_str(u"oggetto_segnalazione"),Paragraph(smart_str(obj.oggetto_segnalazione),style)])
        allproducts.append([smart_str(u"nota_segnalazione"),Paragraph(smart_str(obj.nota_segnalazione),style)])
        allproducts.append([smart_str(u"nominativo_segnalazione"),Paragraph(smart_str(obj.nominativo_segnalazione),style)])
        allproducts.append([smart_str(u"motivo_segnalazione"),Paragraph(smart_str(obj.motivo_segnalazione),style)])
        allproducts.append([smart_str(u"inserimento_dods"),Paragraph(smart_str(obj.inserimento_dods),style)])
        allproducts.append([smart_str(u"desc_sint_crit"),Paragraph(smart_str(obj.desc_sint_crit),style)])
        allproducts.append([smart_str(u"referente_documentazione"),Paragraph(smart_str(obj.referente_documentazione),style)])
        allproducts.append([smart_str(u"set_reg_comp"),Paragraph(smart_str(obj.set_reg_comp),style)])
        allproducts.append([smart_str(u"liv_prog_lav"),Paragraph(smart_str(obj.liv_prog_lav),style)])
        allproducts.append([smart_str(u"desc_sint_int"),Paragraph(smart_str(obj.desc_sint_int),style)])
        allproducts.append([smart_str(u"importo_globale"),Paragraph(smart_str(obj.importo_globale),style)])
        allproducts.append([smart_str(u"importo_richiesto"),Paragraph(smart_str(obj.importo_richiesto),style)])
        allproducts.append([smart_str(u"note"),Paragraph(smart_str(obj.note),style)])
        allproducts.append([smart_str(u"relazione_sopralluogo"),Paragraph(smart_str(obj.relazione_sopralluogo),style)])
        allproducts.append([smart_str(u"nota_risposta"),Paragraph(smart_str(obj.nota_risposta),style)])
        #allproducts.append([smart_str(u"documenti_collegati"),Paragraph(smart_str(obj.documenti_collegati),style)])
        allproducts.append([smart_str(u"stato_istruttoria"),Paragraph(smart_str(obj.stato_istruttoria),style)])
        allproducts.append([smart_str(u"data_inizio_istruttoria"),Paragraph(smart_str(obj.data_inizio_istruttoria),style)])
        allproducts.append([smart_str(u"data_fine_istruttoria"),Paragraph(smart_str(obj.data_fine_istruttoria),style)])
        
        t = Table([headings] + allproducts,[230,250])
        
        t.setStyle(TableStyle([
            (
                'GRID',
                (0,0),
                (1,-1),
                2,
                colors.black
            ),
            (
                'LINEBELOW',
                (0,0),
                (-1,0),
                2,
                colors.red
            ),
            (
                'BACKGROUND',
                (0, 0),
                (-1, 0),
                colors.pink
            )
        ]))
            
        Catalog.append(t)
        
        Catalog.append(PageBreak())     

        allproducts = []
        
    p.build(Catalog)

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
export_pdf.short_description = u"Esporta nel formato PDF"

def export_csv(modeladmin, request, queryset):
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=segnalazione_criticita_lamma.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"codice_segnalazione"),
        smart_str(u"data_prot_arrivo"),
        smart_str(u"prot_arrivo"),
        smart_str(u"bacino_idrografico"),
        smart_str(u"provincia"),
        smart_str(u"comune"),
        smart_str(u"localita"),
        smart_str(u"corso_viabilita"),
        smart_str(u"segnalazione_aggiunta"),
        smart_str(u"oggetto_segnalazione"),
        smart_str(u"nota_segnalazione"),
        smart_str(u"nominativo_segnalazione"),
        smart_str(u"motivo_segnalazione"),
        smart_str(u"inserimento_dods"),
        smart_str(u"desc_sint_crit"),
        smart_str(u"referente_documentazione"),
        smart_str(u"set_reg_comp"),
        smart_str(u"liv_prog_lav"),
        smart_str(u"desc_sint_int"),
        smart_str(u"importo_globale"),
        smart_str(u"importo_richiesto"),
        smart_str(u"note"),
        smart_str(u"relazione_sopralluogo"),
        smart_str(u"nota_risposta"),
        #smart_str(u"documenti_collegati"),
        smart_str(u"stato_istruttoria"),
        smart_str(u"data_inizio_istruttoria"),
        smart_str(u"data_fine_istruttoria"),
    ])
    
    #if request.user.is_superuser:
    #    writer.writerow([
    #        smart_str(u"a_finanziamento"),
    #    ])
        
    for obj in queryset:
       
        writer.writerow([
            smart_str(obj.codice_segnalazione),
            smart_str(obj.data_prot_arrivo),
            smart_str(obj.prot_arrivo),
            smart_str(obj.bacino_idrografico),
            smart_str(obj.provincia),
            smart_str(obj.comune),
            smart_str(obj.localita),
            smart_str(obj.corso_viabilita),
            smart_str(obj.segnalazione_aggiunta),
            smart_str(obj.oggetto_segnalazione),
            smart_str(obj.nota_segnalazione),
            smart_str(obj.nominativo_segnalazione),
            smart_str(obj.motivo_segnalazione),
            smart_str(obj.inserimento_dods),
            smart_str(obj.desc_sint_crit),
            smart_str(obj.referente_documentazione),
            smart_str(obj.set_reg_comp),
            smart_str(obj.liv_prog_lav),
            smart_str(obj.desc_sint_int),
            smart_str(obj.importo_globale),
            smart_str(obj.importo_richiesto),
            smart_str(obj.note),
            smart_str(obj.relazione_sopralluogo),
            smart_str(obj.nota_risposta),
            #smart_str(obj.documenti_collegati),
            smart_str(obj.stato_istruttoria),
            smart_str(obj.data_inizio_istruttoria),
            smart_str(obj.data_fine_istruttoria),
        ])
        
        #if request.user.is_superuser:
        #    writer.writerow([
        #        smart_str(obj.a_finanziamento),
        #    ])        
            
    return response
export_csv.short_description = u"Esporta nel formato CSV"

def export_xls(modeladmin, request, queryset):
    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=segnalazione_criticita_lamma.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Segnalazione criticita LaMMA")
    
    row_num = 0
    
    columns = [
        (u"codice_segnalazione", 8000),
        (u"data_prot_arrivo", 8000),
        (u"prot_arrivo", 8000),
        (u"bacino_idrografico", 8000),
        (u"provincia", 8000),
        (u"comune", 8000),
        (u"localita", 8000),
        (u"corso_viabilita", 8000),
        (u"segnalazione_aggiunta", 8000),
        (u"oggetto_segnalazione", 8000),
        (u"nota_segnalazione", 8000),
        (u"nominativo_segnalazione", 8000),
        (u"motivo_segnalazione", 8000),
        (u"inserimento_dods", 8000),
        (u"desc_sint_crit", 8000),
        (u"referente_documentazione", 8000),
        (u"set_reg_comp", 8000),
        (u"liv_prog_lav", 8000),
        (u"desc_sint_int", 8000),
        (u"importo_globale", 8000),
        (u"importo_richiesto", 8000),
        (u"note", 8000),
        (u"relazione_sopralluogo", 8000),
        (u"nota_risposta", 8000),
        #(u"documenti_collegati", 8000),
        (u"stato_istruttoria", 8000),
        (u"data_inizio_istruttoria", 8000),
        (u"data_fine_istruttoria", 8000),
    ]
        
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1
    
    for obj in queryset:
        
        row_num += 1
        row = [
            smart_str(obj.codice_segnalazione),
            smart_str(obj.data_prot_arrivo),
            smart_str(obj.prot_arrivo),
            smart_str(obj.bacino_idrografico),
            smart_str(obj.provincia),
            smart_str(obj.comune),
            smart_str(obj.localita),
            smart_str(obj.corso_viabilita),
            smart_str(obj.segnalazione_aggiunta),
            smart_str(obj.oggetto_segnalazione),
            smart_str(obj.nota_segnalazione),
            smart_str(obj.nominativo_segnalazione),
            smart_str(obj.motivo_segnalazione),
            smart_str(obj.inserimento_dods),
            smart_str(obj.desc_sint_crit),
            smart_str(obj.referente_documentazione),
            smart_str(obj.set_reg_comp),
            smart_str(obj.liv_prog_lav),
            smart_str(obj.desc_sint_int),
            float(smart_str(obj.importo_globale)) if obj.importo_globale else 0,
            float(smart_str(obj.importo_richiesto)) if obj.importo_richiesto else 0,
            smart_str(obj.note),
            smart_str(obj.relazione_sopralluogo),
            smart_str(obj.nota_risposta),
            #smart_str(obj.documenti_collegati),
            smart_str(obj.stato_istruttoria),
            smart_str(obj.data_inizio_istruttoria),
            smart_str(obj.data_fine_istruttoria),
        ]
                
        for col_num in xrange(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
            
    wb.save(response)
    return response
    
export_xls.short_description = u"Esporta nel formato XLS"

class DocumentazioneCollegataAdmin(GeoModelAdmin):
    
    form = DocumentazioneCollegataAdminForm
    
    list_display = (
        'tipo_doc',
        'documento_collegato',
        'relate',
    )

class DocumentazioneCollegataInline(admin.TabularInline):
    model = DocumentazioneCollegata
    classes = ('grp-collapse grp-open',)
    extra = 1

@admin.register(Segnalazione)    
class SegnalazioneAdmin(VersionAdmin, TabbedModelAdmin, GeoModelAdmin):
    
    model = Segnalazione
    
    def response_change(self, request, obj):
        """ custom method that cacthes a new 'save and edit next' action 
            Remember that the type of 'obj' is the current model instance, so we can use it dynamically!
        """
        if "_save_and_investigation_completed" in request.POST:
        
            #updates the date of transmission
            if obj.data_fine_istruttoria is None:
                obj.stato_istruttoria = True
                obj.data_fine_istruttoria = timezone.now()
                
                #revoke(obj.email_task_id, terminate=True)
                
                obj.save()
                
            return self.response_post_save_change(request, obj)
        elif "_save_and_investigation_not_completed" in request.POST:
        
            if obj.data_inizio_istruttoria is None:                
                obj.stato_istruttoria = False
                obj.data_inizio_istruttoria = timezone.now()
                obj.save()
                
            return self.response_post_save_change(request, obj)
        elif "_save" in request.POST:
            return self.response_post_save_change(request, obj)
        else:
            return super(SegnalazioneAdmin, self).response_change(request, obj)
            
    def response_add(self, request, obj):
        """ custom method that cacthes a new 'save and edit next' action 
            Remember that the type of 'obj' is the current model instance, so we can use it dynamically!
        """
        if "_save_and_investigation_completed" in request.POST:
        
            #updates the date of transmission
            if obj.data_fine_istruttoria is None:
                obj.stato_istruttoria = True
                obj.data_fine_istruttoria = timezone.now()
                obj.data_inizio_istruttoria = obj.data_fine_istruttoria
                obj.save()
                
            return self.response_post_save_add(request, obj)
        elif "_save_and_investigation_not_completed" in request.POST:
        
            #dataProtocollo = obj.data_prot_arrivo
            #oggi = datetime.now().date()
            #giorniScadenza = (dataProtocollo - oggi) + timedelta(days=30)
            
            #if (giorniScadenza.total_seconds() < 0.0):
            #    secondiScadenza = 0.0
            #else:
            #    secondiScadenza = giorniScadenza.total_seconds()    
                 
            if obj.data_inizio_istruttoria is None:
                task_id = uuidp.uuid4()
                #send_feedback_email_task.apply_async((obj.set_reg_comp.email, obj.codice_segnalazione,), countdown=secondiScadenza, task_id=task_id)
                #send_feedback_email_task.apply_async(('rmari76@gmail.com', obj.codice_segnalazione,), countdown=10, task_id=task_id)
                obj.stato_istruttoria = False
                obj.data_inizio_istruttoria = timezone.now()
                obj.email_task_id = task_id
                obj.save()
                
            return self.response_post_save_add(request, obj)
        elif "_save" in request.POST:
            return self.response_post_save_change(request, obj)
        else:
            return super(SegnalazioneAdmin, self).response_add(request, obj)

    actions = [export_csv,export_xls,export_pdf]

    def get_actions(self, request):
        actions = super(SegnalazioneAdmin, self).get_actions(request)
        if request.user.is_superuser == False:
            if 'export_csv' in actions:
                del actions['export_csv']
            if 'export_xls' in actions:
                del actions['export_xls']                
        return actions 
        
    form = CronoprogrammaAdminForm
    
    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(SegnalazioneAdmin, self).get_form(request, obj, **kwargs)
        class ModelFormMetaClass(ModelForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return ModelForm(*args, **kwargs)
        return ModelFormMetaClass

    options = {
        'layers': [
            'geoscopio_intorno_toscana',
            'geoscopio_hillshade',
            'geoscopio_batimetriche',
            'geoscopio_idregione',
            'comprensori',
            'geoscopio_ortofoto',
            'geoscopio_ctr10k',
            'reticolo_gestione',
            'province',
            'comuni',
        ],
        'default_lon': 1243401.13894,
        'default_lat': 5387778.59347,
        'defaultZoom': 1,
    }
    
    inlines = [DocumentazioneCollegataInline]
    
    tab_descrizione_istruttoria = [
        (
        'Descrizione istruttoria', 
            {'classes': ('grp-collapse grp-open',),'fields': 
                [
                'codice_segnalazione',
                'oggetto_segnalazione',
                'data_prot_arrivo',
                'prot_arrivo',
                'nota_segnalazione',
                'nominativo_segnalazione',                
                'motivo_segnalazione',
                'desc_sint_crit',
                'referente_documentazione',
                'set_reg_comp',
                ]
            }
        )
    ]
    
    tab_informazioni_geografiche = [
        (
        'Informazioni geografiche', 
            {'classes': ('grp-collapse grp-open',),'fields': 
                [
                'bacino_idrografico',
                'provincia',
                'comune',
                'localita',
                'corso_viabilita',
                'segnalazione_aggiunta',
                ]
            }
        )
    ]
    
    tab_informazioni_aggiuntive = [
        (
        'Informazioni aggiuntive', 
            {'classes': ('grp-collapse grp-open',),'fields': 
                [
                'inserimento_dods',
                'liv_prog_lav',
                'desc_sint_int',
                'importo_globale',
                'importo_richiesto',
                'note',
                ]
            }
        )
    ]
    
    tab_chiusura_istruttoria = [
        (
        'Chiusura istruttoria', 
            {'classes': ('grp-collapse grp-open',),'fields': 
                [
                'relazione_sopralluogo',
                'nota_risposta',
                #'documenti_collegati',
                ]
            }
        ),
        DocumentazioneCollegataInline
    ]
    
    tab_stato_istruttoria = [
        (
        'Stato istruttoria', 
            {'classes': ('grp-collapse grp-open',),'fields': 
                [
                'stato_istruttoria',
                'data_inizio_istruttoria',
                'data_fine_istruttoria',
                'email_sent',
                ]
            }
        )
    ]
    
    tabs = [
        ('DESCRIZIONE ISTRUTTORIA', tab_descrizione_istruttoria),
        ('INFORMAZIONI GEOGRAFICHE', tab_informazioni_geografiche),
        ('INFORMAZIONI AGGIUNTIVE', tab_informazioni_aggiuntive),
        ('CHIUSURA ISTRUTTORIA', tab_chiusura_istruttoria),
        ('STATO ISTRUTTORIA', tab_stato_istruttoria)
    ]
    
    readonly_fields = [
        'codice_segnalazione',
        'stato_istruttoria',
        'data_inizio_istruttoria',
        'data_fine_istruttoria',
        'email_sent',
    ]

    list_display = (
        'codice_segnalazione',
        'data_prot_arrivo',
        'prot_arrivo',
        'oggetto_segnalazione',
        'comune',
        'localita',
        'corso_viabilita',
        'nominativo_segnalazione',
        'stato_istruttoria',
        'data_inizio_istruttoria',
        'data_fine_istruttoria',
        'utente',
    )
    
    #search_fields = ['bacino_idrografico__text', 'prot_arrivo']
    search_fields = ['prot_arrivo','comune__nom_com','nominativo_segnalazione','localita','corso_viabilita',]
    
    list_per_page = 50
    list_max_show_all = 100
    
    list_filter = ['data_prot_arrivo','data_inizio_istruttoria','data_fine_istruttoria','email_sent','oggetto_segnalazione','stato_istruttoria','comune__nom_com','nominativo_segnalazione','localita','corso_viabilita','utente',]
    exclude = ['utente']

    def get_queryset(self, request):
        qs = super(SegnalazioneAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(utente = request.user)
    
    def save_model(self, request, obj, form, change):
        
        def get_user_suffix(x):
            return {
                'valdarno_superiore': 'VS',
                'toscana_nord': 'TN',            
                'valdarno_inferiore': 'VI',
                'toscana_sud': 'TS',
                'valdarno_centrale': 'VC',
                'assetto_idrogeo': 'AI',
                'protezione_civile': 'PC',
                'admin': 'DS',
            }.get(x, 'DS')

        queryset = Segnalazione.objects.all()
        current_year = timezone.now().year
        suffisso = get_user_suffix(request.user.username)

        if not queryset:
            #codice_segnalazione = 'DA' + '2014' + 'DS' + '0001'
            #codice_segnalazione = 'SEGN-' + 'DS' + current_year + '00001'
            codice_segnalazione = 'SEGN-' + suffisso + str(current_year) + '00001'
            obj.codice_segnalazione = codice_segnalazione
            obj.utente = request.user
            obj.save(force_insert=True)
             
        else:
            lista_codice_segnalazione = [self.codice_segnalazione for self in queryset]
            lista_codice_segnalazione_trim = [self.codice_segnalazione[-5:] for self in queryset]
            lista_codice_segnalazione_trim.sort()
            ultimo_codice_segnalazione = lista_codice_segnalazione_trim[-1]
            ultimo_codice_segnalazione_count = ultimo_codice_segnalazione
            ultimo_codice_segnalazione_count_int = int(ultimo_codice_segnalazione_count)
            ultimo = ['{i:0{width}}'.format(i=i, width=5) for i in range(ultimo_codice_segnalazione_count_int+1, ultimo_codice_segnalazione_count_int+2)]

            #codice_segnalazione = 'SEGN-' + 'DS' + current_year + ultimo[0]
            codice_segnalazione = 'SEGN-' + suffisso + str(current_year) + ultimo[0]

            list = []
            for index in range(len(lista_codice_segnalazione)):
                if obj.codice_segnalazione == lista_codice_segnalazione[index]:
                    list.insert(0, obj.codice_segnalazione)
            # NUOVO INTERVENTO
            if not list:
                obj.codice_segnalazione = codice_segnalazione
                obj.utente = request.user
                obj.save(force_insert=True)

            else:
                # AGGIORNAMENTO INTERVENTO 
                obj.codice_segnalazione = obj.codice_segnalazione
                obj.save(force_update=True)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True # So they can see the change list page
        if request.user.is_superuser or obj.utente == request.user:
            return True
        else:
            return False
    
    has_delete_permission = has_change_permission
    
#admin.site.register(Segnalazione, SegnalazioneAdmin)