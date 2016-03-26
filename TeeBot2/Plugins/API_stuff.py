__author__ = 'Aleksi'
import time
from math import floor
from time import strftime, gmtime


class API_stuff:
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
                              "COMMAND",
                              "BAN_LINE",
                              "LEAVE"]
        self.commands = "commands.cfg"
        pass

    def handle(self, event, bot, plugins):
        bot.debug("API_stuff is handling this.")

        if event["event_type"] == "NICK CHANGE":
            bot.writeLine("status")

        if event["event_type"] == "MAP_CHANGE":
            bot.game["map"] = event["map_name"]
            bot.game["round_start"] = time.time()
            bot.game["red"]["score"] = 0
            bot.game["blue"]["score"] = 0

        if event["event_type"] == "KILL" and event["killer_id"] != event["victim_id"]:
            print("Hellow")
            tee = bot.get_Tee(event["killer_id"])
            team = tee.attributes["team"]
            if (bot.game["red"]["carrier"] is not None) or (bot.game["blue"]["carrier"] is not None):
                red_carry = bot.game["red"]["carrier"]
                blue_carry = bot.game["blue"]["carrier"]
                if red_carry is not None and event["victim_id"] == red_carry.get_idnum():
                    tee = bot.get_Tee(event["killer_id"])
                    tee.set_score(tee.get_score() + 1)
                    bot.game["blue"]["carrier"] = None
                if blue_carry is not None and event["victim_id"] == blue_carry.get_idnum():
                    tee = bot.get_Tee(event["killer_id"])
                    tee.set_score(tee.get_score() + 1)
                    bot.game["blue"]["carrier"] = None
            if team is not None:
                bot.update_team_scores()

        if event["event_type"] == "CAPTURE":
            tee = bot.get_Tee(event["player_id"])
            team = tee.attributes["team"]
            if team is not None:
                if team == "red":
                    bot.game["red"]["carrier"] = None
                    bot.game["red"]["score"] = bot.game["red"]["score"] + 100
                else:
                    bot.game["blue"]["carrier"] = None
                    bot.game["blue"]["score"] = bot.game["blue"]["score"] + 100
            tee.set_score(tee.get_score() + 5)
            bot.update_team_scores()

        if event["event_type"] == "FLAG_GRAB":
            tee = bot.get_Tee(event["player_id"])
            team = tee.attributes["team"]
            if team is not None:
                if team == "red":
                    bot.game["red"]["carrier"] = tee
                    bot.game["red"]["score"] = bot.game["red"]["score"] + 1
                else:
                    bot.game["blue"]["carrier"] = tee
                    bot.game["blue"]["score"] = bot.game["blue"]["score"] + 1
            tee.set_score(tee.get_score() + 1)
            bot.update_team_scores()

        if event["event_type"] == "FLAG_RETURN":
            tee = bot.get_Tee(event["player_id"])
            tee.set_score(tee.get_score() + 1)
            bot.update_team_scores()

        if event["event_type"] == "START":  # Reset scores on new round.
            bot.game["round_start"] = time.time()
            bot.game["gametype"] = event["gametype"]
            tees = bot.get_Teelista()
            for tee in tees:
                tees[tee].set_score(0)
            bot.game["kill_history"] = [[0], [0]]

        if event["event_type"] == "TEAM_JOIN":
            if event["new_team"] is not None:
                tee = bot.get_Tee(event["player_id"])
                team = bot.team_solver(event["new_team"])
                tee.attributes["team"] = team
                if team == "red":
                    del bot.game["blue"]["players"][tee.get_idnum()]
                    bot.game["red"]["players"][tee.get_idnum()] = tee

                if team == "blue":
                    del bot.game["red"]["players"][tee.get_idnum()]
                    bot.game["blue"]["players"][tee.get_idnum()] = tee

            else:
                tee = bot.teelst.add_Tee(event["player_id"], event["player_name"], 0, 0,
                                         0, False, 0)
                team = bot.team_solver(event["old_team"])
                if team == "red":
                    bot.game["red"]["players"][tee.get_idnum()] = tee
                if team == "blue":
                    bot.game["blue"]["players"][tee.get_idnum()] = tee
                tee.attributes["team"] = team

        if event["event_type"] == "STATUS_MESSAGE":
            nick = event["player_name"]
            ide = event["player_id"]
            if nick in bot.banned_nicks:
                bot.writeLine("kick {0}".format(ide))
            lista = bot.updTeeList(event)

        if event["event_type"] == "COMMAND":
            if event["command"] == "ban":
                try:
                    if len(bot.next_ban_id) == 0:
                        ban_id = str(int(sorted(bot.game["bans"].keys())[-1]) + 1)
                    else:
                        ban_id = str(bot.next_ban_id.pop())
                except Exception as e:
                    ban_id = str(0)
                tee = bot.get_Tee(event["params"][0])
                bot.game["bans"][ban_id] = {
                    "player_name": tee.get_nick(),
                }
                bot.writeLine("bans")
            if event["command"] == "unban":
                param = event["params"][0]
                try:
                    if "." in param:
                        for ban_id in bot.game["bans"]:
                            if param == bot.game["bans"][ban_id]["ban_ip"]:
                                ban = bot.game["bans"].pop(ban_id, None)

                                bot.debug("Removed key: {} from bans".format(ban))
                    else:
                        ban = bot.game["bans"].pop(ban_id, None)
                        bot.debug("Removed key: {} from bans".format(ban))
                except Exception as e:
                    bot.debug("Exception occurred while handling unban command with params:\n {}".format(event))
                    bot.exception(e)

        if event["event_type"] == "BAN_LINE":
            ban_id = event["ban_id"]
            if ban_id not in bot.game["bans"]:
                bot.game["bans"][ban_id] = {}
                bot.game["bans"][ban_id]["player_name"] = "NULL"
            bot.game["bans"][ban_id]["ban_ip"] = event["ban_ip"]
            bot.game["bans"][ban_id]["ban_time"] = event["ban_time"]
            bot.game["bans"][ban_id]["ban_reason"] = event["ban_reason"]
            print(bot.game["bans"])

        if event["event_type"] == "LEAVE":
            with open(bot.accesslog, "a", encoding="utf-8") as accesslogi:
                tee = bot.get_Tee(event["player_id"])
                nick = tee.get_nick()
                ip = tee.get_ip()
                time1 = time.strftime("%c", time.localtime())
                team = tee.attributes["team"]
                accesslogi.write(
                    "[{}] ".format(time1) + "{} left the server ({})".format(nick, ip) + "\n")
                if bot.game[team]["carrier"] is not None and bot.game[team]["carrier"].id == tee.id:
                    bot.game[team]["carrier"] = None
                del bot.game[team]["players"][tee.get_idnum()]
            bot.debug("{} has left the game.".format(bot.get_Leaves(event["player_id"])))
            bot.writeLine("status")
            tees = bot.player_count
            if tees == 0:
                bot.game["kill_history"] = [[0], [0]]
                bot.writeLine("reload")
                bot.writeLine("restart")

        else:
            pass
        bot.listeners[0](self.event_maker(bot))

    def event_maker(self, bot):
        bot = bot
        print("Emitting event!")
        print(bot.listeners)
        red_players = {}
        red_p_scores = []
        red_p_total = 0
        rp = bot.game["red"]["players"]
        if bot.game["red"]["carrier"] is not None:
            red_carry = bot.game["red"]["carrier"].attributes
        else:
            red_carry = {}

        for tee in dict(rp):
            red_p_scores.append((rp[tee].get_score(), rp[tee].get_nick()))
            red_players[rp[tee].get_nick()] = rp[tee].attributes

        blue_players = {}
        blue_p_scores = []
        blue_p_total = 0
        bp = bot.game["blue"]["players"]
        if bot.game["blue"]["carrier"] is not None:
            blue_carry = bot.game["blue"]["carrier"].attributes
        else:
            blue_carry = {}
        for tee in dict(bp):
            blue_p_scores.append((bp[tee].get_score(), bp[tee].get_nick()))
            blue_players[bp[tee].get_nick()] = bp[tee].attributes
        red_p_scores.sort()
        blue_p_scores.sort()
        print(bot.game)
        stamp = time.time() - bot.game["round_start"]
        m, s = divmod(floor(stamp - bot.game["round_start"]), 60)
        t = strftime("%M:%S", gmtime(floor(stamp)))
        #    length = "{:.0f}:{:.0f}".format(1.0*m, 1.0*s)

        template = {
            "emit_type": "event",
            "game_info": {
                "round_start": bot.game["round_start"],
                "map": bot.game["map"],
                "kill_history": bot.game["kill_history"],
                "gametype": bot.game["gametype"],
            },
            "redteam": {
                "size": len(bot.game["red"]["players"]),
                "totalscore": bot.game["red"]["score"],
                "players": red_players,
                "player_scores": red_p_scores,
                "player_total_score": red_p_total,
                "carrier": red_carry
            },
            "blueteam": {
                "size": len(bot.game["blue"]["players"]),
                "totalscore": bot.game["blue"]["score"],
                "players": blue_players,
                "player_scores": blue_p_scores,
                "player_total_score": blue_p_total,
                "carrier": blue_carry
            },
            "time_stamp": stamp,
            "round_length": t,
            "room": bot.name
        }
        print(template)
        return template
