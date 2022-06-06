import json
import time
import requests
import responses
import pytest
from datetime import datetime
from responses import matchers
from requests.exceptions import ConnectionError
from responses.registries import OrderedRegistry

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
        req2 = requests.get(f"{base_url}system/clock/value")
        assert req.json()['System time'] == datetime.now().strftime("%H:%M")
        assert req.status_code == 200
        assert req1.status_code == 400
        assert req1.text == "Bad request"
        print()
        if req.json()['System time'] == req2.json()['System time']:
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
        assert req.json()['status'] == "Pass"
        assert req.status_code == 200
        assert req1.text == "Method Not Allowed"
        assert req1.status_code == 405
        print()
        if req.json()['status'] == "Fail":
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
        register, register_value = "0x01", "100"
        responses.post(
            f"{base_url}g2_5mp_camera/set_imx490_register",
            match=[matchers.urlencoded_params_matcher({"register": register, "register_value": register_value})],
            json=[{
                "Status": "Success",
                "register_details": {
                    "register": [register],
                    "register_value": [register_value]
                }
            }],
            status=201
        )
        responses.get(
            f"{base_url}g2_5mp_camera/set_imx490_register",
            body="Bad request",
            status=400
        )

        req = requests.post(f"{base_url}g2_5mp_camera/set_imx490_register",
                            data={"register": register, "register_value": register_value})

        req2 = requests.get(f"{base_url}g2_5mp_camera/set_imx490_register",
                            data={"register": register, "register_value": register_value})

        assert req.json()[0]['Status'] == "Success"
        assert req.json()[0]['register_details'] == {
            "register": [register],
            "register_value": [register_value]
        }
        assert req.status_code == 201

        assert req2.text == "Bad request"
        assert req2.status_code == 400

    @responses.activate(registry=OrderedRegistry)
    def test_read_imx_value(self):
        param = "0x76"
        responses.get(
            f"{base_url}g2_5mp_camera/read_imx490_register/{param}",
            json={"Register": f"{param}", "Status": "Success"},
            status=200
        )
        responses.get(
            f"{base_url}g2_5mp_camera/read_imx490_register/{param}",
            body="Internal server error",
            status=500
        )
        # responses.post(
        #     f"{base_url}g2_5mp_camera/read_imx490_register/{param}",
        #     body="Method not allowed",
        #     status=405
        # )
        req = requests.get(f"{base_url}g2_5mp_camera/read_imx490_register/{param}")
        assert req.json()['Register'] == param
        assert req.json()['Status'] == "Success"
        assert req.url == f"{base_url}g2_5mp_camera/read_imx490_register/{param}"

        req1 = requests.get(f"{base_url}g2_5mp_camera/read_imx490_register/{param}")
        assert req1.status_code == 500
        assert req1.text == "Internal server error"
        assert req1.url == f"{base_url}g2_5mp_camera/read_imx490_register/{param}"

        # req2 = requests.get(f"{base_url}g2_5mp_camera/read_imx490_register/{param}")
        # assert req2.text == "Method not allowed"
        # assert req2.status_code == 405

        print(int(param, 16))

    @responses.activate
    def test_stressapptest(self):
        def request_callback(request):
            payload = json.loads(request.body)
            resp_body = {"memory": payload['memory'], "copy_threads": payload['copy_threads'],
                         "cpu_threads": payload['cpu_threads'], "time": payload['time'],
                         "stressful-memory": payload['stressful-memory'], "tempfile": payload['tempfile'],
                         "persist": payload['persist'], "enable": payload['enable']}
            # resp_body = {"value": payload['memory']}
            headers = {"request-id": "728d329e-0e86-11e4-a748-0c84dc037c13"}
            return 200, headers, json.dumps(resp_body)

        responses.add_callback(
            responses.POST,
            f"{base_url}hardware_test/stressapptest",
            callback=request_callback,
            content_type="application/json"
        )
        req = requests.post(
            f"{base_url}hardware_test/stressapptest",
            json.dumps(
                {"memory": "512", "copy_threads": "8",
                 "cpu_threads": "8", "time": "10",
                 "stressful-memory": False, "tempfile": ["tempfile1", "tempfile2"],
                 "persist": False, "enable": True}
            ),
            headers={"content-type": "application/json"}
        )
        assert req.status_code == 200
        assert req.url == f"{base_url}hardware_test/stressapptest"
        assert req.headers == {"Content-Type": "application/json","request-id": "728d329e-0e86-11e4-a748-0c84dc037c13"}
        print("\n", req.json())

    # @responses.activate
    # def test_calc_api(self):
    #     def request_callback(request):
    #         payload = json.loads(request.body)
    #         resp_body = {"value": payload["numbers"]}
    #         headers = {"request-id": "728d329e-0e86-11e4-a748-0c84dc037c13"}
    #         return 200, headers, json.dumps(resp_body)
    #
    #     responses.add_callback(
    #         responses.POST,
    #         "http://calc.com/sum",
    #         callback=request_callback,
    #         content_type="application/json",
    #     )
    #
    #     resp = requests.post(
    #         "http://calc.com/sum",
    #         json.dumps({"numbers": [1, 2, 3]}),
    #         headers={"content-type": "application/json"},
    #     )
    #
    #     print(resp.json())
