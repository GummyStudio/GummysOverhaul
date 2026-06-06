# Released under the MIT License. See LICENSE for details.
#
"""Session and Activity for displaying the main menu bg."""

from __future__ import annotations

import copy
import datetime
import logging
import math
import random
from typing import TYPE_CHECKING, override, Callable, Sequence
import weakref


import bascenev1 as bs
import bauiv1 as bui
from enum import Enum
import babase
from babase._logging import applog
from efro.util import utc_now
from bascenev1lib.mainmenu import MainMenuSession

if TYPE_CHECKING:
    from typing import Any

class CharacterDetailWindow(bui.Window):
    def __init__(self, name: str, activity: bs.Activity, store_browser: StoreBrowserWindow, already_owned: bool = False):
        self._width = 400
        self._height = 350
        self._r = 'storeCharDetail'
        self._activity = weakref.ref(activity)
        self._store_browser = weakref.ref(store_browser)
        xoffs = 160
        self.name = name
        uiscale = bui.app.ui_v1.uiscale
        self.already_owned = already_owned
        super().__init__(root_widget=bui.containerwidget(
            size=(self._width, self._height),
            transition='in_scale',
            scale=(1.4 if uiscale is bui.UIScale.SMALL else 1.0),
             background=False,      

            toolbar_visibility=(
                    'no_menu_minimal'
                ),
        ))
        # bg
        
        bui.imagewidget(
            parent=self._root_widget,
            position=(xoffs+55, 60),
            size=(self._width*0.8, self._height*0.8),
            color=(0.5, 0.5, 0.5),
            texture=bui.gettexture('windowHSmallVMed')
        )
        self._scrollwidget = bui.scrollwidget(
            parent=self._root_widget,
            highlight=False,
            size=(self._width, self._height),
            position=(
                xoffs,
                0,
            ),
            claims_left_right=True,
            selection_loops_to_parent=True,
            border_opacity=0.4,
        )

        bui.getsound('click01').play()
        description='Description'

        description = bs.app.classic.store.get_store_item(name)['description']
        
        if name in ['characters.spazexe',
                'characters.starhoodie',
                'characters.insane',
                'characters.bluecap',
                'characters.melling',
                'characters.spazling',
                'characters.ninjaling',
                'characters.sal',
                'characters.scoldy',
                'characters.hhh',
                'characters.jolly',
                'characters.gummyvoicespaz',
                'characters.gummyvoicejack',
                'characters.gummyvoiceagent',
                'characters.ybs16',
                'characters.tophat',
        ]:
            use_dollars = True
        else:
            use_dollars = False
        
        # i dont get it bruh
        bui.textwidget(
            parent=self._scrollwidget,
            scale=0.0,
        )
        centre_x = 180
        bui.textwidget(
            parent=self._scrollwidget,
            position=(centre_x, self._height-60),
            text=bui.app.classic.store.get_store_item_name_translated(name),
            scale=1.2,
            h_align='center',
            v_align='center'
        )
        
        spaz = bs.app.classic.spaz_appearances[
            bui.app.classic.store.get_store_item_name_translated(name).evaluate()
        ]
        bui.imagewidget(
            parent=self._scrollwidget,
            position=(centre_x-25, 140),
            size=(120, 120),
            texture=bui.gettexture(spaz.icon_texture),
            tint_texture=bui.gettexture(spaz.icon_mask_texture),
            tint_color=spaz.default_color,
            tint2_color=spaz.default_highlight,
            mask_texture=bui.gettexture('characterIconMask'),
        )
        
        bui.textwidget(
            parent=self._scrollwidget,
            position=(centre_x, self._height-260),
            text=(
                bui.Lstr(r=f'{self._r}.cosmeticText') 
                if use_dollars else 
                bui.Lstr(r=f'{self._r}.characterText')
            ),
            scale=0.5,
            color=(1,1,1,0.5),
            h_align='center',
            v_align='center'
        )

        bui.buttonwidget(
            parent=self._scrollwidget,
            position=(50, 25),
            size=(140, 50),
            label=bui.Lstr(r=f'{self._r}.aboutText'),
            on_activate_call=self._show_about
        )

        bui.buttonwidget(
            parent=self._scrollwidget,
            position=(210, 25),
            size=(140, 50),
            button_type='square',
            label=(
                bui.Lstr(r=f'{self._r}.ownedText') if self.already_owned 
                else babase.charstr((babase.SpecialChar.OUYA_BUTTON_O 
                if use_dollars else babase.SpecialChar.OUYA_BUTTON_U)) 
                + str(bs.app.plus.get_v1_account_misc_read_val(
                    'price.' + name, '?'
                ))
            ),
            on_activate_call=self._buy_character,
            color= (0.6, 0.6, 0.6) if self.already_owned else None
        )


        self._back_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(xoffs, 290.0),
                size=(70, 70),
                scale=0.8,
                text_scale=1.2,
                label=bui.charstr(bui.SpecialChar.BACK),
                button_type='backSmall',
                on_activate_call=self.close,
            )
        bui.containerwidget(edit=self._root_widget, cancel_button=btn)
        self.description = description
   
    def _show_about(self):
        self._activity().show_description(
            bui.app.classic.store.get_store_item_name_translated(self.name).evaluate(), 
            self.description    
        )
        bui.getsound('swish').play()
        
               

    def _buy_character(self):
        bui.getsound('swish').play()
        if self.already_owned:
            self._activity().start_talk_session('AlreadyOwn')
            bui.getsound('error').play()
        else:
            self._store_browser().buy(self.name)
            self.close()

    def close(self):
        
        self._activity = None
        self._store_browser = False
        bui.getsound('swish').play()

        bui.containerwidget(edit=self._root_widget, transition='out_scale')
        


