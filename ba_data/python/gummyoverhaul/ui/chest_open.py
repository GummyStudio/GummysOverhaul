"""Module for a popup window when a chest is opened."""
import bauiv1 as bui
import random

class ChestOpenPopup(bui.Window):
    """Popup window for opening a chest."""
    def __init__(
        self, 
        chest_data: dict, 
        next_chest: dict,
        rewards_data: dict,
        transition: str = 'in_scale',
    ):
        self._width = 300
        self._height = 320
        uiscale = bui.app.ui_v1.uiscale
        scale = (
            1.8 if uiscale is bui.UIScale.SMALL
            else 1.5 if uiscale is bui.UIScale.MEDIUM
            else 1.1
        )
        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height),
                scale=scale,
                transition=transition,
            ),
        )

        self._transitioning_out = False
        imgsize = 120

        bui.getsound('hiss').play()
        bui.getsound('chestOpen01').play(2.5)
        xp_reward = rewards_data.get('xp')
        coins_reward = rewards_data.get('coins')
        dollars_reward = rewards_data.get('dollars')
        if coins_reward:
            bui.getsound('cashRegister').play()
        if dollars_reward:
            bui.getsound('secretKey').play(1.3)
        self.show_chest_rewards(
            xp_reward, 
            coins_reward, 
            dollars_reward,
        )

        # Chest image
        self.chest = bui.imagewidget(
            parent=self._root_widget,
            position=(self._width * 0.5 - imgsize * 0.5, (self._height - 10) - imgsize),
            size=(imgsize, imgsize),
            color=chest_data['color'],
            texture=bui.gettexture("chestOpenIcon"),
            tint_texture=bui.gettexture("chestOpenIconTint"),
            tint_color=chest_data["tint"],
            tint2_color=chest_data["tint2"],
        ) 
        
        ok_phrases = [
            'Nice!',
            'Rigged',
            'scammed', 
            'Thanks I hate it', 
            'wow!',
            'Yummy', 
            'yummres',
            'Wow ill be\nsure to use this',
            'kil it',
            'Ok lol',
            'Man whatever',
            'just put the coins\nin the bag',
            "i'll take it",
            "So basically nothing",
        ]
        
        btn_width = self._width * 0.8
        btn_height = 60
        btn_x = self._width * 0.5
        btn_y = 40
        self._cancel_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(
                btn_x - (btn_width * 0.5), 
                btn_y - (btn_height * 0.5)
            ),
            size=(btn_width, btn_height),
            label='',
            on_activate_call=self._on_cancel_press,
            autoselect=True,
            color=(0.1, 0.6, 0.9),
        )
        bui.textwidget(
            parent=self._root_widget,
            position=(btn_x, btn_y),
            size=(0, 0),
            text=random.choice(ok_phrases),
            h_align='center',
            v_align='center',
            max_height=btn_height - 10,
            maxwidth=btn_width - 30,
            draw_controller=self._cancel_button,
        )
        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=self._cancel_button,
        )
        
    def show_chest_rewards(
        self, 
        xp: int, 
        coins: int, 
        dollars: int,
    ):
        x = self._width * 0.5
        y = self._height - 130
        tdelay = 0.3
        this_tdelay = tdelay
        if xp:
            bui.textwidget(
                parent=self._root_widget,
                position=(x, y),
                size=(0, 0),
                text=f"+{xp} XP",
                scale=1.0,
                color=(1, 0.8, 0.7),
                h_align='center',
                transition_delay=this_tdelay,
            )
            y -= 40
            this_tdelay += 0.1
        if coins:
            bui.textwidget(
                parent=self._root_widget,
                position=(x, y),
                size=(0, 0),
                text=f"+{coins} Coins",
                scale=1.0,
                color=(0, 0.85, 1),
                h_align='center',
                transition_delay=this_tdelay,
            )
            y -= 40
            this_tdelay += 0.1
        if dollars:
            bui.textwidget(
                parent=self._root_widget,
                position=(x, y),
                size=(0, 0),
                text=f"+{dollars} Dollars",
                scale=1.0,
                color=(0, 0.7, 1),
                h_align='center',
                transition_delay=this_tdelay,
            )
            y -= 40
            this_tdelay += 0.1

    def _on_cancel_press(self):
        self._transition_out()

    def _transition_out(self):
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(
                edit=self._root_widget, 
                transition='out_scale',
            )