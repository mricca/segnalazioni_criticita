-- 1 admin
-- 2 consorzio_lamma
-- 3 valdarno_superiore
-- 4 toscana_nord
-- 5 valdarno_inferiore
-- 6 toscana_sud
-- 7 valdarno_centrale
-- 8 assetto_idrogeo
-- 9 protezione_civile
-- 10 difesa_suolo

-- UPDATE difesa_del_suolo_criticita_segnalazione
-- SET nota_segn = REPLACE(nota_segn, 'documents/note_segnalazione', 'documents/utente_toscana_nord/note_segnalazione'),
--     nota_risp = REPLACE(nota_risp, 'documents/nota_risposta', 'documents/utente_toscana_nord/nota_risposta'),
--     rel_sopr = REPLACE(rel_sopr, 'documents/relazione_sopralluogo', 'documents/utente_toscana_nord/relazione_sopralluogo');
    
-- UPDATE documentazione
-- SET doc_coll = REPLACE(nota_segn, 'documents/documenti_collegati_tn', 'documents/utente_toscana_nord/documenti_collegati');

INSERT INTO difesa_del_suolo_criticita_segnalazione (
  codsegn,
  data_prot_arr,
  prot_arrivo,
  geom,
  nota_segn,
  nominativo_s,
  corso_via,
  localita,
  rel_sopr,
  nota_risp,
  desc_sint_crit,
  liv_prog_lav,
  desc_sint_int,
  imp_glob,
  imp_ric,
  ref_doc,
  note,
  istruttoria,
  data_inizio_istr,
  data_fine_istr,
  email_task_id,
  email_sent,
  bacidro,
  comune_id,
  ins_dods,
  mot_segn,
  ogg_segn,
  provincia_id,
  set_reg_comp,
  utente_id
        )
SELECT codsegn,
    data_prot_arr,
    prot_arrivo,
    geom,
    nota_segn,
    nominativo_s, 
    corso_via,
    localita,
    rel_sopr,
    nota_risp,
    desc_sint_crit,
    liv_prog_lav,
    desc_sint_int,
    imp_glob,
    imp_ric,
    ref_doc,
    note,
    istruttoria,
    data_inizio_istr,
    data_fine_istr,
    email_task_id,
    email_sent,
    bacidro,
    comune_id,
    ins_dods,
    mot_segn,
    ogg_segn,
    provincia_id,
    set_reg_comp,
    3
FROM gc_valdarno_superiore_segnalazione
ORDER BY codsegn;

-- UPDATE DOCUMNTAZIONE
INSERT INTO documentazione (
  tipo_doc,
  doc_coll,
  segn_fk
        )
SELECT
  tipo_doc,
  doc_coll,
  segn_fk
FROM documentazione_vs;