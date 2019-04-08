import pytest
import sys, json
sys.path.append("..")
import logging
from __init__ import create_app
from flask import Flask, request, session, jsonify, Blueprint

logging.basicConfig(filename="test/test.log",  format='%(asctime)s %(message)s', filemode='a') 
logger = logging.getLogger()
logger.setLevel(logging.INFO)

USERID, PWD = 'test1', '123'
BUILDING = 'ghc'
ALGO = 'Zodiac'
PGID = 'a4ca9c98-ec5f-433a-91dd-2a3314575c31'
SRCID = ''
LABEL = 'random_label'

"""
test srcipt for plastering api
refer to https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/
"""

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client  # start testing
    ctx.pop()

def test_login(test_client):
    response = test_client.post(
        '/login',
        data=dict(userid=USERID, pwd=PWD)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['userid'] == USERID
    logger.info(data)

def test_build_playground(test_client):
    response = test_client.post(
        '/playground',
        data=dict(userid=USERID, building=BUILDING, algo_type=ALGO)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['userid'] == USERID
    assert data['new_playground'] != None
    PGID = data['new_playground']
    logger.info(data)

def test_select_example(test_client):
    response = test_client.get(
        '/playground/{}/select_example'.format(PGID)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    SRCID = data['srcid']
    logger.info(data)

def test_insert_label(test_client):
    response = test_client.post(
        '/playground/{}/labeled_metadata'.format(PGID),
        data=dict(userid=USERID, srcid=SRCID, expert_label=LABEL)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    logger.info(data)

def test_update_model(test_client):
    response = test_client.get(
        '/playground/{}/update_model'.format(PGID)
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    logger.info(data)