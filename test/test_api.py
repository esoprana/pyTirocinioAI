import json

import pytest
import dateutil

import progTiroc


def check_user(obj):
    assert isinstance(obj, dict)
    assert set(obj.keys()) == {'id', 'username'}


def check_message(obj):
    assert isinstance(obj, dict)
    assert set(obj.keys()) == {'id', 'text', 'timestamp'}
    try:
        dateutil.parser.isoparse(obj['timestamp'])
    except ValueError:
        pytest.fail('Timestamp is not iso8601')


@pytest.yield_fixture(scope='function')
def app():
    yield progTiroc.server_setup()


def test_user_list(app):
    request, response = app.test_client.get('/api/user')

    assert response.status == 200
    assert isinstance(response.json, list)
    for user in response.json:
        check_user(user)


def test_put_get_single_user(app):
    request, response = app.test_client.put(
        '/api/user', data=json.dumps({
            'username': 'test'
        }))
    assert response.status == 200
    check_user(response.json)
    assert response.json['username'] == 'test'

    request2, response2 = app.test_client.get('/api/user/{}'.format(
        response.json['id']))
    assert response2.status == 200
    check_user(response2.json)
    assert response.json == response2.json

    request3, response3 = app.test_client.get('/api/message/user/{}'.format(
        response.json['id']))
    assert response3.status == 200
    assert isinstance(response3.json, list)
    assert len(response3.json) == 1
    for message in response3.json:
        check_message(message)

    request4, response4 = app.test_client.put(
        '/api/message/{}/000000000000000000000001'.format(response.json['id']),
        data=json.dumps({
            'text': 'message'
        }))

    assert response4.status == 200
    check_message(response4.json)
    assert response4.json['text'] == 'message'
    print(response4.json)

    request5, response5 = app.test_client.get('/api/message/user/{}'.format(
        response.json['id']))
    assert response5.status == 200
    assert isinstance(response5.json, list)
    assert len(response5.json) == 2
    for message in response5.json:
        check_message(message)
    assert dateutil.parser.isoparse(
        response5.json[0]['timestamp']) > dateutil.parser.isoparse(
            response5.json[1]['timestamp'])

    assert response5.json[0]['id'] == response4.json['id']
    assert response5.json[0]['text'] == response4.json['text']
    assert abs(
        dateutil.parser.isoparse(response5.json[0]['timestamp']) - dateutil.
        parser.isoparse(response4.json['timestamp'])).total_seconds() <= 0.001


def test_put_malformed(app):
    request, response = app.test_client.put(
        '/api/user', data=json.dumps({
            'dslam': 'dslakm'
        }))
    assert response.status == 400


def test_put_malformed2(app):
    request, response = app.test_client.put(
        '/api/user', data=json.dumps({
            'username': 'dslakm',
            'as': 'dsa'
        }))
    assert response.status == 400
