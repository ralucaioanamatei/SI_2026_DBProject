from sqlalchemy.orm import Session
from models.entities import Cheie

class CheieRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, id_algoritm: int, valoare_criptata: bytes, iv_sau_salt: str = None) -> Cheie:
        try:
            noua_cheie = Cheie(
                id_algoritm=id_algoritm, 
                valoare_criptata=valoare_criptata, 
                vector_initializare_sau_salt=iv_sau_salt
            )
            self.session.add(noua_cheie)
            self.session.commit()
            self.session.refresh(noua_cheie)
            return noua_cheie
        except Exception:
            self.session.rollback()
            raise

    def read(self) -> list[Cheie]:
        return self.session.query(Cheie).all()
    
    def read_paginat(self, pagina: int, pe_pagina: int):
        offset_val = (pagina - 1) * pe_pagina
        
        items = self.session.query(Cheie).offset(offset_val).limit(pe_pagina).all()
        
        total_items = self.session.query(Cheie).count()
        total_pagini = (total_items + pe_pagina - 1) // pe_pagina
        if total_pagini == 0:
            total_pagini = 1
            
        return items, total_pagini

    def read_by_id(self, id_cheie: int) -> Cheie | None:
        return self.session.query(Cheie).filter(Cheie.id_cheie == id_cheie).first()

    def delete(self, id_cheie: int) -> bool:
        try:
            cheie = self.read_by_id(id_cheie)
            if cheie:
                self.session.delete(cheie)
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            raise