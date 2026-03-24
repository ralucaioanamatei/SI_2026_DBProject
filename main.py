from models.database import SessionLocal
from repositories.algoritmi_repo import AlgoritmRepository

def testeaza_crud_algoritmi():
    print("--- Incepere Teste CRUD pentru entitatea ALGORITMI ---")
    
    db_session = SessionLocal()
    repo = AlgoritmRepository(db_session)

    try:
        alg1 = repo.create(nume="AES-256-CBC", tip="Simetric")
        alg2 = repo.create(nume="RSA-2048", tip="Asimetric")   
        print(f"Adaugat: {alg1.nume} (ID: {alg1.id_algoritm})")
        print(f"Adaugat: {alg2.nume} (ID: {alg2.id_algoritm})")

        toti_algoritmii = repo.read()
        for alg in toti_algoritmii:
            print(f"  -> ID: {alg.id_algoritm} | Nume: {alg.nume} | Tip: {alg.tip}")

        alg_actualizat = repo.update(id_algoritm=alg1.id_algoritm, nume_nou="AES-256-GCM")
        print(f"Noua valoare: {alg_actualizat.nume}")

        rezultat_stergere = repo.delete(alg2.id_algoritm)
        if rezultat_stergere:
            print("Algoritmul a fost sters.")


        print("\n Algoritmi ramasi in DB:")
        ramasi = repo.read()
        for alg in ramasi:
            print(f"  -> ID: {alg.id_algoritm} | Nume: {alg.nume}")

    except Exception as e:
        print(f" A aparut o eroare in timpul testelor: {e}")
    finally:
        db_session.close()
        print("\nTeste finalizate.")

if __name__ == "__main__":
    testeaza_crud_algoritmi()