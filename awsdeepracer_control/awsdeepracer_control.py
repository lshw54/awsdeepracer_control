import sys
import json
import logging
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup
import urllib3

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.INFO)


class DeepracerVehicleApiError(Exception):
    pass


# Class that interfaces with thea web page to control the DeepRacer, load models, and receive camera data
class Client:
    BASE_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

    def __init__(self, password, ip="127.0.0.1", name="deepracer"):
        logging.info("Create client with ip = %s", ip)
        self.session = requests.Session()
        urllib3.disable_warnings()
        self.password = password
        self.name = name
        self.ip = ip
        self.headers = None
        self.URL = f"https://{self.ip}/"
        self.csrf_token = None

    def show_vehicle_info(self):
        """Display vehicle information."""
        info = {
            "USB connection": self.get_is_usb_connected(),
            "Battery level": self.get_battery_status(),
            "Angle settings": self.get_calibration_angle(),
            "Throttle settings": self.get_calibration_throttle(),
            "Models": self.get_models(),
            "Network details": self.get_network_details()
        }
        for key, value in info.items():
            print(f"{key}: {value}")

    def get_is_usb_connected(self):
        return self._get("api/is_usb_connected")

    def get_battery_status(self):
        level = self._get("api/get_battery_level")["battery_level"]
        battery_messages = {
            10: "Full charge",
            -1: "Vehicle battery not connected"
        }
        return battery_messages.get(level, f"Battery level: {level}")

    def get_network_details(self):
        return self._get("api/get_network_details")

    def get_raw_video_stream(self):
        self._get_csrf_token()
        video_url = f"{self.URL}/route?topic=/camera_pkg/display_mjpeg&width=1920&height=1080"
        return self.session.get(video_url, headers=self.headers, stream=True, verify=False)

    #  methods for running autonomous mode

    def set_autonomous_mode(self):
        self.stop_car()
        data = {"drive_mode": "auto"}
        return self._put("api/drive_mode", data)

    def set_throttle_percent(self, throttle_percent):
        data = {"throttle": throttle_percent}
        return self._put("api/max_nav_throttle", data)

    #  methods for running manual mode

    def set_manual_mode(self):
        self.stop_car()
        data = {"drive_mode": "manual"}
        return self._put("api/drive_mode", data)

    def start_car(self):
        data = {"start_stop": "start"}
        return self._put("api/start_stop", data)

    def stop_car(self):
        data = {"start_stop": "stop"}
        return self._put("api/start_stop", data)

    def move(self, steering_angle, throttle, max_speed):
        # moving the car
        data = {"angle": steering_angle, "throttle": throttle, "max_speed": max_speed}
        return self._put("api/manual_drive", data)

    # models

    def get_models(self):
        return self._get("api/models")

    def get_uploaded_models(self):
        return self._get("api/uploaded_model_list")

    def load_model(self, model_name):
        model_url = "api/models/" + model_name + "/model"
        return self._put(model_url, None)

    def upload_model(self, model_zip_path, model_name):
        model_file = open(model_zip_path, "rb")
        headers = self.headers
        multipart_data = MultipartEncoder(
            fields={
                # a file upload field
                "file": (model_name, model_file, None)
            }
        )
        headers["content-type"] = multipart_data.content_type
        upload_models_url = self.URL + "/api/uploadModels"

        return self.session.put(
            upload_models_url, data=multipart_data, headers=headers, verify=False
        )

    # calibration

    def set_calibration_mode(self):
        return self._get("api/set_calibration_mode")

    def get_calibration_angle(self):
        return self._get("api/get_calibration/angle")

    def get_calibration_throttle(self):
        return self._get("api/get_calibration/throttle")

    def set_calibration_throttle(self, throttle):
        return self._put("api/set_calibration/throttle", throttle)

    def set_calibration_angle(self, angel):
        return self._put("api/set_calibration/angle", angel)

    # helper methods

    def _get(self, url, check_status_code=True):
        try:
            self._get_csrf_token()
            logging.debug("> Get %s", url)
            response = self.session.get(self.URL + url, headers=self.headers, verify=False)
            if check_status_code:
                if response.status_code != 200:
                    raise DeepracerVehicleApiError(
                        f"Get action failed with status code {response.status_code}"
                    )
            return json.loads(response.text)
        except requests.RequestException as e:
            raise DeepracerVehicleApiError(f"Failed to make GET request due to: {str(e)}")

    def _put(self, url, data, check_success=True):
        try:
            self._get_csrf_token()
            logging.debug("> Put %s with %s", url, data)
            response = self.session.put(
                self.URL + url, json=data, headers=self.headers, verify=False
            )
            response_json = json.loads(response.text)
            if check_success:
                if response.status_code != 200 or not response_json.get("success", False):
                    raise DeepracerVehicleApiError(
                        f"Put action failed with body text {response.text}"
                    )
            return response_json
        except requests.RequestException as e:
            raise DeepracerVehicleApiError(f"Failed to make PUT request due to: {str(e)}")

    def _get_csrf_token(self):
        """Fetch CSRF token."""
        if self.csrf_token:
            return

        response = self._get_initial_page_response()
        self.csrf_token = self._extract_csrf_token(response.text)
        self._perform_login()

    def _get_initial_page_response(self):
        """Get initial DeepRacer page response."""
        try:
            return self.session.get(self.URL, verify=False, timeout=10)
        except requests.exceptions.ConnectTimeout:
            raise DeepracerVehicleApiError(f"The vehicle with URL '{self.URL}' did not respond")

    @staticmethod
    def _extract_csrf_token(page_content):
        """Extract CSRF token from page content."""
        soup = BeautifulSoup(page_content, "lxml")
        return soup.select_one('meta[name="csrf-token"]')["content"]

    def _perform_login(self):
        """Login to DeepRacer control interface."""
        primary_headers = {
            "X-CSRFToken": self.csrf_token,
            "user-agent": self.BASE_USER_AGENT
        }
        payload = {"password": self.password}
        login_url = f"{self.URL}/login"
        post = self.session.post(login_url, data=payload, headers=primary_headers, verify=False)
        if post.status_code != 200:
            raise DeepracerVehicleApiError(f"Log in failed. Error message {post.text}")

        self.headers = {
            "X-CSRFToken": self.csrf_token,
            "user-agent": self.BASE_USER_AGENT,
            "referer": f"{self.URL}home",
            "origin": self.URL,
            "accept-encoding": "gzip, deflate, br",
            "content-type": "application/json;charset=UTF-8",
            "accept": "*/*",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "accept-language": "en-US,en;q=0.9",
            "x-requested-with": "XMLHttpRequest",
        }