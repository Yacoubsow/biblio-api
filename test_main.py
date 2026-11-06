import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB", str(tmp_path / "test.db"))
    main.init_db()                       
    return TestClient(main.app)


LIVRE = {"titre": "Dune", "auteur": "Herbert", "annee": 1965, "genre": "SF"}


def test_creation(client):
    r = client.post("/livres", json=LIVRE)
    assert r.status_code == 201
    assert r.json() == {"id": 1, **LIVRE}


def test_validation(client):
    r = client.post("/livres", json={"titre": "", "auteur": "X"})
    assert r.status_code == 422


def test_inconnu(client):
    assert client.get("/livres/99").status_code == 404


def test_cycle_complet(client):
    client.post("/livres", json=LIVRE)
    r = client.put("/livres/1", json={**LIVRE, "titre": "Dune (poche)"})
    assert r.json()["titre"] == "Dune (poche)"
    assert client.get("/livres").json()[0]["titre"] == "Dune (poche)"
    assert client.delete("/livres/1").status_code == 204
    assert client.get("/livres/1").status_code == 404
