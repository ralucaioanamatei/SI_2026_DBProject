import os

from Crypto.Cipher import AES as PyCryptoAES
from Crypto.Util.Padding import pad as pycrypto_pad, unpad as pycrypto_unpad
from Crypto.PublicKey import RSA as PyCryptoRSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256 as PyCryptoSHA256


def cripteaza_pycryptodome(cale_intrare, cale_iesire, cheie, algoritm, chunk_size):
    memorie_utilizata_kb = 0

    if algoritm.tip == 'asimetric':
        with open(cale_intrare, 'rb') as f_in:
            date_originale = f_in.read()
        
        if len(date_originale) > 190:
            raise ValueError("Fișierul este prea mare pentru RSA direct! RSA suportă doar fișiere mici (ex. texte scurte).")

        memorie_utilizata_kb = len(date_originale) / 1024.0

        cheie_rsa_pycrypto = PyCryptoRSA.import_key(cheie.valoare_criptata)
        cipher_rsa = PKCS1_OAEP.new(cheie_rsa_pycrypto, hashAlgo=PyCryptoSHA256.new())
        date_criptate = cipher_rsa.encrypt(date_originale)
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

        cipher_pycrypto = PyCryptoAES.new(
            cheie.valoare_criptata,
            PyCryptoAES.MODE_CBC,
            iv_bytes
        )

        ultimul_chunk = b""

        with open(cale_intrare, 'rb') as f_in, open(cale_iesire, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)

                if chunk:
                    if ultimul_chunk:
                        f_out.write(cipher_pycrypto.encrypt(ultimul_chunk))
                    ultimul_chunk = chunk
                else:
                    date_finale = pycrypto_pad(ultimul_chunk, PyCryptoAES.block_size)
                    f_out.write(cipher_pycrypto.encrypt(date_finale))
                    break

        memorie_utilizata_kb = chunk_size / 1024.0

    return memorie_utilizata_kb


def decripteaza_pycryptodome(cale_intrare, cale_iesire, cheie, algoritm, chunk_size):
    memorie_utilizata_kb = 0

    if algoritm.tip == 'asimetric':
        with open(cale_intrare, 'rb') as f_in:
            date_criptate = f_in.read()

        memorie_utilizata_kb = len(date_criptate) / 1024.0

        cheie_rsa_pycrypto = PyCryptoRSA.import_key(cheie.valoare_criptata)
        cipher_rsa = PKCS1_OAEP.new(cheie_rsa_pycrypto, hashAlgo=PyCryptoSHA256.new())
        date_originale = cipher_rsa.decrypt(date_criptate)
        with open(cale_iesire, 'wb') as f_out:
            f_out.write(date_originale)

    else: # AES
        iv_hex = cheie.vector_initializare_sau_salt
        iv_bytes = bytes.fromhex(iv_hex)

        cipher_pycrypto = PyCryptoAES.new(
            cheie.valoare_criptata,
            PyCryptoAES.MODE_CBC,
            iv_bytes
        )

        ultimul_chunk = b""

        with open(cale_intrare, 'rb') as f_in, open(cale_iesire, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)

                if chunk:
                    if ultimul_chunk:
                        date_decriptate = cipher_pycrypto.decrypt(ultimul_chunk)
                        f_out.write(date_decriptate)
                    ultimul_chunk = chunk
                else:
                    if not ultimul_chunk:
                        raise ValueError("Fișierul criptat este gol sau invalid.")
                    date_finale = cipher_pycrypto.decrypt(ultimul_chunk)
                    date_fara_padding = pycrypto_unpad(date_finale, PyCryptoAES.block_size)
                    f_out.write(date_fara_padding)
                    break

        memorie_utilizata_kb = chunk_size / 1024.0

    return memorie_utilizata_kb