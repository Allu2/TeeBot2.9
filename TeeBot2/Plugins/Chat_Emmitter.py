__author__ = 'Aleksi'
class Chat:

    def __init__(self):
        self.handle_events = ["CHAT","SERVER SAY"]
        self.commands = "commands.cfg"
        pass
    def handle(self, event, bot, plugins):
        bot.debug("Chat_Emitter is handling this.")
        if event["event_type"] == "CHAT":
            temp = {"player_name": event["player_name"],
                    "message": event["message"], "emit_type":"chat", "room": bot.name}
            bot.listeners[0](temp)
        else:
            server = "*** "
            temp = {"player_name": server,
                    "message": event["message"], "room": bot.name, "emit_type":"chat"}
            bot.listeners[0](temp)