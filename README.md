# Deprecated: CleverBot-Example

---

### Version: 1.1.4

### NOTICE:

This was just an example of how to communicate with the CleverBot website previous to the API becoming popular.

**Please sign up for** [Cleverscript](http://www.cleverscript.com/) to use the CleverBot service on a large scale.

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
