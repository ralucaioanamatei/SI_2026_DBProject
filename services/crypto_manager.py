import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class CryptoManagerService:
    def __init__(self, fisier_repo, cheie_repo, performanta_repo):
        self.fisier_repo = fisier_repo
        self.cheie_repo = cheie_repo
        self.performanta_repo = performanta_repo
        self.backend = default_backend()

    def cripteaza_fisier(self, id_fisier: int, id_cheie: int, id_framework: int):
        fisier = self.fisier_repo.read_by_id(id_fisier)
        cheie = self.cheie_repo.read_by_id(id_cheie)

        if not fisier or not cheie:
            raise ValueError("Fisierul sau cheia nu exista in baza de date.")

        cale_intrare = fisier.cale_stocare
        cale_iesire = f"{cale_intrare}.enc"
        
        iv_bytes = bytes.fromhex(cheie.vector_initializare_sau_salt) if cheie.vector_initializare_sau_salt else os.urandom(16)

        cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=self.backend)
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()

        start_time = time.time()

        with open(cale_intrare, 'rb') as f_in:
            date_originale = f_in.read()

        date_padded = padder.update(date_originale) + padder.finalize()
        date_criptate = encryptor.update(date_padded) + encryptor.finalize()

        with open(cale_iesire, 'wb') as f_out:
            f_out.write(date_criptate)

        end_time = time.time()
        timp_ms = (end_time - start_time) * 1000

        dimensiune_kb = len(date_padded) / 1024.0

        self.fisier_repo.update(id_fisier, cale_noua=cale_iesire, status_nou="criptat")
        
        self.performanta_repo.create(
            id_fisier=id_fisier,
            id_cheie=id_cheie,
            id_framework=id_framework,
            timp_ms=timp_ms,
            memorie_kb=dimensiune_kb
        )

        return cale_iesire

    def decripteaza_fisier(self, id_fisier: int, id_cheie: int):
        fisier = self.fisier_repo.read_by_id(id_fisier)
        cheie = self.cheie_repo.read_by_id(id_cheie)

        cale_intrare = fisier.cale_stocare
        cale_iesire = cale_intrare.replace(".enc", ".dec")
        
        iv_bytes = bytes.fromhex(cheie.vector_initializare_sau_salt)

        cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=self.backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()

        with open(cale_intrare, 'rb') as f_in:
            date_criptate = f_in.read()

        date_padded = decryptor.update(date_criptate) + decryptor.finalize()
        date_originale = unpadder.update(date_padded) + unpadder.finalize()

        with open(cale_iesire, 'wb') as f_out:
            f_out.write(date_originale)

        self.fisier_repo.update(id_fisier, cale_noua=cale_iesire, status_nou="decriptat")

        return cale_iesire