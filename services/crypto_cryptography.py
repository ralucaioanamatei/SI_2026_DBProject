import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend


def cripteaza_cryptography(cale_intrare, cale_iesire, cheie, algoritm, chunk_size):
    memorie_utilizata_kb = 0
    backend = default_backend()

    if algoritm.tip == 'asimetric':
        with open(cale_intrare, 'rb') as f_in:
            date_originale = f_in.read()
        
        if len(date_originale) > 190:
            raise ValueError("Fișierul este prea mare pentru RSA direct! RSA suportă doar fișiere mici (ex. texte scurte).")

        memorie_utilizata_kb = len(date_originale) / 1024.0

        private_key = load_pem_private_key(cheie.valoare_criptata, password=None, backend=backend)
        public_key = private_key.public_key()
        date_criptate = public_key.encrypt(
            date_originale,
            asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        with open(cale_iesire, 'wb') as f_out:
            f_out.write(date_criptate)

    else: # AES
        if cheie.vector_initializare_sau_salt == "RSA_KEY_PAIR":
            raise ValueError("Eroare: Ai selectat o cheie asimetrică (RSA) pentru o operațiune simetrică (AES)!")

        iv_hex = cheie.vector_initializare_sau_salt if cheie.vector_initializare_sau_salt else os.urandom(16).hex()
        
        try:
            iv_bytes = bytes.fromhex(iv_hex)
        except ValueError:
            raise ValueError(f"Eroare: Valoarea IV/Salt ('{iv_hex}') nu este un cod HEX valid!")

        cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()

        with open(cale_intrare, 'rb') as f_in, open(cale_iesire, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if len(chunk) == 0:
                    break
                date_padded = padder.update(chunk)
                date_criptate = encryptor.update(date_padded)
                f_out.write(date_criptate)
            
            date_padded_final = padder.finalize()
            date_criptate_final = encryptor.update(date_padded_final) + encryptor.finalize()
            f_out.write(date_criptate_final)

        memorie_utilizata_kb = chunk_size / 1024.0

    return memorie_utilizata_kb


def decripteaza_cryptography(cale_intrare, cale_iesire, cheie, algoritm, chunk_size):
    memorie_utilizata_kb = 0
    backend = default_backend()

    if algoritm.tip == 'asimetric':
        with open(cale_intrare, 'rb') as f_in:
            date_criptate = f_in.read()

        memorie_utilizata_kb = len(date_criptate) / 1024.0

        private_key = load_pem_private_key(cheie.valoare_criptata, password=None, backend=backend)
        date_originale = private_key.decrypt(
            date_criptate,
            asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        with open(cale_iesire, 'wb') as f_out:
            f_out.write(date_originale)

    else: # AES
        iv_hex = cheie.vector_initializare_sau_salt
        iv_bytes = bytes.fromhex(iv_hex)

        cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()

        with open(cale_intrare, 'rb') as f_in, open(cale_iesire, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if len(chunk) == 0:
                    break
               
                date_decriptate_partial = decryptor.update(chunk)
                date_fara_padding = unpadder.update(date_decriptate_partial)
                f_out.write(date_fara_padding)
                
            date_decriptate_final = decryptor.finalize()
            date_fara_padding_final = unpadder.update(date_decriptate_final) + unpadder.finalize()
            f_out.write(date_fara_padding_final)

        memorie_utilizata_kb = chunk_size / 1024.0

    return memorie_utilizata_kb