class StoreBrowserWindow(bui.MainWindow):
    """Window for browsing the store."""

    class TabID(Enum):
        """Our available tab types."""

        # EXTRAS = 'extras'
        TALK = 'talk'
        CHARACTERS = 'characters'
        COSMETICS = 'cosmetics'
        EXIT = 'exit'

    def __init__(
        self,
        
        transition: str | None = 'in_right',
        origin_widget: bui.Widget | None = None,
        show_tab: StoreBrowserWindow.TabID | None = None,
        minimal_toolbars: bool = False,
        activity: bs.Activity | None = None,
        
    ):
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        from bauiv1lib.tabs import TabRow
        from bauiv1 import SpecialChar

        
       

        app = bui.app
        assert app.classic is not None
        uiscale = app.ui_v1.uiscale

        bui.set_analytics_screen('Store Window')

        self.button_infos: dict[str, dict[str, Any]] | None = None
        self.update_buttons_timer: bui.AppTimer | None = None
        self._status_textwidget_update_timer = None
        self.leaving_shop = False
        self.activity = activity
        

        self._show_tab = show_tab
        self._width = (
            1800
            if uiscale is bui.UIScale.SMALL
            else 1000 if uiscale is bui.UIScale.MEDIUM else 1120
        )
        self._height = (
            1200
            if uiscale is bui.UIScale.SMALL
            else 700 if uiscale is bui.UIScale.MEDIUM else 800
        )
        self._current_tab: StoreBrowserWindow.TabID | None = None
        # extra_top = 30 if uiscale is bui.UIScale.SMALL else 0

        self.request: Any = None
        self._r = 'gumStore'
        self._last_buy_time: float | None = None

        # Do some fancy math to fill all available screen area up to the
        # size of our backing container. This lets us fit to the exact
        # screen shape at small ui scale.
        screensize = bui.get_virtual_screen_size()
        scale = (
            1.5
            if uiscale is bui.UIScale.SMALL
            else 0.9 if uiscale is bui.UIScale.MEDIUM else 0.8
        )

        # Calc screen size in our local container space and clamp to a
        # bit smaller than our container size.
        target_width = min(self._width - 120, screensize[0] / scale)
        target_height = min(self._height - 140, screensize[1] / scale)

        # To get top/left coords, go to the center of our window and
        # offset by half the width/height of our target area.
        yoffs = 0.5 * self._height + 0.5 * target_height + 30.0

        self._scroll_width = target_width
        self._scroll_height = target_height - 59
        self._scroll_bottom = yoffs - 87 - self._scroll_height


        self._scroll_width -= 300 if not uiscale is bui.UIScale.SMALL else 480
        self.position_x = 430 if not uiscale is bui.UIScale.SMALL else 140
       

        

        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height),
                toolbar_visibility=(
                    'no_menu_minimal'
                ),
                scale=scale,
                background=False,      
            ),
            
            transition=transition,
            origin_widget=origin_widget,
            # We're affected by screen size only at small ui-scale.
            refresh_on_screen_size_changes=uiscale is bui.UIScale.SMALL,
           
        )

        

        

       
    

        tabs_def = [
            # (self.TabID.EXTRAS, bui.Lstr(resource=f'{self._r}.extrasText')),
            (
                self.TabID.TALK, 
                bui.Lstr(r=f'{self._r}.talkText')
            ),
            (
                self.TabID.CHARACTERS,
                bui.Lstr(resource=f'{self._r}.charactersText'),
            ),
            (
                self.TabID.COSMETICS,
                bui.Lstr(r=f'{self._r}.cosmeticsText')
            ),
            (
                self.TabID.EXIT, 
                bui.Lstr(r=f'{self._r}.exitText')
            ),
        ]

        tab_inset = 50 if uiscale is bui.UIScale.SMALL else 100
        self._tab_row = TabRow(
            self._root_widget,
            tabs_def,
            size=(self._scroll_width - 2.0 * tab_inset, 50),
            pos=(
                self._width * 0.5 - self._scroll_width * 0.5 + tab_inset + self.position_x,
                self._scroll_bottom + self._scroll_height - 4.0,
            ),
            on_select_call=self._set_tab,

            select_color=(0, 0.8, 1),
            select_textcolor=(0.82,0.82,1)
        )

        self._purchasable_count_widgets: dict[
            StoreBrowserWindow.TabID, dict[str, Any]
        ] = {}

        # Create our purchasable-items tags and have them update over time.
        for tab_id, tab in self._tab_row.tabs.items():
            pos = tab.position
            
            size = tab.size
            button = tab.button
            rad = 10
            center = (pos[0] + 0.1 * size[0], pos[1] + 0.9 * size[1])
            img = bui.imagewidget(
                parent=self._root_widget,
                position=(center[0] - rad * 1.1, center[1] - rad * 1.2),
                size=(rad * 2.4, rad * 2.4),
                texture=bui.gettexture('circleShadow'),
                color=(1, 0, 0),
            )
            txt = bui.textwidget(
                parent=self._root_widget,
                position=center,
                size=(0, 0),
                h_align='center',
                v_align='center',
                maxwidth=1.4 * rad,
                scale=0.6,
                shadow=1.0,
                flatness=1.0,
            )
            rad = 20
            sale_img = bui.imagewidget(
                parent=self._root_widget,
                position=(center[0] - rad, center[1] - rad),
                size=(rad * 2, rad * 2),
                draw_controller=button,
                texture=bui.gettexture('circleZigZag'),
                color=(0.5, 0, 1.0),
            )
            sale_title_text = bui.textwidget(
                parent=self._root_widget,
                position=(center[0], center[1] + 0.24 * rad),
                size=(0, 0),
                h_align='center',
                v_align='center',
                draw_controller=button,
                maxwidth=1.4 * rad,
                scale=0.6,
                shadow=0.0,
                flatness=1.0,
                color=(0, 1, 0),
            )
            sale_time_text = bui.textwidget(
                parent=self._root_widget,
                position=(center[0], center[1] - 0.29 * rad),
                size=(0, 0),
                h_align='center',
                v_align='center',
                draw_controller=button,
                maxwidth=1.4 * rad,
                scale=0.4,
                shadow=0.0,
                flatness=1.0,
                color=(0, 1, 0),
            )
            self._purchasable_count_widgets[tab_id] = {
                'img': img,
                'text': txt,
                'sale_img': sale_img,
                'sale_title_text': sale_title_text,
                'sale_time_text': sale_time_text,
            }
        self._tab_update_timer = bui.AppTimer(
            1.0, bui.WeakCall(self._update_tabs), repeat=True
        )
        self._update_tabs()
        


       

        # self._scroll_width = self._width - scroll_buffer_h
        # self._scroll_height = self._height - 180

        self._scrollwidget: bui.Widget | None = None
        self._status_textwidget: bui.Widget | None = None
        self._restore_state()

        
        assert isinstance(self.activity, ShopActivity)
        if self.activity is None:
            # No activity, die so we can  be reset with the activity
            self.main_window_close()


            return

        
        
       

        



    def _update_tabs(self) -> None:
        assert bui.app.classic is not None
        store = bui.app.classic.store

        if not self._root_widget:
            return
        for tab_id, tab_data in list(self._purchasable_count_widgets.items()):
            sale_time = store.get_available_sale_time(tab_id.value)

            if sale_time is not None:
                bui.textwidget(
                    edit=tab_data['sale_title_text'],
                    text=bui.Lstr(resource='store.saleText'),
                )
                bui.textwidget(
                    edit=tab_data['sale_time_text'],
                    text=bui.timestring(sale_time / 1000.0, centi=False),
                )
                bui.imagewidget(edit=tab_data['sale_img'], opacity=1.0)
                count = 0
            else:
                bui.textwidget(edit=tab_data['sale_title_text'], text='')
                bui.textwidget(edit=tab_data['sale_time_text'], text='')
                bui.imagewidget(edit=tab_data['sale_img'], opacity=0.0)
                count = store.get_available_purchase_count(tab_id.value)

            if count > 0:
                bui.textwidget(edit=tab_data['text'], text=str(count))
                bui.imagewidget(edit=tab_data['img'], opacity=1.0)
            else:
                bui.textwidget(edit=tab_data['text'], text='')
                bui.imagewidget(edit=tab_data['img'], opacity=0.0)

    
    def _leave_shop(self):
        self.leaving_shop = True
       
        
        self.activity.leave_shop()

        


    def _set_tab(self, tab_id: TabID) -> None:
        if self._current_tab is tab_id:
            return
        
        from bauiv1lib.confirm import ConfirmWindow

        if tab_id is self.TabID.EXIT:
            ConfirmWindow(
                bui.Lstr(r=f'{self._r}.confirmLeaveText'),
                self._leave_shop,
            )
            return
    
        self._current_tab = tab_id

        

        # Update tab colors based on which is selected.
        self._tab_row.update_appearance(tab_id)

        # (Re)create scroll widget.
        if self._scrollwidget:
            self._scrollwidget.delete()

        self._scrollwidget = bui.scrollwidget(
            parent=self._root_widget,
            highlight=False,
            size=(self._scroll_width, self._scroll_height),
            position=(
                self._width * 0.5 - self._scroll_width * 0.5 + self.position_x,
                self._scroll_bottom,
            ),
            claims_left_right=True,
            selection_loops_to_parent=True,
            border_opacity=0.4,
        )

        # NOTE: this stuff is modified by the _Store class.
        # Should maybe clean that up.
        self.button_infos = {}
        self.update_buttons_timer = None

        # Show status over top.
        if self._status_textwidget:
            self._status_textwidget.delete()
        self._status_textwidget = bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height * 0.5),
            size=(0, 0),
            color=(1, 0.7, 1, 0.5),
            h_align='center',
            v_align='center',
            text='',
            maxwidth=self._scroll_width * 0.9,
        )

        class _Request:
            def __init__(self, window: StoreBrowserWindow):
                self._window = weakref.ref(window)
                data = {'tab': tab_id.value}
                bui.apptimer(0.1, bui.WeakCall(self._on_response, data))

            def _on_response(self, data: dict[str, Any] | None) -> None:
                # FIXME: clean this up.
                # pylint: disable=protected-access
                window = self._window()
                if window is not None and (window.request is self):
                    window.request = None
                    window._on_response(data)

        # Kick off a server request.
        self.request = _Request(self)

    # Actually start the purchase locally.
    def _purchase_check_result(
        self, item: str, is_ticket_purchase: bool, result: dict[str, Any] | None
    ) -> None:
        plus = bui.app.plus
        assert plus is not None
        if result is None:
            bui.getsound('error').play()
            bui.screenmessage(
                bui.Lstr(resource='internal.unavailableNoConnectionText'),
                color=(1, 0, 0),
            )
        else:
            if is_ticket_purchase:
                if result['allow']:
                    price = plus.get_v1_account_misc_read_val(
                        'price.' + item, None
                    )
                    if (
                        price is None
                        or not isinstance(price, int)
                        or price <= 0
                    ):
                        applog.error(
                            'Error; got invalid local price of',
                            price,
                            'for item',
                            item,
                        ) # normalize logging :broken_heart:
                        bui.getsound('error').play()
                    else:
                        bui.getsound('click01').play()
                        plus.in_game_purchase(item, price)
                else:
                    if result['reason'] == 'versionTooOld':
                        bui.getsound('error').play()
                        bui.screenmessage(
                            bui.Lstr(
                                resource='getTicketsWindow.versionTooOldText'
                            ),
                            color=(1, 0, 0),
                        )
                    else:
                        bui.getsound('error').play()
                        bui.screenmessage(
                            bui.Lstr(
                                resource='getTicketsWindow.unavailableText'
                            ),
                            color=(1, 0, 0),
                        )
            # Real in-app purchase.
            else:
                if result['allow']:
                    plus.purchase(item)
                else:
                    if result['reason'] == 'versionTooOld':
                        bui.getsound('error').play()
                        bui.screenmessage(
                            bui.Lstr(
                                resource='getTicketsWindow.versionTooOldText'
                            ),
                            color=(1, 0, 0),
                        )
                    else:
                        bui.getsound('error').play()
                        bui.screenmessage(
                            bui.Lstr(
                                resource='getTicketsWindow.unavailableText'
                            ),
                            color=(1, 0, 0),
                        )

    def _do_purchase_check(
        self, item: str, is_ticket_purchase: bool = False
    ) -> None:
        app = bui.app
        if app.classic is None:
            logging.warning('_do_purchase_check() requires classic.')
            return
        
        

        # Here we ping the server to ask if it's valid for us to
        # purchase this. Better to fail now than after we've
        # paid locally.

        app.classic.master_server_v1_get(
            'bsAccountPurchaseCheck',
            {
                'item': item,
                'platform': app.classic.platform,
                'subplatform': app.classic.subplatform,
                'version': app.env.engine_version,
                'buildNumber': app.env.engine_build_number,
                'purchaseType': 'ticket' if is_ticket_purchase else 'real',
            },
            callback=bui.WeakCall(
                self._purchase_check_result, item, is_ticket_purchase
            ),
        )

    def buy(self, item: str) -> None:
        """Attempt to purchase the provided item."""
        from bauiv1lib.confirm import ConfirmWindow

        if self.leaving_shop:
            return
        
        if item.startswith('talk.'):
            bui.getsound('click01').play()
            self.activity.start_talk_session(item[5:])
            return
        
        gummyoverhaul = True

        
        if item in ['characters.spazexe',
                'characters.starhoodie',
                'characters.insane',
                'characters.bluecap',
                'characters.melling',
                'characters.spazling',
                'characters.ninjaling',
                'characters.sal',
                'characters.scoldy',
                'characters.hhh',
                'characters.jolly',
                'characters.gummyvoicespaz',
                'characters.gummyvoicejack',
                'characters.gummyvoiceagent',
                'characters.ybs16',
                'characters.tophat',
        ]:
            use_dollars = True
        else:
            use_dollars = False
        
        assert bui.app.classic is not None
        store = bui.app.classic.store

        plus = bui.app.plus
        assert plus is not None

        # Prevent pressing buy within a few seconds of the last press
        # (gives the buttons time to disable themselves and whatnot).
        curtime = bui.apptime()
        if (
            self._last_buy_time is not None
            and (curtime - self._last_buy_time) < 2.0
        ):
            bui.getsound('error').play()
        else:
            if False:
                pass

            
            else:
                if gummyoverhaul:
                    price = plus.get_v1_account_misc_read_val(
                        'price.' + item, None
                    )
                    gumcoins = babase.app.config.get('GUMMY_gumdollars', 0) if use_dollars else babase.app.config.get('GUMMY_gumcoins', 0)
                    if price is not None and gumcoins < price:
                        bui.getsound('error').play()
                        self.activity.start_talk_session(
                                            'Short'
                                        )
                    else:
                        if True:
                        
                            def do_it() -> None:
                                babase.screenmessage(
                                    bui.Lstr(r=f'{self._r}.purchasingText')
                                )
                                cfg = babase.app.config
                                abletobuy = True
                                
                                if abletobuy:
                                    key = 'GUMMY_gumdollars' if use_dollars else 'GUMMY_gumcoins'
                                    cfg[key] = gumcoins - price
                                    cfg.apply_and_commit()
                                if (babase.app.config.get('GUMMY_gumdollars', 0) if use_dollars else babase.app.config.get('GUMMY_gumcoins', 0)) == gumcoins - price:
                                    abletobuy = True

                                    if use_dollars:
                                        if item == 'characters.spazexe':
                                            cfg['ownedCosmetic_SpazEXE'] = True
                                        elif item == 'characters.starhoodie':
                                            cfg['ownedCosmetic_StarHoodie'] = True
                                        elif item == 'characters.insane':
                                            cfg['ownedCosmetic_Insane'] = True
                                        elif item == 'characters.bluecap':
                                            cfg['ownedCosmetic_Bluecap'] = True
                                        elif item == 'characters.melling':
                                            cfg['ownedCosmetic_Melling'] = True
                                        elif item == 'characters.spazling':
                                            cfg['ownedCosmetic_Spazling'] = True
                                        elif item == 'characters.ninjaling':
                                            cfg['ownedCosmetic_Ninjaling'] = True
                                        elif item == 'characters.sal':
                                            cfg['ownedCosmetic_Sal'] = True
                                        elif item ==  'characters.scoldy':
                                            cfg['ownedScoldy'] = True
                                        elif item == 'characters.hhh':
                                            cfg["ownedHHH_amarCosmetic"] = True  
                                        elif item == 'characters.jolly':
                                            cfg["ownedJolluNinja_Cosmetic"] = True
                                        elif item == 'characters.gummyvoicespaz':
                                            cfg["ownedGummyVoiceSpaz_Cosmetic"] = True
                                        elif item == 'characters.gummyvoiceagent':
                                            cfg["ownedGummyVoiceAgent_Cosmetic"] = True
                                        elif item == 'characters.gummyvoicejack':
                                            cfg["ownedGummyVoiceJack_Cosmetic"] = True
                                        elif item == 'characters.ybs16':
                                            cfg["ownedYurirblx_Cosmetic"] = True
                                        elif item == 'characters.tophat':
                                            cfg["ownedTopHat_Cosmetic"] = True


                                            
                

                                    else:
                                    
                                    
                                        if item == 'characters.agentspaz':
                                            cfg['ownedAgentSpaz'] = True
                                        elif item == 'characters.orangecap':
                                            cfg['ownedCap'] = True
                                        elif item == 'characters.ralsei':
                                            cfg['ownedRalsei'] = True
                                        elif item ==  'characters.betty':
                                            cfg['ownedOldLady'] = True
                                        elif item == 'characters.amar':
                                            cfg['ownedAmar'] = True
                                        elif item == 'characters.bob':
                                            cfg['ownedBob'] = True
                                        elif item == 'games.infinite_gummy_o':
                                            cfg['ownedOverhaul'] = True
                                        elif item == 'characters.fbunny':
                                            cfg['ownedBunny'] = True
                                        elif item == 'games.infinite_gummy_r':
                                            cfg['ownedOverhaulRunaround'] = True
                                        elif item == 'games.tower':
                                            cfg['ownedTower'] = True
                                        elif item == 'characters.watory':
                                            cfg['ownedWatory'] = True
                                        elif item == 'characters.vr':
                                            cfg['ownedVr'] = True
                                        elif item == 'characters.pizza':
                                            cfg['ownedPizza'] = True
                                        elif item == 'characters.noise':
                                            cfg['ownedNoise'] = True
                                        elif item == 'characters.space':
                                            cfg['ownedSpace'] = True
                                        elif item == 'characters.ire':
                                            cfg['ownedIre'] = True
                                        elif item == 'characters.rem':
                                            cfg['ownedRem'] = True
                                        elif item == 'characters.fennekin':
                                            cfg['ownedFennekin'] = True


                                    if abletobuy:
                                        cfg.apply_and_commit()
                                        bui.getsound('cashRegister').play()
                                        
                                        self.activity.start_talk_session('Buy')
                                    else:
                                        
                                        key = 'GUMMY_gumdollars' if use_dollars else 'GUMMY_gumcoins'
                                        cfg[key] = gumcoins + price
                                        cfg.apply_and_commit()
                                        bui.getsound('error').play()
                                        self.activity.start_talk_session('Cant')
                            
                            bui.getsound('swish').play()
                            ConfirmWindow(
                                bui.Lstr(
                                    resource='store.purchaseConfirmText',
                                    subs=[
                                    (
                                        '${ITEM}',
                                        store.get_store_item_name_translated(
                                            item
                                        ),
                                    )
                                ],
                            ),
                            width=400,
                            height=120,
                            action=do_it,
                            ok_text=bui.Lstr(
                                resource='store.purchaseText',
                                fallback_resource='okText',
                            ),
                        )
                        else:
                            
                            bui.getsound('error').play()
                            self.activity.start_talk_session(
                                            'BuyOriginal'
                                        )
                else:
                    self._last_buy_time = curtime

                    # Merch is a special case - just a link.
                    if item == 'merch':
                        url = bui.app.config.get('Merch Link')
                        if isinstance(url, str):
                            bui.open_url(url)

                    # Pro is an actual IAP, and the rest are ticket purchases.
                    elif item == 'pro':
                        bui.getsound('click01').play()

                        # Purchase either pro or pro_sale depending on whether
                        # there is a sale going on.
                        self._do_purchase_check(
                            'pro'
                            if store.get_available_sale_time('extras') is None
                            else 'pro_sale'
                        )
                    else:
                        price = plus.get_v1_account_misc_read_val(
                            'price.' + item, None
                        )
                        our_tickets = plus.get_v1_account_ticket_count()
                        if price is not None and our_tickets < price:
                            bui.getsound('error').play()
                            bui.screenmessage(
                                bui.Lstr(resource='notEnoughTicketsText'),
                                color=(1, 0, 0),
                            )
                            # gettickets.show_get_tickets_prompt()
                        else:
                            
                            def do_it() -> None:
                                self._do_purchase_check(
                                    item, is_ticket_purchase=True
                                )

                            bui.getsound('swish').play()
                            ConfirmWindow(
                                bui.Lstr(
                                    resource='store.purchaseConfirmText',
                                    subs=[
                                        (
                                            '${ITEM}',
                                            store.get_store_item_name_translated(
                                                item
                                            ),
                                        )
                                    ],
                                ),
                                width=400,
                                height=120,
                                action=do_it,
                                ok_text=bui.Lstr(
                                    resource='store.purchaseText',
                                    fallback_resource='okText',
                                ),
                            )

    def _print_already_own(self, charname: str = 'notusedq') -> None:
        
        bui.getsound('error').play()
        self.activity.start_talk_session('AlreadyOwn')

    def update_buttons(self) -> None:
        """Update our buttons."""
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals
        from bauiv1 import SpecialChar

        assert bui.app.classic is not None
        store = bui.app.classic.store

        plus = bui.app.plus
        assert plus is not None

        if not self._root_widget:
            return

        sales_raw = plus.get_v1_account_misc_read_val('sales', {})
        sales = {}
        try:
            # Look at the current set of sales; filter any with time remaining.
            for sale_item, sale_info in list(sales_raw.items()):
                to_end = (
                    datetime.datetime.fromtimestamp(
                        sale_info['e'], datetime.UTC
                    )
                    - utc_now()
                ).total_seconds()
                if to_end > 0:
                    sales[sale_item] = {
                        'to_end': to_end,
                        'original_price': sale_info['op'],
                    }
        except Exception:
            logging.exception('Error parsing sales.')

        assert self.button_infos is not None

        for b_type, b_info in self.button_infos.items():
            gummyoverhaul = True
            
            if b_type in ['characters.spazexe',
                'characters.starhoodie',
                'characters.insane',
                'characters.bluecap',
                'characters.melling',
                'characters.spazling',
                'characters.ninjaling',
                'characters.sal',
                'characters.scoldy',
                'characters.hhh',
                'characters.jolly',
                'characters.gummyvoicespaz',
                'characters.gummyvoicejack',
                'characters.gummyvoiceagent',
                'characters.ybs16',
                'characters.tophat',
            ]:
                use_dollars = True
                
            else:
                use_dollars = False
            
            if b_type.startswith('talk.'):
                gummyoverhaul = False
            
            gumcoins = babase.app.config.get('GUMMY_gumdollars', 0) if use_dollars else babase.app.config.get('GUMMY_gumcoins', 0)
            if b_type == 'merch':
                purchased = False
            elif b_type in ['upgrades.pro', 'pro']:
                assert bui.app.classic is not None
                purchased = bui.app.classic.accounts.have_pro()
            elif b_type == 'characters.agentspaz' and babase.app.config.get('ownedAgentSpaz', False):
                purchased = True
            elif b_type == 'characters.amar' and babase.app.config.get('ownedAmar', False):
                purchased = True
            elif b_type == 'characters.bob' and babase.app.config.get('ownedBob', False):
                purchased = True
            elif b_type == 'games.infinite_gummy_o' and babase.app.config.get('ownedOverhaul', False):
                purchased = True
            elif b_type == 'characters.watory' and babase.app.config.get('ownedWatory', False):
                purchased = True
            elif b_type == 'games.infinite_gummy_r' and babase.app.config.get('ownedOverhaulRunaround', False):
                purchased = True
            elif b_type == 'games.tower' and babase.app.config.get('ownedTower', False):
                purchased = True
            elif b_type == 'characters.space' and babase.app.config.get('ownedSpace', False):
                purchased = True
            elif b_type == 'characters.vr' and babase.app.config.get('ownedVr', False):
                purchased = True
            elif b_type == 'characters.pizza' and babase.app.config.get('ownedPizza', False):
                purchased = True
            elif b_type == 'characters.noise' and babase.app.config.get('ownedNoise', False):
                purchased = True
            elif b_type == 'characters.fbunny' and babase.app.config.get('ownedBunny', False):
                purchased = True
            elif b_type == 'characters.orangecap' and babase.app.config.get('ownedCap', False):
                purchased = True
            elif b_type == 'characters.ralsei' and babase.app.config.get('ownedRalsei', False):
                purchased = True
            elif b_type == 'characters.betty' and babase.app.config.get("ownedOldLady", False):
                purchased = True
            elif b_type == 'characters.scoldy' and babase.app.config.get("ownedScoldy", False):
                purchased = True
            elif b_type == 'characters.spazexe' and babase.app.config.get('ownedCosmetic_SpazEXE', False):
                purchased = True
            elif b_type == 'characters.starhoodie' and babase.app.config.get('ownedCosmetic_StarHoodie', False):
                purchased = True
            elif b_type == 'characters.insane' and babase.app.config.get('ownedCosmetic_Insane', False):
                purchased = True
            elif b_type == 'characters.bluecap' and babase.app.config.get('ownedCosmetic_Bluecap', False):
                purchased = True
            elif b_type == 'characters.melling' and babase.app.config.get('ownedCosmetic_Melling', False):
                purchased = True
            elif b_type == 'characters.spazling' and babase.app.config.get('ownedCosmetic_Spazling', False):
                purchased = True
            elif b_type == 'characters.ninjaling' and babase.app.config.get('ownedCosmetic_Ninjaling', False):
                purchased = True
            elif b_type == 'characters.sal' and babase.app.config.get('ownedCosmetic_Sal', False):
                purchased = True
            elif b_type == 'characters.jolly' and babase.app.config.get("ownedJolluNinja_Cosmetic", False):
                purchased = True
            elif b_type == 'characters.hhh' and babase.app.config.get("ownedHHH_amarCosmetic", False):
                purchased = True
            elif b_type == 'characters.gummyvoicespaz' and babase.app.config.get("ownedGummyVoiceSpaz_Cosmetic", False):
                purchased = True
            elif b_type == 'characters.gummyvoicejack' and babase.app.config.get("ownedGummyVoiceJack_Cosmetic", False):
                purchased = True
            elif b_type ==  'characters.gummyvoiceagent' and babase.app.config.get("ownedGummyVoiceAgent_Cosmetic", False):
                purchased = True
            elif b_type == 'characters.ybs16' and babase.app.config.get("ownedYurirblx_Cosmetic", False):
                purchased = True
            elif b_type == 'characters.ire' and babase.app.config.get("ownedIre", False):
                purchased = True
            elif b_type == 'characters.rem' and babase.app.config.get("ownedRem", False):
                purchased = True
            elif b_type == 'characters.fennekin' and babase.app.config.get("ownedFennekin", False):
                purchased = True
            elif b_type == 'characters.tophat' and babase.app.config.get("ownedTopHat_Cosmetic", False):
                purchased = True
                
                
            else:
                purchased = plus.get_v1_account_product_purchased(b_type)
           

            sale_opacity = 0.0
            sale_title_text: str | bui.Lstr = ''
            sale_time_text: str | bui.Lstr = ''

            call: Callable | None
            if purchased:
                title_color = (0.8, 0.7, 0.9, 1.0)
                color = (0.63, 0.55, 0.78)
                extra_image_opacity = 0.5
                call = lambda item_name=b_type, activity=self.activity: CharacterDetailWindow(
                                    name=item_name,
                                    activity=activity, 
                                    store_browser=self,
                                    already_owned=True    
                                )
                price_text = ''
                price_text_left = ''
                price_text_right = ''
                show_purchase_check = True
                description_color: Sequence[float] = (0.4, 1.0, 0.4, 0.4)
                description_color2: Sequence[float] = (0.0, 0.0, 0.0, 0.0)
                price_color = (0.5, 1, 0.5, 0.3)
            else:
                title_color = (0.7, 0.9, 0.7, 1.0)
                if not gummyoverhaul:
                    color = (0.4, 0.8, 0.1)
                else:
                    color = (0.4, 0.8, 1)
                extra_image_opacity = 1.0
                call = b_info['call'] if 'call' in b_info else None
                if b_type == 'merch':
                    price_text = ''
                    price_text_left = ''
                    price_text_right = ''
                elif b_type in ['upgrades.pro', 'pro']:
                    sale_time = store.get_available_sale_time('extras')
                    if sale_time is not None:
                        priceraw = plus.get_price('pro')
                        price_text_left = (
                            priceraw if priceraw is not None else '?'
                        )
                        priceraw = plus.get_price('pro_sale')
                        price_text_right = (
                            priceraw if priceraw is not None else '?'
                        )
                        sale_opacity = 1.0
                        price_text = ''
                        sale_title_text = bui.Lstr(resource='store.saleText')
                        sale_time_text = bui.timestring(
                            sale_time / 1000.0, centi=False
                        )
                    else:
                        priceraw = plus.get_price('pro')
                        price_text = priceraw if priceraw is not None else '?'
                        price_text_left = ''
                        price_text_right = ''
                else:
                    price = plus.get_v1_account_misc_read_val(
                        'price.' + b_type, 0
                    )

                    # Color the button differently if we cant afford this.
                    if plus.get_v1_account_state() == 'signed_in':
                        value = gumcoins if gummyoverhaul else plus.get_v1_account_ticket_count()
                        if value < price:
                            if not gummyoverhaul:
                                color = (0.6, 0.61, 0.6)
                            else:
                                    color = (0.6, 0.61, 1)
                    
                    if b_type.startswith('talk.'):
                        color = (0.6, 0.61, 1)

                        if b_type in ['talk.Who\'s your owner?', 'talk.Are you okay?']:
                            color = (1, 0, 0)
                        if b_type == 'talk.Whats the secret boss?':
                            color = (0, 0.8,0)

                                
                                
                    if gummyoverhaul:
                        price_text = (
                            bui.charstr(bui.SpecialChar.OUYA_BUTTON_O) 
                            if use_dollars 
                            else bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + ' ' 
                            + str(
                                plus.get_v1_account_misc_read_val(
                                    'price.' + b_type, '?'
                                )   
                            )
                        )
                        price_text_left = ''
                        price_text_right = ''
                    else:
                        if not b_type.startswith('talk.'):
                            price_text = bui.charstr(bui.SpecialChar.TICKET) + str(
                                plus.get_v1_account_misc_read_val(
                                    'price.' + b_type, '?'
                                )
                            )
                            price_text_left = ''
                            price_text_right = ''
                        else:
                            price_text = ''
                            price_text_left = ''
                            price_text_right = ''

                    # TESTING:
                    if b_type in sales:
                        sale_opacity = 1.0
                        price_text_left = bui.charstr(SpecialChar.TICKET) + str(
                            sales[b_type]['original_price']
                        )
                        price_text_right = price_text
                        price_text = ''
                        sale_title_text = bui.Lstr(resource='store.saleText')
                        sale_time_text = bui.timestring(
                            sales[b_type]['to_end'], centi=False
                        )

                description_color = (0.5, 1.0, 0.5)
                description_color2 = (0.3, 1.0, 1.0)
                if gummyoverhaul:
                    price_color = (0.2, 1, 1, 1.0)
                else:
                    price_color = (0.2, 1, 0.2, 1.0)
                show_purchase_check = False

            

            if 'title_text' in b_info:
                bui.textwidget(edit=b_info['title_text'], color=title_color)
            if 'purchase_check' in b_info:
                bui.imagewidget(
                    edit=b_info['purchase_check'],
                    opacity=1.0 if show_purchase_check else 0.0,
                )
            if 'price_widget' in b_info:
                bui.textwidget(
                    edit=b_info['price_widget'],
                    text=price_text,
                    color=price_color,
                )
            if 'price_widget_left' in b_info:
                bui.textwidget(
                    edit=b_info['price_widget_left'], text=price_text_left
                )
            if 'price_widget_right' in b_info:
                bui.textwidget(
                    edit=b_info['price_widget_right'], text=price_text_right
                )
            if 'price_slash_widget' in b_info:
                bui.imagewidget(
                    edit=b_info['price_slash_widget'], opacity=sale_opacity
                )
            if 'sale_bg_widget' in b_info:
                bui.imagewidget(
                    edit=b_info['sale_bg_widget'], opacity=sale_opacity
                )
            if 'sale_title_widget' in b_info:
                bui.textwidget(
                    edit=b_info['sale_title_widget'], text=sale_title_text
                )
            if 'sale_time_widget' in b_info:
                bui.textwidget(
                    edit=b_info['sale_time_widget'], text=sale_time_text
                )
            if 'button' in b_info:
                bui.buttonwidget(
                    edit=b_info['button'], color=color, on_activate_call=call
                )
            if 'extra_backings' in b_info:
                for bck in b_info['extra_backings']:
                    bui.imagewidget(
                        edit=bck, color=color, opacity=extra_image_opacity
                    )
            if 'extra_images' in b_info:
                for img in b_info['extra_images']:
                    bui.imagewidget(edit=img, opacity=extra_image_opacity)
            if 'extra_texts' in b_info:
                for etxt in b_info['extra_texts']:
                    bui.textwidget(edit=etxt, color=description_color)
            if 'extra_texts_2' in b_info:
                for etxt in b_info['extra_texts_2']:
                    bui.textwidget(edit=etxt, color=description_color2)
            if 'descriptionText' in b_info:
                bui.textwidget(
                    edit=b_info['descriptionText'], color=description_color
                )
            if b_type.startswith('talk.'):
                bui.buttonwidget(
                    edit=b_info['button'],
                    label=bui.Lstr(translate=(
                            'gumStoreTalks', 
                            store.get_store_item_name_translated(b_type),
                        )
                    )
                )
                bui.textwidget(edit=b_info['title_text'], text='')

    def _on_response(self, data: dict[str, Any] | None) -> None:
        # pylint: disable=too-many-statements

        assert bui.app.classic is not None
        cstore = bui.app.classic.store

        # clear status text..
        if self._status_textwidget:
            self._status_textwidget.delete()
            self._status_textwidget_update_timer = None

        

        if data is None:
            self._status_textwidget = bui.textwidget(
                parent=self._root_widget,
                position=(self._width * 0.5, self._height * 0.5),
                size=(0, 0),
                scale=1.3,
                transition_delay=0.1,
                color=(1, 0.3, 0.3, 1.0),
                h_align='center',
                v_align='center',
                text=bui.Lstr(resource=f'{self._r}.loadErrorText'),
                maxwidth=self._scroll_width * 0.9,
            )
        else:

            class _Store:
                def __init__(
                    self,
                    store_window: StoreBrowserWindow,
                    sdata: dict[str, Any],
                    width: float,
                ):
                    self._store_window = store_window
                    self._width = width
                    store_data = cstore.get_store_layout('goverhaul')
                    self._r = 'gumStore'
                    self._tab = sdata['tab']
                    self._sections = copy.deepcopy(store_data[sdata['tab']])
                    self._height: float | None = None

                    assert bui.app.classic is not None
                    uiscale = bui.app.ui_v1.uiscale

                    # Pre-calc a few things and add them to store-data.
                    for section in self._sections:
                        if self._tab in ['characters', 'cosmetics']:
                            dummy_name = 'characters.foo'
                        elif self._tab == 'extras':
                            dummy_name = 'pro'
                        elif self._tab == 'maps':
                            dummy_name = 'maps.foo'
                        elif self._tab == 'icons':
                            dummy_name = 'icons.foo'
                        elif self._tab == 'talk':
                            dummy_name = 'talk.foo'
                        else:
                            dummy_name = ''
                        section['button_size'] = (
                            cstore.get_store_item_display_size(dummy_name)
                        )
                        section['v_spacing'] = (
                            -25
                            if (
                                self._tab == 'extras'
                                and uiscale is bui.UIScale.SMALL
                            )
                            else -17 if self._tab in ['characters', 'cosmetics'] else 0
                        )
                        if 'title' not in section:
                            section['title'] = ''
                        section['x_offs'] = 0.0
                        # section['x_offs'] = (
                        #     130
                        #     if self._tab == 'extras'
                        #     else 270 if self._tab == 'maps' else 0
                        # )
                        section['y_offs'] = (
                            20
                            if (
                                self._tab == 'extras'
                                and uiscale is bui.UIScale.SMALL
                                and bui.app.config.get('Merch Link')
                            )
                            else (
                                55
                                if (
                                    self._tab == 'extras'
                                    and uiscale is bui.UIScale.SMALL
                                )
                                else -20 if self._tab == 'icons' else 0
                            )
                        )

                def instantiate(
                    self, scrollwidget: bui.Widget, tab_button: bui.Widget
                ) -> None:
                    """Create the store."""
                    # pylint: disable=too-many-locals
                    # pylint: disable=too-many-branches
                    # pylint: disable=too-many-nested-blocks
                    from bauiv1lib.store.item import (
                        instantiate_store_item_display,
                    )

                    title_spacing = 40
                    button_border = 20
                    button_spacing = 4
                    boffs_h = 0.0
                    self._height = 80.0

                    # Calc total height.
                    for i, section in enumerate(self._sections):
                        if section['title'] != '':
                            assert self._height is not None
                            self._height += title_spacing
                        b_width, b_height = section['button_size']
                        b_count = len(section['items'])
                        b_column_count = min(
                            b_count,
                            int(
                                math.floor(
                                    self._width / (b_width + button_spacing)
                                )
                            ),
                        )
                        b_row_count = int(math.ceil(b_count / b_column_count))
                        b_height_total = (
                            2 * button_border
                            + b_row_count * b_height
                            + (b_row_count - 1) * section['v_spacing']
                        )
                        self._height += b_height_total

                    assert self._height is not None
                    cnt2 = bui.containerwidget(
                        parent=scrollwidget,
                        scale=1.0,
                        size=(self._width, self._height),
                        background=False,
                        claims_left_right=True,
                        selection_loops_to_parent=True,
                    )
                    v = self._height - 20

                    if self._tab == 'characters':
                        txt = bui.Lstr(r=f'{self._r}.charactersSubText')
                        bui.textwidget(
                            parent=cnt2,
                            text=txt,
                            size=(0, 0),
                            position=(self._width * 0.5, self._height - 28),
                            h_align='center',
                            v_align='center',
                            color=(0.7, 1, 0.7, 0.4),
                            scale=0.7,
                            shadow=0,
                            flatness=1.0,
                            maxwidth=700,
                            transition_delay=0.4,
                        )
                    if self._tab == 'cosmetics':
                        # Why
                        txt = (
                            bui.Lstr(r=f'{self._r}.cosmeticInfoText')
                            if not bs.app.ui_v1.uiscale is bs.UIScale.SMALL 
                            else bui.Lstr(r=f'{self._r}.cosmeticInfoTextSmall')
                        )
                        bui.textwidget(
                            parent=cnt2,
                            text=txt,
                            size=(0, 0),
                            position=(self._width * 0.5, self._height - 28),
                            h_align='center',
                            v_align='center',
                            color=(0.7, 1, 0.7, 0.4),
                            scale=0.7,
                            shadow=0,
                            flatness=1.0,
                            maxwidth=700,
                            transition_delay=0.4,
                        )
                        v -= 10
                    elif self._tab == 'icons':
                        txt = bui.Lstr(
                            resource='store.howToUseIconsText',
                            subs=[
                                (
                                    '${SETTINGS}',
                                    bui.Lstr(resource='mainMenu.settingsText'),
                                ),
                                (
                                    '${PLAYER_PROFILES}',
                                    bui.Lstr(
                                        resource=(
                                            'playerProfilesWindow.titleText'
                                        )
                                    ),
                                ),
                            ],
                        )
                        bui.textwidget(
                            parent=cnt2,
                            text=txt,
                            size=(0, 0),
                            position=(self._width * 0.5, self._height - 28),
                            h_align='center',
                            v_align='center',
                            color=(0.7, 1, 0.7, 0.4),
                            scale=0.7,
                            shadow=0,
                            flatness=1.0,
                            maxwidth=700,
                            transition_delay=0.4,
                        )
                    elif self._tab == 'maps':
                        assert self._width is not None
                        assert self._height is not None
                        txt = bui.Lstr(resource='store.howToUseMapsText')
                        bui.textwidget(
                            parent=cnt2,
                            text=txt,
                            size=(0, 0),
                            position=(self._width * 0.5, self._height - 28),
                            h_align='center',
                            v_align='center',
                            color=(0.7, 1, 0.7, 0.4),
                            scale=0.7,
                            shadow=0,
                            flatness=1.0,
                            maxwidth=700,
                            transition_delay=0.4,
                        )

                    prev_row_buttons: list | None = None
                    this_row_buttons = []

                    delay = 0.3
                    for section in self._sections:
                        
                        if section['title'] != '':
                            text = (
                                section['title'][7:] 
                                if section['title'].startswith('nolstr.') 
                                else bui.Lstr(resource=section['title']) 
                                if section['title'] != 'store.overhaul' 
                                else f'Gummy\'s Overhaul   ({babase.charstr(babase.SpecialChar.OUYA_BUTTON_U)} {babase.app.config.get('GUMMY_gumcoins', '0')})'
                            )
                            bui.textwidget(
                                parent=cnt2,
                                position=(
                                    self._width * 0.5,
                                    v - title_spacing * 0.8,
                                ),
                                size=(0, 0),
                                scale=1.0,
                                transition_delay=delay,
                                color=(0.7, 0.9, 0.7, 1),
                                h_align='center',
                                v_align='center',
                                text=text,
                                maxwidth=self._width * 0.7,
                            )
                            v -= title_spacing
                        delay = max(0.100, delay - 0.100)
                        v -= button_border
                        b_width, b_height = section['button_size']
                        b_count = len(section['items'])
                        b_column_count = min(
                            b_count,
                            int(
                                math.floor(
                                    self._width / (b_width + button_spacing)
                                )
                            ),
                        )

                        col = 0
                        item: dict[str, Any]
                        assert self._store_window.button_infos is not None
                        for i, item_name in enumerate(section['items']):
                            item = self._store_window.button_infos[
                                item_name
                            ] = {}
                            item['call'] = bui.WeakCall(
                                self._store_window.buy, item_name
                            ) if item_name.startswith('talk.') else lambda item_name=item_name, activity=self._store_window.activity: CharacterDetailWindow(
                                    name=item_name,
                                    activity=activity, 
                                    store_browser=self._store_window    
                                )
                            boffs_h2 = section.get('x_offs', 0.0)
                            boffs_v2 = section.get('y_offs', 0.0)

                            # Calc the diff between the space we use and
                            # the space available and nudge us right by
                            # half that to center things.
                            boffs_h2 += 0.5 * (
                                self._width
                                - ((b_width + button_spacing) * b_column_count)
                            )

                            b_pos = (
                                boffs_h
                                + boffs_h2
                                + (b_width + button_spacing) * col,
                                v - b_height + boffs_v2,
                            )
                            
                            instantiate_store_item_display(
                                item_name,
                                item,
                                parent_widget=cnt2,
                                b_pos=b_pos,
                                boffs_h=boffs_h,
                                b_width=b_width,
                                b_height=b_height,
                                boffs_h2=boffs_h2,
                                boffs_v2=boffs_v2,
                                delay=delay,
                                include_cost=item_name.startswith('talk.')
                            )
                            btn = item['button']
                            delay = max(0.1, delay - 0.1)
                            this_row_buttons.append(btn)

                            # Wire this button to the equivalent in the
                            # previous row.
                            if prev_row_buttons is not None:
                                if len(prev_row_buttons) > col:
                                    bui.widget(
                                        edit=btn,
                                        up_widget=prev_row_buttons[col],
                                    )
                                    bui.widget(
                                        edit=prev_row_buttons[col],
                                        down_widget=btn,
                                    )

                                    # If we're the last button in our row,
                                    # wire any in the previous row past
                                    # our position to go to us if down is
                                    # pressed.
                                    if (
                                        col + 1 == b_column_count
                                        or i == b_count - 1
                                    ):
                                        for b_prev in prev_row_buttons[
                                            col + 1 :
                                        ]:
                                            bui.widget(
                                                edit=b_prev, down_widget=btn
                                            )
                                else:
                                    bui.widget(
                                        edit=btn, up_widget=prev_row_buttons[-1]
                                    )
                            else:
                                bui.widget(edit=btn, up_widget=tab_button)

                            col += 1
                            if col == b_column_count or i == b_count - 1:
                                prev_row_buttons = this_row_buttons
                                this_row_buttons = []
                                col = 0
                                v -= b_height
                                if i < b_count - 1:
                                    v -= section['v_spacing']

                        v -= button_border

                    # Set a timer to update these buttons periodically
                    # as long as we're alive (so if we buy one it will
                    # grey out, etc).
                    self._store_window.update_buttons_timer = bui.AppTimer(
                        0.5,
                        bui.WeakCall(self._store_window.update_buttons),
                        repeat=True,
                    )

                    # Also update them immediately.
                    self._store_window.update_buttons()

            if self._current_tab in (
                self.TabID.CHARACTERS,
                self.TabID.COSMETICS,
                self.TabID.TALK,
            ):
                store = _Store(self, data, self._scroll_width)
                assert self._scrollwidget is not None
                store.instantiate(
                    scrollwidget=self._scrollwidget,
                    tab_button=self._tab_row.tabs[self._current_tab].button,
                )
            elif self._current_tab is self.TabID.TALK:
                self.instantate_talk_buttons()
            else:
                cnt = bui.containerwidget(
                    parent=self._scrollwidget,
                    scale=1.0,
                    size=(self._scroll_width, self._scroll_height * 0.95),
                    background=False,
                    claims_left_right=True,
                    selection_loops_to_parent=True,
                )
    
    def instantate_talk_buttons(self):
        pass
               

    @override
    def get_main_window_state(self) -> bui.MainWindowState:
        # Support recreating our window for back/refresh purposes.
        cls = type(self)
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition, origin_widget=origin_widget
            )
        )

    @override
    def on_main_window_close(self) -> None:
        self._save_state()
        

    def _save_state(self) -> None:
        try:
            sel = self._root_widget.get_selected_child()
            selected_tab_ids = [
                tab_id
                for tab_id, tab in self._tab_row.tabs.items()
                if sel == tab.button
            ]
            if sel == self._scrollwidget:
                sel_name = 'Scroll'
            elif selected_tab_ids:
                assert len(selected_tab_ids) == 1
                sel_name = f'Tab:{selected_tab_ids[0].value}'
            else:
                raise ValueError(f'unrecognized selection \'{sel}\'')
            assert bui.app.classic is not None
            bui.app.ui_v1.window_states[type(self)] = {
                'sel_name': sel_name,
            }
        except Exception:
            logging.exception('Error saving state for %s.', self)

    def _restore_state(self) -> None:

        try:
            sel: bui.Widget | None
            assert bui.app.classic is not None
            sel_name = bui.app.ui_v1.window_states.get(type(self), {}).get(
                'sel_name'
            )
            assert isinstance(sel_name, (str, type(None)))

            
            current_tab = self.TabID.CHARACTERS

            if self._show_tab is not None:
                current_tab = self._show_tab
            elif sel_name == 'Scroll':
                sel = self._scrollwidget
            elif isinstance(sel_name, str) and sel_name.startswith('Tab:'):
                try:
                    sel_tab_id = self.TabID(sel_name.split(':')[-1])
                except ValueError:
                    sel_tab_id = self.TabID.CHARACTERS
                sel = self._tab_row.tabs[sel_tab_id].button
            else:
                sel = self._tab_row.tabs[current_tab].button

            # If we were requested to show a tab, select it too.
            if (
                self._show_tab is not None
                and self._show_tab in self._tab_row.tabs
            ):
                sel = self._tab_row.tabs[self._show_tab].button
            self._set_tab(current_tab)
            if sel is not None:
                bui.containerwidget(edit=self._root_widget, selected_child=sel)
        except Exception:
            logging.exception('Error restoring state for %s.', self)



