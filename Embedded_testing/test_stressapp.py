import json
import time
import requests
import responses
import pytest
from datetime import datetime
from responses import matchers
from requests.exceptions import ConnectionError

base_url = "https://7facbdb5-b28c-46e1-a70f-a00b44f62626.mock.io/api/v1.0/"

class TestCases:
    @responses.activate
    def test_software_version(self):
        resp = responses.Response(method="GET",
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
        responses.add(resp)
        resp1 = responses.Response(
            method="POST",
            url=f"{base_url}swupdate/sw-versions",
            status=400
        )
        responses.add(resp1)
        responses.put(
            url=f"{base_url}swupdate/sw-versions",
            status=400
        )

        req = requests.get(f"{base_url}swupdate/sw-versions")
        req1 = requests.post(f"{base_url}swupdate/sw-versions")
        req2 = requests.put(f"{base_url}swupdate/sw-versions")
        with pytest.raises(ConnectionError):
            requests.get(f"{base_url}/swupdate/soft-ver")

        dictionary = req.json()
        assert dictionary["api"] == "/api/v1.0/swupdate/sw-versions"
        assert dictionary["status"] == "success"
        assert dictionary["versions"]["name"] == "Cruise 1.0"
        assert dictionary["versions"]["version"] >= "1.0"
        assert req.status_code == 200

        assert req1.status_code == 400
        assert req2.status_code == 400
        print()
        if float(req.json()["versions"]['version']) < 1.0:
            print("Result = Update required")

    # hardware version mock
    @responses.activate
    def test_hardware_version(self):
        # api
        resp = responses.Response(method="GET",
                                  url=f"{base_url}swupdate/hw-revision",
                                  json={
                                      "api": "/api/v1.0/swupdate/hw-revision",
                                      "status": "success",
                                      "board": "Cruiseboardname",
                                      "revision": "1.1"
                                  },
                                  status=200
                                  )
        responses.add(resp)
        responses.patch(
            f"{base_url}swupdate/hw-revision",
            body="Method not allowed",
            status=405
        )

        # requests
        req = requests.get(f"{base_url}swupdate/hw-revision")
        req1 = requests.patch(f"{base_url}swupdate/hw-revision")
        with pytest.raises(ConnectionError):
            req2 = requests.get("http://xyz.com/api/1/foobar")
            print(req2.status_code)

        # assertions
        assert req.json()['api'] == "/api/v1.0/swupdate/hw-revision"
        assert req.json()['status'] == "success"
        assert req.json()['board'] == "Cruiseboardname"
        assert req.json()['revision'] >= "1.1"
        assert req.status_code == 200

        assert req1.status_code == 405
        assert req1.text == "Method not allowed"
        print()
        if req.json()['board'] == "Cruiseboardname":
            print("Result = PASS")
        else:
            print("Result = FAIL")

    @responses.activate
    def test_current_system_time(self):
        current_time = datetime.now().strftime("%H:%M")
        resp = responses.Response(
            method="GET",
            url=f"{base_url}system/clock/value",
            json={"System time": current_time},
            status=200
        )
        responses.add(resp)
        responses.put(
            f"{base_url}system/clock/value",
            body="Bad request",
            status=400
        )
        req = requests.get(f"{base_url}system/clock/value")
        req1 = requests.put(f"{base_url}system/clock/value")
        assert req.json()['System time'] == datetime.now().strftime("%H:%M")
        assert req.status_code == 200
        assert req1.status_code == 400
        assert req1.text == "Bad request"
        print()
        if req.json()['System time'] == current_time:
            print("Result = PASS")
        else:
            print("Result = FAIL")

    @responses.activate
    def test_boot_status(self):
        resp = responses.Response(
            method="GET",
            url=f"{base_url}swupdate/boot-status",
            json={
                "api": "/api/v1.0/swupdate/boot-status",
                "boot-status": "success",
                "status": "Pass"
            },
            status=200
        )
        responses.post(
            f"{base_url}swupdate/boot-status",
            body="Method Not Allowed",
            status=405
        )
        responses.add(resp)
        req = requests.get(f"{base_url}swupdate/boot-status")
        req1 = requests.post(f"{base_url}swupdate/boot-status")
        assert req.json()['api'] == "/api/v1.0/swupdate/boot-status"
        assert req.json()['boot-status'] == "success"
        assert req.json()['status'] == "pass"
        assert req.status_code == 200
        assert req1.text == "Method Not Allowed"
        assert req1.status_code == 405
        print()
        if req.json()['status'] == "fail":
            print("Reset Device")

    @responses.activate
    def test_humidity_and_temperature(self):
        t = time.time()
        resp = responses.Response(
            method="GET",
            url=f"{base_url}device/relative_humidity_temperature",
            json=[{
                "device_name": "device_relative_humidity",
                "readings": [7.7],
                "unit": "Relative Humidity (Percentage)"
            },
                {
                    "device_name": "device_temperature",
                    "readings": [55.799],
                    "unit": "Celsius"
                }],
            status=200
        )
        responses.post(
            f"{base_url}device/relative_humidity_temperature",
            body="Method Not Allowed",
            status=405
        )
        responses.add(resp)
        req = requests.get(f"{base_url}device/relative_humidity_temperature")
        req1 = requests.post(f"{base_url}device/relative_humidity_temperature")
        total_time = time.time() - t
        assert req.status_code == 200
        assert req.json()[0]['device_name'] == "device_relative_humidity"
        assert req.json()[1]['device_name'] == "device_temperature"
        assert req.json()[1]['unit'] == "Celsius"
        assert req1.text == "Method Not Allowed"
        assert req1.status_code == 405
        print()
        if total_time < 100:
            print("Result = PASS")
        else:
            print("Result = FAIL")

    @responses.activate
    def test_set_imx_register(self):
        # def request_callback(request):
        #     payload = json.load(request.body)
        #     resp_body = [{
        #         "Status": "Success",
        #         "register_details": {
        #             "register": [payload['register']],
        #             "register_value": [payload['register_value']]
        #         }
        #     }]
        #     return 200, json.dumps(resp_body)

        responses.post(
            f"{base_url}g2_5mp_camera/set_imx490_register",
            match=[matchers.urlencoded_params_matcher({"register": "0x01", "register_value": "100"})],
            json=[{
                "Status": "Success",
                "register_details": {
                    "register": ["0x01"],
                    "register_value": ["100"]
                }
            }],
            status=201
        )
        # responses.add_callback(
        #     responses.POST,
        #     f"{base_url}g2_5mp_camera/set_imx490_register",
        #     callback=request_callback,
        #     content_type="application/json"
        # )
        req = requests.post(f"{base_url}g2_5mp_camera/set_imx490_register",
                            data={"register": "0x01", "register_value": "100"})
        # req1 = requests.post(f"{base_url}g2_5mp_camera/set_imx490_register",
        #                      json.dumps({"register": "0x01", "register_value": "100"}))
        #
        # print(req1.json())

        assert req.json()[0]['Status'] == "Success"
        assert req.json()[0]['register_details'] == {
            "register": ["0x01"],
            "register_value": ["100"]
        }
        assert req.status_code == 201

    @responses.activate
    def test_read_imx_value(self):
        param = "0x7663"
        responses.get(
            f"{base_url}g2_5mp_camera/read_imx490_register/{param}",
            json={"Register": f"{param}", "Status": "Success"},
            status=200
        )
        req = requests.get(f"{base_url}g2_5mp_camera/read_imx490_register/{param}")
        assert req.json()['Register'] == param
        assert req.json()['Status'] == "Success"
        print(int(param, 16))

    @responses.activate
    def test_stressapptest(self):
        pass
