CREATE TABLE ALGORITMI (
    id_algoritm INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(50) NOT NULL,
    tip VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE FISIERE (
    id_fisier INT AUTO_INCREMENT PRIMARY KEY,
    nume_original VARCHAR(255) NOT NULL,
    cale_stocare TEXT NOT NULL,
    hash_sha256 VARCHAR(64) NOT NULL
) ENGINE=InnoDB;


CREATE TABLE FRAMEWORKS (
    id_framework INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(50) NOT NULL,
    versiune VARCHAR(20)
) ENGINE=InnoDB;


CREATE TABLE CHEI (
    id_cheie INT AUTO_INCREMENT PRIMARY KEY,
    id_algoritm INT,
    valoare_criptata BLOB NOT NULL,
    vector_initializare_sau_salt TEXT,
    CONSTRAINT fk_algoritm FOREIGN KEY (id_algoritm) REFERENCES ALGORITMI(id_algoritm) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE PERFORMANTE (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_fisier INT,
    id_cheie INT,
    id_framework INT,
    timp_executie_ms FLOAT,
    memorie_peak_kb FLOAT,
    data_testare DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    CONSTRAINT fk_perf_fisier FOREIGN KEY (id_fisier) 
        REFERENCES FISIERE(id_fisier) ON DELETE CASCADE,
    CONSTRAINT fk_perf_cheie FOREIGN KEY (id_cheie) 
        REFERENCES CHEI(id_cheie) ON DELETE CASCADE,
    CONSTRAINT fk_perf_framework FOREIGN KEY (id_framework) 
        REFERENCES FRAMEWORKS(id_framework) ON DELETE CASCADE
) ENGINE=InnoDB;

select * from algoritmi;
select * from chei;
select * from fisiere;
select * from frameworks;
select * from performante;
