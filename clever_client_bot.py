# -*- coding: utf-8 -*-

""" Clever-client-Bot (A Python simple CleverBot Client).
    _______                               ___            __        ____        __
  / ____/ /__ _   _____  _____      _____/ (_)__  ____  / /_      / __ )____  / /_
 / /   / / _ \ | / / _ \/ ___/_____/ ___/ / / _ \/ __ \/ __/_____/ __  / __ \/ __/
/ /___/ /  __/ |/ /  __/ /  /_____/ /__/ / /  __/ / / / /_/_____/ /_/ / /_/ / /_
\____/_/\___/|___/\___/_/         \___/_/_/\___/_/ /_/\__/     /_____/\____/\__/

"""
# Developed by GoelBiju (2016) - https://github.com/GoelBiju/

import sys
import logging
import requests
import time
import hashlib  # We use hashlib to generate the MD5 checksum to be used in request payloads.
import re

# Backwards compatibility with Python 3+ and Python 2.
if sys.version >= '3':
    # Python 3+.
    from urllib.parse import unquote
    from urllib.parse import quote_plus
    input_type = input
else:
    # Python < 3.
    from urllib import unquote
    from urllib import quote_plus
    input_type = raw_input

# TODO: Add ChangeLog and include all changes from the previous version.
# TODO: Edit access to the debugging options.
# TODO: The quoting on the our requests is still not fully correct.

# NEW: Added fallback to Python 3+.
# NEW: Small tweaks to avoid string formatting via percentage symbol everywhere, using .format as well.
# NEW: The unicode object not being encoded before hashing error has been resolved in Python 3+. We know encode the
#      digest to utf-8 just before hashing and producing the hex-digest.
# NEW: Session id is now not sent on the first post request.
# NEW: The row id information is sent along with the first three characters of the 'xai' web-form field in the
#      in the post url.
# EDIT: Removed testing payload information and added debugging notes to the NOTES file.

__version__ = '1.1.4'

# NOTE: Debugging only works when the script is used within a console and not as an import.
debugging = False  # ONLY set debugging here.
debugging_file = 'cleverbot_debug.log'

# Modifying this variable here will not change if the application
# will work in the console or not.
console = False

log = logging.getLogger(__name__)

BOT_API_TAG = 'clever_client_bot'

DEFAULT_HEADER = {
    'Host': 'www.cleverbot.com',
    'Connection': 'keep-alive',
    'Origin': 'http://www.cleverbot.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ' +
                  '(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': '*/*',
    'Referer': 'http://www.cleverbot.com/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6'
}


