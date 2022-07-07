import pytest
from json import loads
from app import r_p_s_game


@pytest.fixture
def client():
    app = r_p_s_game
    app.config['TESTING'] = True

    with app.test_client() as client:
        return client


def test_status_code(client):
    client.set_cookie('localhost', 'user_id', '1')
    response = client.get("/")
    status_code = response.status_code
    assert status_code == 200


def test_create_new_user(client):
    response = client.post("/api/create-new-user", content_type='application/json')
    data = loads(response.get_data(as_text=True))
    start_credits = 10
    assert 'user_id' in data
    assert data['start_credits'] == start_credits


def test_get_user_list(client):
    response = client.get("/api/get-user-stat")
    data = loads(response.get_data(as_text=True))
    assert 'user_1' in data
    assert 'id' in data['user_1']
    assert 'credits' in data['user_1']


def test_get_result_from_day(client):
    response = client.get("/api/get-result-from-day/2022-07-06")
    data = loads(response.get_data(as_text=True))
    assert 'game_1' in data
    assert 'user_id' in data['game_1']
    assert 'result' in data['game_1']
    assert 'credits_before_game' in data['game_1']
    assert 'game_time' in data['game_1']
