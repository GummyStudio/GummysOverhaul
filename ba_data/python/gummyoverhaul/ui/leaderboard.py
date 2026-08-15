"""UI for the Leaderboard."""
import bauiv1 as bui

class LeaderBoardWindow(bui.Window):
    """A popup window for showing overhaul's epic leaderboard"""

    def __init__(
        self,
        transition: str = 'in_scale',
    ):
        # FIXME: Tidy this up.
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals
        self._r = 'gameListWindow'
        
        self._transitioning_out = False
        uiscale = bui.app.ui_v1.uiscale
        self._width = 500
        self._height = 350
        scale = (
            1.8
            if uiscale is bui.UIScale.SMALL
            else 1.4 if uiscale is bui.UIScale.MEDIUM else 1.1
        )
        
        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height), 
                scale=scale,
                transition=transition,
            ),
        )
        self._subcontainerwidth = self._width
        self._subcontainerheight = 0
        # Alright, let's calculate a nice
        # centered scroll size.
        scroll_width = self._width - 50
        scroll_height = self._height * 0.7
        scroll_x = self._width * 0.5
        scroll_y = self._height * 0.5 
        # Add some offsets to make it fit.
        scroll_y -= 30
        self._scrollwidget = bui.scrollwidget(
            parent=self._root_widget,
            highlight=False,
            size=(scroll_width, scroll_height),
            position=(
                scroll_x - (scroll_width * 0.5),
                scroll_y - (scroll_height * 0.5),
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
            parent=self._root_widget,
            position=(self._width * 0.5, self._height * 0.5),
            style='bomb',
            size=40,
        )

        
        self._title_text = bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - 10),
            size=(0, 0),
            text='Leaderboard',
            scale=1.0,
            color=bui.app.ui_v1.title_color,
            maxwidth=self._width * 0.7,
            h_align='center',
        )

        self._cancel_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(25, self._height - 53),
            size=(50, 50),
            scale=0.7,
            label=bui.charstr(bui.SpecialChar.PLAY_STATION_CROSS_BUTTON),
            on_activate_call=self._on_cancel_press,
            autoselect=True,
            text_scale=1.2,
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=self._cancel_button,
        )
        self.failed = False

        # Update now.
        self._start_async_update()
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
        # Clear everything that existed.
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
        
        spacing = 35
        total_height = spacing * len(sorted_players)
        self._subcontainerheight = total_height

        y_pos = self._subcontainerheight - 10
        coins_glyph = bui.charstr(bui.SpecialChar.OUYA_BUTTON_U)
        dollars_glyph = bui.charstr(bui.SpecialChar.OUYA_BUTTON_O)
        getname = lambda: bui.app.plus.get_v1_account_display_string(True, True)
        tdelay = 0.2
        tdelay_inc = 0.05
        this_tdelay = tdelay

        for i, entry in enumerate(sorted_players, start=1):
            coins = entry.get("coins", 0)
            dollars = entry.get("dollars", 0)
            username = entry.get("username", "???")
            is_us = getname() == username
            color =  (1, 1, 0) if is_us else (1, 1, 1)

            trophy = bui.charstr(bui.SpecialChar(41)) if i == 1 else ""
            user_define_text = f"{trophy}{i}. {username} - "
            amount_text = f"{coins}{coins_glyph} / {dollars}{dollars_glyph}"

            text = bui.textwidget(
                parent=self._subcontainer,
                position=(5, y_pos),
                size=(0, 0),
                text=(
                    user_define_text +
                    amount_text
                ),
                color=color,
                h_align="left",
                shadow=1.0,
                maxwidth=380,
                transition_delay=this_tdelay,
            )
            this_tdelay += tdelay_inc
            self.entries.append(text)

            if is_us:
                text2 = bui.textwidget(
                    parent=self._root_widget,
                    position=(self._width * 0.5, self._height - 50),
                    size=(0, 0),
                    text=(
                        user_define_text +
                        amount_text
                    ),
                    color=(1, 1, 1),
                    h_align="center",
                    shadow=1.0,
                    maxwidth=self._width * 0.8,
                    transition_delay=tdelay,
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
       
    def _transition_out(self):
        bui.containerwidget(
            edit=self._root_widget, 
            transition='out_scale',
        )