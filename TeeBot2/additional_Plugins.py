__author__ = 'Aleksi'
class additional_Plugins():
    def __init__(self, plugin_loader):
        self.register = plugin_loader.register

        from Plugins import Chat_Emmitter, Event_Emmitter
        self.register(Chat_Emmitter.Chat())
        self.register(Event_Emmitter.Event())