class CleverBot:
    """ Main instance of the CleverBot client. """

    def __init__(self):
        """
        Initialise the essential variables.

        NOTE: Several variables make use of unicode instead of a default string, this is simply
              to conform with most encodings whereas using a string or string conversion may
              result in encoding/decoding errors.
        """
        # To manually enable/disable any further conversations with (requests to) CleverBot.
        self.cleverbot_on = True

        # Create a new requests session to act as the CleverBot conversation.
        self.cleverbot_session = requests.Session()

        if debugging and console:
            log.info('--> Initiated CleverBot Session.')

        # Keep a list of the number of POST requests we make, along with the conversation
        # details which were made to it.
        self.post_log = []

        # Time variables.
        self.time_post = 0
        self.timeout = 20

        # Set the version of the webservice(?)
        self.bot_api = BOT_API_TAG
        webservice_version = '3210'

        # Set CleverBot reply language.
        # NOTE: Set to English (en), other country codes can be specified e.g. 'fr' (France).
        #       Whether this works properly, I am unsure.
        manual_language = 'en'

        self.base_url = 'http://www.cleverbot.com/'
        self.full_url = 'http://www.cleverbot.com/webservicemin?uc={0}&botapi={1}&out=&in=&bot=&cbsid=&xai=&ns=&al=' \
                        '&dl=&flag=&user=&mode=&alt=&reac=&emo=&sou=&xed=&t='.format(webservice_version, self.bot_api)

        # TODO: '&sessionid' is missing from the form data.
        # Test the MD5checksum; the 'VText' and 'sessionid form data is not asked for on the initial request.
        self.start_form_data = 'stimulus=&cb_settings_language=&cb_settings_scripting=no&sessionid=&islearning=1' + \
                               '&incognoid=wsf&icognocheck='

        # The essential WebForms query variables:
        # The specifics of what these web-form queries may contain is found on line no. 22727 in
        # the 'conversation-social-min.js' file:
        #   - out: encodeURIComponent(c),
        #   - "in": encodeURIComponent(b),
        #   - bot: (e == "chimbot") ? "h" : e.substring(0, 1),
        #   - cbsid: cleverbot.sessionid ? cleverbot.sessionid : "MYSESSIONID",
        #   - xai: cleverbot.getCookieValue("XAI") + (cleverbot.rowidandref ? ("," + cleverbot.rowidandref) : ""),
        #   - ns: parseInt(cleverbot.numsessioninputs) + 1,
        #   - al: cleverbot.asrlanguage,
        #   - dl: cleverbot.detectedlanguage,
        #   - flag: a,
        #   - user: (cleverbot.hassocial && socialAction && socialAction.getUserName ? socialAction.getUserName() : ""),
        #   - mode: cleverbot.mode,
        #   - alt: cleverbot.numalternates > 0 ? cleverbot.usingalternate : 0,
        #   - reac: cleverbot.reaction,
        #   - emo: cleverbot.emotion,
        #   - sou: cleverbot.source,
        #   - xed: cleverbot.extradata

        self.output = ''
        self.input = ''
        self.bot = 'c'
        self.conversation_id = None
        # TODO: Xai web-form now sends more information as opposed to the three letter field;
        #       e.g. previously: 'WXC', currently: 'WXC,127450838,L020843766'
        #       The extra parameter is from the response body in the first request.
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

        # Extra information.
        self.row_id = None

        # Initiate connection.
        self.connect()

    @staticmethod
    def client_authentication(payload_data):
        """
        Authenticate our connection by generating the necessary token.
        NOTE: Thanks to the original source code from https://github.com/folz/cleverbot.py/
              to work out how the md5checksum was generated from the POST data.
              The particular way to encode the data to md5 can be found in the 'conversation-social-min.js'
              JavaScript file on their website.

        :param payload_data: str the POST stimulus data.
        :return: str "icognocheck" token to place back into the POST form dictionary.
        """
        # Only characters 10 to 36 should be used to produce the token; as stated by folz/cleverbot.py
        digest_encoded = payload_data[9:35].encode('utf-8')  # Referenced on line no. 22826 in JavaScript.
        post_token = hashlib.md5(digest_encoded).hexdigest()
        if debugging and console:
            log.info('Raw authentication sliced-text: %s' % digest_encoded)
            log.info('POST token generated: %s' % post_token)
        return post_token

    def generate_post_url(self):
        """
        Generates the POST url for the next POST query using the default POST url and returns
        the new url.

        NOTE: The only WebForms queries that change so far are "out", "in", "ns" & "t".
              The constants "cbsid", "dl", "bot", "xai", "mode", "alt" and "sou" still need to be placed in.
        :return: str the POST url generated.
        """
        # Retrieve full URL for the POST request to alter to our requirements.
        post_url = self.full_url

        # Set the input from the user.
        post_url = post_url.replace('&in=', '&in=' + str(self.input))

        # Set the output reply from CleverBot in the last POST request.
        if len(self.output) is not 0:
            post_url = post_url.replace('&out=', '&out=' + str(self.output))

        # Set the number of requests we have made to CleverBot.
        if self.ns is not 0:
            post_url = post_url.replace('&ns=', '&ns=' + str(self.ns))

        # Set the time difference between the last POST request sent and this one being prepared.
        if self.time_post is not 0:
            # Calculate the new time difference and place it into the post URL.
            self.t = int(round(time.time()*1000)) - self.time_post
            post_url = post_url.replace('&t=', '&t=' + str(self.t))

        # Set the language to use in the POST url.
        post_url = post_url.replace('&dl=', '&dl=' + str(self.dl))

        # Set the conversation ID.
        if self.conversation_id is not None:
            post_url = post_url.replace('&cbsid=', '&cbsid=' + str(self.conversation_id))

        # Set the conversation code.
        if self.row_id is not None:
            post_url = post_url.replace('&xai=', '&xai=' + str(self.xai) + ',' + self.row_id)
        else:
            post_url = post_url.replace('&xai=', '&xai=' + str(self.xai))

        # Set the bot.
        post_url = post_url.replace('&bot=', '&bot=' + str(self.bot))

        # Set the mode.
        post_url = post_url.replace('&mode=', '&mode=' + str(self.mode))

        # Set the alt.
        post_url = post_url.replace('&alt=', '&alt=' + str(self.alt))

        # Set the sou.
        post_url = post_url.replace('&sou=', '&sou=' + str(self.sou))

        if debugging and console:
            log.info('Generated Post URL: ' + post_url)

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

        # TODO: We only need to send back what we receive from the parsed body, we don't have to keep a record of this.
        #       Try to implement a way in which we can just reverse this, however by using the response body.
        # Handle conversation log, 'VText' is the placeholder for this.
        if len(self.post_log) is not 0:
            # Generate the reversed POST log.
            reversed_log = list(reversed(self.post_log))

            # Record each entry in the list, we start at 2 since 1 is the request we have recently inputted.
            individual_entry = 2
            for x in range(len(reversed_log)):
                raw_stimulus += '&vText{}={}'.format(str(individual_entry), reversed_log[x][1])
                individual_entry += 1
                raw_stimulus += '&vText{}={}'.format(str(individual_entry), reversed_log[x][0])
                individual_entry += 1

        # TODO: This is not being sent on any of the original post requests; this should be sent after the first
        #       and all future requests (we should not have the '&sessionid' in the first request).
        # Handle the 'sessionid' data entry.
        # NOTE: This is not required on the initial POST request. Disabling this allows requests to be sent without
        # replies being in context to the previous inputs, this may give you random outputs from the server.
        if len(self.post_log) is not 0:
            normal_form_data = normal_form_data.replace('&sessionid=', '&sessionid=' + self.conversation_id)
        else:
            normal_form_data = normal_form_data.replace('&sessionid=', '')

        # Set the language.
        normal_form_data = normal_form_data.replace('&cb_settings_language=', '&cb_settings_language=' + self.dl)

        # Place the stimulus generated back into the POST form data.
        normal_form_data = normal_form_data.replace('stimulus=', 'stimulus=' + raw_stimulus)

        # Handle the authentication token.
        authentication_token = self.client_authentication(normal_form_data)
        # The post token is we have generated is now the 'icognocheck' in the POST data.
        normal_form_data = normal_form_data.replace('&icognocheck=', '&icognocheck=' + authentication_token)

        if debugging and console:
            log.info('Generated Form Data: ' + normal_form_data)

        # Returns url encoded POST form data.
        return normal_form_data

    # TODO: Develop a method to parse the response body for the output, conversation id,
    #       a set of alphanumeric characters which is to be sent with the 'xai' field - we can also confirm the
    #       'xai' field with the one received in the header response cookie and the one received in the body.
    @staticmethod
    def parse_response_body(response_content):
        """
        A method to parse the response body sent from each CleverBot POST request.

        :param response_content: bytes the response content from the requests response object.
        :return: response_body dict{'text_response', 'conversation_id', 'row_id', 'raw_response'} or None
                 if we could not decode the body.
        """
        # TODO: Added bytes decoding in order to support parsing the response in Python 3+.
        response_data = response_content.decode(encoding='utf-8')
        response_list = response_data.split('\r')

        response_body = {
            'latest_reply': response_list[0],
            'conversation_id': response_list[1],
            'row_id': response_list[2],
            'latest_posts': response_list[3:10],
        }

        return response_body

    def connect(self):
        """ Establish that a connection can be made with the server. """
        # Initialise a connection with CleverBot.
        if debugging and console:
            log.info('--> Connecting to CleverBot.')
        test_server = self.cleverbot_session.request(method='GET', url=self.base_url, headers=DEFAULT_HEADER,
                                                     timeout=self.timeout)

        # If we received an 'OK' (200) status code, then proceed to begin a conversation.
        if test_server.status_code is requests.codes.ok:
            if debugging and console:
                log.info('*Ready to begin conversation.*')
            return
        else:
            # Otherwise, set CleverBot to be disabled.
            if debugging and console:
                log.error('*Server did not respond with an \'OK\' (status code %s)*' % test_server.status_code)
            self.cleverbot_on = False

    # TODO: The data being sent should really be cleared out, rather than piling it.
    def converse(self, user_input):
        """
        Takes user's input and maintains a continuous conversation with CleverBot.
        :param user_input: str the user's statement/question to query with CleverBot.
        """
        if self.cleverbot_on:
            # Print user's input and log it if necessary.
            log_user_input = 'You: ' + user_input

            if debugging and console:
                print(log_user_input)
                log.info(log_user_input)

            # URL-encode user input.
            self.input = quote_plus(user_input)

            # Increment the number of posts; the number we will
            # end up sending after the request has been sent.
            self.ns += 1

            # Generate both the form data and the POST URL.
            post_data = self.generate_form_data()
            post_url = self.generate_post_url()

            # print('POST Data:', post_data)
            # print('POST URL:', post_url)

            # Send the POST request.
            post_response = self.cleverbot_session.request(method='POST', url=post_url, data=post_data,
                                                           headers=DEFAULT_HEADER, timeout=self.timeout)

            # Handle the POST time.
            self.time_post = int(round(time.time() * 1000))

            if post_response.status_code is requests.codes.ok:
                # Make sure we parse/decode the response we received properly and return it to the user:

                # Retrieve the current conversation id from the cookie header.
                self.conversation_id = post_response.headers['CBCONVID']

                # Retrieve and search for the 'xai' field data from the response headers cookie.
                set_cookie = post_response.headers['set-cookie']
                self.xai = re.search('XAI=(.+?);', set_cookie).group(1)

                # Retrieve the output from the cookie header.
                self.output = post_response.headers['CBOUTPUT']

                # Add conversation to the log list.
                self.post_log.append([self.input, self.output])

                # Return the URL-encoding removed output from the server (add to the log if necessary).
                response = unquote(self.output)
                if debugging and console:
                    log.info(response)

                response = self.parse_response_body(post_response.content)

                # Set the row id for the next response from this post response's body.
                self.row_id = response['row_id']

                # TODO: We could maybe check responses from both the response body and the header 'CBOUTPUT'
                #       (which is saved into self.output) cookie.
                # if self.output == response['latest_reply']:
                #     return response['latest_reply']
                # else:
                #     if debugging and console:
                #         log.warning('The output received in the header cookie does not '
                #                     'match the output in the response body.')

                return response['latest_reply']
            else:
                if debugging and console:
                    log.warning('An error may have occured in the POST request.')
                    log.error(post_response.headers)

                # Raise a requests status code error.
                post_response.raise_for_status()
        else:
            if debugging and console:
                log.error('Clever-client-Bot is unable to reach the CleverBot server.')

            print('We cannot reach the CleverBot server at the moment.')


def main():
    global console

    # Initialise CleverBot instance.
    cb_session = CleverBot()

    # Turn on console mode to allow debugging information to be saved to the debug log,
    # otherwise the instance will function as an import ONLY.
    console = True

    # Start the loop to ask the user for his/her statement/question to send to CleverBot and print the response
    # received from the server.
    while True:
        user_input = input_type('\nEnter in statement/question: ')
        response = cb_session.converse(user_input)
        print('CleverBot response: %s' % response)

if __name__ == '__main__':
    if debugging:
        formatter = '%(asctime)s : %(levelname)s : %(filename)s : %(lineno)d : %(funcName)s() : %(name)s : %(message)s'
        logging.basicConfig(filename=debugging_file, level=logging.DEBUG, format=formatter)
        log.info('Starting Clever-client-Bot version: %s' % __version__)
    else:
        log.addHandler(logging.NullHandler())
    main()
