import os
import time
import hashlib
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

class CryptoManagerService:
    def __init__(self, fisier_repo, cheie_repo, performanta_repo):
        self.fisier_repo = fisier_repo
        self.cheie_repo = cheie_repo
        self.performanta_repo = performanta_repo
        self.backend = default_backend()

    def calculeaza_hash(self, cale_fisier):
        sha256 = hashlib.sha256()
        try:
            with open(cale_fisier, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return "hash_indisponibil"

    def cripteaza_fisier(self, id_fisier: int, id_cheie: int, framework_nume: str, id_framework: int):
        fisier = self.fisier_repo.read_by_id(id_fisier)
        cheie = self.cheie_repo.read_by_id(id_cheie)

        if not fisier or not cheie:
            raise ValueError("Fișierul sau cheia nu există în baza de date.")

        algoritm = cheie.algoritm
        cale_intrare = fisier.cale_stocare
        cale_iesire = f"{cale_intrare}.enc"
        
        start_time = time.time()

        if algoritm.tip == 'asimetric':
            with open(cale_intrare, 'rb') as f_in:
                date_originale = f_in.read()
            
            if len(date_originale) > 190:
                raise ValueError("Fișierul este prea mare pentru RSA direct! RSA suportă doar fișiere mici (ex. texte scurte).")

            private_key = load_pem_private_key(cheie.valoare_criptata, password=None, backend=self.backend)
            public_key = private_key.public_key()
            
            date_criptate = public_key.encrypt(
                date_originale,
                asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            with open(cale_iesire, 'wb') as f_out:
                f_out.write(date_criptate)

        else:
            if cheie.vector_initializare_sau_salt == "RSA_KEY_PAIR":
                raise ValueError("Eroare: Ai selectat o cheie asimetrică (RSA) pentru o operațiune simetrică (AES)!")

            iv_hex = cheie.vector_initializare_sau_salt if cheie.vector_initializare_sau_salt else os.urandom(16).hex()
            
            try:
                iv_bytes = bytes.fromhex(iv_hex)
            except ValueError:
                raise ValueError(f"Eroare: Valoarea IV/Salt ('{iv_hex}') nu este un cod HEX valid!")
            if "CLI" in framework_nume.upper() or "SUBPROCESS" in framework_nume.upper():
                cmd = [
                    "openssl", "enc", "-aes-256-cbc",
                    "-in", cale_intrare, "-out", cale_iesire,
                    "-K", cheie.valoare_criptata.hex(),
                    "-iv", iv_hex
                ]
                rezultat = subprocess.run(cmd, capture_output=True, text=True)
                if rezultat.returncode != 0:
                    raise RuntimeError(f"Eroare OpenSSL CLI: {rezultat.stderr}")
            
            else:
                cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=self.backend)
                encryptor = cipher.encryptor()
                padder = padding.PKCS7(128).padder()

                with open(cale_intrare, 'rb') as f_in:
                    date_padded = padder.update(f_in.read()) + padder.finalize()
                
                date_criptate = encryptor.update(date_padded) + encryptor.finalize()
                with open(cale_iesire, 'wb') as f_out:
                    f_out.write(date_criptate)

        end_time = time.time()
        timp_ms = (end_time - start_time) * 1000
        dimensiune_kb = os.path.getsize(cale_iesire) / 1024.0
        noul_hash = self.calculeaza_hash(cale_iesire)

        self.fisier_repo.update(id_fisier, cale_noua=cale_iesire, status_nou="criptat", hash_nou=noul_hash)
        
        self.performanta_repo.create(
            id_fisier=id_fisier, id_cheie=id_cheie, id_framework=id_framework,
            timp_ms=timp_ms, memorie_kb=dimensiune_kb
        )
        return cale_iesire

    def decripteaza_fisier(self, id_fisier: int, id_cheie: int, framework_nume: str, id_framework: int):
        fisier = self.fisier_repo.read_by_id(id_fisier)
        cheie = self.cheie_repo.read_by_id(id_cheie)

        algoritm = cheie.algoritm
        cale_intrare = fisier.cale_stocare
        cale_iesire = cale_intrare.replace(".enc", ".dec")
        
        start_time = time.time()

        if algoritm.tip == 'asimetric':
            with open(cale_intrare, 'rb') as f_in:
                date_criptate = f_in.read()

            private_key = load_pem_private_key(cheie.valoare_criptata, password=None, backend=self.backend)
            date_originale = private_key.decrypt(
                date_criptate,
                asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            with open(cale_iesire, 'wb') as f_out:
                f_out.write(date_originale)
        else:
            iv_hex = cheie.vector_initializare_sau_salt
            iv_bytes = bytes.fromhex(iv_hex)

            if "CLI" in framework_nume.upper() or "SUBPROCESS" in framework_nume.upper():
                cmd = [
                    "openssl", "enc", "-aes-256-cbc", "-d",
                    "-in", cale_intrare, "-out", cale_iesire,
                    "-K", cheie.valoare_criptata.hex(), "-iv", iv_hex
                ]
                rezultat = subprocess.run(cmd, capture_output=True, text=True)
                if rezultat.returncode != 0:
                    raise RuntimeError(f"Eroare OpenSSL CLI: {rezultat.stderr}")
            else:
                cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=self.backend)
                decryptor = cipher.decryptor()
                unpadder = padding.PKCS7(128).unpadder()

                with open(cale_intrare, 'rb') as f_in:
                    date_padded = decryptor.update(f_in.read()) + decryptor.finalize()
                
                date_originale = unpadder.update(date_padded) + unpadder.finalize()
                with open(cale_iesire, 'wb') as f_out:
                    f_out.write(date_originale)

        end_time = time.time()
        timp_ms = (end_time - start_time) * 1000
        dimensiune_kb = os.path.getsize(cale_iesire) / 1024.0
        noul_hash = self.calculeaza_hash(cale_iesire)

        self.fisier_repo.update(id_fisier, cale_noua=cale_iesire, status_nou="decriptat", hash_nou=noul_hash)
        
        self.performanta_repo.create(
            id_fisier=id_fisier, id_cheie=id_cheie, id_framework=id_framework,
            timp_ms=timp_ms, memorie_kb=dimensiune_kb
        )
        return cale_iesire