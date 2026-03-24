CREATE TABLE ALGORITMI (
    id_algoritm INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(50) NOT NULL,
    tip VARCHAR(50) NOT NULL,
    CONSTRAINT uq_algoritm UNIQUE (nume),
    CONSTRAINT chk_tip_algoritm CHECK (tip IN ('simetric', 'asimetric'))
) ENGINE=InnoDB;

CREATE TABLE FISIERE (
    id_fisier INT AUTO_INCREMENT PRIMARY KEY,
    nume_original VARCHAR(255) NOT NULL,
    cale_stocare TEXT NOT NULL,
    hash_sha256 VARCHAR(64) NOT NULL,
    status_fisier VARCHAR(20) NOT NULL,
    CONSTRAINT chk_status_fisier CHECK (status_fisier IN ('original', 'criptat', 'decriptat'))
) ENGINE=InnoDB;


CREATE TABLE FRAMEWORKS (
    id_framework INT AUTO_INCREMENT PRIMARY KEY,
    nume VARCHAR(50) NOT NULL,
    versiune VARCHAR(20),
    CONSTRAINT uq_framework UNIQUE (nume, versiune)
) ENGINE=InnoDB;


CREATE TABLE CHEI (
    id_cheie INT AUTO_INCREMENT PRIMARY KEY,
    id_algoritm INT NOT NULL,
    valoare_criptata BLOB NOT NULL,
    vector_initializare_sau_salt TEXT,
    CONSTRAINT fk_algoritm FOREIGN KEY (id_algoritm) REFERENCES ALGORITMI(id_algoritm) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE PERFORMANTE (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_fisier INT NOT NULL,
    id_cheie INT NOT NULL,
    id_framework INT NOT NULL,
    timp_executie_ms FLOAT,
    memorie_peak_kb FLOAT,
    data_testare DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    CONSTRAINT chk_timp CHECK (timp_executie_ms IS NULL OR timp_executie_ms >= 0),
    CONSTRAINT chk_memorie CHECK (memorie_peak_kb IS NULL OR memorie_peak_kb >= 0),
    CONSTRAINT fk_perf_fisier FOREIGN KEY (id_fisier) REFERENCES FISIERE(id_fisier) ON DELETE CASCADE,
    CONSTRAINT fk_perf_cheie FOREIGN KEY (id_cheie) REFERENCES CHEI(id_cheie) ON DELETE CASCADE,
    CONSTRAINT fk_perf_framework FOREIGN KEY (id_framework) REFERENCES FRAMEWORKS(id_framework) ON DELETE CASCADE
) ENGINE=InnoDB;