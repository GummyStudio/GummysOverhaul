# Released under the MIT License. See LICENSE for details.
#
"""Provides help related ui."""

from __future__ import annotations

from typing import override

import bauiv1 as bui
import babase
from bauiv1lib.popup import PopupWindow



class InventoryWindow(bui.MainWindow):
    """Shows what you got."""

    def __init__(
        self,
        transition: str | None = 'in_right',
        origin_widget: bui.Widget | None = None,
    ):

        bui.set_analytics_screen('Help Window')

        assert bui.app.classic is not None
        uiscale = bui.app.ui_v1.uiscale
        self._width = 1400 if uiscale is bui.UIScale.SMALL else 750
        self._height = (
            1200
            if uiscale is bui.UIScale.SMALL
            else 530 if uiscale is bui.UIScale.MEDIUM else 600
        )
        # xoffs = 70 if uiscale is bui.UIScale.SMALL else 0
        # yoffs = -45 if uiscale is bui.UIScale.SMALL else 0

        # Do some fancy math to fill all available screen area up to the
        # size of our backing container. This lets us fit to the exact
        # screen shape at small ui scale.
        screensize = bui.get_virtual_screen_size()
        scale = (
            1.55
            if uiscale is bui.UIScale.SMALL
            else 1.15 if uiscale is bui.UIScale.MEDIUM else 1.0
        )

        # Calc screen size in our local container space and clamp to a
        # bit smaller than our container size.
        # target_width = min(self._width - 60, screensize[0] / scale)
        target_height = min(self._height - 100, screensize[1] / scale)

        # To get top/left coords, go to the center of our window and
        # offset by half the width/height of our target area.
        yoffs = 0.5 * self._height + 0.5 * target_height + 30.0

        self.allow_exit = True

        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height),
                toolbar_visibility=(
                    'menu_full' if uiscale is bui.UIScale.SMALL else 'menu_full'
                ),
                scale=scale,
            ),
            transition=transition,
            origin_widget=origin_widget,
            # We're affected by screen size only at small ui-scale.
            refresh_on_screen_size_changes=uiscale is bui.UIScale.SMALL,
        )

        bui.textwidget(
            parent=self._root_widget,
            position=(
                self._width * 0.5,
                yoffs - (50 if uiscale is bui.UIScale.SMALL else 30),
            ),
            size=(0, 0),
            text=bui.Lstr(resource='inventoryText'),
            color=bui.app.ui_v1.title_color,
            scale=0.9 if uiscale is bui.UIScale.SMALL else 1.0,
            maxwidth=(130 if uiscale is bui.UIScale.SMALL else 200),
            h_align='center',
            v_align='center',
        )

        if uiscale is bui.UIScale.SMALL:
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self.main_window_back
            )
        else:
            btn = bui.buttonwidget(
                parent=self._root_widget,
                position=(50, yoffs - 50),
                size=(60, 55),
                scale=0.8,
                label=bui.charstr(bui.SpecialChar.BACK),
                button_type='backSmall',
                extra_touch_border_scale=2.0,
                autoselect=True,
                on_activate_call=self.main_window_back,
            )
            bui.containerwidget(edit=self._root_widget, cancel_button=btn)

        button_width = 300
        self._player_profiles_button = btn = bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width * 0.5 - button_width * 0.5, yoffs - 200),
            autoselect=True,
            size=(button_width, 60),
            label=bui.Lstr(resource='playerProfilesWindow.titleText'),
            color=(0.55, 0.5, 0.6),
            icon=bui.gettexture('cuteSpaz'),
            textcolor=(0.75, 0.7, 0.8),
            on_activate_call=self._player_profiles_press,
        )
        yoffs -= 110
        x = self._width * 0.5 - 100
        x_extra = 180

        
        self._subcontainerwidth = self._width * 0.2
        self._subcontainerheight = self._height * 0.70
        self._container_default_height = self._subcontainerheight

        if not uiscale is bui.UIScale.SMALL:
            
            self._scrollwidget = bui.scrollwidget(
                parent=self._root_widget,
                highlight=False,
                size=(self._width * 0.2, self._height * 0.70),
                position=(
                    self._width * 0.74,
                    self._height * 0.1,
                ),
                simple_culling_v=10.0,
                selection_loops_to_parent=True,
                border_opacity=0.8,
            )
            self._subcontainer = bui.containerwidget(
                parent=self._scrollwidget,
                size=(self._subcontainerwidth, self._subcontainerheight),
                background=False,
                claims_left_right=True,
                selection_loops_to_parent=True,
            )
            bui.textwidget(
                parent=self._root_widget,
                position=(
                    self._width * 0.84,
                    yoffs - (50 if uiscale is bui.UIScale.SMALL else 30) + (75 if uiscale is bui.UIScale.MEDIUM else 60),
                ),
                size=(0, 0),
                text='Overhaul Chests',
                color=bui.app.ui_v1.title_color,
                scale=0.9 if uiscale is bui.UIScale.SMALL else 1.0,
                maxwidth=(130 if uiscale is bui.UIScale.SMALL else 200),
                h_align='center',
                v_align='center',
            )
        else:
            self._scrollwidget = None
            self._subcontainer = None

        # gumcoin text
        self.coin_count = bui.textwidget(
            parent=self._root_widget,
            position=(x, yoffs),
            size=(self._width, 25),
            text=str(babase.app.config.get('GUMMY_gumcoins', 0)),
            color=(1, 1, 1),
            h_align='left',
            v_align='top',
            maxwidth=80
        )
        
        # gumcoin image
        bui.imagewidget(
            parent=self._root_widget,
            size=(50, 50),
            position=(x - 65, yoffs - 15),
            texture=bui.gettexture('gumcoin'),
        )

        # gumdollar text
        self.dollar_count = bui.textwidget(
            parent=self._root_widget,
            position=(x + x_extra, yoffs),
            size=(self._width, 25),
            text=str(babase.app.config.get('GUMMY_dollars', 0)),
            color=(1, 1, 1),
            h_align='left',
            v_align='top',
            maxwidth=80
        )
        
        # gumdollar image
        bui.imagewidget(
            parent=self._root_widget,
            size=(50, 50),
            position=(x - 65 + x_extra, yoffs - 15),
            texture=bui.gettexture('gumdollar'),
        )

        yoffs -= 140
        # Add a button to open the stats window.
        self.stats_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width * 0.5 - 280, yoffs),
            size=(120, 50),
            label="Stats",
            button_type=None,
            on_activate_call=self.stats_open,
        )
        yoffs -= 10
        cfg = babase.app.config
        
       

        self.chest_closed = "chestIcon"
        self.chest_closed_color = "chestIconTint"

        self.chest_open = "chestOpenIcon"
        self.chest_open_color = "chestOpenIconTint"

        self.slot_data = cfg["gummy_chestinslot"] 
        
        # exmaple ig
        {
            "type": "coins",
            "name": "Test Chest",
            "color": (1, 0.84, 0),
            "tint": (1, 0.9, 0.2),
            "tint2": (1, 1, 0.6),
            "rewards": 1
        }
        imgsize = 100
        yoffs -=  50 if uiscale is bui.UIScale.MEDIUM else  57
        self.off_centr = 60
        self.back = 10
        
        if self.slot_data:
            
            self.chest = bui.imagewidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - imgsize * 0.5 - self.off_centr - self.back, yoffs),
                color=self.slot_data["color"],
                size=(imgsize, imgsize),
                texture=bui.gettexture(self.chest_closed),
                tint_texture=bui.gettexture(self.chest_closed_color),
                tint_color=self.slot_data["tint"],
                tint2_color=self.slot_data["tint2"],
            )
            self._yoffs = yoffs
            self.open_button = bui.buttonwidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - 60 + self.off_centr - self.back, yoffs + 20),
                size=(120, 50),
                label="Open me!",
                button_type=None,
                on_activate_call=self._open_chest,
             )
            self.chest_name = bui.textwidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - imgsize * 0.5 - self.off_centr - self.back - 13, yoffs - 9),
                size=(self._width, 25),
                text=f'{self.slot_data['name']}',
                color=(1, 1, 1, 0.5),
                h_align='left',
                v_align='top',
                maxwidth=200
            )
        else:
            bui.imagewidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - imgsize * 0.5 - self.off_centr - self.back, yoffs),
                color=(1, 1, 1),
                opacity=0.3,
                size=(imgsize, imgsize),
                texture=bui.gettexture(self.chest_closed),
                tint_texture=bui.gettexture(self.chest_closed_color),
                tint_color=(1,1,1),
                tint2_color=(1,1,1),
            )
            self.chest_name = bui.textwidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - 60 + self.off_centr - self.back, yoffs+40),
                size=(self._width, 25),
                text=f'Open Me!',
                color=(1, 1, 1, 0.5),
                h_align='left',
                v_align='top',
                maxwidth=200
            )

        yoffs -=  25

        #bui.textwidget(
        #    parent=self._root_widget,
        #    position=(self._width * 0.5, yoffs),
        #    size=(0, 0),
        #    text=bui.Lstr(resource='moreSoonText'),
        #    scale=0.7,
        #    maxwidth=self._width * 0.9,
        #    h_align='center',
        #    v_align='center',
        #)
        if bui.app.plus:
            yoffs += 40
            self.leaderboard_button = bui.buttonwidget(
                    parent=self._root_widget,
                    position=(self._width * 0.5 - 280, yoffs),
                    size=(120, 50),
                    label="Leaderboard",
                    button_type=None,
                    on_activate_call=self._open_leaderboard,
            )
        self.widget_items = []
        babase.apptimer(0.1, self._update)

        yoffs -= 40
        
        
        
        xp = cfg.get('GUMMY_xp', 0)
        level = cfg.get('GUMMY_level', 1)
        xp_to_next_level = 15 + ((level - 1) * 10)

        text = (
            f'Level {level} - XP {xp}/{xp_to_next_level}' 
            if level < 200 else
            f'Level MAX (200) - XP {xp}'
            
        )
        self.xp_text = bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.35, yoffs),
            size=(0, 0),
            text=text,
            color=(1, 1, 1),
            scale=0.9,
            h_align='center',
            v_align='center',
            maxwidth=400
        )
        yoffs -= 45
        bui.imagewidget(
            parent=self._root_widget,
            size=(200, 20),
            position=(self._width * (0.22 if not uiscale is bui.UIScale.SMALL else 0.29), yoffs),
            texture=bui.gettexture('black'),
        )
        

        self.xp_bar = bui.imagewidget(
            parent=self._root_widget,
            size=(((xp / xp_to_next_level) * 200) if level < 200 else 200, 20),
            position=(self._width * (0.22 if not uiscale is bui.UIScale.SMALL else 0.29), yoffs),
            texture=bui.gettexture('bar'),
            color=(0, 1, 1)
        )
    
    def _open_leaderboard(self):
        #bui.screenmessage('leaderboards disabled until i can fix it :/')
        #bui.getsound('error').play()
        #return
        LeaderBoardWindow(
            
        )

    def _update(self):
        # No-op if our ui is dead.
        if not self._root_widget:
            return
        cfg = babase.app.config

        
        if self.coin_count:
            bui.textwidget(edit=self.coin_count, text=str(cfg["GUMMY_gumcoins"]))
        if self.dollar_count:
            bui.textwidget(edit=self.dollar_count, text=str(cfg["GUMMY_gumdollars"]))
        xp = cfg.get('GUMMY_xp', 0)
        level = cfg.get('GUMMY_level', 1)
        xp_to_next_level = 15 + ((level - 1) * 10)


        if self.xp_text:
            
            text = (
                f'Level {level} - XP {xp}/{xp_to_next_level}' 
                if level < 200 else
                f'Level MAX (200) - XP {xp}'
                
            )
            bui.textwidget(
                edit=self.xp_text,
                text=text,
            )

        if self.xp_bar:
        
            bui.imagewidget(
                edit=self.xp_bar,
                size=(((xp / xp_to_next_level) * 200) if level < 200 else 200, 20),
            )

        if self._scrollwidget:
            for widget in self.widget_items:
                widget.delete()

            

            all_chests = []
            if cfg["gummy_chestinslot"]:
                all_chests.append(cfg["gummy_chestinslot"])
            all_chests += cfg["gummy_chestqueue"]

            spacing = 10
            size = 120
         

            # Calculate total height first
            total_height = (size + spacing + 2) * len(all_chests)
            self._subcontainerheight = total_height
            
           

            # Start yoffset from the top of container
            yoffset = self._subcontainerheight - size

            for widget in self.widget_items:
                widget.delete()

            for chest in all_chests:
                image = bui.imagewidget(
                    parent=self._subcontainer,
                    position=(0, yoffset),
                    size=(size, size),
                    color=chest['color'],
                    texture=bui.gettexture(self.chest_closed),
                    tint_texture=bui.gettexture(self.chest_closed_color),
                    tint_color=chest["tint"],
                    tint2_color=chest["tint2"],
                )
                yoffset -= size + spacing
                txt = bui.textwidget(
                    parent=self._subcontainer,
                    position=(0, yoffset + size//2),
                    size=(size, size),
                    text=chest['name'],
                    color=(1, 1, 1, 0.5),
                    scale=1.0,
                    maxwidth=100,
                    h_align='center',
                    v_align='center',
                )
                self.widget_items.extend([image, txt])
            if not all_chests:
                txt = bui.textwidget(
                    parent=self._subcontainer,
                    position=(0, yoffset + size//2 - 20),
                    size=(size, size),
                    text='You have no chests.',
                    color=(1, 1, 1, 0.5),
                    scale=1.0,
                    maxwidth=100,
                    h_align='center',
                    v_align='center',
                )
                
                self.widget_items.extend([txt])
                yoffset -= 20
                txt = bui.textwidget(
                    parent=self._subcontainer,
                    position=(0, yoffset + size//2 - 20),
                    size=(size, size),
                    text='Get chests by playing Co-op\n or Finishing FFA/Teams Games!',
                    color=(1, 1, 1, 0.5),
                    scale=1.0,
                    maxwidth=100,
                    h_align='center',
                    v_align='center',
                )
                self.widget_items.extend([txt])

            bui.containerwidget(edit=self._subcontainer, size=(self._subcontainerwidth, self._subcontainerheight))
            


                
        babase.apptimer(1, self._update)

    def _open_chest(self):
        if self.chest and self.open_button and self.slot_data:
            # No-op if our ui is dead.
            if not self._root_widget:
                return

            if not self.allow_exit:
                bui.getsound('error').play()
                return
            import random
            self.allow_exit = False
            self.chest.delete()

            # Award rewards immediately and store for animation
            xp_reward = random.randint(1, 4)
            cfg = babase.app.config
            if self.slot_data['type'] == 'coins':
                reward = self.slot_data['rewards']
                cfg["GUMMY_gumcoins"] += reward
                bui.getsound('cashRegister').play()
                coins_reward = reward
                dollars_reward = 0
            elif self.slot_data['type'] == 'dollars':
                reward = self.slot_data['rewards']
                cfg["GUMMY_gumdollars"] += reward
                bui.getsound('secretKey').play(1.3)
                coins_reward = 0
                dollars_reward = reward
            elif self.slot_data['type'] == 'both':
                coins_reward = self.slot_data['coins']
                dollars_reward = self.slot_data['dollars']
                cfg["GUMMY_gumcoins"] += coins_reward
                cfg["GUMMY_gumdollars"] += dollars_reward
                bui.getsound('cashRegister').play()
                bui.getsound('secretKey').play(1.3)
            else:
                coins_reward = 0
                dollars_reward = 0

            bui.app.plus.xp_sys.award_xp(xp_reward, True, scrnmessage=False)

            # Always clear the current chest slot
            old_data = cfg["gummy_chestinslot"]
            cfg["gummy_chestinslot"] = {}
            if cfg["gummy_chestqueue"]:
                next_chest = cfg["gummy_chestqueue"].pop(0)
                cfg["gummy_chestinslot"] = next_chest
            cfg.apply_and_commit()
            self.slot_data = cfg["gummy_chestinslot"]

            # Popup animation for opening chest with shake then open

            # this is so unoptimized but i NEED sleep bro 🥹
            popup = ChestOpenPopup(old_data, self.slot_data)
            def swing_and_open():
             
               

                steps = 6
                
                
                babase.apptimer((steps + 2) * 0.05, lambda: popup.show_chest_rewards(xp_reward, coins_reward, dollars_reward))

            babase.apptimer(0, swing_and_open)
            babase.apptimer(1.5, self.reset_)
    
    def reset_(self):
        # No-op if our ui is dead.
        if not self._root_widget:
            return
        
       

        cfg = babase.app.config
        

        

      

        
        self.slot_data = cfg["gummy_chestinslot"] 
        imgsize = 100


        if self.slot_data:
            if self.chest:
                self.chest.delete()
            if self.chest_name:
                self.chest_name.delete()
            self.chest = bui.imagewidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - imgsize * 0.5 - self.off_centr - self.back, self._yoffs),
                color=self.slot_data["color"],
                size=(imgsize, imgsize),
                texture=bui.gettexture(self.chest_closed),
                tint_texture=bui.gettexture(self.chest_closed_color),
                tint_color=self.slot_data["tint"],
                tint2_color=self.slot_data["tint2"],
            )
            self.chest_name = bui.textwidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - imgsize * 0.5 - self.off_centr - self.back - 13, self._yoffs - 9),
                size=(self._width, 25),
                text=f'{self.slot_data['name']}',
                color=(1, 1, 1, 0.5),
                h_align='left',
                v_align='top',
                maxwidth=200
            )
        else:
            if self.chest:
                self.chest.delete()
            if self.open_button:
                self.open_button.delete()
            if self.chest_name:
                self.chest_name.delete()

            bui.imagewidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - imgsize * 0.5 - self.off_centr - self.back, self._yoffs),
                color=(1, 1, 1),
                opacity=0.15,
                size=(imgsize, imgsize),
                texture=bui.gettexture(self.chest_closed),
                tint_texture=bui.gettexture(self.chest_closed_color),
                tint_color=(1,1,1),
                tint2_color=(1,1,1),
            )
            self.chest_name = bui.textwidget(
                parent=self._root_widget,
                position=(self._width * 0.5 - 60 + self.off_centr - self.back, self._yoffs+40),
                size=(self._width, 25),
                text=f'Open Me!',
                color=(1, 1, 1, 0.15),
                h_align='left',
                v_align='top',
                maxwidth=200
            )
       


        self.allow_exit = True


    

  
    

    def _player_profiles_press(self) -> None:
        # pylint: disable=cyclic-import
        from bauiv1lib.profile.browser import ProfileBrowserWindow

        # no-op if our underlying widget is dead or on its way out.
        if not self._root_widget or self._root_widget.transitioning_out:
            return

        self.main_window_replace(
            ProfileBrowserWindow(origin_widget=self._player_profiles_button)
        )

    def stats_open(self) -> None:

      
        StatsWindow()
        

    @override
    def get_main_window_state(self) -> bui.MainWindowState:
        # Support recreating our window for back/refresh purposes.
        cls = type(self)
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition, origin_widget=origin_widget
            )
        )

