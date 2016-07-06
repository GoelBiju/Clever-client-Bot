#!/usr/bin/env python2
# -*- coding: utf-8 -*-

""" Clever-client-Bot (A Python CleverBot Client) """

# Developed by GoelBiju (2016)
# https://github.com/GoelBiju/

# Version: 0.0.3

import requests
import re
import hashlib  # To generate a hash we use hashlib MD5 checksum.
import time
import string

# TODO: Implement logging.
# import logging

from requests.compat import urlencode
from urllib import unquote
from urllib import quote_plus

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
              to conform with most encodings whereas using a string or string conversion may 
              result in encoding/decoding errors.
        """

        # To manually enable/disable any further conversations with (requests to) CleverBot.
        self.cleverbot_on = True

        # Our CleverBot HTTP session.
        self.cleverbot_session = requests.Session()
        print('Initiated CleverBot HTTP Session.')
        
        # Keep a list of the number of POST requests we make, along with the conversation
        # details which were made to it.
        self.post_log = []

        # Time variables.
        self.time_post = 0
        self.timeout = 20
        
        # Set CleverBot reply language.
        # NOTE: Set to English, other country codes can be specificed e.g. 'fr' (France).
        manual_language = 'en'  

        self.base_url = 'http://www.cleverbot.com/'
        self.full_url = 'http://www.cleverbot.com/webservicemin?uc=255&out=&in=' + \
                        '&bot=&cbsid=&xai=&ns=&al=&dl=&flag=&user=&mode=&alt=&reac=&t='

        # Test the MD5checksum; the "VText" and "sessionid" form data is not asked for on the initial request.
        self.start_form_data = {
            'stimulus': '',
            'cb_settings_scripting': 'no',
            'islearning': '1',
            'incognoid': 'wsf',
            'icognocheck': ''
        }


        # The essential WebForms query variables.
        self.input = ''
        self.output = ''
        self.bot = 'c'
        self.conversation_id = None
        self.xai = ''
        self.ns = 0
        self.al = ''
        self.dl = manual_language
        self.flag = ''
        self.user = ''
        self.mode = '1'
        self.alt = '0'
        self.reac = ''
        self.emo = ''
        self.t = None

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

        # print('Payload data:', payload_data)
        # Only characters 10 to 36 should be used to produce the token; as stated by folz/cleverbot.py
        digest_encoded = payload_data[9:35]
        token = hashlib.md5(digest_encoded).hexdigest()
        # print('Token:', token)
        return token

    def generate_post_url(self):
        """
        Generates the POST url for the next POST query using the default POST url and returns 
        the new url.
        
        NOTE: The only WebForms queries that change so far are "out", "in", "ns" & "t".
              The constants "cbsid", "dl", "bot", "xai", "mode" and "alt" still needs to be placed in.
        :return: str the POST url generated.
        """
        
        # Retrieve full URL for the POST request to alter to our requirements.
        post_url = self.full_url
        
        # Set the input from the user.
        post_url = post_url.replace('&in=', '&in=' + str(self.input))
        
        # Set the output reply from CleverBot in the last POST request.
        if len(self.output) is not 0:
            post_url = post_url.replace('&out=', '&out=' + str(self.output))
        
        # TODO: Make sure this number is accurate.
        # Set the number of requests we have made to CleverBot.
        if self.ns is not 0:
            post_url = post_url.replace('&ns=', '&ns=' + str(self.ns))
            
        # TODO: Implement the time difference between POST requests.
        # Set the time difference between the last POST request sent and this one being prepared.
        if self.time_post is not 0:
            
            self.t = int(round(time.time() * 1000)) - self.time_post
            # print "Posted time and current time difference:", self.t
            post_url = post_url.replace('&t=', '&t=' + str(self.t))
        
        # Set the language to use in the POST url.
        post_url = post_url.replace('&dl=', '&dl=' + str(self.dl))
        
        # Set the conversation ID.
        if self.conversation_id is not None:
            post_url = post_url.replace('&cbsid=', '&cbsid=' + str(self.conversation_id))
            
        # Set the conversation code.
        post_url = post_url.replace('&xai=', '&xai=' + str(self.xai))
        
        # Set the bot.
        post_url = post_url.replace('&bot=', '&bot=' + str(self.bot))
        
        # Set the mode.
        post_url = post_url.replace('&mode=', '&mode=' + str(self.mode))
        
        # Set the alt.
        post_url = post_url.replace('&alt=', '&alt=' + str(self.alt))
        
        # print('Generated POST URL:', post_url) 
        return post_url
        

    def generate_form_data(self):
        """
        Takes current POST form data and sets data to be sent off as url encoded.
        NOTE: All data to be sent must be placed into the normal form data before an authentication token is
              generated, otherwise a valid token will not be sent over (due to the fact that we would be working
              with two different copies of POST form data).

        :return: The formatted POST form data.
        """
    
        # Retreive the normal form data structure.
        normal_form_data = self.start_form_data

        # Handle user's input.
        normal_form_data['stimulus'] = quote_plus(self.input)
        
        # TODO: Wee need to flip over the replies and increase the numbers.
        # Handle conversation log, "VText" is the placeholder for this.
        if len(self.post_log) is not 0:
            # print('POST LOG before vText:', self.post_log)
            
            # Generate the reversed POST log.
            reversed_log = list(reversed(self.post_log))

            # Record each entry in the list, we start at 2 since 1 is the request 
            # we have recently inputted.
            individual_entry = 2
            for x in range(len(reversed_log)):
                normal_form_data['stimulus'] = normal_form_data['stimulus'] + '&vText' + str(individual_entry) + '=' + reversed_log[x][1]
                individual_entry = individual_entry + 1
                normal_form_data['stimulus'] = normal_form_data['stimulus'] + '&vText' + str(individual_entry) + '=' + reversed_log[x][0]
                individual_entry = individual_entry + 1
            
            print('New Stimulus with vText:', normal_form_data['stimulus'])
        
        # Handle the sessionid data entry.
        # NOTE: This is not required on the initial POST request.
        # Disabling this allows requests to be sent without replies being in context to the previous replies.
        if len(self.post_log) is not 0:
             normal_form_data['sessionid'] = self.conversation_id
            
        # Handle language settings.
        if len(self.post_log) is not 0:
            normal_form_data['cb_settings_language'] = self.dl
            
        # Handle the authentication token.
        authentication_token = self.client_authentication(urlencode(normal_form_data))
        # print('Generating token.')
        normal_form_data['icognocheck'] = authentication_token

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
            # print('Server response:', test_server.status_code, 'With cookies:', test_server.cookies)
            # print('Connection headers', test_server.headers)
            
            # if test_server:
            #    self.test_response()
            
            print('Ready to begin conversation.')
            
        else:
            print('Server did not respond with an \'OK\' (status code %s)' % test_server.status_code)
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
            >>> text = "And%20what%20is%20your%20dog's%20name"
            >>> print(unquote(text))
        """

        if self.cleverbot_on:
            
            # print('Conversing with CleverBot.')
            print 'You:', user_input
            
            self.input = quote_plus(user_input)
            
            # print('Generating form data.')
            post_data = self.generate_form_data()
            # print('POST form data was generated.')
            post_url = self.generate_post_url()
            
            # print('Sending POST request.')
            post_response = self.cleverbot_session.request(method='POST', url=post_url, data=post_data,
                                                           headers=DEFAULT_HEADER, timeout=self.timeout)
                                       
            # Handle the POST time.                    
            self.time_post = int(round(time.time() * 1000))
            # print "Time posted at:", self.time_post
                                                           
            if post_response.status_code is requests.codes.ok:
                # print('Response received successfully.')
                
                # print('POST response headers:', post_response.headers)
                
                # Make sure we parse/decode the response we received properly and return it to the user.
                self.conversation_id = post_response.headers['cbconvid']
                set_cookie = post_response.headers['set-cookie']
                self.xai = re.search('XAI=(.+?);', set_cookie).group(1)
                self.output = post_response.headers['cboutput']
                
                # Increment the response count.
                self.ns += 1
                
                # Add conversation to the log list.
                self.post_log.append([self.input, self.output])
            
                return unquote(self.output)
            else:
                print('An error may have occured in the POST request.')
                post_response.raise_for_status()
        else:
            print('Clever-client-bot is unable to reach the CleverBot server.')
            

# Debugging:
# Test CleverBot:
cb_session = CleverBot()

while True:
     usr = raw_input('Enter in statement/question: ')
     response = cb_session.converse(usr)
     print 'CleverBot response:', response
