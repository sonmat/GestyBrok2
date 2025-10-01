-- ----------------------------------------------------------
-- MDB Tools - A library for reading MS Access database files
-- Copyright (C) 2000-2011 Brian Bruns and others.
-- Files in libmdb are licensed under LGPL and the utilities under
-- the GPL, see COPYING.LIB and COPYING files respectively.
-- Check out http://mdbtools.sourceforge.net
-- ----------------------------------------------------------

-- That file uses encoding UTF-8

CREATE TABLE `t_articoli`
 (
	`id_articolo`			INTEGER, 
	`nome_articolo`			varchar, 
	`unita_misura`			varchar, 
	`famiglia`			varchar, 
	`tipologia`			varchar
);

CREATE TABLE `t_compratore_cerca`
 (
	`id_cerca`			INTEGER, 
	`compratore`			INTEGER, 
	`articolo`			INTEGER, 
	`note`			TEXT
);

CREATE TABLE `t_compratori`
 (
	`id_compratore`			INTEGER, 
	`azienda`			varchar, 
	`indirizzo`			varchar, 
	`cap`			varchar, 
	`citta`			varchar, 
	`stato`			varchar, 
	`fax`			varchar, 
	`telefono`			varchar, 
	`piva`			varchar, 
	`italiano`			INTEGER, 
	`tipo_pagamento`			INTEGER, 
	`iva`			INTEGER
);

CREATE TABLE `t_conferme`
 (
	`id_conferma`			INTEGER, 
	`compratore`			INTEGER, 
	`venditore`			INTEGER, 
	`qta`			INTEGER, 
	`prezzo`			REAL, 
	`articolo`			INTEGER, 
	`n_conf`			varchar, 
	`data_conf`			DateTime, 
	`provvigione`			REAL, 
	`tipologia`			varchar, 
	`luogo_consegna`			varchar, 
	`condizioni_pag`			INTEGER, 
	`note`			TEXT, 
	`carico`			INTEGER, 
	`arrivo`			INTEGER, 
	`emailv`			INTEGER, 
	`emailc`			INTEGER
);

CREATE TABLE `t_date_consegna`
 (
	`ID`			INTEGER, 
	`id_conferma`			INTEGER, 
	`data_consegna`			DateTime, 
	`qta_consegna`			INTEGER
);

CREATE TABLE `t_dati_compratori`
 (
	`id_compratore`			INTEGER, 
	`email`			varchar, 
	`fax`			varchar, 
	`ntel`			varchar, 
	`ntel_tipologia`			varchar, 
	`contatto`			varchar
);

CREATE TABLE `t_famiglia_articoli`
 (
	`descrizione`			varchar
);

CREATE TABLE `t_fat_studio_dett`
 (
	`ID_fat_studio_det`			INTEGER, 
	`id_fatt_studio`			INTEGER, 
	`compratore`			INTEGER, 
	`qta`			INTEGER, 
	`prezzo`			REAL, 
	`provvigione`			REAL, 
	`tipologia`			varchar, 
	`data_consegna`			DateTime
);

CREATE TABLE `t_fatture`
 (
	`id_fattura`			INTEGER, 
	`confermaordine`			INTEGER, 
	`n_fat`			INTEGER, 
	`data_fat`			DateTime, 
	`nota_acr`			INTEGER, 
	`articolo`			INTEGER, 
	`qta`			INTEGER, 
	`prezzo`			REAL, 
	`iva_perc`			REAL, 
	`data_consegna`			DateTime, 
	`compilato`			INTEGER, 
	`fatturata`			INTEGER
);

CREATE TABLE `t_fatture_studio`
 (
	`id_fatt_studio`			INTEGER, 
	`n_fat`			INTEGER, 
	`data_fat`			DateTime, 
	`nota_acr`			INTEGER, 
	`cliente`			INTEGER, 
	`t_iva`			INTEGER, 
	`t_pagamento`			INTEGER, 
	`note`			TEXT, 
	`id_banca`			INTEGER
);

