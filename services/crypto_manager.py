import os
import time
import hashlib

from services.crypto_openssl import cripteaza_openssl, decripteaza_openssl
from services.crypto_pycryptodome import cripteaza_pycryptodome, decripteaza_pycryptodome
from services.crypto_cryptography import cripteaza_cryptography, decripteaza_cryptography


class CryptoManagerService:
    def __init__(self, fisier_repo, cheie_repo, performanta_repo):
        self.fisier_repo = fisier_repo
        self.cheie_repo = cheie_repo
        self.performanta_repo = performanta_repo

    def calculeaza_hash(self, cale_fisier):
        sha256 = hashlib.sha256()
        try:
            with open(cale_fisier, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return "hash_indisponibil"

    def este_openssl(self, framework_nume: str):
        return "OPENSSL" in framework_nume.upper() or "CLI" in framework_nume.upper() or "SUBPROCESS" in framework_nume.upper()

    def este_pycryptodome(self, framework_nume: str):
        return "PYCRYPTODOME" in framework_nume.upper() or "PYCRYPTO" in framework_nume.upper()

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
        memorie_utilizata_kb = 0

        if self.este_openssl(framework_nume):
            memorie_utilizata_kb = cripteaza_openssl(
                cale_intrare=cale_intrare,
                cale_iesire=cale_iesire,
                cheie=cheie,
                algoritm=algoritm,
                chunk_size=chunk_size
            )

        elif self.este_pycryptodome(framework_nume):
            memorie_utilizata_kb = cripteaza_pycryptodome(
                cale_intrare=cale_intrare,
                cale_iesire=cale_iesire,
                cheie=cheie,
                algoritm=algoritm,
                chunk_size=chunk_size
            )

        else:
            memorie_utilizata_kb = cripteaza_cryptography(
                cale_intrare=cale_intrare,
                cale_iesire=cale_iesire,
                cheie=cheie,
                algoritm=algoritm,
                chunk_size=chunk_size
            )
            
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

        if not fisier or not cheie:
            raise ValueError("Fișierul sau cheia nu există în baza de date.")

        algoritm = cheie.algoritm
        cale_intrare = fisier.cale_stocare
        cale_iesire = cale_intrare.replace(".enc", ".dec")
        
        start_time = time.perf_counter()

        chunk_size = 64 * 1024
        memorie_utilizata_kb = 0

        if self.este_openssl(framework_nume):
            memorie_utilizata_kb = decripteaza_openssl(
                cale_intrare=cale_intrare,
                cale_iesire=cale_iesire,
                cheie=cheie,
                algoritm=algoritm,
                chunk_size=chunk_size
            )

        elif self.este_pycryptodome(framework_nume):
            memorie_utilizata_kb = decripteaza_pycryptodome(
                cale_intrare=cale_intrare,
                cale_iesire=cale_iesire,
                cheie=cheie,
                algoritm=algoritm,
                chunk_size=chunk_size
            )

        else:
            memorie_utilizata_kb = decripteaza_cryptography(
                cale_intrare=cale_intrare,
                cale_iesire=cale_iesire,
                cheie=cheie,
                algoritm=algoritm,
                chunk_size=chunk_size
            )

        end_time = time.perf_counter()
        timp_ms = (end_time - start_time) * 1000
        dimensiune_bytes = os.path.getsize(cale_intrare)
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