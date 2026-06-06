import bascenev1 as bs
from bascenev1._session import Session
from typing import Sequence
import babase
from typing import Any, override
from gummyoverhaul.single_player_games import ExtraGamesWindow
from bascenev1._activitytypes import JoinActivity
from bascenev1lib.game.thebattlespazes import TheBattleSpazGame
from bascenev1lib.game.onenightatgummys import OneNightAtGummysGame
from bascenev1lib.game.limbo import LimboGame
from bascenev1lib.game.minesweeper import MinesweeperGame
from bascenev1lib.game.pacman import PacManGame
from bascenev1lib.game.tetris import tetrisGame
from bascenev1lib.game.aigame import BotGame
from bascenev1lib.game.roaryingknite import roaryGame
from bascenev1lib.game.pvz import PVZGame
# from gummyoverhaul._singleplayergame import SinglePlayerSession; import bascenev1 as bs; bs.new_host_session(SinglePlayerSession)

class SinglePlayerSession(Session):

    use_teams = False
    use_team_colors = False


    def __init__(self, game: str) -> None:
        depsets: Sequence[bs.DependencySet] = []
        from bascenev1._activitytypes import JoinActivity
        self.minimum = 1
        maximum = 1

        if game == 'Battle Spazes 2P':
            self.minimum = 2
            maximum = 2
        if game == 'Tetris':
            self.minimum = 1
            maximum = 4
        if game == "The Roaring Knight":
            self.minimum = 1
            maximum = 3
        if game == "AI Fight":
            self.minimum = 0
            maximum = 6
      
        
        super().__init__(
            depsets,
            team_names=None,
            team_colors=None,
            min_players=self.minimum,
            max_players=maximum,
        )
        self.back_to_lobby_mode = False
        self.game = game
        self._custom_menu_ui = [
             {
                    'label': 'Reset',
                    'call': babase.WeakCall(self.reset),
                },
                                {
                    'label': 'New Game',
                    'call': babase.WeakCall(self.new_game),
                },
                 
            ]

        self.setactivity(bs.newactivity(JoinActivity))
        
        bs.timer(0.1, self.player_tick, repeat=True)

   
       
        
    @override
    def get_custom_menu_entries(self) -> list[dict[str, Any]]:
        return self._custom_menu_ui
    
    def everyone_leave(self):
        for p in self.sessionplayers:
                p.remove_from_game()
    
    def reset(self):
        bs.new_host_session(lambda: SinglePlayerSession(self.game))

    def new_game(self):
        # open the singleplayer thing
       
        
        babase.app.ui_v1.set_main_window(
            ExtraGamesWindow(),
            is_top_level=True,
            suppress_warning=True,
        )
       
    
    def on_activity_end(self, activity, results):
        
       


        if self.game == 'Battle Spazes':

                next_instance = TheBattleSpazGame
        elif self.game == 'Battle Spazes 2P':

                next_instance = TheBattleSpazGame
        elif self.game == 'One Night At Gummy\'s':
                next_instance = OneNightAtGummysGame
        elif self.game == 'Limbo':
                next_instance = LimboGame
        elif self.game ==  'Minesweeper':
                next_instance = MinesweeperGame
        elif self.game ==  'Pac-Man':
                next_instance = PacManGame
        elif self.game ==  'Tetris':
                next_instance = tetrisGame
        elif self.game == "The Roaring Knight":
                
                next_instance = roaryGame
        elif self.game == "AI Fight":
                next_instance = BotGame
        elif self.game == 'Plants vs Zombies':
                next_instance = PVZGame
        else:
            raise ValueError('unknown game')
        
        if not results:
            results = {'outcome': None}
        


        if results['outcome'] == 'reset':
            next_instance = JoinActivity
        elif isinstance(activity, JoinActivity):
            
            # dont end
            pass
        elif results['outcome'] == 'restart':
            # dont end
            pass
        else:
            self.return_to_main_menu()
            return
        
        
        new_activity = bs.newactivity(next_instance)
        self.stats.setactivity(new_activity)
        self.setactivity(new_activity)

    def player_tick(self):
        from bascenev1._activitytypes import JoinActivity
        if len(self.sessionplayers) < self.minimum and not isinstance(self.getactivity(), JoinActivity):
            self.return_to_main_menu()

    def restart_game(self):
        activity = self.getactivity()
        if activity is not None and not activity.expired:
            with activity.context:
                activity.end(results={'outcome': 'restart'}, force=True)

    def return_to_main_menu(self):
        bs.app.classic.return_to_main_menu_session_gracefully(reset_ui=False)
        
    def get_next_game_description(self) -> str:
        """Returns a description of the next game on deck."""
        # make it return some shi uhh in the ui tknw
        if self.game in ['Battle Spazes', 'Battle Spazes 2P']:
            name = 'The Battle Spaz\'s'
        elif self.game in ['One Night At Gummy\'s']:
            name = 'One Night At Gummy\'s'
        elif self.game == 'Limbo':
            name = 'Limbo'
        elif self.game ==  'Minesweeper':
            name = 'Minesweeper'
        elif self.game == 'Pac-Man':
            name = 'Pac-Man'
        elif self.game == 'Tetris':
            name = 'Tetris'
        elif self.game == "The Roaring Knight":
            name = "The Roaring Knight"
        elif self.game == 'Bomb Party':
            name = 'Bomb Party'
        else:
                raise ValueError('unknown game')
        return name