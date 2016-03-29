__author__ = 'Aleksi'


class Chat:
    def __init__(self):
        self.handle_events = ["NICK CHANGE",
                              "MAP_CHANGE",
                              "KILL",
                              "CAPTURE",
                              "FLAG_GRAB",
                              "FLAG_RETURN",
                              "START",
                              "TEAM_JOIN",
                              "STATUS_MESSAGE",
                              # "COMMAND", # We probably wont want to show everyone what commands are ran :P
                              "BAN_LINE",
                              "LEAVE",
                              "PICKUP",
                              "CHAT",
                              "TEAMCHAT",
                              "NICK_CHANGE",
                              "SERVER_SAY",
                              "MAP_CHANGE"]
        pass

    def handle(self, event, bot, plugins):
        bot.debug("Event_Emitter is handling this.")
        temp = {"info": event, "emit_type": event["event_type"].lower(), "room": bot.name}
        bot.listeners[0](temp)
