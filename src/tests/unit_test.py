import json

from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)

def authorization():
    token = client.post("/login", data={'username': 'asdf@mail.ru', 'password': 'asdf'})
    return json.loads(token.content.decode('utf-8'))

def test_list_mem():
    response = client.get("/memes")
    assert response.status_code == 200
    assert type(response.json()) == dict

def test_add_mem():
    access_token = authorization()
    files = {'file': open('src/tests/test.jpg', 'rb')}
    response = client.post("/memes", files=files, data = {'text':'value'}, headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Photo saved successfully"}

def test_err_add_mem():
    access_token = authorization()
    files = {'file': open('src/tests/test1.txt', 'rb')}
    response = client.post("/memes", files=files, data = {'text':'value'}, headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 400
    assert response.json() == {"message": "Photo saved error. Incorrect image format"}

def test_show_mem_noauthorization():
    response = client.get("/memes/5")
    assert response.status_code == 401

def test_err_show_mem():
    access_token = authorization()
    response = client.get("/memes/1000", headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 400
    assert response.json() == {"message": "Incorrect Data. This id is not in the database"}

def test_err_show_mem_nonumber():
    access_token = authorization()
    response = client.get("/memes/e", headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 422

def test_err_delete_mem():
    access_token = authorization()
    response = client.delete("/memes/r", headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 422

def test_err_update_mem():
    access_token = authorization()
    files = {'file': open('src/tests/test1.txt', 'rb')}
    response = client.put("/memes/7", files=files, data={'text': 'value'}, headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 400
    assert response.json() == {"message": "Photo update error. Incorrect image format"}

def test_err_update_mem_nonumber():
    access_token = authorization()
    files = {'file': open('src/tests/test.jpg', 'rb')}
    response = client.put("/memes/r", files=files, data={'text': 'value'}, headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 422

def test_err_update_mem_incorect_number():
    access_token = authorization()
    files = {'file': open('src/tests/test.jpg', 'rb')}
    response = client.put("/memes/6", files=files, data={'text': 'value'}, headers={"Authorization": f"Bearer {access_token['access_token']}"})
    assert response.status_code == 400
    assert response.json() == {"message": "Incorrect Data. Error id"}