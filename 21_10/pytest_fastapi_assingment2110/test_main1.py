# from fastapi.testclient import TestClient
# from main1 import app,products
# client = TestClient(app)
#
# def test_get_products():
#     response = client.get("/products")
#     assert response.status_code == 200
#     data = response.json() == []
#
# def test_add_product():
#     response = client.post(
#         "/products",
#         json={
#             "id": 101,
#             "name": "Webcam",
#             "price": 3200
#         }
#     )
#
#     assert response.status_code == 200
#
#     data = response.json()
#
#     assert data["id"] == 101
#     assert data["name"] == "Webcam"
#     assert data["price"] == 3200
#
#
#
# def test_get_products_after_add():
#     client.post(
#         "/products",
#         json={
#             "id": 102,
#             "name": "Microphone",
#             "price": 4500
#         }
#     )
#
#     response = client.get("/products")
#
#     assert response.status_code == 200
#     assert len(response.json()) > 0
#
#
#
# def test_invalid_product():
#     response = client.post(
#         "/products",
#         json={
#             # "id": 103,
#             "name": "Speaker",
#             "price": "hello"
#         }
#     )
#
#     assert response.status_code == 422