class StatsWindow(PopupWindow):
    """A popup window for showing stats in a vertical layout."""
    def __init__(
        self,
    ):
        self._width = 340
        self._height = 390
        super().__init__(
            position=(0, 0),
            size=(self._width, self._height),
            scale=1.4,
            bg_color=None,
        )
        self._transitioning_out = False
        cfg = babase.app.config
        stats = [
            ('CRITICAL HITS:', 'GUMMY_statscrit', (0.2,1,0.2)),
            ('MINI CRITS:', 'GUMMY_statsminicrit', (1,1,0.2)),
            ('SHIELD BREAKS:', 'GUMMY_statsshieldbreaks', (0,1,1)),
            ('BOLTEDs:', 'GUMMY_statsbolteds', (1,1,1)),
            ('MINEXECUTIONs:', 'GUMMY_statsminexecutions', (1,0.5,0)),
            ("IMPULS'Ds:", 'GUMMY_statsimpulsd', (0.5,0.25,1)),
            ('GOLD STATUES:', 'GUMMY_statsgoldstatue', (1,1,0)),
            ('ANKLES BROKEN:', "GUMMY_statsbrokenankles", (0.8, 0.8, 0.8))
        ]
        y = self._height - 68
        bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height - 35),
            size=(0, 0),
            text='Stats',
            color=(1, 1, 1),
            scale=1.2,
            maxwidth=self._width * 0.8,
            h_align='center',
            v_align='center',
        )
        for label, key, color in stats:
            bui.textwidget(
                parent=self.root_widget,
                position=(40, y),
                size=(0, 0),
                text=label,
                color=color,
                h_align='left',
                v_align='center',
                maxwidth=180,
                scale=0.95,
            )
            bui.textwidget(
                parent=self.root_widget,
                position=(self._width - 60, y),
                size=(0, 0),
                text=str(cfg.get(key, '0')),
                color=(1, 1, 1),
                h_align='right',
                v_align='center',
                maxwidth=70,
                scale=0.95,
            )
            y -= 30
        self._cancel_button = bui.buttonwidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - 60, 22),
            size=(120, 50),
            label="Close",
            color=(0.42, 0.73, 0.2),
            on_activate_call=self._on_cancel_press,
            autoselect=True,
            icon=None,
            iconscale=1.1,
        )
        bui.containerwidget(
            edit=self.root_widget,
            cancel_button=self._cancel_button,
        )

    def _on_cancel_press(self):
        self._transition_out()
       
    def _transition_out(self, transition: str = 'out_scale') -> None:
        bui.getsound('swish').play()
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition=transition)

