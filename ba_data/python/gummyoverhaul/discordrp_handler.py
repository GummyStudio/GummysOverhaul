
""" had to rewrite everything aahh... """
import time
import threading
from gummyoverhaul.discordrp_folder import Presence
import babase
import bascenev1 as bs
import queue
from bascenev1lib.mainmenu import MainMenuActivity
from bascenev1._activitytypes import JoinActivity
from bascenev1._gameactivity import GameActivity
from bascenev1lib.game.thetower import TheTowerGame
from gummyoverhaul._singleplayergame import SinglePlayerSession
import bauiv1 as bui
from gummyoverhaul.shop import ShopActivity
from gummyoverhaul.online import OnlineActivity

portal_id = "1374787903334514699"

MAPS: dict = {
    'Hockey Stadium': 'hockey_stadium',
    'Football Stadium': 'football_stadium',
    'Bridgit': 'bridgit',
    'Big G': 'big_g',
    'Roundabout': 'roundabout',
    'Monkey Face': 'monkey_face',
    'Zigzag': 'zigzag',
    'The Pad': 'thepad',
    'Doom Shroom': 'doom_shroom',
    'Lake Frigid': 'lake_fridget',
    'Tip Top': 'tiptop',
    'Crag Castle': 'crag_castle',
    'Tower D': 'tower_d',
    'Happy Thoughts': 'happy_thoughts',
    'Step Right Up': 'step_right_up',
    'Courtyard': 'courtyard',
    'Rampage': 'rampage',
    'Gummy Stage': 'gummy_stage',
    'Table': 'table',
    'Tower G': 'tower_g',
    'The Tower': 'thetower',
    'Package Minigame': 'step_right_upminigame',
    'Nintendo DS': 'nintendods',
    'Space Station': 'spacestation',
    'Pit Pass': 'pitpassing',
    'Bomb Jump Park': 'bjpark',
    'Great Fucking Britian': 'gb',
}

class RichPresence:
    def __init__(self):
        self.presence = Presence(portal_id)
        self.mode = 'menu'
        self.starting_time = int(time.time())
        self.map = None
        self.last_mode = None
        
        self.update_queue = queue.Queue()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        
        self.check()

    def _worker_loop(self):
        while True:
            try:
                # i love usign new imports ive never used  b efore
                payload = self.update_queue.get()
                self.presence.set(payload)
                self.update_queue.task_done()
            except Exception as e:
                print(f"Discord Worker Error: {e}")
            time.sleep(1.5) # preventing rate limit

    def check(self):
        try:
            activity = bs.get_foreground_host_activity()
            session = bs.get_foreground_host_session()
            
            try:
                self.map = activity.map.name
            except:
                pass

            new_mode = self.mode
            if bui.get_input_idle_time() > 30 and self.mode in ('menu', 'menu_idle'):
                new_mode = 'menu_idle'
            elif isinstance(activity, JoinActivity):
                new_mode = 'lobby'
            elif bs.get_connection_to_host_info_2():
                new_mode = 'online'
            elif bs.is_in_replay():
                new_mode = 'replay'
            elif isinstance(session, SinglePlayerSession):
                new_mode = 'extra'
            elif isinstance(activity, GameActivity):
                new_mode = 'gameplay'
            elif isinstance(activity, MainMenuActivity):
                new_mode = 'menu'
            elif isinstance(activity, ShopActivity):
                new_mode = 'shop'
            elif isinstance(activity, OnlineActivity):
                new_mode = 'online_browser'

            if new_mode != self.last_mode:
                self.mode = new_mode
                self.last_mode = new_mode
                self.starting_time = int(time.time())

            # prepare payload
            payload = self.prepare_payload(activity, session)
            
            self.update_queue.put(payload)
        except Exception as e:
            print(f"Rich Presence Check Error: {e}")

            
        
        

    def prepare_payload(self, activity, session):
        
        sess_name = "None"
        sess_img = "null"
        if isinstance(session, bs.FreeForAllSession):
            sess_name, sess_img = 'FFA', 'ffa'
        elif isinstance(session, bs.CoopSession):
            sess_name, sess_img = 'Co-op', 'coop'
        elif isinstance(session, bs.DualTeamSession):
            sess_name, sess_img = 'Teams', 'teams'

        try:
            roster_len = max(1, len(bs.get_game_roster()))
            party_max = bs.get_public_party_max_size()
        except:
            roster_len, party_max = 1, 8

        data = {
            "timestamps": {"start": self.starting_time},
            "party": {"id": "00", "size": (roster_len, party_max)},
            "assets": {"large_image": "logo"}
        }

        if self.mode in ('menu', 'menu_idle'):
            data["details"] = 'Browsing the Menus...' if self.mode == 'menu' else 'Idle in the Menus..'
            data["state"] = 'Party'
            data["assets"]["large_text"] = f"Listening to {babase.app.config.get('GUMMY_Main Menu Music', 'Mario Paint')}\nVersion 3.0"

        elif self.mode == 'online_browser':
            data["details"] = 'Browsing for an online game...'
            data["assets"]["large_image"] = "online"

        elif self.mode == 'shop':
            data["details"] = 'Browsing through the Store..'
            data["assets"]["large_image"] = "shop"

        elif self.mode == 'gameplay':
            map_image = MAPS.get(self.map, 'null')
            
            if isinstance(session, bs.CoopSession):
                try:
                    score_type = 'Altitude' if isinstance(activity, TheTowerGame) else 'Score'
                    details = f"{score_type} {activity._score}"
                except:
                    details = "Watching score"
            else:
                details = f"Playing {activity.name}"

            data.update({
                "details": details,
                "state": "Party",
                "assets": {
                    "large_image": map_image,
                    "large_text": self.map,
                    "small_image": sess_img,
                    "small_text": f"{sess_name} ({activity.name})" if isinstance(session, bs.CoopSession) else sess_name
                }
            })

        elif self.mode == 'lobby':
            data.update({
                "details": "Selecting a character",
                "assets": {"large_image": "lobby", "small_image": sess_img, "small_text": sess_name}
            })

        elif self.mode == 'online':
            try:
                name = bs.get_connection_to_host_info_2().name or 'a Party'
            except:
                name = 'a Party'
            data.update({
                "details": f"Playing in {name}",
                "assets": {"large_image": "online", "large_text": "Playing Online"}
            })

        elif self.mode == 'replay':
            data.update({
                "details": "Watching a replay",
                "assets": {"large_image": "replay", "large_text": "In a replay"}
            })

        elif self.mode == 'extra':
            game_name = getattr(session, 'game', 'Unknown')
            data.update({
                "details": f"Playing an extra game ({game_name})",
                "assets": {"large_image": MAPS.get(self.map, 'null'), "large_text": self.map}
            })

        return data