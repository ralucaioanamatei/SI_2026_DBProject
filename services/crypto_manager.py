import os
import time
import hashlib
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES as PyCryptoAES
from Crypto.Util.Padding import pad as pycrypto_pad, unpad as pycrypto_unpad

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
        
        start_time = time.perf_counter()

        chunk_size = 64 * 1024
        memorie_utilizata_kb=0

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

            #la rsa totul intra in memorie, deci calculez direct dimensiunea
            memorie_utilizata_kb = len(date_originale) / 1024.0

        else:
            if cheie.vector_initializare_sau_salt == "RSA_KEY_PAIR":
                raise ValueError("Eroare: Ai selectat o cheie asimetrică (RSA) pentru o operațiune simetrică (AES)!")

            iv_hex = cheie.vector_initializare_sau_salt if cheie.vector_initializare_sau_salt else os.urandom(16).hex()
            
            try:
                iv_bytes = bytes.fromhex(iv_hex)
            except ValueError:
                raise ValueError(f"Eroare: Valoarea IV/Salt ('{iv_hex}') nu este un cod HEX valid!")
            
            if "OPENSSL" in framework_nume.upper() or "CLI" in framework_nume.upper() or "SUBPROCESS" in framework_nume.upper():
                cmd = [
                    "openssl", "enc", "-aes-256-cbc",
                    "-in", cale_intrare, "-out", cale_iesire,
                    "-K", cheie.valoare_criptata.hex(),
                    "-iv", iv_hex
                ]
                rezultat = subprocess.run(cmd, capture_output=True, text=True)
                if rezultat.returncode != 0:
                    raise RuntimeError(f"Eroare OpenSSL CLI: {rezultat.stderr}")
                #aici procesul extern gestioneaza memoria
                memorie_utilizata_kb=0

            elif "PYCRYPTODOME" in framework_nume.upper() or "PYCRYPTO" in framework_nume.upper():
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

            else:
                cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=self.backend)
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
            
        end_time = time.perf_counter()
        timp_ms = (end_time - start_time) * 1000
        dimensiune_bytes = os.path.getsize(cale_intrare)
        timp_pe_octet_ms = (timp_ms / dimensiune_bytes) if dimensiune_bytes > 0 else 0
        noul_hash = self.calculeaza_hash(cale_iesire)

        self.fisier_repo.update(id_fisier, cale_noua=cale_iesire, status_nou="criptat", hash_nou=noul_hash)
        
        self.performanta_repo.create(
            id_fisier=id_fisier,
            id_cheie=id_cheie,
            id_framework=id_framework,
            timp_ms=timp_ms,
            memorie_kb=memorie_utilizata_kb,
            timp_pe_octet_ms=timp_pe_octet_ms,
            tip_operatie="criptare"
        )

        print(f"Timp total: {timp_ms:.4f} ms; Timp/octet: {timp_pe_octet_ms:.6f} ms; Memorie Chunk: {memorie_utilizata_kb} KB")
        return cale_iesire

    def decripteaza_fisier(self, id_fisier: int, id_cheie: int, framework_nume: str, id_framework: int):
        fisier = self.fisier_repo.read_by_id(id_fisier)
        cheie = self.cheie_repo.read_by_id(id_cheie)

        algoritm = cheie.algoritm
        cale_intrare = fisier.cale_stocare
        cale_iesire = cale_intrare.replace(".enc", ".dec")
        
        start_time = time.perf_counter()

        chunk_size= 64 * 1024
        memorie_utilizata_kb = 0

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

            memorie_utilizata_kb = len(date_criptate) / 1024.0
        else:
            iv_hex = cheie.vector_initializare_sau_salt
            iv_bytes = bytes.fromhex(iv_hex)

            if "OPENSSL" in framework_nume.upper() or "CLI" in framework_nume.upper() or "SUBPROCESS" in framework_nume.upper():
                cmd = [
                    "openssl", "enc", "-aes-256-cbc", "-d",
                    "-in", cale_intrare, "-out", cale_iesire,
                    "-K", cheie.valoare_criptata.hex(), "-iv", iv_hex
                ]
                rezultat = subprocess.run(cmd, capture_output=True, text=True)
                if rezultat.returncode != 0:
                    raise RuntimeError(f"Eroare OpenSSL CLI: {rezultat.stderr}")
                
                memorie_utilizata_kb = 0
            elif "PYCRYPTODOME" in framework_nume.upper() or "PYCRYPTO" in framework_nume.upper():
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

            else:
                cipher = Cipher(algorithms.AES(cheie.valoare_criptata), modes.CBC(iv_bytes), backend=self.backend)
                decryptor = cipher.decryptor()
                unpadder = padding.PKCS7(128).unpadder()

                with open(cale_intrare, 'rb') as f_in, open(cale_iesire, 'wb') as f_out:
                    while True:
                        chunk = f_in.read(chunk_size)
                        if len(chunk) == 0:
                            break
                       
                        #decriptez chunkul
                        date_decriptate_partial = decryptor.update(chunk)
                        
                        date_fara_padding = unpadder.update(date_decriptate_partial)
                        f_out.write(date_fara_padding)
                        
                    date_decriptate_final = decryptor.finalize()
                    date_fara_padding_final = unpadder.update(date_decriptate_final) + unpadder.finalize()
                    f_out.write(date_fara_padding_final)

                memorie_utilizata_kb = chunk_size / 1024.0

        end_time = time.perf_counter()
        timp_ms = (end_time - start_time) * 1000
        dimensiune_bytes = os.path.getsize(cale_intrare) #ma raportez la dim fisierului citit
        timp_pe_octet_ms = (timp_ms / dimensiune_bytes) if dimensiune_bytes > 0 else 0
        noul_hash = self.calculeaza_hash(cale_iesire)

        self.fisier_repo.update(id_fisier, cale_noua=cale_iesire, status_nou="decriptat", hash_nou=noul_hash)
        
        self.performanta_repo.create(
            id_fisier=id_fisier,
            id_cheie=id_cheie,
            id_framework=id_framework,
            timp_ms=timp_ms,
            memorie_kb=memorie_utilizata_kb,
            timp_pe_octet_ms=timp_pe_octet_ms,
            tip_operatie="decriptare"
        )
        
        print(f"Timp decriptare total: { timp_ms: .4f} ms; Timp/octet: {timp_pe_octet_ms:.6f} ms; Memorie Chunk: {memorie_utilizata_kb} KB")
        return cale_iesire