
def test_empty_db(client):
    rv = client.get('/')
    assert b'No entries here so far' in rv.data