CREATE TABLE `t_iva`
 (
	`id_iva`			INTEGER, 
	`descriz`			varchar, 
	`iva`			INTEGER
);

CREATE TABLE `t_pagamenti`
 (
	`id_pagamento`			INTEGER, 
	`tipo`			varchar
);

CREATE TABLE `t_venditori`
 (
	`id_venditore`			INTEGER, 
	`azienda`			varchar, 
	`indirizzo`			varchar, 
	`cap`			varchar, 
	`citta`			varchar, 
	`stato`			varchar, 
	`fax`			varchar, 
	`telefono`			varchar, 
	`piva`			varchar, 
	`italiano`			INTEGER, 
	`tipo_pagamento`			INTEGER, 
	`iva`			INTEGER
);

CREATE TABLE `t_venditori_offre`
 (
	`id_offre`			INTEGER, 
	`venditore`			INTEGER, 
	`articolo`			INTEGER, 
	`prezzo`			REAL, 
	`provvigione`			REAL, 
	`tipologia`			varchar
);

CREATE TABLE `t_dati_venditori`
 (
	`id_venditore`			INTEGER, 
	`email`			varchar, 
	`fax`			varchar, 
	`ntel`			varchar, 
	`ntel_tipologia`			varchar, 
	`contatto`			varchar
);

CREATE TABLE `t_tipo_articoli`
 (
	`tipologia`			varchar
);

CREATE TABLE `t_conferme_trading`
 (
	`id_conferma`			INTEGER, 
	`compratore`			INTEGER, 
	`venditore`			INTEGER, 
	`qta`			INTEGER, 
	`prezzo_acq`			REAL, 
	`articolo`			INTEGER, 
	`n_conf`			varchar, 
	`data_conf`			DateTime, 
	`prezzo_vend`			REAL, 
	`luogo_consegna`			varchar, 
	`condizioni_pag`			INTEGER, 
	`note`			TEXT, 
	`carico`			INTEGER, 
	`arrivo`			INTEGER, 
	`emailv`			INTEGER, 
	`emailc`			INTEGER, 
	`condizioni_pag_venditore`			INTEGER
);

CREATE TABLE `t_date_consegna_trading`
 (
	`ID`			INTEGER, 
	`id_conferma`			INTEGER, 
	`data_consegna`			DateTime, 
	`qta_consegna`			INTEGER, 
	`fatturata`			INTEGER, 
	`data_pagamento_uscita`			DateTime, 
	`data_pagamento_entrata`			DateTime
);

CREATE TABLE `t_fatture_trading`
 (
	`id_fattura`			INTEGER, 
	`confermaordine`			INTEGER, 
	`n_fat`			INTEGER, 
	`data_fat`			DateTime, 
	`nota_acr`			INTEGER, 
	`articolo`			INTEGER, 
	`qta`			INTEGER, 
	`prezzo`			REAL, 
	`iva_perc`			REAL, 
	`data_consegna`			DateTime, 
	`compilato`			INTEGER, 
	`fatturata`			INTEGER
);

CREATE TABLE `t_fatture_studio_trading`
 (
	`id_fatt_studio`			INTEGER, 
	`n_fat`			INTEGER, 
	`data_fat`			DateTime, 
	`nota_acr`			INTEGER, 
	`cliente`			INTEGER, 
	`t_iva`			INTEGER, 
	`t_pagamento`			INTEGER, 
	`note`			TEXT, 
	`id_banca`			INTEGER, 
	`n_conf`			INTEGER
);

CREATE TABLE `t_fat_studio_dett_trading`
 (
	`ID_fat_studio_det`			INTEGER, 
	`id_fatt_studio`			INTEGER, 
	`articolo`			INTEGER, 
	`qta`			INTEGER, 
	`prezzo`			REAL, 
	`data_consegna`			DateTime
);

CREATE TABLE `t_banche`
 (
	`id_banca`			INTEGER, 
	`banca`			varchar, 
	`riga1`			varchar, 
	`riga2`			varchar, 
	`riga3`			varchar
);


