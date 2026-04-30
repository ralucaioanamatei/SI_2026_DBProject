from sqlalchemy.orm import Session
from models.entities import Framework

class FrameworkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, nume: str, versiune: str = None) -> Framework:
        try:
            nou_framework = Framework(nume=nume, versiune=versiune)
            self.session.add(nou_framework)
            self.session.commit()
            self.session.refresh(nou_framework)
            return nou_framework
        except Exception:
            self.session.rollback()
            raise

    def read(self) -> list[Framework]:
        return self.session.query(Framework).all()

    def read_paginat(self, pagina: int, pe_pagina: int):
        offset_val = (pagina - 1) * pe_pagina
        
        items = self.session.query(Framework).offset(offset_val).limit(pe_pagina).all()
        
        total_items = self.session.query(Framework).count()
        total_pagini = (total_items + pe_pagina - 1) // pe_pagina
        if total_pagini == 0:
            total_pagini = 1
            
        return items, total_pagini
    
    def read_by_id(self, id_framework: int) -> Framework | None:
        return self.session.query(Framework).filter(Framework.id_framework == id_framework).first()

    def update(self, id_framework: int, nume_nou: str = None, versiune_noua: str = None) -> Framework | None:
        try:
            framework = self.read_by_id(id_framework)
            if framework:
                if nume_nou:
                    framework.nume = nume_nou
                if versiune_noua:
                    framework.versiune = versiune_noua
                self.session.commit()
                self.session.refresh(framework)
            return framework
        except Exception:
            self.session.rollback()
            raise

    def delete(self, id_framework: int) -> bool:
        try:
            framework = self.read_by_id(id_framework)
            if framework:
                self.session.delete(framework)
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            raise