from sqlalchemy.orm import Session, joinedload
from models.entities import Performanta, Cheie, Algoritm, Framework
from sqlalchemy import func

class PerformantaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        id_fisier: int,
        id_cheie: int,
        id_framework: int,
        timp_ms: float,
        memorie_kb: float,
        timp_pe_octet_ms: float,
        tip_operatie: str
    ) -> Performanta:
        try:
            nou_log = Performanta(
                id_fisier=id_fisier,
                id_cheie=id_cheie,
                id_framework=id_framework,
                tip_operatie=tip_operatie,
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
        
        items = (
            self.session.query(Performanta)
            .options(
                joinedload(Performanta.fisier),
                joinedload(Performanta.framework),
                joinedload(Performanta.cheie).joinedload(Cheie.algoritm)
            )
            .order_by(Performanta.id_log.desc())
            .offset(offset_val)
            .limit(pe_pagina)
            .all()
        )
        
        total_items = self.session.query(Performanta).count()
        total_pagini = (total_items + pe_pagina - 1) // pe_pagina

        if total_pagini == 0:
            total_pagini = 1
            
        return items, total_pagini
        
    def read_by_id(self, id_log: int) -> Performanta | None:
        return self.session.query(Performanta).filter(Performanta.id_log == id_log).first()

    def read_statistici_medii(self):
        statistici = (
            self.session.query(
                Algoritm.nume.label("algoritm"),
                Framework.nume.label("framework"),
                Framework.versiune.label("versiune"),
                Performanta.tip_operatie.label("tip_operatie"),
                func.count(Performanta.id_log).label("numar_operatii"),
                func.avg(Performanta.timp_executie_ms).label("timp_mediu_ms"),
                func.avg(Performanta.memorie_peak_kb).label("memorie_medie_kb"),
                func.avg(Performanta.timp_pe_octet_ms).label("timp_mediu_pe_octet_ms")
            )
            .join(Cheie, Performanta.id_cheie == Cheie.id_cheie)
            .join(Algoritm, Cheie.id_algoritm == Algoritm.id_algoritm)
            .join(Framework, Performanta.id_framework == Framework.id_framework)
            .group_by(
                Algoritm.nume,
                Framework.nume,
                Framework.versiune,
                Performanta.tip_operatie
            )
            .order_by(func.avg(Performanta.timp_executie_ms).asc())
            .all()
        )

        return statistici