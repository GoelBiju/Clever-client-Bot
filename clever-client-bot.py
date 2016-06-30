#!/usr/bin/env python2
# -*- coding: utf-8 -*-

""" Clever-client-Bot (A Python CleverBot Client) """

# Developed by GoelBiju (2016)
# https://github.com/GoelBiju/

# Version: 0.0.1

import requests
import time
import string
import hashlib  # To generate MD5 checksum.
from requests.compat import urlencode
from urllib import unquote

DEFAULT_HEADER = {
    'Host': 'www.cleverbot.com',
    'Proxy-Connection': 'keep-alive',
    'Origin': 'http://www.cleverbot.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ' +
                  '(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': '*/*',
    'DNT': '1',
    'Referrer': 'http://www.cleverbot.com/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6'
}

# Test the reply from the server by posting a random sample text.
# test_server = True



class CleverBot:
    """ Main instance of CleverBot. """

    def __init__(self):
        """
        Initialise the essential variables.

        NOTE: Several variables make use of unicode instead of a default string, this is simply
              to conform with most encodings whereas using a string or string conversion may result
              in encoding/decoding errors.
        """

        # To manually enable/disable any further conversations with (requests to) CleverBot.
        self.cleverbot_on = True

        # Our CleverBot HTTP session.
        self.cleverbot_session = requests.Session()
        print("Initiated CleverBot HTTP Session.")
        
        # Keep a list of the number of POST requests we make, along with the conversation
        # details which were made to it.
        self.post_log = []

        # Time variables.
        self.init_time = time.time()
        self.timeout = 20
        
        # Set CleverBot reply language.
        # NOTE: Set to English, other country codes can be specificed e.g. 'fr' (France).
        manual_language = 'en'  

        self.base_url = 'http://www.cleverbot.com/'
        self.full_url = 'http://www.cleverbot.com/webservicemin?uc=255&out=&in=' + \
                        '&bot=c&cbsid=&xai=&ns=&al=&dl=en&flag=&user=&mode=1&alt=0&reac=&t='
                        
        #self.post_suffix = 'webservicemin?uc=255'

        # Test the MD5checksum; the VText and sessionid form data is not asked for on the initial request.
        self.start_form_data = {
            'stimulus': u'',
            'cb_settings_scripting': u'no',
            'is_learning': 1,
            'incognoid': u'wsf',
            'icognocheck': u''
        }

        # WebForms code queries.
        # self.webforms_codes = {
        #     'output_code': '&out=',
        #     'input_code': '&in=',
        #     'bot_code': '&bot=c',
        #     'session_code': '&cbsid=',
        #     'cookie_code': '&xai=',
        #     'ns_code': '&ns=1',
        #     'al_code': '&al=',
        #     'dl_code': '&dl=en',
        #     'flag_code': '&flag=',
        #     'user_code': '&user=',
        #     'mode_code': '&mode=1',
        #     'alt_code': '&alt=0',
        #     'reac_code': '&reac=',
        #     'emo_code': '&emo=',
        #     'time_code': '&t='
        # }

        # Set essential variables.
        self.input = u''

        # The essential WebForms query variables.
        self.output = ''
        self.bot = 'c'
        self.conversation_id = None
        self.xai = None
        self.ns = 1
        self.al = ''
        self.dl = manual_language
        self.flag = ''
        self.user = ''
        self.mode = 1
        self.alt = 0
        self.reac = ''
        self.emo = ''
        self.t = 0  # time between each request, as an integer

        # Initiate connection.
        self.connect()

    @staticmethod
    def client_authentication(payload_data):
        """
        Authenticate our connection by generating the necessary token.
        NOTE: Thanks to the original source code from https://github.com/folz/cleverbot.py/
              to work out how the md5checksum was generated from the POST data.
        :param payload_data: str the POST form data url encoded.
        :return: str the "icognocheck" token to place back into the POST form data dict.
        
        NOTES:
        
            Test the MD5checksum:
            >>> CleverBot = CleverBot()
            >>> token = CleverBot.client_authentication(form_data)
            >>> print token
            
            NOTE: Returns: stimulus=Hi.&cb_settings_scripting=no&is_learning=1&icognocheck=&incognoid=wsf,
            NOTE: Example token: 6ecdfa2f75fca2f26d1763b85f534218
            >>> url_encoded_data = urlencode(form_data)
            >>> print url_encoded_data
            
            >>> digest_encoded = url_encoded_data[9:35]
            >>> token = hashlib.md5(digest_encoded).hexdigest()
            >>> print token
        """

        print("Payload data:", payload_data)
        # Only characters 10 to 36 should be used to produce the token; as stated by folz/cleverbot.py
        digest_encoded = payload_data[9:35]
        token = hashlib.md5(digest_encoded).hexdigest()
        print("Token:", token)
        return token

    def generate_post_url(self):
        """
        Generates the POST url for the final POST data.
        :return: The POST url generated.
        """
        pass

    def generate_form_data(self, normal_form_data):
        """
        Takes current POST form data and sets data to be sent off as url encoded.
        NOTE: All data to be sent must be placed into the normal form data before an authentication token is
              generated, otherwise a valid token will not be sent over (due to the fact that we would be working
              with two different copies of POST form data).

        :param normal_form_data: dict the form data to be url encoded with the correct parameters.
        :return: The formatted POST form data.
        """

        # Handle user's input.
        normal_form_data['stimulus'] = u'' + self.input

        # Handle the authentication token.
        authentication_token = self.client_authentication(urlencode(normal_form_data))
        print('Generating token.')
        normal_form_data['icognocheck'] = authentication_token
        
        # Handle the sessionid data entry.
        # NOTE: This is not required on the initial POST request.
        #if len(self.post_log) is not 0:
        #    normal_form_data['sessionid'] = self.conversation_id
        #    print('Set seesionid token')

        # Returns url encoded POST form data.
        normal_form_data = urlencode(normal_form_data)
        print('POST form data generated:', normal_form_data)
        return normal_form_data

    def connect(self):
        """ Establish that a connection can be made with the server. """
        
        print('Connecting to CleverBot.')
        test_server = self.cleverbot_session.request(method='GET', url=self.base_url,
                                                     headers=DEFAULT_HEADER, timeout=self.timeout)

        if test_server.status_code is requests.codes.ok:
            print('Server response:', test_server.status_code, 'With cookies:', test_server.cookies)
            print('Connection headers', test_server.headers)
            
            # if test_server:
            #    self.test_response()
            print('Ready to begin conversation.')
            
        else:
            print("Server did not respond with an 'OK' (status code %s)" % test_server.status_code)
            self.cleverbot_on = False

    # def test_response(self):
    #     """ Test the response we received from the server. """
    
    #     self.input = "Hello World!"
    #     post_url = self.base_url + self.post_suffix
    #     form_data = self.start_form_data
    #     post_data = self.generate_form_data(form_data)
    #     test_response = self.cleverbot_session.request(method="POST", url=post_url, data=post_data,
    #                                                    headers=DEFAULT_HEADER, timeout=self.timeout)
    #     if test_response.status_code is requests.codes.ok:
    #         print('CleverBot Test Response:'', unquote(test_response.headers['CBOUTPUT']))
    #         print('Testing if the reply returned was valid with conversation ID:', self.conversation_id)
    #         get_url = self.base_url + self.post_suffix + self.webforms_codes['output_code'] + \
    #                   self.webforms_codes['input_code'] + self.input + self.webforms_codes['bot_code'] + self.bot + \
    #                   self.webforms_codes['session_code'] + self.conversation_id + self.webforms_codes['cookie_code'] + \
    #                   self.xai + self.webforms_codes['ns_code'] + str(self.ns) + self.webforms_codes['al_code'] + self.al + \
    #                   self.webforms_codes['dl_code'] + self.dl + self.webforms_codes['flag_code'] + str(self.flag) + \
    #                   self.webforms_codes['user_code'] + self.user + self.webforms_codes['mode_code'] + str(self.mode) + \
    #                   self.webforms_codes['alt_code'] + str(self.alt) + self.webforms_codes['reac_code'] + str(self.reac) + \
    #                   self.webforms_codes['emo_code'] + self.emo
    #         print('Requesting GET:', get_url)
    #     else:
    #         print('The server returned no response in the server test response sequence.')
    #         self.cleverbot_on = False

    def converse(self, user_input):
        """
        Takes user's input and maintains a continuous conversation with CleverBot.
        :param user_input: str the users statement/question to query with CleverBot.
        
        NOTES:
        
            NOTE: Urllib unquoting.
            >>> text = "And%20what%20is%20your%20dog's%20name%3F"
            >>> print(unquote(text))
        """

        if self.cleverbot_on:
            print('Conversing with CleverBot.')
            print('You:', user_input)
            self.input = user_input
            form_data = self.start_form_data
            print('Generating form data.')
            post_data = self.generate_form_data(form_data)
            print('POST form data was generated.')
            #post_url = self.base_url + self.post_suffix
            print('Sending POST request.')
            post_response = self.cleverbot_session.request(method='POST', url=self.full_url, data=post_data,
                                                           headers=DEFAULT_HEADER, timeout=self.timeout)
            if post_response.status_code is requests.codes.ok:
                print('Response received successfully.')
                print('POST response headers:', post_response.headers)
                # Make sure we decode the response we received properly and return it to the user.
                self.conversation_id = post_response.headers['CBCONVID']
                self.output = post_response.headers['CBOUTPUT']
                self.post_log.append([len(self.post_log), self.input, self.output])
                print self.post_log
                return unquote(self.output)
                # self.read_response(post_response)
            else:
                print('An error may have occured in the POST request.')
                post_response.raise_for_status()
        else:
            print('Clever-client-bot is unable to reach the CleverBot server.')
            
    # TODO: Solve the whitespaces/newlines issue without compromising the output.
    @staticmethod
    def read_response(response_object):
        """
        Reads the raw response returned by the POST request.
        NOTE: This decodes the whole response taking into account any unicode encoding.

        :param response_object: requests response object.
        :return: str the response that was decoded.
        """
        content = u''
        all_bytes = []
        try:
            for byte in response_object.iter_content(decode_unicode=False):
                # byte = byte.strip()
                # print [byte]
                all_bytes.append(byte)
                #for char in byte:
                for char in range(len(all_bytes)):
                    if type(char) is not int:
                        char = char.strip()
                        if len(char) is not 0:
                            csd = ord(char)
                            individual = unichr(csd)
                            content += u'' + individual
                    
            # Urllib unquoting.
            content = unquote(content)
            return content
            
        # We really shouldn't be expecting any Unicode errors, however we shall handle for the eventuality.
        except UnicodeDecodeError:
            return None


# Debugging:
# Test CleverBot:
# cb_session = CleverBot()

# while True:
#     usr = raw_input("Enter in statement/question: ")
#     response = cb_session.converse(usr)
#     print("CleverBot response:", response)
