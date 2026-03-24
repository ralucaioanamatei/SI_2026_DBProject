from models.database import SessionLocal
from repositories.algoritm_repo import AlgoritmRepository
from repositories.fisier_repo import FisierRepository
from repositories.framework_repo import FrameworkRepository
from repositories.cheie_repo import CheieRepository
from repositories.performanta_repo import PerformantaRepository

def ruleaza_teste_integrare():
    db_session = SessionLocal()
    
    repo_alg = AlgoritmRepository(db_session)
    repo_fis = FisierRepository(db_session)
    repo_fw = FrameworkRepository(db_session)
    repo_cheie = CheieRepository(db_session)
    repo_perf = PerformantaRepository(db_session)

    try: 
        print("\n (CREATE) Adaugam date.")
        
        alg = repo_alg.create(nume="AES-256-CBC", tip="simetric")
        print(f"Algoritm adaugat: {alg.nume} (Tip: {alg.tip})")

        fw = repo_fw.create(nume="OpenSSL", versiune="3.1.0")
        print(f"Framework adaugat: {fw.nume}")

        fis = repo_fis.create(nume_original="document.pdf", cale_stocare="/fisiere/doc.pdf", hash_sha256="abcd1234hash", status_fisier="original")
        print(f"Fisier adaugat: {fis.nume_original} (Status: {fis.status_fisier})")

        cheie = repo_cheie.create(id_algoritm=alg.id_algoritm, valoare_criptata=b"bytes_12345", iv_sau_salt="random_iv")
        print(f"Cheie generata pentru algoritmul ID {cheie.id_algoritm}")

        perf = repo_perf.create(id_fisier=fis.id_fisier, id_cheie=cheie.id_cheie, id_framework=fw.id_framework, timp_ms=45.2, memorie_kb=1024.5)
        print(f"Log performanta inregistrat: {perf.timp_executie_ms} ms")

        print("\n(READ) Citim fisierul din DB:")
        fisiere_db = repo_fis.read()
        for f in fisiere_db:
            print(f"  -> Gasit in DB: {f.nume_original} cu Status: {f.status_fisier}")

        print("\n(UPDATE) Criptam fisierul si ii schimbam statusul in DB.")
        fis_upd = repo_fis.update(id_fisier=fis.id_fisier, status_nou="criptat")
        print(f"Noul status al fisierului este: {fis_upd.status_fisier}")

        print("\n(DELETE) Stergerea fisierului din sistem.")
        repo_fis.delete(fis.id_fisier)
        
        perf_ramase = repo_perf.read()
        if len(perf_ramase) == 0:
            print("Log-ul de performanta a fost sters automat (stergere in cascada)")
        else:
            print("Logul de performanta inca exista.")

        print("\nToate testele au trecut.")

    except Exception as e:
        print(f"\nEROARE: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    ruleaza_teste_integrare()