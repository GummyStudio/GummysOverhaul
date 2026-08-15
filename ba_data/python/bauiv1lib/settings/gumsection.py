"""Provides UI for graphics settings."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from bauiv1lib.popup import PopupMenu
import bauiv1 as bui
import babase
import logging
import _bauiv1
from bauiv1lib.popup import PopupWindow

if TYPE_CHECKING:
    from typing import Any



class gumsectionSettingsWindow(bui.MainWindow):
    """Window for graphics settings."""

    def __init__(
        self,
        transition: str = 'in_right',
        origin_widget: bui.Widget | None = None,
    ):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements

        # if they provided an origin-widget, scale up from that
        scale_origin: tuple[float, float] | None
        if origin_widget is not None:
            self._transition_out = 'out_scale'
            scale_origin = origin_widget.get_screen_space_center()
            transition = 'in_scale'
        else:
            self._transition_out = 'out_right'
            scale_origin = None
        
       

        self._r = 'gumWindow'
        app = bui.app
        assert app.classic is not None

        spacing = 32
        self._have_selected_child = False
        uiscale = app.ui_v1.uiscale
        discord_rp_enabled = babase.app.classic.platform != 'android'
        width = 450.0
        height = (470.0 if discord_rp_enabled else 430) + 170
        self._max_fps_dirty = False
        self._last_max_fps_set_time = bui.apptime()
        self._last_max_fps_str = ''
        self._show_fn = True


        assert bui.app.classic is not None
        uiscale = bui.app.ui_v1.uiscale
        base_scale = (
            2.0
            if uiscale is bui.UIScale.SMALL
            else 1.5 if uiscale is bui.UIScale.MEDIUM else 1.0
        )
        popup_menu_scale = base_scale * 1.2
        
        super().__init__(
            root_widget=bui.containerwidget(
                size=(width, height),
                transition=transition,
                scale_origin_stack_offset=scale_origin,
                scale=base_scale,
            ),
            transition=transition,
            origin_widget=origin_widget

        )

        back_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(35, height - 50),
            # size=(120, 60),
            size=(60, 60),
            scale=0.8,
            text_scale=1.2,
            autoselect=True,
            label=bui.charstr(bui.SpecialChar.BACK),
            button_type='backSmall',
            on_activate_call=self._back,
        )

        bui.containerwidget(edit=self._root_widget, cancel_button=back_button)

        bui.textwidget(
            parent=self._root_widget,
            position=(10, height - 44),
            size=(width, 25),
            text=bui.Lstr(r='titleText'),
            color=bui.app.ui_v1.title_color,
            h_align='center',
            v_align='top',
            maxwidth=230,
        )
        # main menu musics!!
        v = (375 if discord_rp_enabled else 345) + 160

        bui.textwidget(
            parent=self._root_widget,
            position=(60, v),
            size=(160, 25),
            text=bui.Lstr(r=f'{self._r}.menuMusicText'),
            color=bui.app.ui_v1.heading_color,
            scale=1,
            maxwidth=150,
            h_align='center',
            v_align='center',
        )
        PopupMenu(
            parent=self._root_widget,
            position=(245, v - 13),
            width=150,
            scale=popup_menu_scale,
            choices=[
                "Mario Paint", "You Don't Know Me", "Roblox Xbox One", 
                "Geometry Dash", "Wii Party", "Half-Life 2", 
                "Mario's Maddness", "Ballin X Die in a Fire", "Portal Radio", 
                "PHIGHTING!", "Pizza Tower", 'Fall Guys SS1', 
                'Running From the Internet', 'Dazzling Dark Future', 
                'Join Us for a Bite Remix', 'Mario VS Luigi', "Fucking Pea k",
                'TEKASHIRUNE', 'Smash Bros. Ultimate'
            ],
        current_choice=bui.app.config.get('GUMMY_Main Menu Music', 'Mario Paint'),
        on_value_change_call=self._fnsong,
        )

        v = v - 55

        #randomcrits

        self._disablecrits_checkbox = bui.checkboxwidget(
            parent=self._root_widget,
            position=(100, v),
            size=(160, 30),
            autoselect=True,
            maxwidth=280,
            textcolor=(0.8, 0.8, 0.8),
            value=bui.app.config.get("GUMMY_disablerandomcrit", False),
            text=bui.Lstr(r=f'{self._r}.disableCritsText'),
            on_value_change_call=self._on_randomcritchange
)
        
        # crit chance

        v = v - 55

        bui.textwidget(
            parent=self._root_widget,
            position=(60, v),
            size=(160, 25),
            text=bui.Lstr(r=f'{self._r}.critChanceText'),
            color=bui.app.ui_v1.heading_color,
            scale=1,
            maxwidth=150,
            h_align='center',
            v_align='center',
        )
        PopupMenu(
            parent=self._root_widget,
            position=(245, v - 13),
            width=150,
            scale=popup_menu_scale,
            choices=["(1/24)", "(1/9)", "(1/4)", "100%"],
            current_choice=bui.app.config.get('GUMMY_RandomCritChance', '(1/4)'),
            on_value_change_call=self._critchance,
        )

        v = v - 50

        #block vanilla players from joining (unused)

        self._block_vanilla_players = bui.checkboxwidget(
            parent=self._root_widget,
            position=(50, v),
            size=(160, 30),
            autoselect=True,
            maxwidth=300,
            textcolor=(0.8, 0.8, 0.8),
            value=bui.app.config.get("GUMMY_blockvanillaplayers", False),
            text=bui.Lstr(r=f'{self._r}.comboMeterText'),
            on_value_change_call=self._block_vanilla
        )

        v = v - 50

        # Tower Expert mode.

        self._skip_cards_tower = bui.checkboxwidget(
            parent=self._root_widget,
            position=(50, v),
            size=(160, 30),
            autoselect=True,
            maxwidth=300,
            textcolor=(0.8, 0.8, 0.8),
            value=bui.app.config.get("GUMMY_expertmode", False),
            text=bui.Lstr(r=f'{self._r}.skipCardsText'),
            on_value_change_call=self._expert_mode
        )
        v = v - 35

        bui.checkboxwidget(
            parent=self._root_widget,
            position=(50, v),
            size=(160, 30),
            autoselect=True,
            maxwidth=300,
            textcolor=(0.8, 0.8, 0.8),
            value=bui.app.config.get('remove_xp_stuff_lomao', True),
            text=bui.Lstr(r=f'{self._r}.disableXPPopupText'),
            on_value_change_call=self._xp
        )

        

        v = v - 60
        bui.buttonwidget(
            parent=self._root_widget,
            label=bui.Lstr(r=f'{self._r}.globeSettingsText'),
            position=(width * 0.3, v),
            size=(200, 50),
            on_activate_call=self.globe_settings_window
        )

        v = v - 60
        self.events = bui.checkboxwidget(
                parent=self._root_widget,
                position=(50, v),
                size=(160, 30),
                autoselect=True,
                maxwidth=300,
                textcolor=(0.8, 0.8, 0.8),
                value=bui.app.config.get("GUMMY_showevents", False),
                text=bui.Lstr(r=f'{self._r}.alwaysShowHolidaysText'),
                on_value_change_call=self.holiday
        )

        v = v - 60
        bui.buttonwidget(
            parent=self._root_widget,
            label=bui.Lstr(r=f'{self._r}.figurePlayerManText'),
            position=(width * 0.3, v),
            size=(200, 50),
            on_activate_call=self.fp_manager
        )

        if discord_rp_enabled:
            v = v - 60
            self._discord_rp = bui.checkboxwidget(
                parent=self._root_widget,
                position=(50, v),
                size=(160, 30),
                autoselect=True,
                maxwidth=300,
                textcolor=(0.8, 0.8, 0.8),
                value=bui.app.config.get("GUMMY_discordrp", False),
                text=bui.Lstr(r=f'{self._r}.enableRPCText'),
                on_value_change_call=self.dicsord_rp
            )
    
    
    def globe_settings_window(self):
        GlobeSettingsWindow()
    
    
    def main_window_replace(
        self,
        new_window: bui.MainWindow,
        back_state: bui.MainWindowState | None = None,
        is_auxiliary: bool = False,
    ) -> None:
        """Replace ourself with a new MainWindow."""

        # Users should always check main_window_has_control() *before*
        # creating new MainWindows and passing them in here. Kill the
        # passed window and Error if it seems they did not.
        if not self.main_window_has_control():
            new_window.get_root_widget().delete()
            raise RuntimeError(
                f'main_window_replace() called on a not-in-control window'
                f' ({self}); always check main_window_has_control() before'
                f' calling main_window_replace().'
            )

        # Just shove the old out the left to give the feel that we're
        # adding to the nav stack.
        transition = 'out_left'

        # Transition ourself out.
        try:
            self.on_main_window_close()
        except Exception:
            logging.exception('Error in on_main_window_close() for %s.', self)

        _bauiv1.containerwidget(edit=self._root_widget, transition=transition)
        babase.app.ui_v1.set_main_window(
            new_window,
            from_window=self,
            back_state=back_state,
            is_auxiliary=is_auxiliary,
            suppress_warning=True,
        )

    @override
    def get_main_window_state(self) -> bui.MainWindowState:
        # Support recreating our window for back/refresh purposes.
        cls = type(self)
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition, origin_widget=origin_widget
            )
        )

    def _back(self) -> None:
        """Move back in the main window stack.

        Is a no-op if the main window does not have control;
        no need to check main_window_has_control() first.
        """

        # Users should always check main_window_has_control() before
        # calling us. Error if it seems they did not.
        if not self.main_window_has_control():
            return

        uiv1 = babase.app.ui_v1

        # Get the 'back' window coming in.
        if not self.main_window_is_top_level:

            back_state = self.main_window_back_state
            if back_state is None:
                raise RuntimeError(
                    f'Main window {self} provides no back-state.'
                )

            # Valid states should have values here.
            assert back_state.is_top_level is not None
            assert back_state.is_auxiliary is not None
            assert back_state.window_type is not None

            backwin = back_state.create_window(transition='in_left')

            uiv1.set_main_window(
                backwin,
                from_window=self,
                is_back=True,
                back_state=back_state,
                suppress_warning=True,
            )

        # Transition ourself out.
        self.main_window_close()

    def fp_manager(self):
        from gummyoverhaul.amiibo.manager import FigureSession
        from bascenev1 import new_host_session

        new_host_session(FigureSession)
            
    
    def _xp(self, val: bool):
        cfg = bui.app.config
        cfg['remove_xp_stuff_lomao'] = val
        cfg.apply_and_commit()
        
    def holiday(self, val: bool):
        cfg = bui.app.config
        cfg['GUMMY_showevents'] = val
        cfg.apply_and_commit()

    def _fnsong(self, val: str) -> None:

        cfg = bui.app.config
        cfg['GUMMY_Main Menu Music'] = val
        cfg.apply_and_commit()
    
    def _critchance(self, val: bool) -> None:
        cfg = bui.app.config
        cfg['GUMMY_RandomCritChance'] = val
        cfg.apply_and_commit()
    
    def dicsord_rp(self, val: bool) -> None:
        cfg = bui.app.config
        cfg['GUMMY_discordrp'] = val
        cfg.apply_and_commit()
        babase.screenmessage(
            bui.Lstr(r='restartGameWarning')
        )

    def _on_randomcritchange(self, val: bool) -> None:
        cfg = bui.app.config
        cfg['GUMMY_disablerandomcrit'] = val
        cfg.apply_and_commit()

    def _block_vanilla(self, val: bool) -> None:
        cfg = bui.app.config
        cfg['GUMMY_blockvanillaplayers'] = val
        cfg.apply_and_commit()
    
    def _expert_mode(self, val: bool) -> None:
        cfg = bui.app.config
        cfg['GUMMY_expertmode'] = val
        cfg.apply_and_commit()

    


class GlobeSettingsWindow(PopupWindow):
    def __init__(self):
        self._transitioning_out = False
        self._r = 'globeSettings'
        width = 520
        height = 365
        super().__init__(
            size=(width, height),
            position=(0, 0),
            scale=1,
            bg_color=None
        )
        back_button = bui.buttonwidget(
            parent=self.root_widget,
            position=(35, height - 50),
            size=(60, 60),
            scale=0.8,
            text_scale=1.2,
            autoselect=True,
            icon=bui.gettexture('crossOut'),
            button_type='backSmall',
            on_activate_call=self._close,
        )
        bui.containerwidget(edit=self.root_widget, cancel_button=back_button)

        v = height - 10

        bui.textwidget(
            parent=self.root_widget,
            position=(width * 0.5, v),
            size=(0, 0),
            h_align='center',
            v_align='top',
            scale=1.2,
            text='Globe Settings',
            color=(1, 1, 1, 1)
        )

        v -= 120 

        # Disable Messages
        self._disable_messages = bui.checkboxwidget(
            parent=self.root_widget,
            position=(50, v),
            size=(300, 30),
            text=bui.Lstr(r=f'{self._r}.disableMessagesText'),
            value=bui.app.config.get('GUMMY_disable_messages', False),
            on_value_change_call=self._on_disable_messages
        )

        v -= 80 

        # Message Frequency
        bui.textwidget(
            parent=self.root_widget,
            position=(50, v + 20),
            size=(0, 0),
            text=bui.Lstr(r=f'{self._r}.msgFrequencyText'),
            h_align='left',
            v_align='center',
            scale=1.0,
            color=(1, 1, 1)
        )

        PopupMenu(
            parent=self.root_widget,
            position=(290, v),
            width=150,
            choices=['Low', 'Medium', 'High'],
            current_choice=bui.app.config.get('GUMMY_message_frequency', 'Medium'),
            on_value_change_call=self._on_msg_frequency
        )

        v -= 110 

        # Toggle the Globe
        self._toggle_globe = bui.checkboxwidget(
            parent=self.root_widget,
            position=(50, v),
            size=(300, 30),
            text=bui.Lstr(r=f'{self._r}.toggleGlobeText'),
            value=bui.app.config.get('GUMMY_toggle_globe', True),
            on_value_change_call=self._on_toggle_globe
        )
    def _on_disable_messages(self, val: bool):
        cfg = bui.app.config
        cfg['GUMMY_disable_messages'] = val
        cfg.apply_and_commit()

    def _on_msg_frequency(self, val: str):
        cfg = bui.app.config
        cfg['GUMMY_message_frequency'] = val
        cfg.apply_and_commit()

    def _on_toggle_globe(self, val: bool):
        cfg = bui.app.config
        cfg['GUMMY_toggle_globe'] = val
        cfg.apply_and_commit()

    def _close(self):
        bui.getsound('swish').play()
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition='out_right')

