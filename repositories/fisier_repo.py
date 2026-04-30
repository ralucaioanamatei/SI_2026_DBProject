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

    def read_paginat(self, pagina: int, pe_pagina: int):
        offset_val = (pagina - 1) * pe_pagina
        
        fisiere = self.session.query(Fisier).offset(offset_val).limit(pe_pagina).all()
        
        #cate fisiere am in total pe pag
        total_fisiere = self.session.query(Fisier).count()
        total_pagini = (total_fisiere + pe_pagina - 1) // pe_pagina
    
        if total_pagini == 0:
            total_pagini = 1
            
        return fisiere, total_pagini
    
    def read_by_id(self, id_fisier: int) -> Fisier | None:
        return self.session.query(Fisier).filter(Fisier.id_fisier == id_fisier).first()

    def update(self, id_fisier: int, cale_noua: str = None, status_nou: str = None, hash_nou: str = None) -> Fisier | None:
        try:
            fisier = self.read_by_id(id_fisier)
            if fisier:
                if cale_noua:
                    fisier.cale_stocare = cale_noua
                if status_nou:
                    fisier.status_fisier = status_nou
                if hash_nou: 
                    fisier.hash_sha256 = hash_nou
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