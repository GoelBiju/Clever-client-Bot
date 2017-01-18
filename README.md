# Clever-client-Bot

---

### Version: 1.1.4

### NOTICE:

The developers of the CleverBot service/website work hard to provide this service for free. This should not really be used in this way as I am doing, and it is damaging their ability to work further on the CleverBot project.

Their funding comes from revenue from their website and I encourage **everyone** to use the service via the website.

If in the situation that you wll need to use a package, this package is to be used with the **bot-api** name:

					    															'clever_client_bot'

Please support their work and view their official notice for further information:

**Pleae sign up for** [Cleverscript](http://www.cleverscript.com/) if you want to  use their service on a large scale and to help support their development.


### *Overview*
Clever-client-Bot is a reboot of the original Cleverbot client developed by initially by [Rodney Folz](https://github.com/folz/) - [Cleverbot.py](http://github.com/folz/cleverbot.py).

This module has been developed as a more cut down and easy-to-use version of the original package. There is a new coding style and the methods used to communicate with the server have been re-arranged for your convenience.

### Example

The following is an example to how the module can be used:
```python
Editor:
# Import the Clever-client-Bot module.
import clever_client_bot

# Intiate a conversation with CleverBot by starting an instance
# of the CleverBot class from the module.
cleverbot = clever_client_bot.CleverBot()

# A query to send to the CleverBot server.
query = 'How are you today?'

# Send the query off and return it's response.
response = cleverbot.converse(query)

# Now you can use the response in any way you want.
print(response)

Console
>>> "Actually very good. I had a softball all-stars tournament and we won. I am so happy. We had pizza after the game by the way."  
```