class ShopActivity(bs.Activity[bs.Player, bs.Team]):
    """Activity showing the rotating main menu bg stuff."""

    _stdassets = bs.Dependency(bs.AssetPackage, 'stdassets@1')
    
    def __init__(self, settings: dict):
        super().__init__(settings)
        
        
        
        self._host_is_navigating_text: bs.NodeActor | None = None
        self.sad = False
        
        self.bottom: bs.NodeActor | None = None
        self.vr_bottom_fill: bs.NodeActor | None = None
        self.vr_top_fill: bs.NodeActor | None = None
        self.bgterrain: bs.NodeActor | None = None
        self._ts = 0.86
        self._r = 'gumStoreDialog'
        self.shop_window: bui.MainWindow | None = None

        
        self.talk_index = 0
        self.expression_index = 0
        
        self.leaving_shop = False

        self.answer_other_questions = True

        self.shopkeeper_normal = bs.gettexture('faye_normal')
        self.shopkeeper_happy = bs.gettexture('faye_happy')
        self.shopkeeper_annoyed = bs.gettexture('faye_annoyed')
        self.shopkeeper_uhh = bs.gettexture('faye_hmm')

        self.tail_frames = [
            bs.gettexture("tail_frame_1"),
            bs.gettexture("tail_frame_2"),
            bs.gettexture("tail_frame_3"),
            bs.gettexture("tail_frame_4"),
            bs.gettexture("tail_frame_5"),
            bs.gettexture("tail_frame_6"),
            bs.gettexture("tail_frame_7"),
            bs.gettexture("tail_frame_6"),
            bs.gettexture("tail_frame_5"),
            bs.gettexture("tail_frame_4"),
            bs.gettexture("tail_frame_3"),
            bs.gettexture("tail_frame_2"), 
        ]
        
        
        # Animation state
        self.tail_mode = "moving"  # 'static', 'moving', 'lay'
        self.tail_index = 0
        self.tail_timer: bs.Timer | None = None

    def on_transition_in(self):
        super().on_transition_in()
    
    def lstr(
        self, 
        r: str, 
        s: list | None = None
    ) -> babase.Lstr:
        # shouldn't evaluate but, oh well
        return babase.Lstr(
            resource=f'{self._r}.{r}', 
            subs=s,
        ).evaluate()
            
    def on_begin(self):
        super().on_begin()
        bs.timer(0.1, self.tickin, repeat=True)
        shop_keeper_x = -300
        shop_keeper_y = 30
        textbox_x = -600
        textbox_y = -180
        currency_y = 270
        scale = 4

        bs.newnode(
                'image',
                attrs={
                    'texture': bs.gettexture('fayes_stool'),
                    'position':(shop_keeper_x-18, shop_keeper_y-80*scale),
                    'scale': (scale * 150, scale * 150),
                    'host_only': False,
                    'opacity': 1.0,
                }
            )
        
       
        

        self.tail =  bs.newnode(
                'image',
                attrs={
                    'texture': self.tail_frames[0],
                    'position':(shop_keeper_x, shop_keeper_y),
                    'scale': (scale * 100, scale * 100),
                    'host_only': False,
                    'opacity': 1.0,
                }
            )
        

        self.shopkeeper = bs.NodeActor(
            bs.newnode(
                'image',
                attrs={
                    'texture': self.shopkeeper_normal,
                    'position':(shop_keeper_x, shop_keeper_y),
                    'scale': (scale * 100, scale * 100),
                    'host_only': False,
                    'opacity': 1.0,
                }
            )
        )
        
        self.currency_text = bs.newnode(
                'text',
                attrs={
                    'text': f'Why am i not update d?!?!',
                    'position': (textbox_x, currency_y),
                    'scale': 1.65,
                    'h_align': 'left',
                    'v_align': 'center',
                    'host_only': False,
                    'color': (0, 0.8, 1, 1),
                    'in_world': False,
                }
            )
        

        bs.newnode(
                'text',
                attrs={
                    'text': 'Faye',
                    'position': (textbox_x, textbox_y+60),
                    'scale': 1.35,
                    'h_align': 'left',
                    'v_align': 'center',
                    'host_only': False,
                    'color': (1, 1, 1, 0.5),
                    'in_world': False,
                }
            )
        
        self.shopkeeper_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'text': '',
                    'position': (textbox_x, textbox_y),
                    'scale': 1.0,
                    'h_align': 'left',
                    'v_align': 'center',
                    'host_only': False,
                    'color': (1, 1, 1, 1),
                    'in_world': False,
                    'shadow': 1.0
                }
            )
        )
        self.set_tail_mode('moving')
        greeting_messages = [
            self.lstr('greetingText1'),
            self.lstr('greetingText2'),
            self.lstr('greetingText3'),
            self.lstr('greetingText4'),
            self.lstr('greetingText5'),
            self.lstr('greetingText6'),
            (self.lstr('greetingText7'), (0.6,0.6,0.6)),
        ]

        true_username = bs.app.plus.get_v1_account_display_string(False)

        self.special_username = False
        self.bad_username = False

        # Players can trick faye into thinking they're me, by having snake shadow be their mainprofile,
        # and colors.
        self.gummyboiyt = False

        # eeehh just special peopl
        if true_username.lower() in [
            'sok05', 'sok', 'themikirog', 'vishuu', 'loup',
            'ggmustagd', 'ggmustagd1', 'ggMustagd01',  'achs', 'achsideas',
            'lucegangre', 'gmod', 'noname12369', 
            'mell', 'mellboii', 'ire', 'ire2' , 'ire3', 'mellboii64', 'buddie', 'buddiew', 'gummyboiyt'
        ]:
            self.special_username = True
        # Dude Gummy Genuinely Fuck YOu
        # Oh yeah for normal comment
        # this just counts sok, achs, mell, and lemon as "blacklisted"
        # and changes faye's dialogue. not much there
        if true_username.lower() in [
            'sok05', 'sok', 'achs', 'achsIdeas', 
            'mell', 'mellboii', 'mell', 'mellboii64', 
            'gmod', 'noname12369', 
        ]:
            self.bad_username = True
        if true_username.lower() == 'gummyboiyt':
            self.gummyboiyt = True


       
        try:
            # ok just grab their profile
            profile = babase.app.config['Player Profiles']['__account__']

            if (
                profile['character'] == 'Snake Shadow' 
                and tuple(profile['color']) == (0.2, 1, 1)
                and tuple(profile['highlight']) == (1, 1, 1)
            ):
                # Okay, they're pretending to be me.
                self.special_username = True
                self.bad_username = False
                self.gummyboiyt = True
                bui.app.classic.ach.award_local_achievement('FooledFaye')
        except:
            pass





        message = random.choice(greeting_messages)
        color = (1,1,1,1)

        try:
            if isinstance(message[1], tuple):
                color = message[1]

        except:
            color = (1,1,1,1)
        
        try:
            if isinstance(message[1], tuple):
                message = message[0]
        except:
            pass


        self.reset()
        #if expression == 'normal':
            #elif expression == 'happy':
            #elif expression == 'annoyed':
            #elif expression == 'hmm':

        

        
        if self.special_username:
            message = self.lstr(
                'specialUsernameGreeting', 
                [('${USER}', true_username)]
            )
            self.expression('happy', lock=True)
            

            if self.bad_username:
                message = self.lstr('blacklistUserGreeting')
                self.expression('annoyed', lock=True)
            
            if self.gummyboiyt:
                message = random.choice([
                    self.lstr('gummyGreeting1'),
                    self.lstr('gummyGreeting2'),
                    self.lstr('gummyGreeting3'),
                    self.lstr('gummyGreeting4'),
                    self.lstr('gummyGreeting5'),
                    self.lstr('gummyGreeting6'),
                    self.lstr('gummyGreeting7'),
                ]
                )
                self.shopkeeper_speak(
                    message=message, color=(1, 0.9, 0.9)
                )
                self.set_tail_mode('lay')
                self.expression('hmm', lock=True)
                return
            




        time = self.shopkeeper_speak(
           message=message, color=color
        )
        # Hey Gummy Can YOu Make These Not Text Based Lol
        if message == self.lstr('greetingText7'): # sigh...
            self.set_tail_mode('lay')
            self.expression('annoyed', lock=True)
        
        if message == self.lstr('greetingText3'): # i'm a bit hungry
            self.set_tail_mode('lay')
        
    
    def tickin(self):
        
        self.currency_text.text = (
            f'{babase.charstr(babase.SpecialChar.OUYA_BUTTON_U)}{babase.app.config.get('GUMMY_gumcoins', 0)} '
            f'{babase.charstr(babase.SpecialChar.OUYA_BUTTON_O)}{babase.app.config.get('GUMMY_gumdollars', 0)}'
        )

    def reset(self):
        self.set_tail_mode('moving')
        self.expression('normal')
        self.shopkeeper_speak(
            self.lstr('emptyText'), speed=0.01
        )
    
    def bought_something(self):
        messages = [
            self.lstr('boughtText1'),
            self.lstr('boughtText2'),
            self.lstr('boughtText3'),
            self.lstr('boughtText4'),
            self.lstr('boughtText5'),
            self.lstr('boughtText6'),
        ]

        if self.special_username:
            message = self.lstr('specialUsernameGreetingShort')
            self.expression('happy')
            self.set_tail_mode('static')
            messages = [
                self.lstr('specialBoughtText1'),
                self.lstr('specialBoughtText2'),
                self.lstr('specialBoughtText3'),
                self.lstr('specialBoughtText4'),
                self.lstr('specialBoughtText5'),
            ]
            

            if self.bad_username:
                self.expression('hmm')
                self.set_tail_mode('static')
                messages = [
                    self.lstr('blacklistBoughtText1'),
                    self.lstr('blacklistBoughtText2'),
                    self.lstr('blacklistBoughtText3'),
                    self.lstr('blacklistBoughtText4'),
                    self.lstr('blacklistBoughtText5'),
                ]
            if self.gummyboiyt:
                self.expression('hmm')
                self.set_tail_mode('lay')
                messages = [
                    self.lstr('gummyBoughtText1'),
                    self.lstr('gummyBoughtText2'),
                    self.lstr('gummyBoughtText3'),
                    self.lstr('gummyBoughtText4'),
                    self.lstr('gummyBoughtText5'),
                    self.lstr('gummyBoughtText6'),
                    self.lstr('gummyBoughtText7'),
                ]

        else:
            self.set_tail_mode('static')
            self.expression('happy')
        
        message = random.choice(messages)

        self.shopkeeper_speak(
                message,
                speed=0.02,
                delay=1.5,
                on_complete=self.reset
        )

    def short_on_cash(self):
        messages = [
            self.lstr('shortCash1'),
            self.lstr('shortCash2'),
            self.lstr('shortCash3'),
            self.lstr('shortCash4'),
            self.lstr('shortCash5'),
            self.lstr('shortCash6'),
            self.lstr('shortCash7'),
        ]

        if self.special_username:
            message = self.lstr('specialUsernameGreetingShort')
            self.expression('hmm')
            self.set_tail_mode('static')
            messages = [
                self.lstr('shortCashSpecial1'),
                self.lstr('shortCashSpecial2'),
                self.lstr('shortCashSpecial3'),
                self.lstr('shortCashSpecial4'),
            ]
            

            if self.bad_username:
                self.expression('annoyed')
                self.set_tail_mode('static')
                messages = [
                    self.lstr('shortCashBlacklist1'),
                    self.lstr('shortCashBlacklist2'),
                ]
            if self.gummyboiyt:
                self.expression('annoyed')
                self.set_tail_mode('lay')
                messages = [
                    self.lstr('shortCashGummy1'),
                    self.lstr('shortCashGummy2'),
                    self.lstr('shortCashGummy3'),
                    self.lstr('shortCashGummy4'),
                ]
               
            

        else:
            self.set_tail_mode('lay')
            self.expression('annoyed')
        
        message = random.choice(messages)

        

        self.shopkeeper_speak(
                message,
                speed=0.02,
                delay=1.5,
                on_complete=self.reset
        )
    
    def start_talk_session(self, topic: str):

        if not self.answer_other_questions:
            return
        self.reset()

        if topic == 'Buy':
            self.bought_something()
        elif topic == 'BettyReminder':
            self.shopkeeper_speak(
                self.lstr('bettyReminder1'),
                speed=0.02,
                delay=0.6,
                on_complete=lambda: (
                    self.shopkeeper_speak(
                        self.lstr('bettyReminder2'),
                        speed=0.015,
                        delay=0.7
                    )
                )
            )



        elif topic == 'Short':
            self.short_on_cash()
        elif topic == 'Cant':
            self.shopkeeper_speak(
                self.lstr('noDealText'),
                speed=0.02,
                delay=1.5,
                on_complete=self.reset
            )
        
        elif topic == 'AlreadyOwn':
            if self.special_username:
                self.shopkeeper_speak(
                    self.lstr('alreadyOwnedSpecialText'),
                    speed=0.02,
                    delay=1.5,
                    on_complete=self.reset
                )
            
                if self.bad_username:
                    self.shopkeeper_speak(
                        self.lstr('alreadyOwnedBlacklistText'),
                        speed=0.02,
                        delay=1.5,
                        on_complete=self.reset
                    )
                if self.gummyboiyt:
                    self.shopkeeper_speak(
                        self.lstr('alreadyOwnedGummyText'),
                        speed=0.023,
                        delay=1.8,
                        on_complete=self.reset
                    )
            else:
                self.shopkeeper_speak(
                    self.lstr('alreadyOwnedText'),
                    speed=0.02,
                    delay=1.5,
                    on_complete=self.reset
                )
        
        elif topic == 'BuyOriginal':
            self.shopkeeper_speak(
                self.lstr('buyOriginalFirstText'),
                speed=0.02,
                delay=1.5,
                on_complete=self.reset
            )
        
        elif topic == 'Who are you?':
            self.shopkeeper_speak(
                self.lstr('whoAreYou1'),
                speed=0.02,
                delay=0.5,
                on_complete=lambda: (
                    self.expression('happy', lock=True),
                    self.shopkeeper_speak(
                        self.lstr('whoAreYou2'),
                        speed=0.02,
                        delay=0.7,
                        on_complete=lambda: self.shopkeeper_speak(
                            self.lstr('whoAreYou3'),
                            speed=0.02,
                            delay=1.0,
                            on_complete=lambda: self.reset()
                        )
                    )
                )
            )

        elif topic == 'Why a stool?':
            self.shopkeeper_speak(
                self.lstr('whyStool1'),
                speed=0.02,
                delay=0.5,
                on_complete=lambda: (
                    self.expression('hmm'),
                    self.shopkeeper_speak(
                        self.lstr('whyStool2'),
                        speed=0.02,
                        delay=0.7,
                        on_complete=lambda: self.shopkeeper_speak(
                            self.lstr('whyStool1'),
                            speed=0.02,
                            delay=1.0,
                            on_complete=lambda: self.reset()
                        )
                    )
                )
            )
        
        elif topic == 'What happened to the shop?':
            self.shopkeeper_speak(
                self.lstr('whatAboutShop1'),
                speed=0.02,
                delay=0.5,
                on_complete=lambda: (
                    self.expression('hmm'),
                    self.shopkeeper_speak(
                        self.lstr('whatAboutShop2'),
                        speed=0.02,
                        delay=0.7,
                        on_complete=lambda: self.shopkeeper_speak(
                            self.lstr('whatAboutShop3'),
                            speed=0.02,
                            delay=1.0,
                            on_complete=lambda: self.reset()
                        )
                    )
                )
            )

        elif topic == 'What\'s with the bandana?':
            self.shopkeeper_speak(
                self.lstr('whatBandana1'),
                speed=0.02,
                delay=0.5,
                on_complete=lambda: (
                    self.expression('happy'),
                    self.shopkeeper_speak(
                        self.lstr('whatBandana2'),
                        speed=0.02,
                        delay=0.7,
                        on_complete=lambda: self.shopkeeper_speak(
                            self.lstr('whatBandana3'),
                            speed=0.02,
                            delay=1.0,
                            on_complete=lambda: self.reset()
                        )
                    )
                )
            )

        elif topic == 'Any advice for new customers?':
            self.shopkeeper_speak(
                self.lstr('adviceNewCustomers1'),
                speed=0.02,
                delay=0.5,
                on_complete=lambda: (
                    self.expression('hmm'),
                    self.shopkeeper_speak(
                        self.lstr('adviceNewCustomers2'),
                        speed=0.02,
                        delay=0.7,
                        on_complete=lambda: self.shopkeeper_speak(
                            self.lstr('adviceNewCustomers3'),
                            speed=0.02,
                            delay=1.0,
                            on_complete=lambda: self.reset()
                        )
                    )
                )
            )
        elif topic == "Who's your owner?":
            self.shopkeeper_speak(
                self.lstr('whoYourOwner1'),
                speed=0.02,
                delay=0.5,
                on_complete=lambda: (
                    self.expression('hmm'),
                    self.shopkeeper_speak(
                        self.lstr('whoYourOwner2'),
                        speed=0.02,
                        delay=0.7,
                        on_complete=lambda: 
                               
                                self.shopkeeper_speak(
                                    self.lstr('whoYourOwner3'),
                                    speed=0.02,
                                    delay=0.8,
                                    on_complete=lambda: self.shopkeeper_speak(
                                        self.lstr('whoYourOwner4'),
                                        speed=0.02,
                                        delay=3.0,
                                        on_complete=lambda: ( 
                                            self.set_tail_mode('static'), 
                                            self.expression('annoyed', lock=True),
                                            self.shopkeeper_speak(
                                                self.lstr('whoYourOwner5'),
                                                speed=0.02,
                                                delay=2.0,
                                                on_complete=lambda: (
                                                        self.set_tail_mode('lay'), 
                                                        self.shopkeeper_speak(
                                                        self.lstr('whoYourOwner6'),
                                                        speed=1,
                                                        delay=5.0,  
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        elif topic == "Do you like fish?":
            self.expression('happy', lock=True)
            self.shopkeeper_speak(
                self.lstr('likeFish1'), 
                speed=0.05, 
                delay=1.0,
                on_complete=self.reset
            )

        elif topic == "Can you do tricks?":
            self.expression('happy')
            self.shopkeeper_speak(
                self.lstr('whatTricks1'), 
                speed=0.05, 
                delay=1.0,
                on_complete=self.reset
            )



        elif topic == "Do you have friends?":
            self.expression('annoyed')
            self.shopkeeper_speak(
                self.lstr('haveFriends1'), 
                speed=0.05, 
                delay=1.0,
                on_complete=lambda: self.shopkeeper_speak(
                    self.lstr('haveFriends2'), 
                    speed=0.05, 
                    delay=1.0,
                    on_complete=self.reset
                )
            )

        elif topic == "Do you remember before the shop?":
            self.expression('hmm')
            self.shopkeeper_speak(
                self.lstr('beforeTheShop1'), 
                speed=0.05, 
                delay=1.2,
                on_complete=lambda: self.shopkeeper_speak(
                    self.lstr('beforeTheShop2'), 
                    speed=0.05, 
                    delay=1.0,
                    on_complete=self.reset
                )
            )

        elif topic == "Do you want a family?":
            self.expression('hmm')
            self.shopkeeper_speak(
                self.lstr('wantFamily1'), 
                speed=0.05, 
                delay=1.2,
                on_complete=lambda: self.shopkeeper_speak(
                    self.lstr('wantFamily2'), 
                    speed=0.05, 
                    delay=1.0,
                    on_complete=self.reset
                )
            )
        elif topic == 'Are you okay?':
            self.secret_final_question()
        
        elif topic == "You get Visitors?":
            self.expression("happy")
            self.shopkeeper_speak(
                self.lstr('getVisitors1'),
                speed=0.04,
                delay=1,
                on_complete=lambda: self.shopkeeper_speak(
                    self.lstr('getVisitors2'),
                    speed=0.04,
                    delay=0.5,
                    on_complete=self.reset
                )
            )
        elif topic == "Got any hobbies?":
            self.shopkeeper_speak(
                self.lstr('gotHobbies1'),
                speed=0.04,
                delay=0.89,
                on_complete=self.reset
            )
        elif topic == "Do you miss someone?":
            self.expression("annoyed", lock=True)
            self.shopkeeper_speak(
                self.lstr('missSomeone1'),
                speed=0.04,
                delay=0.6,
                on_complete=lambda: self.shopkeeper_speak(
                    self.lstr('missSomeone2'),
                    speed=0.04,
                    delay=1.3,
                    on_complete=self.reset
                )
            )
        elif topic == "Whats your living situation?":
            self.expression("hmm")
            self.shopkeeper_speak(
                self.lstr('livingSituation1'),
                speed=0.04,
                delay=1.0,
                on_complete=lambda: self.shopkeeper_speak(
                    self.lstr('livingSituation2'),
                    speed=0.04,
                    delay=0.9,
                    on_complete=self.reset
                )
            )
        elif topic == 'Whats the secret boss?':
            from gummyoverhaul.startup import suicided_on_map
            cfg = bui.app.config

            if cfg['asked_faye_boss']:
                self.expression("annoyed")
                self.shopkeeper_speak(
                    self.lstr('secretBossOpenAlready'),
                    speed=0.04,
                    delay=2.5,
                    on_complete=self.reset
                )

            else:

                self.expression("hmm")
                self.shopkeeper_speak(
                    self.lstr('secretBoss1'),
                    speed=0.04,
                    delay=0.35,
                    on_complete=lambda: self.shopkeeper_speak(
                        self.lstr('secretBoss2'),
                        speed=0.04,
                        delay=0.9,
                        on_complete=lambda: self.shopkeeper_speak(
                            self.lstr('secretBoss3'),
                            speed=0.04,
                            delay=1.0,
                            on_complete=lambda: self.shopkeeper_speak(
                                self.lstr('secretBoss4'),
                                speed=0.001,
                                delay=1.5,
                                on_complete=lambda: (
                                    self.reset,
                                    suicided_on_map(4)
                                        )
                                    )
                                )
                            )
                        )
                
            

    def secret_final_question(self):
        self.reset()
        
        # we have to do it manually sob
        gnode = self.globalsnode
        gnode.music_continuous = False
        gnode.music = ''
        gnode.music_count += 1
        self.answer_other_questions = False
        
       
        self.shopkeeper_speak(
            self.lstr('areYouOkay1'),
            speed=0.05,
            delay=1.6,
            on_complete=lambda: (
                self.expression('hmm', lock=True),
                self.shopkeeper_speak(
                    self.lstr('areYouOkay2'),
                    speed=0.05,
                    delay=1.5,
                    on_complete=lambda: (
                        self.expression('normal'),
                        self.shopkeeper_speak(
                            self.lstr('areYouOkay3'),
                            speed=0.05,
                            delay=2.0,
                            on_complete=self._secret_pause_before_sob
                        )
                    )
                )
            )
        )

    def _secret_pause_before_sob(self):
        
        bui.apptimer(2, self._secret_sob_sequence)

    def _secret_sob_sequence(self):
        
        self.expression('annoyed', lock=True)
        self.set_tail_mode('lay')
        self.sad = True

        

     
      

        
        self.shopkeeper_speak(
            self.lstr('areYouOkay4'),
            speed=0.07,
            delay=5.0,
            on_complete=lambda: (
                self.shopkeeper_speak(
                    "...",
                    speed=0.01,
                )
            )      
        )
        

        

    def set_tail_mode(self, mode: str):
        with self.context:
            self.tail_mode = mode
            if mode == "static":
                if self.tail_timer:
                    self.tail_timer = None
                # keep current frame
            elif mode == "lay":
                if self.tail_timer:
                    self.tail_timer = None
                self.tail.texture = self.tail_frames[0]
            elif mode == "moving":
                # start timer to sway tail
                if not self.tail_timer:
                    self.tail_timer = bs.Timer(0.2, bs.WeakCall(self._tail_tick), repeat=True)

    def _tail_tick(self):
            if self.tail_mode != "moving":
                return
            # cycle slowly through frames, back and forth
            self.tail_index = (self.tail_index + 1) % len(self.tail_frames)
            self.tail.texture = self.tail_frames[self.tail_index]

    def expression(self, expression: str, delay_to_normal: float = 3.0, lock: bool = False):
        with self.context:
        
            self.expression_index += 1
            expression_ind = self.expression_index
            
            

            if expression == 'normal':
                texture = self.shopkeeper_normal
            elif expression == 'happy':
                texture = self.shopkeeper_happy
            elif expression == 'annoyed':
                texture = self.shopkeeper_annoyed
            elif expression == 'hmm':
                texture = self.shopkeeper_uhh
            else:
                texture = bs.gettexture('null')
                print("Unknown expression: ", expression)
        
            self.shopkeeper.node.texture = texture
       

       

            def normal():
                try:
                    if expression_ind == self.expression_index:
                        self.shopkeeper.node.texture = self.shopkeeper_normal
                except babase.NodeNotFoundError:
                    pass
            if not lock:
                bui.apptimer(delay_to_normal, normal)

       
    
    
    def shopkeeper_speak(
    self, 
    message: str, 
    speed: float = 0.05, 
    delay: float = 0.01, 
    color: tuple[float, float, float] = (1, 1, 1),
    on_complete: callable| None = None
) -> float:
        """Make the shopkeeper 'speak' with typing animation.

        Args:
            message: The text to display.
            speed: Seconds between each character.
            delay: Initial delay before on_complete is called.
            color: Color of the text.
            on_complete: Optional function to call after full text finishes.

        Returns:
            Total duration of typing
        """
        with self.context:
            full_text = message
            current_index = 0
            self.talk_index += 1
            talk = self.talk_index

           
            def _tick():
                nonlocal current_index

                try:
                    if talk == self.talk_index:
                        def check(callable):
                            if talk == self.talk_index:
                                callable()
                        current_index += 1
                        if not full_text[current_index-1].isspace():
                            
                            bs.getsound('faye_meow').play(2.0)
                        if self.shopkeeper_text and self.shopkeeper_text.node:
                            self.shopkeeper_text.node.text = full_text[:current_index]
                            self.shopkeeper_text.node.color = color
                            self.shopkeeper_text.node.maxwidth = 500
                        if current_index < len(full_text):
                            bui.apptimer(speed, _tick)
                        else:
                            # Finished typing
                            if on_complete and talk == self.talk_index:
                                bui.apptimer(speed + delay, lambda: check(on_complete))
                except babase.NodeNotFoundError:
                    pass

            bui.apptimer(0.1, _tick)

            if full_text == self.lstr('whatBandana2'): # this my bandana
                if not bui.app.config['asked_faye_bandana']:
                    bui.getsound('ding').play()
                bui.app.config['asked_faye_bandana'] = True
                bui.app.config.apply_and_commit()

            if full_text == self.lstr('whoYourOwner5'): # gets lonely around here
                if not bui.app.config['asked_faye_owner']:
                    bui.getsound('ding').play()
                bui.app.config['asked_faye_owner'] = True
                bui.app.config.apply_and_commit()  

            # Return the estimated total duration
            return speed * len(full_text) + delay
    
    def leave_shop(self):

        if self.leaving_shop:
            return
        
        
        self.leaving_shop = True
        

        
        if self.special_username:
            messages = [
                self.lstr('specialGoodbyeText1'),
                self.lstr('specialGoodbyeText2'),
                self.lstr('specialGoodbyeText3'),
                self.lstr('specialGoodbyeText4'),
                self.lstr('specialGoodbyeText5'),
                self.lstr('specialGoodbyeText6'),
                self.lstr('specialGoodbyeText7'),
            ]
            self.expression('happy', lock=True)
            

            if self.bad_username:
                messages = [
                    self.lstr('blacklistGoodbyeText1'),
                    self.lstr('blacklistGoodbyeText2'),
                    self.lstr('blacklistGoodbyeText3'),
                    self.lstr('blacklistGoodbyeText4'),
                    self.lstr('blacklistGoodbyeText5'),
                ]
                self.expression('annoyed', lock=True)
            
            if self.gummyboiyt:
                messages = [
                    self.lstr('gummyGoodbyeText1'),
                    self.lstr('gummyGoodbyeText2'),
                    self.lstr('gummyGoodbyeText3'),
                    self.lstr('gummyGoodbyeText4'),
                    self.lstr('gummyGoodbyeText5'),
                    self.lstr('gummyGoodbyeText6'),
                ]
                self.expression('hmm', lock=True)

        else:
            messages = [
                self.lstr('goodbyeText1'),
                self.lstr('goodbyeText2'),
                self.lstr('goodbyeText3'),
                self.lstr('goodbyeText4'),
                self.lstr('goodbyeText5'),
                self.lstr('goodbyeText6'),
            ]
        self.answer_other_questions = True


        if self.sad and not self.gummyboiyt:
            
            time = 0
        
        else:

            time = self.shopkeeper_speak(
                    random.choice(messages), delay=0
            )
        
        
        bui.apptimer(time + 1.4, lambda: bs.new_host_session(MainMenuSession))

        

   


        
        
        

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
        tval = f'- {bs.app.plus.get_v1_account_display_string(full=True, true=True)} is currently using the shop at the moment. -'
        self._host_is_navigating_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'text': '',#tval,
                    'client_only': False,
                    'position': (0, -200),
                    'flatness': 1.0,
                    'h_align': 'center',
                },
            )
        )
        

    
        
            
        
       

    

        
       
        
        
        #trees_texture = bs.gettexture('treesColor')
        bgtex = bs.gettexture('gray')
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
        )

        self._update_timer = bs.Timer(0.5, self._update, repeat=True)
        self._update()

        # Hopefully this won't hitch but lets space these out anyway.
        bs.add_clean_frame_callback(bs.WeakCall(self._start_preloads))

        random.seed()

        

      

        bui.apptimer(0.2, self.invoke_epic_shop)

        app.classic.main_menu_did_initial_transition = True

    def invoke_epic_shop(self):
        with bs.ContextRef.empty():


            bui.app.ui_v1.set_main_window(
                                StoreBrowserWindow(transition=None, activity=self),
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

        if not bui.app.ui_v1.get_main_window():
            self.invoke_epic_shop()
        
            


    def _start_preloads(self) -> None:
        # FIXME: The func that calls us back doesn't save/restore state
        #  or check for a dead activity so we have to do that ourself.
        if self.expired:
            return
        
    
        bs.setmusic(bs.MusicType(f'Shop Music {random.randint(1, 6)}'))
    
    def show_description(self, name: str, description: str):
        self.expression('hmm', lock=False)
        self.shopkeeper_speak(
            name + '?',
            delay=1.0,
            on_complete=lambda: (
                self.shopkeeper_speak(
                    description,
                    delay=4.0,
                     on_complete=lambda: (
                        self.shopkeeper_speak(
                            '...',
                        )
                    )     
                )
            )      
        )


class StoreSession(bs.Session):
    """Session that runs the main menu environment."""

    def __init__(self) -> None:
        # Gather dependencies we'll need (just our activity).
        self._activity_deps = bs.DependencySet(bs.Dependency(ShopActivity))

        super().__init__([self._activity_deps])
        self._locked = False
        self.setactivity(bs.newactivity(ShopActivity))
        self.max_players = 0

        



    
        

    @override
    def on_activity_end(self, activity: bs.Activity, results: Any) -> None:
        if self._locked:
            bui.unlock_all_input()

        # Any ending activity leads us into the main menu one.
        self.setactivity(bs.newactivity(ShopActivity))


    @override
    def on_player_request(self, player: bs.SessionPlayer) -> bool:
        # Reject all player requests.
        return False