class ChestOpenPopup(PopupWindow):
    """Popup animation shown when opening a chest."""

    def __init__(self, chest_data, next_chest):
        self._width = 420
        self._height = 300
        super().__init__(
            position=(0, 0),
            size=(self._width, self._height),
            scale=1.6,
            bg_color=None
        )

        self._transitioning_out = False
        imgsize = 120

        bui.getsound('hiss').play()
        babase.apptimer(0.1, lambda: bui.getsound('chestOpen01').play(2.5))

        # Chest image
        self.chest = bui.imagewidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - imgsize * 0.5, self._height * 0.55),
            size=(imgsize, imgsize),
            color=chest_data['color'],
            texture=bui.gettexture("chestOpenIcon"),
            tint_texture=bui.gettexture("chestOpenIconTint"),
            tint_color=chest_data["tint"],
            tint2_color=chest_data["tint2"],
        ) 
        import random
        
        self._cancel_button = bui.buttonwidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - 60, 15),
            size=(120, 40),
            label=random.choice([
                'Nice!','Rigged','scammed', 'Thanks i hate it', 'wow!',
                'Yummy', 'yummres','Wow ill be\nsure to use this','kil it','Ok lol'
            ]),
            on_activate_call=self._on_cancel_press,
            autoselect=True,
        )

        bui.containerwidget(
            edit=self.root_widget,
            cancel_button=self._cancel_button,
        )
    def show_chest_rewards(self, xp: int, coins: int, dollars: int):
        x=160
        y=125
   
        bui.textwidget(
            parent=self.root_widget,
            position=(x, y+40),
            size=(0, 0),
            text=f"+{xp} XP",
            scale=1.0,
            color=(1, 0.8, 0.7),
            h_align='center'
        )
        bui.textwidget(
            parent=self.root_widget,
            position=(x+40, y),
            size=(0, 0),
            text=f"+{coins} Coins",
            scale=1.0,
            color=(0, 0.85, 1),
            h_align='center'
        )
        bui.textwidget(
            parent=self.root_widget,
            position=(x+80, y-40),
            size=(0, 0),
            text=f"+{dollars} Dollars",
            scale=1.0,
            color=(0, .7, 1),
            h_align='center'
        )

    def _on_cancel_press(self):
        self._transition_out()

    def _transition_out(self, transition: str = 'out_scale') -> None:
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.getsound('swish').play()
            bui.containerwidget(edit=self.root_widget, transition=transition)

