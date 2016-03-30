#!/usr/bin/env python
# -*- coding: utf-8 -*-
#       Author: Aleksi Palomäki, a.k.a Allu2 <aleksi.ajp@gmail.com>
#        Copyright: GPL3 2011
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import telnetlib
from threading import Thread
import time, logging, importlib
from math import floor
from time import strftime, gmtime
from json import dumps, load, loads
from tw_api import get_server_info
import Tees
import plugin_loader
import Events_TeeBot

class TeeBot(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        with open("config/"+name+".cfg", "r", encoding="utf-8") as config:
            cfg = load(config)
        self.banned_nicks = cfg["banned_nicks"]
        self.next_ban_id = []
        self.accesslog = cfg["accesslog"]
        self.passwd = cfg["password"]
        self.host = cfg["hostname"]
        self.port = cfg["port"]
        self.address = self.host + ":" + str(self.port)
        self.teelst = Tees.Tees()
        self.events = Events_TeeBot.Events()
        self.name = name
        logging.basicConfig()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.debug = self.pretty_debug
        self.info = self.logger.info
        self.exception = self.logger.exception
        self.plugin_loader = plugin_loader.Plugin_loader(self)
        self.listeners = [print]
        self.game = {
            "bans": {},
            "type": "",
            "round_start": 0,
            "map": "",
            "gametype": "",
            "kill_history": [[0], [0]],
            "red":{
                "score": 0,
                "players": {},
                "players_total_kills": 0,
                "history": [],
                "carrier": None
            },
            "blue": {
                "score": 0,
                "players": {},
                "players_total_kills": 0,
                "history": [],
                "carrier": None
            },
            "purple": {
                "score": 0,
                "players": {},
            },
        }

    def pretty_debug(self, string):
        try:
            pretty = loads(string)
            self.logger.debug(dumps(pretty, indent=3))
        except:
            self.logger.debug(string)

    @property
    def player_count(self):
        return len(self.teelst.get_TeeLst().keys())

    @property
    def connect(self):
        self.debug("Connecting to server..")
        self.tn = telnetlib.Telnet(self.host, self.port)
        self.debug("Telnet Object created.")
        lines = self.tn.read_until(b"Enter password:")
        self.tn.write(str(self.passwd).encode('utf-8') + b'\n')
        return self.tn

    def talk(self, msg, method):
        #self.logger.debug(msg)
        if method == "game_chat":
            self.say(msg)
        elif method == "terminal":
            pass
        else:
            pass

    def team_solver(self, team_id):
        team_id = int(team_id)
        teams = {
            0: "red",
            1: "blue",
            -1: "purple"
        }
        return teams[team_id]

    def readLine(self):
        return self.tn.read_until(b"\n")

    def writeLine(self, line):
        self.tn.write(str(line).encode('utf-8') + b"\n")

    def readLines(self, until):
        return self.tn.read_until(str(until).encode('utf-8'), 0.6)

    def echo(self, message):
        self.debug("Echoing: {}".format(message))
        self.writeLine('echo "'+self.name+': ' + message.replace('"', "'") + "\"'")

    def say(self, message):
        self.info("Saying: {}".format(message))
        self.writeLine('say "'+self.name+': ' + message.replace('"', "'") + "\"'")

    def brd(self, message):
        self.info("Broadcating: {}".format(message))
        self.writeLine('broadcast "' + message.replace('"', "'") + "\"'")

    def killSpree(self, id):
        tee = self.get_Tee(id)
        spree = tee.get_spree()
        if (spree % 5) == 0 and spree != 0:
            msg = tee.get_nick().decode('utf-8') + " is on a killing spree with " + str(tee.get_spree()) + " kills!"
            self.brd(msg)
            pass
    def Multikill(self, id):
        tee = self.get_Tee(id)
        multikill = tee.get_multikill()
        if multikill>=2:
            if multikill == 2:
                self.brd(tee.get_nick().decode('utf-8') + " DOUBLEKILL!")
                pass
            if multikill == 3:
                self.brd(tee.get_nick().decode('utf-8') + " TRIPLEKILL!")
                pass
            if multikill == 4:
                self.brd(tee.get_nick().decode('utf-8') + " QUODRAKILL!!")
                pass
            if multikill == 5:
                self.brd(tee.get_nick().decode('utf-8') + " PENTAKILL!")
                pass
            if multikill >=6:
                self.brd(tee.get_nick().decode('utf-8') + " IS A BADASS!")
                self.writeLine("pause")
                self.say("Alright stop, everybody stop!")
                time.sleep(3)
                self.say("Someone just killed over 5 people in a multikill..")
                time.sleep(3)
                self.say("That was damn AMAZING!")
                time.sleep(3)
                self.say("Damn.. Ok guys, continue, just had to take a moment to point out this epic achievement.")
                self.writeLine("pause")
            else:
                pass
        else:
            pass
    def shutdown(self, victim_tee, killer_tee, spree):
        self.brd(
            "{0}'s {2} kill spree was shutdown by {1}!".format(victim_tee.get_nick(),
                                                                         killer_tee.get_nick(), str(spree)))

    def get_Teelista(self):
        return self.teelst.get_TeeLst()

    def get_Tee(self, id):
        return self.teelst.get_Tee(int(id))

    def updTeeList(self, event):

        # try:
        # self.debug(result.groups(), "DEBUG")
        # if result.groups()[3] in banned_nicks:
        #         self.writeLine("kick {0}".format(result.groups()[0]))
        #
        # except AttributeError as e:
        #     self.debug("Error: {0}".format(e), "CRITICAL")
        try:
            tee = self.teelst.get_Tee(event["player_id"])
            if tee.get_nick() != event["player_name"] or tee.get_ip() == 0:
                old_ip = tee.get_ip()
                tee.set_nick(event["player_name"])
                tee.set_score(event["score"])
                tee.set_ip(event["ip"])
                tee.set_port(event["port"])
                tee.attributes["isAdmin"] = event["isAdmin"]
                if old_ip != tee.get_ip():
                    with open(self.accesslog, "a", encoding="utf-8") as accesslogi:
                        time1 = time.strftime("%c", time.localtime())
                        accesslogi.write("[{}] ".format(time1) + "{} joined the server ({})".format(tee.get_nick(),
                                                                                                    tee.get_ip()) + "\n")
                else:
                    pass
            if tee.get_score() != event["score"]:
                tee.set_score(event["score"])
        except AttributeError as e:
            self.exception(repr(e))
        except KeyError as e:
            self.exception(repr(e))
            self.debug("Didn't find Tee: {} in player lists, adding it now:".format(event["player_name"]))
            with open(self.accesslog, "a", encoding="utf-8") as accesslogi:
                nick = event["player_name"]
                ip = event["ip"]
                time1 = time.strftime("%c", time.localtime())
                accesslogi.write(
                    "[{}] ".format(time1) + "{} joined the server ({})".format(nick, ip) + "\n")
            self.teelst.add_Tee(event["player_id"], event["player_name"], event["ip"], event["port"],
                                event["score"], event["isAdmin"], 0)  # id, name, ip, port, score
        return self.teelst.get_TeeLst()

    def get_Leaves(self, ide):
        nick = self.teelst.get_Tee(ide).get_nick()
        self.teelst.rm_Tee(ide)
        return nick

    def get_Chat(self, line):
        return self.events.conversation(line)

    def ban(self, player_id):
        self.writeLine("ban {} 30 Banned by {} for being naughty!".format(player_id, self.name))

    def update_team_scores(self):
        redteam = self.game["red"]["players"]
        blueteam = self.game["blue"]["players"]
        red_total = 0
        blue_total = 0
        for tee in redteam:
            red_total = red_total+int(redteam[tee].get_score())
        for tee in blueteam:
            blue_total = blue_total+int(blueteam[tee].get_score())
        if red_total != self.game["kill_history"][0][-1] or blue_total != self.game["kill_history"][1][-1]:
            self.game["kill_history"][0].append(red_total)
            self.game["kill_history"][1].append(blue_total)
            self.game["red"]["players_total_kills"] = red_total
            self.game["blue"]["players_total_kills"] = blue_total

    def handle_event(self, lst):
        if lst["event_type"] == "RELOAD ORDER":
            self.info("Reloaded plugins")
            importlib.reload(plugin_loader)

    def get_Event(self, line):

        lst = self.events.game_events(line)
        lst["line"] = line
        self.debug("We got event:\n"+dumps(lst))
        if lst is not None:
            self.handle_event(lst)
            self.plugin_loader.event_handler(lst)
        return lst

    def force_event(self):
        self.writeLine("status")

    def run(self):
        self.tn  = self.connect
        info = get_server_info()
        self.game["map"] = info["map"]
        self.game["gametype"] = info["gametype"]
        #self.writeLine("reload")
        #self.writeLine("restart")
        self.writeLine("status")
        self.say("Connected.")
        ticks = 0.1
        line = ""
        while True:
            time.sleep(ticks)
            try:
                try:
                    new_line = self.readLine().decode()
                    if new_line != line:
                        line = new_line
                    else:
                        line = "\n"
                    if line != "\n":
                        self.debug("We got line: {}".format(line))
                except Exception as e:
                    self.exception(e)
                    exit()
                if "[server]:" in line.split(" ")[0] and ("player" in line.split(" ")[1] and "has" in line.split(" ")[2]):
                    self.info("I am the culprit")
                    self.writeLine("status")
                if line == "\n":
                    pass
                else:
                    event = self.get_Event(line)
            except (KeyError, TypeError, AttributeError, NameError, UnicodeDecodeError) as e:
                self.exception(e)
                self.writeLine("status")




