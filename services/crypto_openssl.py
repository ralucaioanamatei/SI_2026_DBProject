import os
import subprocess
import tempfile


def cripteaza_openssl(cale_intrare, cale_iesire, cheie, algoritm, chunk_size):
    memorie_utilizata_kb = 0

    if algoritm.tip == 'asimetric':
        with open(cale_intrare, 'rb') as f_in:
            date_originale = f_in.read()
        
        if len(date_originale) > 190:
            raise ValueError("Fișierul este prea mare pentru RSA direct! RSA suportă doar fișiere mici (ex. texte scurte).")

        memorie_utilizata_kb = len(date_originale) / 1024.0

        fd_priv, cale_cheie_privata = tempfile.mkstemp(suffix=".pem")
        fd_pub, cale_cheie_publica = tempfile.mkstemp(suffix=".pem")
        os.close(fd_pub)
        
        try:
            with os.fdopen(fd_priv, 'wb') as f_temp:
                f_temp.write(cheie.valoare_criptata)
            
            #extragere cheia publica din cea privata pt a putea cripta
            subprocess.run(["openssl", "rsa", "-in", cale_cheie_privata, "-pubout", "-out", cale_cheie_publica], capture_output=True, check=True)
            
            cmd = [
                "openssl", "pkeyutl", "-encrypt", "-in", cale_intrare, "-out", cale_iesire,
                "-pubin", "-inkey", cale_cheie_publica,
                "-pkeyopt", "rsa_padding_mode:oaep",
                "-pkeyopt", "rsa_oaep_md:sha256"
            ]
            rezultat = subprocess.run(cmd, capture_output=True, text=True)
            if rezultat.returncode != 0:
                raise RuntimeError(f"Eroare OpenSSL CLI RSA: {rezultat.stderr}")
        finally:
            if os.path.exists(cale_cheie_privata): os.remove(cale_cheie_privata)
            if os.path.exists(cale_cheie_publica): os.remove(cale_cheie_publica)

    else: # AES
        if cheie.vector_initializare_sau_salt == "RSA_KEY_PAIR":
            raise ValueError("Eroare: Ai selectat o cheie asimetrică (RSA) pentru o operațiune simetrică (AES)!")

        iv_hex = cheie.vector_initializare_sau_salt if cheie.vector_initializare_sau_salt else os.urandom(16).hex()
        
        try:
            bytes.fromhex(iv_hex)
        except ValueError:
            raise ValueError(f"Eroare: Valoarea IV/Salt ('{iv_hex}') nu este un cod HEX valid!")
        
        cmd = [
            "openssl", "enc", "-aes-256-cbc",
            "-in", cale_intrare, "-out", cale_iesire,
            "-K", cheie.valoare_criptata.hex(),
            "-iv", iv_hex
        ]
        rezultat = subprocess.run(cmd, capture_output=True, text=True)
        if rezultat.returncode != 0:
            raise RuntimeError(f"Eroare OpenSSL CLI: {rezultat.stderr}")
        memorie_utilizata_kb = 0

    return memorie_utilizata_kb


def decripteaza_openssl(cale_intrare, cale_iesire, cheie, algoritm, chunk_size):
    memorie_utilizata_kb = 0

    if algoritm.tip == 'asimetric':
        with open(cale_intrare, 'rb') as f_in:
            date_criptate = f_in.read()

        memorie_utilizata_kb = len(date_criptate) / 1024.0

        fd_priv, cale_cheie_privata = tempfile.mkstemp(suffix=".pem")
        try:
            with os.fdopen(fd_priv, 'wb') as f_temp:
                f_temp.write(cheie.valoare_criptata)
            
            cmd = [
                "openssl", "pkeyutl", "-decrypt", "-in", cale_intrare, "-out", cale_iesire,
                "-inkey", cale_cheie_privata,
                "-pkeyopt", "rsa_padding_mode:oaep",
                "-pkeyopt", "rsa_oaep_md:sha256"
            ]
            rezultat = subprocess.run(cmd, capture_output=True, text=True)
            if rezultat.returncode != 0:
                raise RuntimeError(f"Eroare OpenSSL RSA decriptare: {rezultat.stderr}")
        finally:
            if os.path.exists(cale_cheie_privata): os.remove(cale_cheie_privata)

    else: # AES
        iv_hex = cheie.vector_initializare_sau_salt
        bytes.fromhex(iv_hex)

        cmd = [
            "openssl", "enc", "-aes-256-cbc", "-d",
            "-in", cale_intrare, "-out", cale_iesire,
            "-K", cheie.valoare_criptata.hex(), "-iv", iv_hex
        ]
        rezultat = subprocess.run(cmd, capture_output=True, text=True)
        if rezultat.returncode != 0:
            raise RuntimeError(f"Eroare OpenSSL CLI: {rezultat.stderr}")
        
        memorie_utilizata_kb = 0

    return memorie_utilizata_kb