class LeaderBoardWindow(PopupWindow):
    """A popup window for showing overhaul's epic leaderboard"""

    def __init__(
        self,
    ):
        # FIXME: Tidy this up.
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        

        self._r = 'gameListWindow'
        
        self._transitioning_out = False
        self._width = 500
        self._height = 350

        
        # Creates our _root_widget.
        super().__init__(
            position=(0, 0), size=(self._width, self._height), scale=2, bg_color=None
        )
        self._subcontainerwidth = self._width
        self._subcontainerheight = 0
        self._scrollwidget = bui.scrollwidget(
                parent=self.root_widget,
                highlight=False,
                size=(self._width * 0.9, (self._height * 0.7) - 30),
                position=(
                    self._width * 0.05,
                    self._height * 0.1,
                ),
                simple_culling_v=10.0,
                selection_loops_to_parent=True,
                border_opacity=0.8,
            )
        self._subcontainer = bui.containerwidget(
                parent=self._scrollwidget,
                size=(self._subcontainerwidth, self._subcontainerheight),
                background=False,
                claims_left_right=True,
                selection_loops_to_parent=True,
            )

        # Create a spinner widget, because we're loading from a server.
        self._join_status_spinner = bui.spinnerwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.5),
            style='bomb',
            size=64,
        )

        
        self._title_text = bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height - 89 + 51),
            size=(0, 0),
            text='Leaderboard',
            scale=1.4,
            color=(1, 1, 1),
            maxwidth=self._width * 0.7,
            h_align='center',
            v_align='center',
        )

        self._cancel_button = bui.buttonwidget(
            parent=self.root_widget,
            position=(25, self._height - 53),
            size=(50, 50),
            scale=0.7,
            label='',
            color=(0.42, 0.73, 0.2),
            on_activate_call=self._on_cancel_press,
            autoselect=True,
            icon=bui.gettexture('crossOut'),
            iconscale=1.2,
        )

        bui.containerwidget(
            edit=self.root_widget,
            cancel_button=self._cancel_button,
        )
        self.failed = False

        # Update now and once per second.
        self._update_timer = bui.AppTimer(
            4, bui.WeakCall(self._update), repeat=True
        )
        bui.apptimer(1, self._update)
        bui.apptimer(0.2, self._start_async_update)
        self.entries = []

    def _start_async_update(self):
        # Run the server fetch in a background thread.
        import threading
        threading.Thread(
            target=self._fetch_data_threaded,
            daemon=True
        ).start()

    def _fetch_data_threaded(self):
        import urllib.request, json
        try:
            URL = bui.app.plus.get_gummysoverhaul_server_url()
            with urllib.request.urlopen(f"{URL}/leaderboards.json") as f:
                players_data = json.loads(f.read().decode()) or {}
            with urllib.request.urlopen(f"{URL}/banned.json") as f:
                banned_data = json.loads(f.read().decode()) or {}

            # Store into instance variables
            self._fetched_players = players_data
            self._fetched_banned = banned_data
            self.failed = False
        except Exception:
            self.failed = True

        # Apply the data update on the UI thread
        bui.pushcall(self._update, from_other_thread=True)

    def _update(self) -> None:
        # All we do here is make sure our targeted playlist still exists,
        # and close ourself if not.

        for widget in self.entries:
            widget.delete()

        # Do nothing if window is closing.
        if self._transitioning_out:
            self.failed = True
            return

        # If async failed, bail.
        if self.failed:
            return

        players_data = getattr(self, '_fetched_players', {})
        banned_data = getattr(self, '_fetched_banned', {})

        # Filter banned players.
        filtered_players = [p for pid, p in players_data.items() if pid not in banned_data]

        # Sort players by coins then dollars.
        sorted_players = sorted(
            filtered_players,
            key=lambda x: (x.get("coins", 0), x.get("dollars", 0)),
            reverse=True
        )

        size = 30
        spacing = 30
        total_height = spacing * len(sorted_players)
        self._subcontainerheight = total_height

        y_pos = self._subcontainerheight - size

        for i, entry in enumerate(sorted_players, start=1):
            coins = entry.get("coins", 0)
            dollars = entry.get("dollars", 0)
            username = entry.get("username", "???")
            color = (1, 1, 1) if bui.app.plus.get_v1_account_display_string(True, True) != username else (1, 1, 0)
            us = bui.app.plus.get_v1_account_display_string(True, True) == username

            trophy = babase.charstr(babase.SpecialChar(41)) if i == 1 else ""

            text = bui.textwidget(
                parent=self._subcontainer,
                position=(10, y_pos),
                size=(self._subcontainerwidth, 30),
                text=f"{trophy}{i}. {username} - {coins}{babase.charstr(babase.SpecialChar.OUYA_BUTTON_U)} / {dollars}{babase.charstr(babase.SpecialChar.OUYA_BUTTON_O)}",
                color=color,
                h_align="left",
                shadow=1.0,
                maxwidth=380
            )
            self.entries.append(text)

            if us:
                text2 = bui.textwidget(
                    parent=self.root_widget,
                    position=(self._width * 0.1, 260),
                    size=(self._width, 30),
                    text=f"{trophy}{i}. {username} - {coins}{babase.charstr(babase.SpecialChar.OUYA_BUTTON_U)} / {dollars}{babase.charstr(babase.SpecialChar.OUYA_BUTTON_O)}",
                    color=(1, 1, 1),
                    h_align="left",
                    shadow=1.0,
                    maxwidth=380
                )
                self.entries.append(text2)

            y_pos -= spacing

        bui.containerwidget(
            edit=self._subcontainer,
            size=(self._subcontainerwidth, self._subcontainerheight)
        )

        bui.spinnerwidget(edit=self._join_status_spinner, visible=False)
        
    def _on_cancel_press(self):
        self._transition_out()
       
    def _transition_out(self, transition: str = 'out_scale') -> None:
        bui.getsound('swish').play()
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition=transition)