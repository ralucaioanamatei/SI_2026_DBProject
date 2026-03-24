from sqlalchemy import Column, Integer, String, Text, LargeBinary, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Algoritm(Base):
    __tablename__ = 'ALGORITMI'
    
    id_algoritm = Column(Integer, primary_key=True, autoincrement=True)
    nume = Column(String(50), nullable=False)
    tip = Column(String(50), nullable=False)

    chei = relationship("Cheie", back_populates="algoritm", cascade="all, delete")

class Fisier(Base):
    __tablename__ = 'FISIERE'
    
    id_fisier = Column(Integer, primary_key=True, autoincrement=True)
    nume_original = Column(String(255), nullable=False)
    cale_stocare = Column(Text, nullable=False)
    hash_sha256 = Column(String(64), nullable=False)
    status_fisier = Column(String(20), nullable=False)

    performante = relationship("Performanta", back_populates="fisier", cascade="all, delete")

class Framework(Base):
    __tablename__ = 'FRAMEWORKS'
    
    id_framework = Column(Integer, primary_key=True, autoincrement=True)
    nume = Column(String(50), nullable=False)
    versiune = Column(String(20))

    performante = relationship("Performanta", back_populates="framework", cascade="all, delete")

class Cheie(Base):
    __tablename__ = 'CHEI'
    
    id_cheie = Column(Integer, primary_key=True, autoincrement=True)
    id_algoritm = Column(Integer, ForeignKey('ALGORITMI.id_algoritm', ondelete="CASCADE"), nullable=False)
    
    valoare_criptata = Column(LargeBinary, nullable=False) 
    vector_initializare_sau_salt = Column(Text)

    algoritm = relationship("Algoritm", back_populates="chei")
    performante = relationship("Performanta", back_populates="cheie", cascade="all, delete")

class Performanta(Base):
    __tablename__ = 'PERFORMANTE'
    
    id_log = Column(Integer, primary_key=True, autoincrement=True)
    id_fisier = Column(Integer, ForeignKey('FISIERE.id_fisier', ondelete="CASCADE"), nullable=False)
    id_cheie = Column(Integer, ForeignKey('CHEI.id_cheie', ondelete="CASCADE"), nullable=False)
    id_framework = Column(Integer, ForeignKey('FRAMEWORKS.id_framework', ondelete="CASCADE"), nullable=False)
    
    timp_executie_ms = Column(Float)
    memorie_peak_kb = Column(Float)
    data_testare = Column(DateTime, default=datetime.utcnow) 

    fisier = relationship("Fisier", back_populates="performante")
    cheie = relationship("Cheie", back_populates="performante")
    framework = relationship("Framework", back_populates="performante")