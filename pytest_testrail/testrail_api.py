# -*- coding: UTF-8 -*-
#
# TestRail API binding for Python 2.x (API v2, available since
# TestRail 3.0)
#
# Learn more:
#
# http://docs.gurock.com/testrail-api2/start
# http://docs.gurock.com/testrail-api2/accessing
#
# Copyright Gurock Software GmbH. See license.md for details.
#
import json
import json as j
import sys
import requests
import time

from pytest_testrail.plugin import TESTRAIL_PREFIX

if sys.version_info.major == 2:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin


class APIClient:
    def __init__(self, base_url, user, password, **kwargs):
        '''
        Instantiate the APIClient class.

        :param base_url: The same TestRail address for the API client you also use to access TestRail with your web
            browser (e.g., https://<your-name>.testrail.com/ or http://<server>/testrail/).
        :type base_url: str
        :param user: Username for the account on the TestRail server.
        :type user: str
        :param password: Password for the account on the TestRail server.
        :type password: str
        :param headers: (optional) Dictionary of HTTP Headers to send with each request.
        :type headers: dict
        :param cert_check: (optional) Either a boolean, in which case it controls whether we verify the server's TLS
            certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to ``True``.
        :type cert_check: bool or str
        :param timeout: (optional) How many seconds to wait for the server to send data before giving up, as a float,
            or a :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        '''
        self.user = user
        self.password = password
        self._url = urljoin(base_url, 'index.php?/api/v2/')
        self.headers = kwargs.get('headers', {'Content-Type': 'application/json'})
        self.cert_check = kwargs.get('cert_check', True)
        self.timeout = kwargs.get('timeout', 10.0)
        if self.timeout is not None:
            self.timeout = isinstance(self.timeout, float) if False else float(self.timeout)

    def send_get(self, uri, **kwargs):
        '''
        Send GET

        Issues a GET request (read) against the API and returns the result (as Python dict).

        :param uri: The API method to call including parameters (e.g. get_case/1)
        :type uri: str
        :param headers: (optional) Dictionary of HTTP Headers to send with the request.
        :type headers: dict
        :param cert_check: (optional) Either a boolean, in which case it controls whether we verify the server's TLS
            certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to ``True``.
        :type cert_check: bool or str
        :param timeout: (optional) How many seconds to wait for the server to send data before giving up, as a float,
            or a :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        '''
        cert_check = kwargs.get('cert_check', self.cert_check)
        headers = kwargs.get('headers', self.headers)
        url = self._url + uri
        print(f"[{TESTRAIL_PREFIX}][GET] Sending GET request to {url}")
        r = requests.get(
            url,
            auth=(self.user, self.password),
            headers=headers,
            verify=cert_check,
            timeout=self.timeout
        )
        print(f"[{TESTRAIL_PREFIX}][GET] Response status code: {r.status_code}")
        print(f"[{TESTRAIL_PREFIX}][GET] Content: {r.content}")

        if r.status_code == 429:  # Too many requests
            pause = int(r.headers.get('Retry-After', 60))
            print("Too many requests: pause for {}s".format(pause))
            time.sleep(pause)
            return self.send_get(uri, **kwargs)
        else:
            try:
                response_json = r.json()
                return response_json
            except json.JSONDecodeError as e:
                print(f"[{TESTRAIL_PREFIX}][GET] JSON decoding error:", e)
                print(f"[{TESTRAIL_PREFIX}][GET] Received non-JSON response:", r.content)
                return str(r.content)

    def send_post(self, uri, data, **kwargs):
        '''
        Send POST

        Issues a POST request (write) against the API and returns the result (as Python dict).

        :param uri: The API method to call including parameters (e.g. get_case/1)
        :type uri: str
        :param data: The data to submit as part of the request (strings must be UTF-8 encoded).
        :type data: dict
        :param headers: (optional) Dictionary of HTTP Headers to send with the request.
        :type headers: dict
        :param cert_check: (optional) Either a boolean, in which case it controls whether we verify the server's TLS
            certificate, or a string, in which case it must be a path to a CA bundle to use. Defaults to ``True``.
        :type cert_check: bool or str
        :param timeout: (optional) How many seconds to wait for the server to send data before giving up, as a float,
            or a :ref:`(connect timeout, read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        '''
        cert_check = kwargs.get('cert_check', self.cert_check)
        headers = kwargs.get('headers', self.headers)
        url = self._url + uri
        payload = bytes(j.dumps(data), 'utf-8')
        print(f"[{TESTRAIL_PREFIX}][POST] Sending POST request to {url}")
        print(f"[{TESTRAIL_PREFIX}][POST] Data: {payload}")
        r = requests.post(
            url,
            auth=(self.user, self.password),
            headers=headers,
            data=payload,
            verify=cert_check,
            timeout=self.timeout
        )
        print(f"[{TESTRAIL_PREFIX}][POST] Response status code: {r.status_code}")
        print(f"[{TESTRAIL_PREFIX}][POST] Content: {r.content}")
        if r.status_code == 429:  # Too many requests
            pause = int(r.headers.get('Retry-After', 60))
            print("Too many requests: pause for {}s".format(pause))
            time.sleep(pause)
            return self.send_post(uri, payload, **kwargs)
        else:
            try:
                response_json = r.json()
                return response_json
            except json.JSONDecodeError as e:
                print(f"[{TESTRAIL_PREFIX}][POST] JSON decoding error:", e)
                print(f"[{TESTRAIL_PREFIX}][POST] Received non-JSON response:", r.content)
                return str(r.content)

    @staticmethod
    def get_error(response):
        """ Extract error contained in a API response.
            If no error occured, return None

            :param response: response of request
            :return: String of the error
        """
        try:
            json.loads(response)
            if 'error' in response and response['error']:
                return response['error']
        except ValueError:
            if 'error' in response:
                return response
