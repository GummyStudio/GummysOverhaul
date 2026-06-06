import bascenev1 as bs
import babase
import os
import bauiv1 as bui
import threading
import json
import urllib.request
import time
import _bascenev1
import sys
import bauiv1


from bauiv1lib.confirm import ConfirmWindow

from babase import (
overlay_web_browser_open_url as url,
overlay_web_browser_close as url_close,
overlay_web_browser_is_open as is_url_open,
overlay_web_browser_is_supported as is_url_supported,
)


class Updater:

    def __init__(self, interval: float = 20.0):
        self.last_coins = 0
        self.last_dollars = 0
        self.interval = interval
        self.start_ticking_leaderboard()

       
    
        
        

        
        
    def update_self_on_leaderboard(self):
        """Send the leaderboard PATCH request (blocking)."""
        plus = bs.app.plus
        if not plus or not plus.cloud.connected or plus.get_v1_account_state() != 'signed_in':
            return

        URL = bs.app.plus.get_gummysoverhaul_server_url()
        player_id = plus.get_v1_account_public_login_id()
        coins = bs.app.config.get("GUMMY_gumcoins", 0)
        dollars = bs.app.config.get("GUMMY_gumdollars", 0)

        data = {
            "username": plus.get_v1_account_display_string(True, True),
            "coins": coins,
            "dollars": dollars
        }
        url = f"{URL}/leaderboards/{player_id}.json"

        if (self.last_coins == coins) and (self.last_dollars == dollars):
            return  # nothing changed
        
        # Not logged in to V2?
        if player_id is None:
            return

        

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="PATCH"
        )
        try:
            urllib.request.urlopen(req)
        except Exception as e:
            print("Failed to update leaderboard:", e)
            print("Please contact Gummy on Discord if the servers are down !!!")

        self.last_coins, self.last_dollars = coins, dollars

    def update_self_on_leaderboard_async(self):
        """Run the leaderboard update in a background thread."""
        threading.Thread(target=self.update_self_on_leaderboard, daemon=True).start()

    def start_ticking_leaderboard(self):
        """Tick every `interval` seconds without freezing the game."""
       

        self.update_self_on_leaderboard_async()
        
        bui.apptimer(self.interval, self.start_ticking_leaderboard)
        
        


    


