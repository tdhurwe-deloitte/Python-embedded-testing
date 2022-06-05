import responses
import requests
import pytest

base_url = "http://127.0.0.1:8000/api/v1.0/"


@responses.activate
def test_get_software_version():
    responses.add_passthru("https://7facbdb5-b28c-46e1-a70f-a00b44f62626.mock.pstmn.io/api/v1.0/swupdate/sw-version")

    req = requests.get("https://7facbdb5-b28c-46e1-a70f-a00b44f62626.mock.pstmn.io/api/v1.0/swupdate/sw-version")
    dictionary = req.json()
    assert dictionary["api"] == "/api/v1.0/swupdate/sw-versions"
    assert dictionary["status"] == "success"
    assert dictionary["versions"]["name"] == "Crusie 1.0"
    assert dictionary["versions"]["version"] == "1.0"
    assert req.status_code == 200


@responses.activate
def test_simple():
    responses.add(responses.GET, 'http://twitter.com/api/1/foobar',
                  body=Exception('...'))
    with pytest.raises(Exception):
        requests.get('http://twitter.com/api/1/foobar')


# software version mock
# http://<url>:<port>/api/v1.0/swupdate/sw-versions
@responses.activate
def test_software_version():
    resp1 = responses.Response(method="GET",
                               url=f"{base_url}swupdate/sw-versions",
                               json={
                                   "api": "/api/v1.0/swupdate/sw-versions",
                                   "status": "success",
                                   "versions":
                                       {
                                           "name": "Cruise 1.0",
                                           "version": "1.0"
                                       }
                               },
                               status=200
                               )
    responses.add(resp1)
    req = requests.get(f"{base_url}swupdate/sw-versions")

    dictionary = req.json()
    assert dictionary["api"] == "/api/v1.0/swupdate/sw-versions"
    assert dictionary["status"] == "success"
    assert dictionary["versions"]["name"] == "Cruise 1.0"
    assert dictionary["versions"]["version"] == "1.0"
    assert req.status_code == 200


# hardware version mock
def test_hardware_version():
    resp1 = responses.Response(method="GET",
                               url=f"{base_url}swupdate/hw-revision",
                               status=200,
                               json={
                                   "api": "/api/v1.0/swupdate/hw-revision",
                                   "status": "success",
                                   "board": "Cruiseboardname",
                                   "revision": "1.1"
                               }
                               )
    responses.add(resp1)
    req = requests.get(f"{base_url}swupdate/hw-revision")
