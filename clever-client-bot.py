#!/usr/bin/env python2
# -*- coding: utf-8 -*-

""" Clever-client-Bot (A Python CleverBot Client) """

# Developed by GoelBiju (2016)
# https://github.com/GoelBiju/

# Version: 0.4

import requests
import re
import hashlib  # To generate a hash we use hashlib MD5 checksum.
import time

# TODO: Make sure we send the POST variables in the right order.
# TODO: Make sure the vText equals symbol is not encoded; maybe make the vText first then get the hash from that(?)

# TODO: Implement logging.
# import logging

from urllib import unquote
from urllib import quote_plus

DEFAULT_HEADER = {
    'Host': 'www.cleverbot.com',
    'Connection': 'keep-alive',
    'Origin': 'http://www.cleverbot.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ' +
                  '(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': '*/*',
    'DNT': '1',
    'Referer': 'http://www.cleverbot.com/',
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
                        '&bot=&cbsid=&xai=&ns=&al=&dl=&flag=&user=&mode=&alt=&reac=&emo=&sou=&xed=&t='

        # Test the MD5checksum; the "VText" and "sessionid" form data is not asked for on the initial request.
        self.start_form_data = 'stimulus=&cb_settings_language=&cb_settings_scripting=no&islearning=1' + \
                               '&incognoid=wsf&icognocheck='

        # The essential WebForms query variables.
        self.output = ''
        self.input = ''
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
        self.sou = 'website'
        self.xed = ''
        self.t = None

        # Initiate connection.
        self.connect()

    @staticmethod
    def client_authentication(payload_data):
        """
        Authenticate our connection by generating the necessary token.
        NOTE: Thanks to the original source code from https://github.com/folz/cleverbot.py/
              to work out how the md5checksum was generated from the POST data.
        :param payload_data: str the POST stimulus data.
        :return: str "icognocheck" token to place back into the POST form dictionary.
        """
        # Only characters 10 to 36 should be used to produce the token; as stated by folz/cleverbot.py
        digest_encoded = payload_data[9:35]
        post_token = hashlib.md5(digest_encoded).hexdigest()
        return post_token

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

        # Set the sou.
        post_url = post_url.replace('&sou=', '&sou=' + str(self.sou))

        print('Generated POST URL: %s' % post_url)
        return post_url

    def generate_form_data(self):
        """
        Takes current POST form data and sets data to be sent off as url encoded.
        NOTE: All data to be sent must be placed into the normal form data before an authentication token is
              generated, otherwise a valid token will not be sent over (due to the fact that we would be working
              with two different copies of POST form data).

        :return: The formatted POST form data.
        """
        # Retrieve the normal form data structure.
        normal_form_data = self.start_form_data

        # Place the initial stimulus as the user's input (URL-encoded).
        raw_stimulus = quote_plus(self.input)

        # TODO: Wee need to flip over the replies and increase the numbers.
        # Handle conversation log, "VText" is the placeholder for this.
        if len(self.post_log) is not 0:
            # Generate the reversed POST log.
            reversed_log = list(reversed(self.post_log))

            # Record each entry in the list, we start at 2 since 1 is the request we have recently inputted.
            individual_entry = 2
            for x in range(len(reversed_log)):
                raw_stimulus += '&vText%s=%s' % (str(individual_entry), reversed_log[x][1])
                individual_entry += 1
                raw_stimulus += '&vText%s=%s' % (str(individual_entry), reversed_log[x][0])
                individual_entry += 1
            print('New Stimulus with vText:', raw_stimulus)

        # Handle the sessionid data entry.
        # NOTE: This is not required on the initial POST request.
        # Disabling this allows requests to be sent without replies being in context to the previous replies.
        if len(self.post_log) is not 0:
            normal_form_data = normal_form_data.replace('&sessionid=', '&sessionid=' + self.conversation_id)

        # Set the language.
        normal_form_data = normal_form_data.replace('&cb_settings_language=', '&cb_settings_language=' + self.dl)

        # Place the stimulus generated back into the POST form data.
        normal_form_data = normal_form_data.replace('stimulus=', 'stimulus=' + raw_stimulus)

        # Handle the authentication token.
        authentication_token = self.client_authentication(normal_form_data)
        # The post token is we have generated is now the "icognocheck" in the POST data.
        normal_form_data = normal_form_data.replace('&icognocheck=', '&icognocheck=' + authentication_token)

        # Returns url encoded POST form data.
        print('POST form data generated:', normal_form_data)
        return normal_form_data

    def connect(self):
        """ Establish that a connection can be made with the server. """

        # Initialise a connection with CleverBot.
        print('Connecting to CleverBot.')
        test_server = self.cleverbot_session.request(method='GET', url=self.base_url,
                                                     headers=DEFAULT_HEADER, timeout=self.timeout)

        # If we received an "OK" (200) status code, then proceed to begin a conversation.
        if test_server.status_code is requests.codes.ok:
            print('Ready to begin conversation.')
        else:
            # Otherwise, set CleverBot to be disabled.
            print('Server did not respond with an \'OK\' (status code %s)' % test_server.status_code)
            self.cleverbot_on = False

    def converse(self, user_input):
        """
        Takes user's input and maintains a continuous conversation with CleverBot.
        :param user_input: str the users statement/question to query with CleverBot.
        """

        if self.cleverbot_on:
            print 'You:', user_input
            # URL-encode user input.
            self.input = quote_plus(user_input)

            # Generate both the form data and the POST URL.
            post_data = self.generate_form_data()
            post_url = self.generate_post_url()

            # Send the POST request.
            post_response = self.cleverbot_session.request(method='POST', url=post_url, data=post_data,
                                                           headers=DEFAULT_HEADER, timeout=self.timeout)

            # Handle the POST time.
            self.time_post = int(round(time.time() * 1000))

            if post_response.status_code is requests.codes.ok:
                # Make sure we parse/decode the response we received properly and return it to the user.
                self.conversation_id = post_response.headers['cbconvid']
                set_cookie = post_response.headers['set-cookie']
                self.xai = re.search('XAI=(.+?);', set_cookie).group(1)
                self.output = post_response.headers['cboutput']

                # Increment the response count.
                self.ns += 1

                # Add conversation to the log list.
                self.post_log.append([self.input, self.output])

                # Return the URL-encoding removed output from the server.
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

# payload = ''
# token = CleverBot.client_authentication(payload)
# print token

# The difference in requests:
"""
Website: stimulus=Are%20you%20OK%3F&vText2=Czesc.&vText3=Hi.
         &sessionid=WXDADF3BM3
Bot: stimulus=Are%252Byou%252BOK%25253F%26vText2%3DCze%25C5%259B%25C4%2587.%26vText3%3DHi.
     &sessionid=WXHD9BVD1H

With same website sessionids:
     Bot token: f18dc646e67c52c42075dbdad2067830
     Therefore, variances in sessionid does not change the outcome of the payload token.

With same stimulus data from website:
    Bot token: f18dc646e67c52c42075dbdad2067830
    We see that there is still no difference even when having the same stimulus.

With the same order:
    Order: stimulus, cb_settings_language, cb_settings_scripting, sessionid, islearning, icognoid & icognocheck
    Token: 22d993714e5dba1620050948761c513f

    With same stimulus as well:
        Token: 11af21b2970b852fe7790ce0f66e688e
        Here is a match with the same token.

    Therefore we need to have this same order and also we need to have the stimulus first.

    Mainly it is based on the stimulus.
"""


