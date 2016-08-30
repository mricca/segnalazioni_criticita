# -*- coding: utf-8 -*-
#!/usr/local/bin/python2.7

import sys
import psycopg2
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser
import logging
import connessione

parametri = connessione.Parametri()

hostname = parametri.hostname
username = parametri.username
password = parametri.password
database = parametri.database

logger = logging.getLogger('settore_assetto_idrogeologico_segnalazione')
hdlr = logging.FileHandler('/var/tmp/settore_assetto_idrogeologico_segnalazione.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def py_mail(SUBJECT, BODY, TO, FROM, BCC):
    """With this function we send out our html email"""
 
    # Create message container - the correct MIME type is multipart/alternative here!
    MESSAGE = MIMEMultipart('alternative')
    MESSAGE['subject'] = SUBJECT
    MESSAGE['To'] = TO
    MESSAGE['From'] = FROM
    MESSAGE.preamble = """
        Your mail reader does not support the report format.
        Please visit us <a href="http://www.mysite.com">online</a>!"""
 
    # Record the MIME type text/html.
    HTML_BODY = MIMEText(BODY, 'plain')
 
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    MESSAGE.attach(HTML_BODY)
 
    # The actual sending of the e-mail
    server = smtplib.SMTP('172.16.1.2:25')
 
    # Print debugging output when testing
    #if __name__ == "__main__":
    #    server.set_debuglevel(1)
 
    # Credentials (if needed) for sending the mail
    password = "mypassword"
 
    server.starttls()
    #server.login(FROM,password)
    server.sendmail(FROM, [TO, BCC], MESSAGE.as_string())
    server.quit()
    
# Simple routine to run a query on a database and print the results:
def doQuery( conn ) :

    TO = 'assettoidrogeologico@regione.toscana.it'
    FROM ='dbsegnalazioni@lamma.rete.toscana.it'
    BCC = 'mari@lamma.rete.toscana.it'
    
    cur = conn.cursor()

    cur.execute( "SELECT ogg_segn, data_prot_arr, prot_arrivo, codsegn, data_inizio_istr, data_fine_istr, email_sent FROM settore_assetto_idrogeologico_segnalazione" )

    for ogg_segn, data_prot_arr, prot_arrivo, codsegn, data_inizio_istr, data_fine_istr, email_sent in cur.fetchall() :
        if ogg_segn != '04' or data_prot_arr is not None: 
            dataProtocollo = data_prot_arr
            #print "Default - " + str(dataProtocollo)
        else:
            dataProtocollo = data_inizio_istr.date()
            #print "Altro - " + str(dataProtocollo)
        oggi = datetime.now().date()
        giorniScadenza = (dataProtocollo - oggi) + timedelta(days=30)

        email_content = "Segnalazione n° "+codsegn+"\r\rIn relazione alla segnalazione in oggetto si comunica che in data odierna è stato oltrepassato il termine dei 30 giorni dall'apertura dell'istruttoria.\rTale istruttoria è stata aperta in data "+str(data_prot_arr)+" con protocollo "+prot_arrivo+".\rSe ne sollecita pertanto il completamento entro la prossima settimana.\r\r------\rCordiali salutiLa Direzione"
        
        #FORSE IL CONSTROLLO PUO' ESSERE FATTO ANCHE UTILIZZANDO IL CAMPO STATO ISTRUTTORIA
        if (giorniScadenza.total_seconds() <= 0.0 and data_fine_istr is None and email_sent == False):
            secondiScadenza = 0.0
            py_mail("Segnalazione n° " + codsegn, email_content, TO, FROM, BCC)
            cur.execute("UPDATE settore_assetto_idrogeologico_segnalazione set email_sent = TRUE where codsegn='"+codsegn+"'");

            conn.commit()
            print 'Email spedita: Numero giorni alla scadenza: ' + str(dataProtocollo) + " -> " + str(giorniScadenza)
            logger.info("- Email spedita al referente della segnalazione n: "+codsegn+". Tale istruttoria è stata aperta in data "+str(data_prot_arr)+" con protocollo "+prot_arrivo+".")
        #else:
        #    secondiScadenza = giorniScadenza.total_seconds()
        #    print 'Numero giorni alla scadenza: ' + str(dataProtocollo) + " -> " + str(giorniScadenza)

try:
    myConnection = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
except:
    print "I am unable to connect to the database"
    logger.error('I am unable to connect to the database: '+database)

doQuery( myConnection )
myConnection.close()