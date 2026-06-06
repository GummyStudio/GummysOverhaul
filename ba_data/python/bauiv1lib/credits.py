# Released under the MIT License. See LICENSE for details.
#
"""Provides a window to display game credits."""

from __future__ import annotations

import os
import json
import logging
from typing import TYPE_CHECKING, override

import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Sequence


class CreditsWindow(bui.MainWindow):
    """Window for displaying game credits."""

    def __init__(
        self,
        transition: str | None = 'in_right',
        origin_widget: bui.Widget | None = None,
    ):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements

        bui.set_analytics_screen('Credits Window')

        assert bui.app.classic is not None
        uiscale = bui.app.ui_v1.uiscale
        width = 990 if uiscale is bui.UIScale.SMALL else 670
        height = 750 if uiscale is bui.UIScale.SMALL else 500

        # Do some fancy math to fill all available screen area up to the
        # size of our backing container. This lets us fit to the exact
        # screen shape at small ui scale.
        screensize = bui.get_virtual_screen_size()
        scale = (
            2.0
            if uiscale is bui.UIScale.SMALL
            else 1.2 if uiscale is bui.UIScale.MEDIUM else 1.0
        )
        # Calc screen size in our local container space and clamp to a
        # bit smaller than our container size.
        target_width = min(width - 80, screensize[0] / scale)
        target_height = min(height - 80, screensize[1] / scale)

        # To get top/left coords, go to the center of our window and
        # offset by half the width/height of our target area.
        yoffs = 0.5 * height + 0.5 * target_height + 30.0

        scroll_width = target_width
        scroll_height = target_height - 29
        scroll_y = yoffs - 58 - scroll_height

        self._r = 'creditsWindow'
        super().__init__(
            root_widget=bui.containerwidget(
                size=(width, height),
                toolbar_visibility=(
                    'menu_minimal'
                    if uiscale is bui.UIScale.SMALL
                    else 'menu_full'
                ),
                scale=scale,
            ),
            transition=transition,
            origin_widget=origin_widget,
            # We're affected by screen size only at small ui-scale.
            refresh_on_screen_size_changes=uiscale is bui.UIScale.SMALL,
        )

        if uiscale is bui.UIScale.SMALL:
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self.main_window_back
            )
        else:
            btn = bui.buttonwidget(
                parent=self._root_widget,
                position=(40, yoffs - 46),
                size=(60, 48),
                scale=0.8,
                label=bui.charstr(bui.SpecialChar.BACK),
                button_type='backSmall',
                on_activate_call=self.main_window_back,
                autoselect=True,
            )
            bui.containerwidget(edit=self._root_widget, cancel_button=btn)

        bui.textwidget(
            parent=self._root_widget,
            position=(
                width * 0.5,
                yoffs - (44 if uiscale is bui.UIScale.SMALL else 28),
            ),
            size=(0, 0),
            scale=0.8 if uiscale is bui.UIScale.SMALL else 1.0,
            text='Credits',#bui.Lstr(
                #resource=f'{self._r}.titleText',
                #subs=[('${APP_NAME}', bui.Lstr(resource='titleText'))],
            #),
            h_align='center',
            v_align='center',
            color=bui.app.ui_v1.title_color,
            maxwidth=scroll_width * 0.7,
        )

        scroll = bui.scrollwidget(
            parent=self._root_widget,
            size=(scroll_width, scroll_height),
            position=(width * 0.5 - scroll_width * 0.5, scroll_y),
            capture_arrows=True,
            border_opacity=0.4,
            center_small_content_horizontally=True,
        )

        bui.widget(
            edit=scroll,
            right_widget=bui.get_special_widget('squad_button'),
        )
        if uiscale is bui.UIScale.SMALL:
            bui.widget(
                edit=scroll,
                left_widget=bui.get_special_widget('back_button'),
            )

        def _format_names(names2: Sequence[str], inset: float) -> str:
            sval = ''
            # measure a series since there's overlaps and stuff..
            space_width = (
                bui.get_string_width(' ' * 10, suppress_warning=True) / 10.0
            )
            spacing = 330.0
            col1 = inset
            col2 = col1 + spacing
            col3 = col2 + spacing
            line_width = 0.0
            nline = ''
            for name in names2:
                # move to the next column (or row) and print
                if line_width > col3:
                    sval += nline + '\n'
                    nline = ''
                    line_width = 0

                if line_width > col2:
                    target = col3
                elif line_width > col1:
                    target = col2
                else:
                    target = col1
                spacingstr = ' ' * int((target - line_width) / space_width)
                nline += spacingstr
                nline += name
                line_width = bui.get_string_width(nline, suppress_warning=True)
            if nline != '':
                sval += nline + '\n'
            return sval

        sound_and_music = bui.Lstr(
            resource=f'{self._r}.songCreditText'
        ).evaluate()
        sound_and_music = sound_and_music.replace(
            '${TITLE}', "'William Tell (Trumpet Entry)'"
        )
        sound_and_music = sound_and_music.replace(
            '${PERFORMER}', 'The Apollo Symphony Orchestra'
        )
        sound_and_music = sound_and_music.replace(
            '${PERFORMER}', 'The Apollo Symphony Orchestra'
        )
        sound_and_music = sound_and_music.replace(
            '${COMPOSER}', 'Gioacchino Rossini'
        )
        sound_and_music = sound_and_music.replace('${ARRANGER}', 'Chris Worth')
        sound_and_music = sound_and_music.replace('${PUBLISHER}', 'BMI')
        sound_and_music = sound_and_music.replace(
            '${SOURCE}', 'www.AudioSparx.com'
        )
        spc = '     '
        sound_and_music = spc + sound_and_music.replace('\n', '\n' + spc)
        names = [
            'HubOfTheUniverseProd',
            'Jovica',
            'LG',
            'Leady',
            'Percy Duke',
            'PhreaKsAccount',
            'Pogotron',
            'Rock Savage',
            'anamorphosis',
            'benboncan',
            'cdrk',
            'chipfork',
            'guitarguy1985',
            'jascha',
            'joedeshon',
            'loofa',
            'm_O_m',
            'mich3d',
            'sandyrb',
            'shakaharu',
            'sirplus',
            'stickman',
            'thanvannispen',
            'virotic',
            'zimbot',
        ]
        names.sort(key=lambda x: x.lower())
        freesound_names = _format_names(names, 90)

        try:
            with open(
                os.path.join(
                    bui.app.env.data_directory,
                    'ba_data',
                    'data',
                    'langdata.json',
                ),
                encoding='utf-8',
            ) as infile:
                translation_contributors = json.loads(infile.read())[
                    'translation_contributors'
                ]
        except Exception:
            logging.exception('Error reading translation contributors.')
            translation_contributors = []

        translation_names = _format_names(translation_contributors, 60)
        import babase

        # Need to bake this out and chop it up since we're passing our
        # 65535 vertex limit for meshes..
        # We can remove that limit once we drop support for GL ES2.. :-/
        # (or add mesh splitting under the hood)
        credits_text = (
                "    Gummy's Overhaul Credits\n\n" +

                "    Main Producer: GummyBoiYT\n\n" +


                "    HUGE HELP (Memes, Art, Audio, Coding):\n" +

                "    Lucy\n" +
                "    Mell\n" +
                "    Lemon\n" +
                "    nogestk1\n" +
                "    Redicey\n\n"


                "    Music/Sound Effects:\n" +

                "    Daniel Bautista - Recycled Intro 2019\n" +
                "    Mario Kart 8 & 64\n" +
                "    Outcome Memories (Specifically) juno!, \n" +
                "    aerozity, and ThatGuyRamon\n" +
                "    Mario's Maddness\n" +
                "    'Mario Paints you some hoes' by Neutroa\n" +
                "    'Painting Some Hoes' (Lyrics) Ft. Kasane Teto' By Jibber Jabber\n" +
                "    Fall Guys\n" +
                "    someboywhomusics\n" +
                "    Blue Licorice - Paper Kitty Originals\n" +
                "    The Living Tombstone - Join Us for a Bite Remix\n" +
                "    Rivals of Aether\n" +
                "    Super Smash Bros.\n" +
                "    Manabu Namiki - Vertex (Stage 1)\n" +
                "    Ballin' X Die in a Fire\n" +
                "    Team Fortress 2\n" +
                "    3DS Mii Maker\n" +
                "    Dark Souls 3\n" +
                "    Tony Hawks Pro Skater - Stunt Sound Effect\n" +
                "    Deltarune\n" +
                "    Minecraft\n" +
                "    Pizza Tower\n" +
                "    random cat game\n" +
                "    Eek!\n" +
                "    PHIGHTING!\n" +
                "    Just a Burning Memory\n" +
                "    Roblox\n" +
                "    Jetpack Joyride\n" +
                "    Kirby\n" +
                "    Miitopia\n" +
                "    THE 6ORLD IS 9EVOLVING - var (holy shit this is so good)\n\n"


                "    Friends:\n" +

                "    4Broken8\n" +
                "    AchsIdeas\n" +
                "    Lemon\n" +
                "    Gabe\n" +
                "    ggMustaGD1\n" +
                "    Bobra\n" +
                "    Mell\n" +
                "    Lucy\n" +
                "    boomcatto\n" +
                "    buddiew\n\n" +


                "    Special Thanks:\n" +

                "    Rikkolovescats: Zoe and Pixel cat ears\n\n" +
                "    Bombdash: The lightning effect.\n\n" +
                "    TheMikirog: Minexecution. (you can stfu now lemon, i made the code for the function btw)\n" +
                "    Also gave good criticim\n\n" +
                "    MATLEF: fortnite impulse grenade model\n" +
                "    Link: https://www.thingiverse.com/thing:2813732\n\n" +
                "    GatoBugadoBR: Boogie Bomb model\n" +
                "    Link: https://skfb.ly/oRWrH\n\n" +
                "    Leb: Bed Minecraft Model\n" +
                "    Link:(https://sketchfab.com/3d-models/minecraft-inspired-bed-57baa63d8afa40cf93a5c12f693e5784#download)\n\n" +
                "    NFeldman00: Felt Cap\n" +
                "    Link:(https://skfb.ly/VWzT)\n\n" +
                "    Earth Model: https://sketchfab.com/3d-models/earth-41fc80d85dfd480281f21b74b2de2faa\n\n" + 
                "    Era and Vishuuu: helped me when i couldnt figure out simple shit 😭\n\n" +
                "    Boom-Box by Ginsta [CC-BY] (https://creativecommons.org/licenses/by/3.0/)\n" +
                "    via Poly Pizza (https://poly.pizza/m/z7e8fXnuXh)\n\n" +
                "    Bombsquad: Explodinary (yes yes i know its stupid, but i love the punchStrong sounds ok?\n" +
                "    and uhh the snake shadowmdoesl please dont hurt me sok)\n\n" +
                "    VibaPop: Peppino and Noise models, we made em into bobs tho\n" +
                "    https://sketchfab.com/3d-models/pizza-tower-low-poly-366dd3149c3f484bb633a2533c939a48\n\n" +
                "    Rich Presence By: TenType\n" +
                "    https://github.com/TenType/discord-rich-presence\n\n" +
                "    alycia_x21: Sal character, her art is amazing.\n\n" +
                "    discont230: Scoldy character\n\n" +
                "    tu panita el random: Ilyich character (Tophat cosmetic)\n\n" +
                "    Poyo20: Simple Christmas Hat\n" +
                "    Link:(https://sketchfab.com/3d-models/christmas-hat-low-poly-c4064c0b99f748928d06ed319db9982e)\n\n" +
                "    Ducko: Roblox Pumpkin Head\n" +
                "    Link:(https://sketchfab.com/3d-models/roblox-pumpkin-head-61a30e06728944b6bbf2677908059c5f#download)\n\n" +
                f"    {babase.charstr(babase.SpecialChar.V2_LOGO)}SoK: The Betty Character, now in Vanilla!\n\n" +
                "    Plants VS Zombies Models:" +
                "    Plants VS Zombies - Peashooter aidenmirandavfx\n  (http://creativecommons.org/licenses/by-nc/4.0/).\n"+
                "    Plants vs. Zombies 3 (Pre-Alpha) - Sunflower by eduardosouzabarbosadasilva\n   (http://creativecommons.org/licenses/by/4.0/)\n"+
                "    all other models belong to:  Nazar Okruzhko (Назар Окружко) goated bro\n  (https://sketchfab.com/Hot-Dog_1947)\n"+

                "\n\n"+



                "    Bombsquad Credits:\n\n" +
            #Translators:\nMell: Portuguese\n\n\n


            '  '
            + bui.Lstr(resource=f'{self._r}.codingGraphicsAudioText')
            .evaluate()
            .replace('${NAME}', 'Eric Froemling')
            + '\n'
            '\n'
            '  '
            + bui.Lstr(resource=f'{self._r}.additionalAudioArtIdeasText')
            .evaluate()
            .replace('${NAME}', 'Raphael Suter')
            + '\n'
            '\n'
            '  '
            + bui.Lstr(resource=f'{self._r}.soundAndMusicText').evaluate()
            + '\n'
            '\n' + sound_and_music + '\n'
            '\n'
            '     '
            + bui.Lstr(resource=f'{self._r}.publicDomainMusicViaText')
            .evaluate()
            .replace('${NAME}', 'Musopen.com')
            + '\n'
            '        '
            + bui.Lstr(resource=f'{self._r}.thanksEspeciallyToText')
            .evaluate()
            .replace('${NAME}', 'the US Army, Navy, and Marine Bands')
            + '\n'
            '\n'
            '     '
            + bui.Lstr(resource=f'{self._r}.additionalMusicFromText')
            .evaluate()
            .replace('${NAME}', 'The YouTube Audio Library')
            + '\n'
            '\n'
            '     '
            + bui.Lstr(resource=f'{self._r}.soundsText')
            .evaluate()
            .replace('${SOURCE}', 'Freesound.org')
            + '\n'
            '\n' + freesound_names + '\n'
            '\n'
            '  '
            + bui.Lstr(
                resource=f'{self._r}.languageTranslationsText'
            ).evaluate()
            + '\n'
            '\n'
            + '\n'.join(translation_names.splitlines()[:146])
            + '\n'.join(translation_names.splitlines()[146:])
            + '\n'
            '\n'
            '  Shout Out to Awesome Mods / Modders / Contributors:\n\n'
            '     BombDash ModPack\n'
            '     TheMikirog & SoK - BombSquad Joyride Modpack\n'
            '     Mrmaxmeier - BombSquad-Community-Mod-Manager\n'
            '     Ritiek Malhotra \n'
            '     Dliwk\n'
            '     vishal332008\n'
            '     itsre3\n'
            '     Drooopyyy\n'
            '\n'
            '  Holiday theme vector art designed by Freepik\n'
            '\n'
            '  '
            + bui.Lstr(resource=f'{self._r}.specialThanksText').evaluate()
            + '\n'
            '\n'
            '     Todd, Laura, and Robert Froemling\n'
            '     '
            + bui.Lstr(resource=f'{self._r}.allMyFamilyText')
            .evaluate()
            .replace('\n', '\n     ')
            + '\n'
            '     '
            + bui.Lstr(
                resource=f'{self._r}.whoeverInventedCoffeeText'
            ).evaluate()
            + '\n'
            '\n'
            '  ' + bui.Lstr(resource=f'{self._r}.legalText').evaluate() + '\n'
            '\n'
            '     '
            + bui.Lstr(resource=f'{self._r}.softwareBasedOnText')
            .evaluate()
            .replace('${NAME}', 'the Khronos Group')
            + '\n'
            '\n'
            '                                       '
            '                      www.ballistica.net\n'
        )

        txt = credits_text
        lines = txt.splitlines()
        line_height = 20

        scale = 0.55
        self._sub_width = min(700, width - 80)
        self._sub_height = line_height * len(lines) + 40

        container = self._subcontainer = bui.containerwidget(
            parent=scroll,
            size=(self._sub_width, self._sub_height),
            background=False,
            claims_left_right=False,
        )

        voffs = 0
        for line in lines:
            bui.textwidget(
                parent=container,
                padding=4,
                color=(0.7, 0.9, 0.7, 1.0),
                scale=scale,
                flatness=1.0,
                size=(0, 0),
                position=(0, self._sub_height - 20 + voffs),
                h_align='left',
                v_align='top',
                text=bui.Lstr(value=line),
            )
            voffs -= line_height

    @override
    def get_main_window_state(self) -> bui.MainWindowState:
        # Support recreating our window for back/refresh purposes.
        cls = type(self)
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition, origin_widget=origin_widget
            )
        )
