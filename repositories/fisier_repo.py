from sqlalchemy.orm import Session
from models.entities import Fisier

class FisierRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, nume_original: str, cale_stocare: str, hash_sha256: str, status_fisier: str) -> Fisier:
        try:
            nou_fisier = Fisier(
                nume_original=nume_original, 
                cale_stocare=cale_stocare, 
                hash_sha256=hash_sha256,
                status_fisier=status_fisier
            )
            self.session.add(nou_fisier)
            self.session.commit()
            self.session.refresh(nou_fisier)
            return nou_fisier
        except Exception:
            self.session.rollback()
            raise

    def read(self) -> list[Fisier]:
        return self.session.query(Fisier).all()

    def read_by_id(self, id_fisier: int) -> Fisier | None:
        return self.session.query(Fisier).filter(Fisier.id_fisier == id_fisier).first()

    def update(self, id_fisier: int, cale_noua: str = None, status_nou: str = None) -> Fisier | None:
        try:
            fisier = self.read_by_id(id_fisier)
            if fisier:
                if cale_noua:
                    fisier.cale_stocare = cale_noua
                if status_nou:
                    fisier.status_fisier = status_nou
                self.session.commit()
                self.session.refresh(fisier)
            return fisier
        except Exception:
            self.session.rollback()
            raise

    def delete(self, id_fisier: int) -> bool:
        try:
            fisier = self.read_by_id(id_fisier)
            if fisier:
                self.session.delete(fisier)
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            raise