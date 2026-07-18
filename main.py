from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

import models
from database import engine, get_db

# Crear tablas en DB (En producción usar Alembic)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Plataforma de Diseño de Riego y Fertirrigación",
    description="API para calcular y gestionar sistemas de riego localizado de precisión.",
    version="1.0.0"
)

# --- Pydantic Schemas ---
class ParcelaBase(BaseModel):
    nombre: str
    cultivo: str
    textura_suelo: str
    area_util_ha: float
    cad: Optional[float] = None
    profundidad_radicular: Optional[float] = None
    fraccion_agotamiento: Optional[float] = None

class ParcelaCreate(ParcelaBase):
    pass

class ParcelaResponse(ParcelaBase):
    id: int
    class Config:
        orm_mode = True

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la Plataforma de Diseño de Riego. Dirígete a /docs para ver la API."}

@app.post("/parcelas/", response_model=ParcelaResponse, tags=["Parcelas"])
def crear_parcela(parcela: ParcelaCreate, db: Session = Depends(get_db)):
    db_parcela = models.Parcela(**parcela.dict())
    db.add(db_parcela)
    db.commit()
    db.refresh(db_parcela)
    return db_parcela

@app.get("/parcelas/", response_model=List[ParcelaResponse], tags=["Parcelas"])
def listar_parcelas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Parcela).offset(skip).limit(limit).all()

# Endpoint para calcular la FASE 1: Necesidades de Riego (Agronómico)
class NecesidadesInput(BaseModel):
    eto: float = Field(..., description="Evapotranspiración de referencia (mm/día)")
    kc: float = Field(..., description="Coeficiente de cultivo")
    pe: float = Field(..., description="Precipitación efectiva (mm/día)")
    ea: float = Field(..., description="Eficiencia de aplicación (0-1)")
    
class NecesidadesOutput(BaseModel):
    etc: float = Field(..., description="Evapotranspiración del cultivo (mm/día)")
    nn: float = Field(..., description="Necesidad Neta de Riego (mm/día)")
    db: float = Field(..., description="Dosis Bruta de Riego (mm/día)")

@app.post("/calculos/necesidades", response_model=NecesidadesOutput, tags=["Cálculos Agronómicos"])
def calcular_necesidades(datos: NecesidadesInput):
    """
    Realiza los cálculos de la Fase 1: Evapotranspiración y Necesidades de Riego.
    """
    etc = datos.eto * datos.kc
    nn = max(0, etc - datos.pe)
    
    if datos.ea <= 0 or datos.ea > 1:
        raise HTTPException(status_code=400, detail="La Eficiencia de Aplicación debe estar entre 0 y 1.")
        
    db = nn / datos.ea
    
    return NecesidadesOutput(
        etc=round(etc, 2),
        nn=round(nn, 2),
        db=round(db, 2)
    )

# Endpoint para cálculo de AFD e Intervalo
class RiegoInput(BaseModel):
    cad: float = Field(..., description="Capacidad de Almacenamiento de Agua (%)")
    pr: float = Field(..., description="Profundidad radicular (mm)")
    f: float = Field(..., description="Fracción de agotamiento permisible (0-1)")
    etc: float = Field(..., description="Evapotranspiración del cultivo (mm/día)")

class RiegoOutput(BaseModel):
    afd: float = Field(..., description="Agua Fácilmente Disponible (mm)")
    intervalo_maximo_dias: int = Field(..., description="Intervalo máximo de riego (días)")

@app.post("/calculos/programacion", response_model=RiegoOutput, tags=["Cálculos Agronómicos"])
def programar_riego(datos: RiegoInput):
    """
    Realiza los cálculos de la Fase 1: Agua Fácilmente Disponible e Intervalos.
    """
    afd = (datos.pr * datos.cad * datos.f) / 100
    
    if datos.etc <= 0:
        raise HTTPException(status_code=400, detail="ETc debe ser mayor a 0.")
        
    intervalo = int(afd // datos.etc)  # Redondeo hacia abajo
    
    return RiegoOutput(
        afd=round(afd, 2),
        intervalo_maximo_dias=intervalo
    )