class GummysOverhaulStartUp():

    def reload_preloads(self):
       bs.pushcall(lambda: setattr(
            self, 'preloads', {
                    'SendMessage': bs.gettexture('menuButton'),
                    'AllMessage': bs.gettexture('menuButton')
                }
            )
       )
        
    
    def __init__(self):
        self.our_version = '3.2'
        self.game_header = 'Reforged Update'
        self.preloads: dict[str: bs.Texture]
        
        
        key_verifier = 'Local Account Name'

        # check if gumoverhaul values exists in the config *** THX VISHUU!!! ***
        #pseudo-code
        global cfg
        cfg = bui.app.config

        # made by temp in the 'bombarmy' discussion in the discord server.
        config = bs.app.config
        conflist = {
        "GUMMY_Main Menu Music": "Mario Paint",
        "GUMMY_RandomCritChance": "(1/4)",
        "GUMMY_blockvanillaplayers": False,
        "GUMMY_disablerandomcrit": False,
        "GUMMY_gumcoins": 0,
        "GUMMY_gumdollars": 0,
        "GUMMY_statscrit": 0,
        "GUMMY_statsminicrit": 0,
        "GUMMY_statsshieldbreaks": 0,
        "GUMMY_statsminexecutions": 0,
        "GUMMY_statsbolteds": 0,
        "GUMMY_statsimpulsd": 0,
        "GUMMY_statsgoldstatue": 0,
        "GUMMY_statsbrokenankles": 0,
        "GUMMY_discordrp": True,
        "ownedSweetman": False,
        "ownedAgentSpaz": False,
        "ownedAmar": False,
        "ownedBob": False,
        "ownedOverhaul": False,
        "ownedWatory": False,
        "ownedTower": False,
        "ownedIre": False,
         "ownedRem": False,
         "ownedFennekin": False,
         "ownedTopHat_Cosmetic": False,
        "OVERHAUL_firstLaunchNEW": True,
        "firstLaunch": False,

        # Probably not gonna do achievements this time?
        # yes we are stfu
        "ownedDARK": False,
        "ownedHELL": False,
        "ownedGOD": False,
        "ownedGODEX": False,
        "ownedHYPER": False,
        "ownedBREAKER": False,
        "ownedEXEC": False,
        "ownedBOLT": False,
        "ownedSNIPER": False,
        #'ownedLOVER': False,
        'ownedSPIKER': False ,
        'ownedCHARGER': False,
        'ownedCHARGER2':False,
        'ownedCHARGER3': False,
        'ownedMILESTONE1': False,
        'ownedMILESTONE2': False,
        'ownedMILESTONE3':False,
        'ownedMILESTONE4': False,
        'ownedMILESTONE5': False,
        'ownedFOOLEDFAYE': False,
        'ownedROARING': False,
        "ownedCat": False,
        "ownedScoldy": False,
        "ownedOldLady": False,
        "ownedJolluNinja_Cosmetic": False,
        "ownedHHH_amarCosmetic": False,
        "ownedYurirblx_Cosmetic": False,
        "ownedGummyVoiceSpaz_Cosmetic": False,
        "ownedGummyVoiceJack_Cosmetic": False,
        "ownedGummyVoiceAgent_Cosmetic": False,
        "ownedSpace": False,
        "ownedVr": False,
        "ownedPizza": False,
        "ownedNoise": False,
        "ownedRalsei": False,
        "ownedBunny": False,
        "ownedCap": False,
        "GUMMY_expertmode": False,
        "ownedOverhaulRunaround": False,
        "gummy_chestinslot": {},
        "gummy_chestqueue": [],
        'ownedCosmetic_SpazEXE': False,
        'ownedCosmetic_StarHoodie': False,
        'ownedCosmetic_Insane': False,
        'ownedCosmetic_Bluecap': False,
        'ownedCosmetic_Melling': False,
        'ownedCosmetic_Ninjaling': False,
        'ownedCosmetic_Spazling': False,
        'ownedCosmetic_Sal': False,
        'asked_faye_bandana': False,
        'asked_faye_owner': False,
        'secret_boss_1': False,
        'secret_boss_2': False,
        'secret_boss_3': False,
        'asked_faye_boss': False,
        'GUMMY_xp': 0,
        'GUMMY_level': 1,
        'GUMMY_max_level': 200,
        'remove_xp_stuff_lomao': False,
        'GUMMY_disable_messages': False,
        'GUMMY_message_frequency': 'Medium',
        'GUMMY_toggle_globe': True,
        'GUMMY_pvzsave': {},
        'GUMMY_showevents': False,
        }
        # "setdefault" to create config settings
        # won't affect already existing ones.
        for k,v in conflist.items():
            config.setdefault(k, v)
        # save changes
        cfg['GUMMY_game'] = None
        config.apply_and_commit()
        try:
            cfg['ownedOverhaulRunaround']
        except:
            print('FATAL ERROR!!')
            print('Unable to automatically add Required Gummy\'s Overhaul Config Values.')
        
        # Enable certain "ERROR: This object has not died." messages.
        self.debug = False 
        # They're helpful, but.. honestly they dont ** SEEM ** to effect gameplay majorly
        # And i'd want the terminal to be clean
        
            

        # pls dont hack 🙏🙏🙏
        

        if babase.app.config.get('OVERHAUL_firstLaunchNEW', False):
            from gummyoverhaul.overhaul_chests import give_chest
            from baclassic._chest import CHEST_APPEARANCE_DISPLAY_INFOS
            import bacommon.bs
            lg_info = CHEST_APPEARANCE_DISPLAY_INFOS.get(bacommon.bs.ClassicChestAppearance.LG)
            cfg = bui.app.config
            cfg['OVERHAUL_firstLaunchNEW'] = False
            cfg.apply_and_commit()
        
            if babase.app.config.get('Local Account Name') == 'PC133635':
                bui.getsound('gunCocking').play()
                babase.screenmessage('mikirog jumpscare')
                
                
                give_chest(
                    {
                        "type": "both",
                        "name": "Mikirog Special Chest",
                        "color": lg_info.color,
                        "tint":  lg_info.tint,
                        "tint2": lg_info.tint2,
                        "coins": 10000,
                        "dollars": 20
                    }
                )
                
                
                
                
            else:

                bui.getsound('gunCocking').play()
                babase.screenmessage('Thank you for downloading Gummy\'s Overhaul!')
                give_chest(
                    {
                        "type": "both",
                        "name": "New User Chest",
                        "color": lg_info.color,
                        "tint":  lg_info.tint,
                        "tint2": lg_info.tint2,
                        "coins": 1000,
                        "dollars": 10
                    }
                )
                
            
            
                

        os.environ["BA_SUPPRESS_SCREEN_MESSAGE_WARNING"] = "1"

        # those idiots are now removed so o
        if babase.app.config.get('ownedSweetman', False):
            bs.screenmessage('Sweetman has been removed. You got ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + ' 1500!',
                            color=(0, 1, 1)
                            
                            )
            bui.getsound('cashRegister').play()
            cfg['GUMMY_gumcoins'] = babase.app.config.get('GUMMY_gumcoins', False) + 1500
            cfg['ownedSweetman'] = False
            cfg.apply_and_commit()

        if babase.app.config.get('ownedCat', False):
            bs.screenmessage('Tucker has been removed. You got ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + ' 12500!',
                            color=(0, 1, 1)
                            )
            bui.getsound('cashRegister').play()
            cfg['GUMMY_gumcoins'] = babase.app.config.get('GUMMY_gumcoins', False) + 12500
            cfg['ownedCat'] = False
            cfg.apply_and_commit()

        # start up rich presence

        try:

            if babase.app.classic.platform not in [
                'android'
            ] and babase.app.config.get('GUMMY_discordrp'):
                try:
                    from .discordrp_handler import RichPresence
                    babase.apptimer(5, RichPresence)
                except Exception as e:
                    print(f'Enable to start rich presence: {e}')
        
        except AttributeError:
            pass
        
        Updater()
        from gummyoverhaul.earth_submit import goober
        goober()

       

    
        def ask():
                
                latest_version_url = "https://raw.githubusercontent.com/GummyStudio/GummysOverhaul/refs/heads/main/game_verison.txt"

                def get_latest_version():
                    try:
                        req = urllib.request.Request(
                            latest_version_url + f'?nocache={int(time.time())}',
                            headers={
                                "User-Agent": "GummysOverhaul/VersionCheck",
                                "Cache-Control": "no-cache",
                                "Pragma": "no-cache"
                            }
                        )
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            text = resp.read().decode()
                            # Normalize: remove whitespace and BOM if present
                            clean = text.strip().lstrip('\ufeff')
                          
                            if clean:
                                return clean
                    except Exception as e:
                        return False
                    return False

                github_version = get_latest_version()

                # dont show if we failed
                if (not github_version) or (str(github_version).strip() == str(self.our_version).strip()):
                    return

                if babase.is_browser_likely_available():
                    ConfirmWindow(
                        f'Hey! You\'re using an older version of Gummy\'s Overhaul. ({self.our_version})\n'
                        f'Theres a newer version avaliable on GameJolt. ({github_version})\nPlease Update!',
                        lambda: babase.open_url('https://gamejolt.com/games/gummysoverhaul/923618'),
                        cancel_is_selected=True,
                        cancel_text='Go fuck yourself',
                        ok_text='Yes, take me to Gamejolt.',
                        width=600,
                        height=240
                    )
        babase.apptimer(1, ask)
        # Andd put some stuff into the console so its easier
        main_mod = sys.modules['__main__']
        setattr(main_mod, 'bs', bs)
        setattr(main_mod, 'bui', bauiv1)
        setattr(main_mod, 'babase', babase)
        setattr(main_mod, 'getactivity', bs.getactivity)
        setattr(main_mod, 'getplayers', bs.getplayers)

        # setup a local connection to da bot
        if babase.app.config.get('Local Account Name', 'Account1') == 'Mac289345' and False:
            import socket
         

            import io
            import traceback
            from contextlib import redirect_stdout

            def handle_command(command: str):
                import re

                DANGEROUS_WORDS = [
                    "quit", "exit", "os", "sys", "__import__", "eval", "exec", "open", "bui", "getattr", "config", "__all__", 'Account V2 State', "ADD_PLAYER_PROFILE"
                    "subproccess", "REMOVE_PLAYER_PROFILE", "give_chest"
                ]

                # Only match whole words
                for word in DANGEROUS_WORDS:
                    pattern = r'\b' + re.escape(word) + r'\b'
                    if re.search(pattern, command, flags=re.IGNORECASE):
                        return {"ok": False, "error": "Blocked unsafe command."}
              
                #if "=" in command:
                #    return {"ok": False, "error": "Assignments are not allowed in console commands."}
                
                stdout_buffer = io.StringIO()
                done = threading.Event()
                result_holder = {"ok": True, "output": None, "error": None}

                def _run_on_logic_thread():
                    with bs.get_foreground_host_activity().context:
                        try:
                            with redirect_stdout(stdout_buffer):
                                try:
                                    result = eval(command, globals(), globals())
                                    if result is not None:
                                        stdout_buffer.write(repr(result))
                                except SyntaxError:
                                    exec(command, globals(), globals())
                        except Exception:
                            result_holder["ok"] = False
                            result_holder["error"] = traceback.format_exc()
                        finally:
                            done.set()

                # Ensure execution happens on the BombSquad logic thread
                bs.pushcall(_run_on_logic_thread, from_other_thread=True)

                # Wait until execution finishes
                done.wait(timeout=5.0)

                if not done.is_set():
                    return {
                        "ok": False,
                        "error": "Execution timed out."
                    }

                if result_holder["ok"]:
                    output = stdout_buffer.getvalue().strip()
                    return {
                        "ok": True,
                        "output": output or "NoneType"
                    }
                else:
                    return {
                        "ok": False,
                        "error": result_holder["error"]
                    }


            def socket_server():
              


                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(("127.0.0.1", 51234))
                s.listen(1
                )
                print("[DISCORD] BombSquad console bridge listening on 127.0.0.1:51234")


                while True:
                    conn, _ = s.accept()
                    data = conn.recv(8192)

                    if not data:
                        conn.close()
                        continue

                    payload = json.loads(data.decode())

                    author = payload.get("author", "Unknown")
                    command = payload.get("command", "")

                    print(f"[DISCORD] {author} executed: {command}")

                    response = handle_command(command)

                    # Attach metadata to response
                    response["author"] = author
                    response["command"] = command

                    conn.sendall(json.dumps(response).encode())


            threading.Thread(target=socket_server, daemon=True).start()

                

    
def suicided_on_map(index):
    cfg = bs.app.config
    volume = 5
    if index == 1:
        if not cfg['secret_boss_1']:
            bui.getsound('dot_dot_dot').play(volume)
        cfg['secret_boss_1'] = True
    
    

    elif index == 2:
        if not cfg['secret_boss_2']:
            bui.getsound('dot_dot_dot').play(volume)
        cfg['secret_boss_2'] = True
    
    elif index == 3:
        if not cfg['secret_boss_3']:
            bui.getsound('dot_dot_dot').play(volume)
        cfg['secret_boss_3'] = True
    
    elif index == 4:
       

        if not cfg['asked_faye_boss']:
            bui.getsound('dot_dot_dot').play(volume)
        cfg['asked_faye_boss'] = True
    else:
        raise ValueError('Index unknown')
    
    cfg.apply_and_commit()
    

    






   
    
    
    




{
    'leaderboard': {
        '<PLAYERID>': {
            'username': 'GummyBoiYT',
            'coins': 13124,
            'dollars': 21,
        },
    },
}








