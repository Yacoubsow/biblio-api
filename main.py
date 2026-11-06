import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field


class LivreIn(BaseModel):                     
    model_config = ConfigDict(str_strip_whitespace=True)
    titre: str = Field(min_length=1, max_length=200)
    auteur: str = Field(min_length=1, max_length=100)
    annee: int | None = Field(default=None, ge=1000, le=2100)
    genre: str | None = Field(default=None, min_length=1, max_length=50)


class Livre(LivreIn):                         
    id: int



DB = "biblio.db"


def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS livre (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            titre  TEXT NOT NULL,
            auteur TEXT NOT NULL,
            annee  INTEGER,
            genre  TEXT)""")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()                                  
    yield


app = FastAPI(title="API Bibliothèque", lifespan=lifespan)


def get_db():                                  
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()                          


Db = Annotated[sqlite3.Connection, Depends(get_db)]



def lire_ou_404(db: sqlite3.Connection, livre_id: int) -> dict:
    ligne = db.execute(
        "SELECT * FROM livre WHERE id = ?", (livre_id,)).fetchone()
    if ligne is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return dict(ligne)



@app.get("/")
def accueil():
    return {"message": "Bonjour, atelier !"}


@app.post("/livres", response_model=Livre, status_code=status.HTTP_201_CREATED)
def creer(livre: LivreIn, db: Db):
    cur = db.execute(
        "INSERT INTO livre (titre, auteur, annee, genre) VALUES (?, ?, ?, ?)",
        (livre.titre, livre.auteur, livre.annee, livre.genre))
    db.commit()
    return Livre(id=cur.lastrowid, **livre.model_dump())


@app.get("/livres", response_model=list[Livre])
def lister(db: Db,
           q: str | None = None,
           skip: int = Query(0, ge=0),
           limit: int = Query(20, ge=1, le=100)):
    sql, params = "SELECT * FROM livre", []
    if q:
        sql += " WHERE titre LIKE ?"
        params.append(f"%{q}%")
    sql += " ORDER BY titre LIMIT ? OFFSET ?"
    params += [limit, skip]
    return [dict(ligne) for ligne in db.execute(sql, params).fetchall()]


@app.get("/livres/{livre_id}", response_model=Livre)
def lire(livre_id: int, db: Db):
    return lire_ou_404(db, livre_id)


@app.put("/livres/{livre_id}", response_model=Livre)
def modifier(livre_id: int, livre: LivreIn, db: Db):
    lire_ou_404(db, livre_id)
    db.execute(
        "UPDATE livre SET titre = ?, auteur = ?, annee = ?, genre = ? WHERE id = ?",
        (livre.titre, livre.auteur, livre.annee, livre.genre, livre_id))
    db.commit()
    return Livre(id=livre_id, **livre.model_dump())


@app.delete("/livres/{livre_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(livre_id: int, db: Db):
    lire_ou_404(db, livre_id)
    db.execute("DELETE FROM livre WHERE id = ?", (livre_id,))
    db.commit()
