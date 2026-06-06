import bascenev1 as bs
import bauiv1 as bui

class ExtraGamesWindow(bui.MainWindow):
    """Window displaying extra single-player games."""

    def __init__(
        self,
        transition: str = 'in_right',
        origin_widget: bui.Widget | None = None,
    ):
        scale_origin: tuple[float, float] | None
        if origin_widget is not None:
            self._transition_out = 'out_scale'
            scale_origin = origin_widget.get_screen_space_center()
            transition = 'in_scale'
        else:
            self._transition_out = 'out_right'
            scale_origin = None

        width = 600
        height = 500
        uiscale = bs.app.ui_v1.uiscale
        base_scale = 0.9 if uiscale is bs.UIScale.MEDIUM else 0.8
        if uiscale is bs.UIScale.SMALL:
            base_scale = 1.2

        super().__init__(
            root_widget=bui.containerwidget(
                size=(width, height),
                transition=transition,
                scale_origin_stack_offset=scale_origin,
                scale=base_scale,
                stack_offset=(0,0),
            ),
            transition=transition,
            origin_widget=origin_widget,
        )

        self.back_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(35, height - 50),
            size=(60, 60),
            scale=0.8,
            text_scale=1.2,
            autoselect=True,
            label="<",
            button_type='backSmall',
            on_activate_call=self._back,
        )
        bui.containerwidget(edit=self._root_widget, cancel_button=self.back_button)

        bui.textwidget(
            parent=self._root_widget,
            position=(10, height - 44),
            size=(width, 25),
            text="Extra Games",
            color=bs.app.ui_v1.title_color,
            h_align='center',
            v_align='top',
            maxwidth=400,
        )
        # the fgames
        extra_games = [
            {'name': 'Battle Spazes', 'description': 'Have a nice sandbox!'},
            {'name': 'Battle Spazes 2P', 'description': 'Have a sandbox together, make sure not to um... Crash your PC.'},
            {'name': 'Limbo', 'description': 'ITS BLUE!'},
            {'name': 'Minesweeper', 'description': 'Bomb: Flag, Jump: Select, Dont blow up!'},
            {'name': 'Pac-Man', 'description': 'Eats balls. n shit. (WARNING: Requires beefy device)'},
            {'name': 'Tetris', 'description': 'play tetris with yo peeps. 1-4 players. WARNING: Laggy'},
            {'name': 'The Roaring Knight', 'description': 'DELTAGOON. 1-3 players'},
             {'name': 'AI Fight', 'description': 'an old ai that i optimized, fight them here.'},
             {'name': 'Plants vs Zombies', 'description': 'breizn'},


            #{'name': 'One Night At Gummy\'s', 'description': 'Survive one night.'},
        ]

        scroll = bui.scrollwidget(
            parent=self._root_widget,
            position=(width*0.12, height*0.08),
            size=(width*0.8, height*0.8),
            highlight=False,
        )

        v = 0
        
        spacing = 80
        entry_height = len(extra_games) * spacing + 50
        entry = bui.containerwidget(
                parent=scroll,
                size=(width, entry_height),
                background=False,
            )
        

        

        for g in extra_games:
            

   

   
            bui.textwidget(
                parent=entry,
                position=(50, entry_height - 60 - v),
                size=(width - 160, 40),
                text=g['name'],
                color=(1,1,1,1),
                h_align='left',
                v_align='center',
                scale=1.2,
            )
            bui.textwidget(
                parent=entry,
                position=(30, entry_height - 90 - v),
                size=(width - 160, 30),
                text=g['description'],
                color=(0.8,0.8,0.8,1),
                h_align='left',
                v_align='center',
                scale=1.0,
                maxwidth=310,
            )

  
            bui.buttonwidget(
                parent=entry,
                position=(360, entry_height - 90 - v),
                size=(100, 60),
                label='Play',
                on_activate_call=lambda gname=g['name']: self._launch(gname),
            )

            v += spacing
    
    def _launch(self, name):
        from gummyoverhaul._singleplayergame import SinglePlayerSession
        

        bs.new_host_session(lambda: SinglePlayerSession(name))
    



    def _back(self) -> None:
        # pylint: disable=cyclic-import
        from bauiv1lib.play import PlayWindow

        # no-op if we're not in control.
        if not self.main_window_has_control():
            return
        
        self.main_window_back()
        return
        bui.app.ui_v1.set_main_window(
            PlayWindow(
                origin_widget=self.back_button,
            ),
            suppress_warning=True,
            from_window=self,
        )

    def get_main_window_state(self):
        cls = type(self)

       
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition,
                origin_widget=origin_widget,
            )
        )

    