from sqlalchemy.orm import Session
from models.entities import Performanta

class PerformantaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, id_fisier: int, id_cheie: int, id_framework: int, timp_ms: float, memorie_kb: float, timp_pe_octet_ms: float) -> Performanta:
        try:
            nou_log = Performanta(
                id_fisier=id_fisier, 
                id_cheie=id_cheie, 
                id_framework=id_framework, 
                timp_executie_ms=timp_ms, 
                memorie_peak_kb=memorie_kb,
                timp_pe_octet_ms=timp_pe_octet_ms
            )
            self.session.add(nou_log)
            self.session.commit()
            self.session.refresh(nou_log)
            return nou_log
        except Exception:
            self.session.rollback()
            raise

    def read(self) -> list[Performanta]:
        return self.session.query(Performanta).all()
    
    def read_paginat(self, pagina: int, pe_pagina: int):
        offset_val = (pagina - 1) * pe_pagina
        
        items = self.session.query(Performanta).offset(offset_val).limit(pe_pagina).all()
        
        total_items = self.session.query(Performanta).count()
        total_pagini = (total_items + pe_pagina - 1) // pe_pagina
        if total_pagini == 0:
            total_pagini = 1
            
        return items, total_pagini
        
    def read_by_id(self, id_log: int) -> Performanta | None:
        return self.session.query(Performanta).filter(Performanta.id_log == id_log).first()