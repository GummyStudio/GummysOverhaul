# Released under the MIT License. See LICENSE for details.
#
"""Provides help related ui."""

from __future__ import annotations

from typing import override

import bauiv1 as bui
import babase
import random
from bauiv1lib.popup import PopupWindow
from gummyoverhaul.ui.chest_open import ChestOpenPopup
from gummyoverhaul.ui.stats import StatsWindow
from gummyoverhaul.ui.leaderboard import LeaderBoardWindow

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
                    yoffs - 30 + (75 if uiscale is bui.UIScale.MEDIUM else 60),
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
        LeaderBoardWindow()

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

            bui.containerwidget(
                edit=self._subcontainer, 
                size=(
                    self._subcontainerwidth, 
                    self._subcontainerheight
                )
            )
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
            # Award rewards immediately and store for animation
            xp_reward = random.randint(1, 4)
            cfg = babase.app.config
            # Maybe clean this up????
            # Fuckin dumbass....
            if self.slot_data['type'] == 'coins':
                reward = self.slot_data['rewards']
                cfg["GUMMY_gumcoins"] += reward
                coins_reward = reward
                dollars_reward = 0
            elif self.slot_data['type'] == 'dollars':
                reward = self.slot_data['rewards']
                cfg["GUMMY_gumdollars"] += reward
                coins_reward = 0
                dollars_reward = reward
            elif self.slot_data['type'] == 'both':
                coins_reward = self.slot_data['coins']
                dollars_reward = self.slot_data['dollars']
                cfg["GUMMY_gumcoins"] += coins_reward
                cfg["GUMMY_gumdollars"] += dollars_reward
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
            coins_reward = 1
            dollars_reward = 3
            xp_reward = 2
            self.slot_data = cfg["gummy_chestinslot"]
            rewards_data = {
                'coins': coins_reward,
                'dollars': dollars_reward,
                'xp': xp_reward,
            }
            ChestOpenPopup(
                chest_data=old_data, 
                next_chest=self.slot_data,
                rewards_data=rewards_data,
            )
            self._reset()
    
    def _reset(self):
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
                text='Open Me!',
                color=(1, 1, 1, 0.15),
                h_align='left',
                v_align='top',
                maxwidth=200
            )

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