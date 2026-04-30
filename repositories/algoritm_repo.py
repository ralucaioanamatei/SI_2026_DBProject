from sqlalchemy.orm import Session
from models.entities import Algoritm

class AlgoritmRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, nume: str, tip: str) -> Algoritm:
        try:
            nou_algoritm = Algoritm(nume=nume, tip=tip)
            self.session.add(nou_algoritm)
            self.session.commit()
            self.session.refresh(nou_algoritm) 
            return nou_algoritm
        except Exception:
            self.session.rollback()
            raise

    def read(self) -> list[Algoritm]:
        return self.session.query(Algoritm).all()
    
    def read_paginat(self, pagina: int, pe_pagina: int):
        offset_val = (pagina - 1) * pe_pagina
        
        items = self.session.query(Algoritm).offset(offset_val).limit(pe_pagina).all()
        
        total_items = self.session.query(Algoritm).count()
        total_pagini = (total_items + pe_pagina - 1) // pe_pagina
        if total_pagini == 0:
            total_pagini = 1
            
        return items, total_pagini

    def read_by_id(self, id_algoritm: int) -> Algoritm | None:
        return self.session.query(Algoritm).filter(Algoritm.id_algoritm == id_algoritm).first()

    def update(self, id_algoritm: int, nume_nou: str = None, tip_nou: str = None) -> Algoritm | None:
        try:
            algoritm = self.read_by_id(id_algoritm)
            if algoritm:
                if nume_nou:
                    algoritm.nume = nume_nou
                if tip_nou:
                    algoritm.tip = tip_nou
                self.session.commit()
                self.session.refresh(algoritm)
            return algoritm
        except Exception:
            self.session.rollback()
            raise

    def delete(self, id_algoritm: int) -> bool:
        try:
            algoritm = self.read_by_id(id_algoritm)
            if algoritm:
                self.session.delete(algoritm)
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            raise