# Released under the MIT License. See LICENSE for details.
#
"""Session and Activity for displaying the main menu bg."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, override
import bascenev1 as bs
import bauiv1 as bui
import babase
from bauiv1lib.popup import PopupWindow
import logging
from bascenev1lib.actor.popuptext import PopupText

if TYPE_CHECKING:
    from typing import Any



class OnlineActivity(bs.Activity[bs.Player, bs.Team]):
    """Activity showing the rotating main menu bg stuff."""

    _stdassets = bs.Dependency(bs.AssetPackage, 'stdassets@1')



    def __init__(self, settings: dict):
        super().__init__(settings)
        
        
        
        self._host_is_navigating_text: bs.NodeActor | None = None
        self._main_window_instance: GatherWindow | None = None
        self._active_popups = []
        

        
            
            
    def on_begin(self):
        super().on_begin()
        self.earth: bs.NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': (-5, 0, 0),
                    'velocity': (0, 0, 0),
                    'mesh': bs.getmesh('earth'),
                    'light_mesh': bs.getmesh('earth'),
                    'body': 'sphere',
                    'mesh_scale': 9.5,
                    'shadow_size': 0.44,
                    'gravity_scale': 0.0,
                    'color_texture': bs.gettexture('earthColor'),
                    'reflection': 'powerup',
                    'reflection_scale': [1.0],
                },
            )
       
        bs.timer(0.5, self.prop_tick, repeat=True)
    
    def prop_tick(self):
        if not self.earth.exists():
            return
        
        value = bui.app.config.get('GUMMY_message_frequency', 'Medium')
        randomvalue = 0.5 if value == 'High' else 0.35 if value == 'Medium' else 0.2
        if random.random() < randomvalue: 
            if bui.app.config.get('GUMMY_disable_messages', False):
                self._spawn_random_text(True)
            else:
                self._spawn_random_text()
                #self._send_online_message()
                
            
               

        
    
    def _spawn_random_text(self, force_random: bool = False):
        if random.randint(0, 7) == 0 or force_random:
            # Generate a fake player message with random username and flag (to avoid repetition)
            phrases = [
                "Hello from space!",
                "Is anybody out there?",
                "Random popup text!",
                "The Earth says hi!",
                "Spinning around...",
                "What a cool day!",
                "Greetings from afar!",
                "Just chilling in orbit.",
                "Enjoying the view!",
                "Hi everyone!"
            ]
            FLAGS = [
                babase.SpecialChar.FLAG_UNITED_STATES,
                babase.SpecialChar.FLAG_MEXICO,
                babase.SpecialChar.FLAG_GERMANY,
                babase.SpecialChar.FLAG_BRAZIL,
                babase.SpecialChar.FLAG_RUSSIA,
                babase.SpecialChar.FLAG_CHINA,
                babase.SpecialChar.FLAG_UNITED_KINGDOM,
                babase.SpecialChar.FLAG_CANADA,
                babase.SpecialChar.FLAG_INDIA,
                babase.SpecialChar.FLAG_JAPAN,
                babase.SpecialChar.FLAG_FRANCE,
                babase.SpecialChar.FLAG_INDONESIA,
                babase.SpecialChar.FLAG_ITALY,
                babase.SpecialChar.FLAG_SOUTH_KOREA,
                babase.SpecialChar.FLAG_NETHERLANDS,
            ]
            username = random.choice(bs.get_random_names())
            flag_char = babase.charstr(random.choice(FLAGS))
            message = random.choice(phrases)
            text = f'"{message}"\n-{username} ({flag_char})'
            self._spawn_text(text)
        else:
            self._send_online_message()
            

    def _send_online_message(self):
        from gummyoverhaul.earth_submit import get_world_messages

        def on_messages(msg_list):
            if not msg_list:
                # Fetch failed or empty; show random fallback
                self._spawn_random_text(force_random=True)
                return

            import random
            msg = random.choice(msg_list)
            name = msg['username']
            flag = msg['flag']
            message = msg['message']
            text = (
                f'{message}\n'
                f'-{name} ({flag})'
            )
            self._spawn_text(text)

        try:
            get_world_messages(on_messages)
        except Exception:
            # In case the fetch itself throws an error
            self._spawn_random_text(force_random=True)


    def _spawn_text(self, text):
        if self.expired:
            return
        try:
            with self.context:
                base_x = self.earth.position[0]
                base_y = self.earth.position[1] + 3
                z = self.earth.position[2]

               

                slots = [-2.4, -1.2, 0, 1.2, 2.4]

                y_offset = sum([p['spacing'] for p in self._active_popups[-5:]])
                y = base_y + y_offset
                used_slots = [p['x_offset'] for p in self._active_popups[-5:]]
                available_slots = [s for s in slots if s not in used_slots]
                if available_slots:
                    x_offset = random.choice(available_slots)
                else:
                    x_offset = random.choice(slots)
                x = base_x + x_offset
                popup = PopupText(
                    text,
                    position=(x, y, z),
                    color=bs.safecolor((random.random(), random.random(), random.random())),
                    scale=2.0 if bs.app.ui_v1.uiscale is bs.UIScale.SMALL else 1.5,
                    lifespan=2.5
                )
                popup.autoretain()
                self._active_popups.append({'popup': popup, 'spacing': 1.2, 'x_offset': x_offset})
                def remove_popup():
                    self._active_popups = [p for p in self._active_popups if p['popup'] is not popup]
                bs.timer(2.5, remove_popup)

        except RuntimeError:
            pass
    
    def on_expire(self):
        super().on_expire()
        if self._main_window_instance:
            self._main_window_instance.main_window_close()
            self._main_window_instance = None
        self._active_popups.clear()
        

       
        
        
        

    @override
    def on_transition_in(self) -> None:
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        super().on_transition_in()
        
        
        random.seed(123)
        app = bs.app
        env = app.env
        assert app.classic is not None

        plus = bs.app.plus
        assert plus is not None

        # Throw up some text that only clients can see so they know that
        # the host is navigating menus while they're just staring at an
        # empty-ish screen.
        tval = f'- {bs.app.plus.get_v1_account_display_string(full=True, true=True)} is currently using the online browser at the moment. -'
        self._host_is_navigating_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'text': tval,
                    'client_only': True,
                    'position': (0, -200),
                    'flatness': 1.0,
                    'h_align': 'center',
                },
            )
        ).autoretain()
        

    
        
            
        
       

    

        
       
        
        
        #trees_texture = bs.gettexture('treesColor')
        bgtex = bs.gettexture('DSspace')
        bgmesh = bs.getmesh('thePadBG')

        

        gnode = self.globalsnode
        gnode.camera_mode = 'follow'
        

        gnode.tint = (0.12, 0.48, 0.59)
        gnode.ambient_color = (0.5, 0.5, 0.5)
        gnode.shadow_ortho = False
        gnode.vignette_outer = (0.76, 0.76, 0.76)
        gnode.vignette_inner = (0.95, 0.95, 0.99)

        
       
        
        
        
        self.bgterrain = bs.NodeActor(
            bs.newnode(
                'terrain',
                attrs={
                    'mesh': bgmesh,
                    'color': (0.92, 0.91, 0.9),
                    'lighting': False,
                    'background': True,
                    'color_texture': bgtex,
                },
            )
        ).autoretain()

       

        # Hopefully this won't hitch but lets space these out anyway.
        bs.add_clean_frame_callback(bs.WeakCall(self._start_preloads))

        random.seed()

        

      

        self._update_timer = bs.Timer(0.2, self._update, repeat=True)
        self._update()


    def invoke_epic_shop(self):
        
        with bs.ContextRef.empty():
            
            bui.app.ui_v1.clear_main_window()
            
            self._main_window_instance = GatherWindow(transition=None)

            bui.app.ui_v1.set_main_window(
                                self._main_window_instance,
                                is_top_level=True,
                                suppress_warning=True,
                            )
            
            
            
       
       

    def _update(self) -> None:
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        app = bs.app
        env = app.env
        assert app.classic is not None

        if self.is_transitioning_out(): 
            return

        if not self._main_window_instance:
            self.invoke_epic_shop()
        
            


    def _start_preloads(self) -> None:
        # FIXME: The func that calls us back doesn't save/restore state
        #  or check for a dead activity so we have to do that ourself.
        if self.expired:
            return
        
        music = bs.MusicType.MK8_WIFI
      
        
       

        bs.setmusic(music)




class OnlineSession(bs.Session):
    """Session that runs the main menu environment."""

    def __init__(self) -> None:
        # Gather dependencies we'll need (just our activity).
        self._activity_deps = bs.DependencySet(bs.Dependency(OnlineActivity))

        super().__init__([self._activity_deps])
        self._locked = False
        self.setactivity(bs.newactivity(OnlineActivity))
        self.max_players = 0

        



    
        

    @override
    def on_activity_end(self, activity: bs.Activity, results: Any) -> None:
        if self._locked:
            bui.unlock_all_input()

        # Any ending activity leads us into the main menu one.
        self.setactivity(bs.newactivity(OnlineActivity))


    @override
    def on_player_request(self, player: bs.SessionPlayer) -> bool:
        # Reject all player requests.
        return False


class BrowserPopup(PopupWindow):
    def __init__(self):
        width = 900
        height = 650

        self._transitioning_out = False
        super().__init__(
            position=(-145, 0),
            size=(width, height),
            scale=1.0,
            has_background=False,
            bg_color=None,
            toolbar_visibility='no_menu_minimal',
        )

        # Title
        bui.textwidget(
            parent=self.root_widget,
            position=(width * 0.3, height - 54),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.3,
            text='Browser',
            color=(1, 1, 1, 1),
        )
        # Close button
        bui.buttonwidget(
            parent=self.root_widget,
            label=babase.charstr(babase.SpecialChar.BACK),
            size=(50, 50),
            position=(width - 870, height - 60),
            color=(1, 0, 0),
            on_activate_call=self.close
        )
        bui.containerwidget(edit=self.root_widget, on_cancel_call=self.close)

        try:

            from bauiv1lib.gather.publictab import PublicGatherTab
            from bauiv1lib.gather.privatetab import PrivateGatherTab

        except Exception:
            logging.exception('Failed to import gather tabs')
            return
        



        class _DummyGatherWindow:
            def __init__(self, root):
                self._root_widget = root

        dummy_root = _DummyGatherWindow(self.root_widget)
        self._public_tab = PublicGatherTab(dummy_root)
        self._private_tab = PrivateGatherTab(dummy_root)


        # Activate only the public tab initially
        self._active_tab = None

        def activate_tab(tab):
            if self._active_tab is tab:
                return
            # Deactivate current tab
            if self._active_tab is not None:
                # Remove all children widgets of the container
                if hasattr(self._active_tab, '_container') and self._active_tab._container:
                    for widget in list(self._active_tab._container.get_children()):
                        widget.delete()
                if hasattr(self._active_tab, 'on_deactivate'):
                    self._active_tab.on_deactivate()
            # Activate new tab
            tab.on_activate(
                parent_widget=self.root_widget,
                tab_button=self.root_widget,
                region_width=width,
                region_height=height - 60,
                region_left=0,
                region_bottom=0,
            )
            self._active_tab = tab

        def switch_to_public():
            activate_tab(self._public_tab)

        def switch_to_private():
            #activate_tab(self._private_tab)
            bs.screenmessage('Private Tab Breaks here\nBut be honest, who even uses this?', color=(1,0,0))
            bui.getsound('error').play()


        activate_tab(self._public_tab)

        bui.buttonwidget(
            parent=self.root_widget,
            label='Public',
            size=(100, 50),
            position=(width * 0.7  - 120, height - 80),
            on_activate_call=switch_to_public,
        )
        bui.buttonwidget(
            parent=self.root_widget,
            label='Private',
            size=(100, 50),
            position=(width * 0.7 + 20, height - 80),
            on_activate_call=switch_to_private,
        )
        

        self._check_timer = bui.apptimer(0.1, self._periodic_checks)

    def _periodic_checks(self):
        if self._transitioning_out:
            return
        if self._active_tab:
            if self._active_tab.should_close:
                self.close()
                return
        self._check_timer = bui.apptimer(0.1, self._periodic_checks)

    
   
    def close(self):
        if self._transitioning_out:
            return
        self._transition_out()

        if hasattr(self, '_check_timer') and self._check_timer:
            self._check_timer = None

        if hasattr(self, '_active_tab') and self._active_tab is not None:
            if hasattr(self._active_tab, 'on_deactivate'):
                self._active_tab.on_deactivate()
            if hasattr(self._active_tab, '_container') and self._active_tab._container:
                for w in list(self._active_tab._container.get_children()):
                    w.delete()
            self._active_tab = None

        for tab_attr in ['_public_tab', '_private_tab']:
            tab = getattr(self, tab_attr, None)
            if tab is not None:
                if hasattr(tab, '_container') and tab._container:
                    for w in list(tab._container.get_children()):
                        w.delete()
                setattr(self, tab_attr, None)

        if hasattr(self, 'root_widget') and self.root_widget:
            self.root_widget.delete()
            self.root_widget = None
        
    def _transition_out(self, transition: str = 'out_scale') -> None:
        bui.getsound('swish').play()
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition=transition)


class ManualNearbyPopup(PopupWindow):
    def __init__(self):
        width = 900
        height = 750

        self._transitioning_out = False
        super().__init__(
            position=(-145, 0),
            size=(width, height),
            scale=1.0,
            has_background=False,
            bg_color=None,
            toolbar_visibility='no_menu_minimal',
        )

        # Title
        bui.textwidget(
            parent=self.root_widget,
            position=(width * 0.3, height - 54),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.3,
            text='Manual / Nearby',
            color=(1, 1, 1, 1),
        )
        # Close button
        bui.buttonwidget(
            parent=self.root_widget,
            label=babase.charstr(babase.SpecialChar.BACK),
            size=(50, 50),
            position=(width - 870, height - 60),
            color=(1, 0, 0),
            on_activate_call=self.close
        )
        bui.containerwidget(edit=self.root_widget, on_cancel_call=self.close)
        from bauiv1lib.gather.nearbytab import NearbyGatherTab
        from bauiv1lib.gather.manualtab import ManualGatherTab

     
      

        class _DummyGatherWindow:
            def __init__(self, root):
                self._root_widget = root

        dummy_root = _DummyGatherWindow(self.root_widget)
        self._manual_tab = ManualGatherTab(dummy_root)
        self._nearby_tab = NearbyGatherTab(dummy_root)

        self._manual_tab.on_activate(
            parent_widget=self.root_widget,
            tab_button=self.root_widget,
            region_width=width,
            region_height=height - 60,
            region_left=0,
            region_bottom=0,
        )

        def switch_to_manual():
            if getattr(self, '_active_tab', None) is self._manual_tab:
                return
            if getattr(self, '_active_tab', None) is not None:
                for widget in list(self._active_tab._container.get_children()):
                    widget.delete()
                self._active_tab.on_deactivate()
            self._manual_tab.on_activate(
                parent_widget=self.root_widget,
                tab_button=self.root_widget,
                region_width=width,
                region_height=height - 60,
                region_left=0,
                region_bottom=0,
            )
            self._active_tab = self._manual_tab

        def switch_to_nearby():
            if getattr(self, '_active_tab', None) is self._nearby_tab:
                return
            if getattr(self, '_active_tab', None) is not None:
                for widget in list(self._active_tab._container.get_children()):
                    widget.delete()
                self._active_tab.on_deactivate()
            self._nearby_tab.on_activate(
                parent_widget=self.root_widget,
                tab_button=self.root_widget,
                region_width=width,
                region_height=height - 60,
                region_left=0,
                region_bottom=0,
            )
            self._active_tab = self._nearby_tab

        self._active_tab = self._manual_tab

        bui.buttonwidget(
            parent=self.root_widget,
            label='Manual',
            size=(100, 50),
            position=(width * 0.7 - 120, height - 80),
            on_activate_call=switch_to_manual,
        )
        bui.buttonwidget(
            parent=self.root_widget,
            label='Nearby',
            size=(100, 50),
            position=(width * 0.7 + 20, height - 80),
            on_activate_call=switch_to_nearby,
        )
        
    def close(self):
        if self._transitioning_out:
            return
        self._transition_out()

        # Deactivate tabs first
        if hasattr(self, '_active_tab') and self._active_tab is not None:
            if hasattr(self._active_tab, 'on_deactivate'):
                self._active_tab.on_deactivate()
            if hasattr(self._active_tab, '_container') and self._active_tab._container:
                for w in list(self._active_tab._container.get_children()):
                    w.delete()
            self._active_tab = None

        # Delete manual/nearby tabs to break cycles
        if hasattr(self, '_manual_tab'):
            if hasattr(self._manual_tab, '_container') and self._manual_tab._container:
                for w in list(self._manual_tab._container.get_children()):
                    w.delete()
            self._manual_tab = None

        if hasattr(self, '_nearby_tab'):
            if hasattr(self._nearby_tab, '_container') and self._nearby_tab._container:
                for w in list(self._nearby_tab._container.get_children()):
                    w.delete()
            self._nearby_tab = None

        # Delete root widget
        if hasattr(self, 'root_widget') and self.root_widget:
            self.root_widget.delete()
            self.root_widget = None

    def _transition_out(self, transition: str = 'out_scale') -> None:
        bui.getsound('swish').play()
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition=transition)

class MessageInputPopup(PopupWindow):

    def __init__(self):
        
        width = 600
        height = 250
        self._transitioning_out = False

        super().__init__(
            position=(-145, 0),
            size=(width, height),
            scale=1.0,
            has_background=False,
            bg_color=(0.2, 0.2, 0.2),
            toolbar_visibility='no_menu_minimal'
        )
        bui.buttonwidget(
            parent=self.root_widget,
            label=babase.charstr(babase.SpecialChar.BACK),
            size=(50, 50),
            position=(width - 620, height - 60),
            color=(1, 0, 0),
            on_activate_call=self.close
        )
        bui.containerwidget(edit=self.root_widget, on_cancel_call=self.close)

        bui.textwidget(
            parent=self.root_widget,
            position=(width * 0.5, height - 50),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.0,
            text='Submit a message to be seen on the earth',
            color=(1, 1, 1, 1)
        )
        bui.textwidget(
            parent=self.root_widget,
            position=(width * 0.5, height - 280),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.85,
            text='WARNING:\nYour message is permanent and will be seen by everyone.',
            color=(1, 0, 0, 1)
        )

        self._text_field = bui.textwidget(
            parent=self.root_widget,
            position=(50, height - 150),
            size=(width - 100, 38),
            text='',
            max_chars=30,
            editable=True,
            color=(1, 1, 1),
            on_return_press_call=self._submit
        )

        bui.buttonwidget(
            parent=self.root_widget,
            label='Submit',
            size=(150, 50),
            position=(width * 0.5 - 75, 20),
            on_activate_call=self._submit
        )
    def close(self):  
        self._transition_out()


    def _transition_out(self, transition: str = 'out_scale') -> None:
        bui.getsound('swish').play()
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition=transition)

    def _submit(self):
        text = bui.textwidget(query=self._text_field)
        if text.strip():
            self._on_submit(text.strip())
        self.close()
    
    def _on_submit(self, text: str):
        from gummyoverhaul.earth_submit import submit_world_message
        submit_world_message(text)


class MessageListPopup(PopupWindow):
    """Popup showing all online world messages in a scroll list."""

    def __init__(self):
        width = 750
        height = 650

        self._transitioning_out = False
        super().__init__(
            position=(-145, 0),
            size=(width, height),
            scale=1.0,
            has_background=False,
            bg_color=(0.2, 0.2, 0.2),
            toolbar_visibility='no_menu_minimal'
        )

        bui.buttonwidget(
            parent=self.root_widget,
            label=babase.charstr(babase.SpecialChar.BACK),
            size=(50, 50),
            position=(width - 820, height - 60),
            color=(1, 0, 0),
            on_activate_call=self.close
        )
        bui.containerwidget(edit=self.root_widget, on_cancel_call=self.close)

        bui.textwidget(
            parent=self.root_widget,
            position=(width * 0.5, height - 60),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.1,
            text='World Messages',
            color=(1, 1, 1, 1)
        )

        # Scroll area container
        self._scroll = bui.scrollwidget(
            parent=self.root_widget,
            position=(40, 60),
            size=(width - 80, height - 140),
            simple_culling_v=10.0
        )

        self._content = bui.columnwidget(parent=self._scroll)

        self._load_messages()

    def _load_messages(self):
        from gummyoverhaul.earth_submit import get_world_messages

        def _done(msg_list):
            if not msg_list:
                bui.textwidget(
                    parent=self._content,
                    text='No messages found or failed to load.',
                    scale=1.0,
                    color=(1, 0.3, 0.3),
                )
                return

            for msg in msg_list:
                try:
                    txt = (
                        f"{msg['message']}"
                        f" by {msg['username']} from {msg['flag']}"
                    )
                except Exception:
                    txt = str(msg)

                bui.textwidget(
                    parent=self._content,
                    text=txt,
                    h_align='left',
                    v_align='center',
                    maxwidth=620,
                    scale=0.9,
                    shadow=1.0,
                    color=(1, 1, 1),
                )

        try:
            get_world_messages(_done)
        except Exception:
            bui.textwidget(
                parent=self._content,
                text='Error fetching messages.',
                scale=1.0,
                color=(1, 0.3, 0.3),
            )

    def close(self):
        self._transition_out()

    def _transition_out(self, transition: str = 'out_scale') -> None:
        bui.getsound('swish').play()
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition=transition)



class GatherWindow(bui.MainWindow):
    """Window for joining/inviting friends."""


    def __init__(
        self,
        transition: str | None = 'in_right',
        origin_widget: bui.Widget | None = None,

    ):
        # pylint: disable=too-many-locals
        # pylint: disable=cyclic-import
       
        
        plus = bui.app.plus
        assert plus is not None

        bui.set_analytics_screen('Gather Window')
        uiscale = bui.app.ui_v1.uiscale
        scale = 1.0
        extra_x = 425
        startup = plus.startup
     
  
       
        
        super().__init__(root_widget=bui.containerwidget(
            size=(320, 450),
            toolbar_visibility='no_menu_minimal',
            scale=scale,
            background=False
        ), 
        transition=transition,
          origin_widget=origin_widget
          )
        
       

  
            

        bui.textwidget(
                parent=self._root_widget,
                position=(290*0.5+extra_x, 400),
                size=(20, 20),
                h_align='center',
                v_align='center',
                scale=1.2,
                text='Gather',
                color=(1, 1, 1, 1)
        )

        bui.buttonwidget(
                parent=self._root_widget,
                label='Browser',
                button_type=None,
                size=(240, 80),
                position=(40+extra_x, 300),
                on_activate_call=BrowserPopup
        )

        bui.buttonwidget(
                parent=self._root_widget,
                label='Manual',
                button_type=None,
                size=(240, 80),
                position=(40+extra_x, 200),
                on_activate_call=ManualNearbyPopup
        )
        


        back_button = bui.buttonwidget(
                parent=self._root_widget,
                label='Exit',
                button_type=None,
                size=(240, 80),
                position=(40+extra_x, 100),
                on_activate_call=bui.WeakCall(bs.app.classic.return_to_main_menu_session_gracefully)
        )
        bui.containerwidget(edit=self._root_widget, cancel_button=back_button)
        xx_x = 43
        bui.buttonwidget(
                parent=self._root_widget,
                icon=bui.gettexture('chatLogLogo'),
                size=(65, 65),
                button_type=None,
                position=(40+extra_x+xx_x, 20),
                on_activate_call=MessageInputPopup
        )
        bui.buttonwidget(
                parent=self._root_widget,
                size=(65, 65),
                button_type=None,
                position=(140+extra_x+xx_x, 20),
                icon=bui.gettexture('SubmitLogo'),
                on_activate_call=MessageListPopup
        )
        
        



         
        
    @override
    def get_main_window_state(self) -> bui.MainWindowState:
        # Support recreating our window for back/refresh purposes.
        from bauiv1lib.mainmenu import MainMenuWindow
        cls = type(self)
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition, origin_widget=origin_widget
            )
        )