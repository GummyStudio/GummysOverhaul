# Released under the MIT License. See LICENSE for details.
#
"""Appearance functionality for spazzes."""
from __future__ import annotations

import bascenev1 as bs
import babase


def get_appearances(include_locked: bool = False) -> list[str]:
    """Get the list of available spaz appearances."""
    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    plus = bs.app.plus
    assert plus is not None

    assert bs.app.classic is not None
    get_purchased = plus.get_v1_account_product_purchased
    disallowed = []
    if not include_locked:
        # Hmm yeah this'll be tough to hack...
        if not get_purchased('characters.santa'):
            disallowed.append('Santa Claus')
        if not get_purchased('characters.frosty'):
            disallowed.append('Frosty')
        if not get_purchased('characters.bones'):
            disallowed.append('Bones')
        if not get_purchased('characters.bernard'):
            disallowed.append('Bernard')
        if not get_purchased('characters.pixie'):
            disallowed.append('Pixel')
        if not get_purchased('characters.pascal'):
            disallowed.append('Pascal')
        if not get_purchased('characters.actionhero'):
            disallowed.append('Todd McBurton')
        if not get_purchased('characters.taobaomascot'):
            disallowed.append('Taobao Mascot')
        if not get_purchased('characters.agent'):
            disallowed.append('Agent Johnson')
        if not get_purchased('characters.cowboy'):
            disallowed.append('Butch')
        if not get_purchased('characters.jumpsuit'):
            disallowed.append('Lee')
        if not get_purchased('characters.assassin'):
            disallowed.append('Zola')
        if not get_purchased('characters.wizard'):
            disallowed.append('Grumbledorf')
        if not get_purchased('characters.witch'):
            disallowed.append('Witch')
        if not get_purchased('characters.warrior'):
            disallowed.append('Warrior')
        if not get_purchased('characters.superhero'):
            disallowed.append('Middle-Man')
        if not get_purchased('characters.alien'):
            disallowed.append('Alien')
        if not get_purchased('characters.gladiator'):
            disallowed.append('Gladiator')
        if not get_purchased('characters.wrestler'):
            disallowed.append('Wrestler')
        if not get_purchased('characters.operasinger'):
            disallowed.append('Gretel')
        if not get_purchased('characters.robot'):
            disallowed.append('Robot')
        if not get_purchased('characters.cyborg'):
            disallowed.append('B-9000')
        if not get_purchased('characters.bunny'):
            disallowed.append('Easter Bunny')
        if not get_purchased('characters.kronk'):
            disallowed.append('Kronk')
        if not get_purchased('characters.zoe'):
            disallowed.append('Zoe')
        if not get_purchased('characters.jackmorgan'):
            disallowed.append('Jack Morgan')
        if not get_purchased('characters.mel'):
            disallowed.append('Mel')
        if not get_purchased('characters.snakeshadow'):
            disallowed.append('Snake Shadow')
        if not babase.app.config.get('ownedAgentSpaz', 0):
            disallowed.append('Agent Spaz')
        if not babase.app.config.get('ownedAmar', 0):
            disallowed.append('Amar')
        if not babase.app.config.get('ownedBob', 0):
            disallowed.append('Bob')
        if not babase.app.config.get('Local Account Name', 'Account1') == 'Mac289345':
            disallowed.append('Cyber Shadow')
        if not babase.app.config.get('ownedWatory', False):
            disallowed.append('Watory')
        if not babase.app.config.get('ownedSpace', False):
            disallowed.append('Space Guy')
        if not babase.app.config.get('ownedVr', False):
            disallowed.append('VR-Cache')
        if not babase.app.config.get('ownedNoise', False):
            disallowed.append('Theodore Noise')
        if not babase.app.config.get('ownedPizza', False):
            disallowed.append('Peppino Spaghetti')
        if not babase.app.config.get('ownedBunny', False):
            disallowed.append('Penny')
        if not babase.app.config.get('ownedCap', False):
            disallowed.append('Orangecap')
        if not babase.app.config.get('ownedRalsei', False):
            disallowed.append('Ralsei')
        if not babase.app.config.get("ownedOldLady", False):
            disallowed.append('Betty')
        if not babase.app.config.get("ownedIre", False):
            disallowed.append('ire')
        if not babase.app.config.get("ownedRem", False):
            disallowed.append('Rem')
        if not babase.app.config.get("ownedFennekin", False):
            disallowed.append('Fennekin')

        # Only used in the roarying knight fight, except ralsei
        disallowed.append('Kris')
        disallowed.append('Susie')
        disallowed.append('Roaring Knight')

        # Lets not allow these custom bot behaving mfs to be used
        disallowed.append('Land-Mine')
        disallowed.append('Empty')


        # Cosmetic items... being allowed to be used ingame without proper managment will cause errors.
        disallowed.append('Spaz.EXE')
        disallowed.append('Star Hoodie')
        disallowed.append('Full-Insanity')
        disallowed.append('Blue Cap')
        disallowed.append('Spazling')
        disallowed.append('Melling')
        disallowed.append('Ninjaling')
        disallowed.append('Salvatore')
        disallowed.append('Scoldy')
        disallowed.append('Jolly')
        disallowed.append('Horseless Headless Horseman')
        disallowed.append('Gummy Voice Spaz')
        disallowed.append('Gummy Voice Jack')
        disallowed.append('Gummy Voice Agent')
        disallowed.append('YBS16')
        disallowed.append('Tophat')
    return [
        s
        for s in list(bs.app.classic.spaz_appearances.keys())
        if s not in disallowed
    ]


class Appearance:
    """Create and fill out one of these suckers to define a spaz appearance."""

    def __init__(self, name: str):
        assert bs.app.classic is not None
        self.name = name
        if self.name in bs.app.classic.spaz_appearances:
            raise RuntimeError(
                f'spaz appearance name "{self.name}" already exists.'
            )
        bs.app.classic.spaz_appearances[self.name] = self

        # These we're causing 'unable to load x' errors so i gotta put in some default attributes
        self.color_texture = 'null'
        self.color_mask_texture = 'black'
        self.icon_texture = 'null'
        self.icon_mask_texture = 'black'
        self.head_mesh = 'invisible'
        self.torso_mesh = 'invisible'
        self.pelvis_mesh = 'invisible'
        self.upper_arm_mesh = 'invisible'
        self.forearm_mesh = 'invisible'
        self.hand_mesh = 'invisible'
        self.upper_leg_mesh = 'invisible'
        self.lower_leg_mesh = 'invisible'
        self.toes_mesh = 'invisible'
        self.jump_sounds: list[str] = ['nothing']
        self.attack_sounds: list[str] = ['nothing']
        self.impact_sounds: list[str] = ['nothing']
        self.death_sounds: list[str] = ['nothing']
        self.pickup_sounds: list[str] = ['nothing']
        self.fall_sounds: list[str] = ['nothing']
        self.style = 'agent'
        self.default_color: tuple[float, float, float] | None = None
        self.default_highlight: tuple[float, float, float] | None = None

        # The two first custom things
        self.render = 'null'
        self.render_color_mask = 'black'
        self.screen_ko_texture = 'null'
        self.screen_ko_color_mask = 'black'


def register_appearances() -> None:
    """Register our builtin spaz appearances."""

    # This is quite ugly but will be going away so not worth cleaning up.
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    # Spaz #######################################
    t = Appearance('Spaz')
    t.color_texture = 'neoSpazColor'
    t.color_mask_texture = 'neoSpazColorMask'
    t.icon_texture = 'neoSpazIcon'
    t.icon_mask_texture = 'neoSpazIconColorMask'
    t.head_mesh = 'neoSpazHead'
    t.torso_mesh = 'neoSpazTorso'
    t.pelvis_mesh = 'neoSpazPelvis'
    t.upper_arm_mesh = 'neoSpazUpperArm'
    t.forearm_mesh = 'neoSpazForeArm'
    t.hand_mesh = 'neoSpazHand'
    t.upper_leg_mesh = 'neoSpazUpperLeg'
    t.lower_leg_mesh = 'neoSpazLowerLeg'
    t.toes_mesh = 'neoSpazToes'
    t.jump_sounds = ['spazJump01', 'spazJump02', 'spazJump03', 'spazJump04']
    t.attack_sounds = [
        'spazAttack01',
        'spazAttack02',
        'spazAttack03',
        'spazAttack04',
    ]
    t.impact_sounds = [
        'spazImpact01',
        'spazImpact02',
        'spazImpact03',
        'spazImpact04',
    ]
    t.death_sounds = ['spazDeath01']
    t.pickup_sounds = ['spazPickup01']
    t.fall_sounds = ['spazFall01']
    t.style = 'spaz'
    t.render = 'renders/spazlingRender'
    t.render_color_mask = 'renders/spazlingRenderColorMask'
    t.screen_ko_texture = 'renders/spazlingScreenKO'
    t.screen_ko_color_mask = 'renders/spazlingScreenKOColorMask'

    # Zoe #####################################
    t = Appearance('Zoe')
    t.color_texture = 'zoeColor'
    t.color_mask_texture = 'zoeColorMask'
    t.icon_texture = 'zoeIcon'
    t.icon_mask_texture = 'zoeIconColorMask'
    t.head_mesh = 'zoeHead'
    t.torso_mesh = 'zoeTorso'
    t.pelvis_mesh = 'zoePelvis'
    t.upper_arm_mesh = 'zoeUpperArm'
    t.forearm_mesh = 'zoeForeArm'
    t.hand_mesh = 'zoeHand'
    t.upper_leg_mesh = 'zoeUpperLeg'
    t.lower_leg_mesh = 'zoeLowerLeg'
    t.toes_mesh = 'zoeToes'
    t.jump_sounds = ['zoeJump01', 'zoeJump02', 'zoeJump03']
    t.attack_sounds = [
        'zoeAttack01',
        'zoeAttack02',
        'zoeAttack03',
        'zoeAttack04',
    ]
    t.impact_sounds = [
        'zoeImpact01',
        'zoeImpact02',
        'zoeImpact03',
        'zoeImpact04',
    ]
    t.death_sounds = ['zoeDeath01']
    t.pickup_sounds = ['zoePickup01']
    t.fall_sounds = ['zoeFall01']
    t.style = 'female'
    t.default_color = (0.6, 0.6, 0.6)
    t.default_highlight = (0, 1, 0)
    t.render = 'renders/ZoeRender'
    t.render_color_mask = 'renders/ZoeRenderColorMask'
    t.screen_ko_texture = 'renders/ZoeScreenKO'
    t.screen_ko_color_mask = 'renders/ZoeScreenKOColorMask'

    # Ninja ##########################################
    t = Appearance('Snake Shadow')
    t.color_texture = 'ninjaColor'
    t.color_mask_texture = 'ninjaColorMask'
    t.icon_texture = 'ninjaIcon'
    t.icon_mask_texture = 'ninjaIconColorMask'
    t.head_mesh = 'ninjaHead'
    t.torso_mesh = 'ninjaTorso'
    t.pelvis_mesh = 'ninjaPelvis'
    t.upper_arm_mesh = 'ninjaUpperArm'
    t.forearm_mesh = 'ninjaForeArm'
    t.hand_mesh = 'ninjaHand'
    t.upper_leg_mesh = 'ninjaUpperLeg'
    t.lower_leg_mesh = 'ninjaLowerLeg'
    t.toes_mesh = 'ninjaToes'
    ninja_attacks = ['ninjaAttack' + str(i + 1) + '' for i in range(7)]
    ninja_hits = ['ninjaHit' + str(i + 1) + '' for i in range(8)]
    ninja_jumps = ['ninjaAttack' + str(i + 1) + '' for i in range(7)]
    t.jump_sounds = ninja_jumps
    t.attack_sounds = ninja_attacks
    t.impact_sounds = ninja_hits
    t.death_sounds = ['ninjaDeath1']
    t.pickup_sounds = ninja_attacks
    t.fall_sounds = ['ninjaFall1']
    t.style = 'ninja'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0.55, 0.8, 0.55)
    t.render = 'renders/NinjaRender'
    t.render_color_mask = 'renders/NinjaRenderColorMask'
    t.screen_ko_texture = 'renders/NinjaScreenKO'
    t.screen_ko_color_mask = 'renders/NinjaScreenKOColorMask'

    # Barbarian #####################################
    t = Appearance('Kronk')
    t.color_texture = 'kronk'
    t.color_mask_texture = 'kronkColorMask'
    t.icon_texture = 'kronkIcon'
    t.icon_mask_texture = 'kronkIconColorMask'
    t.head_mesh = 'kronkHead'
    t.torso_mesh = 'kronkTorso'
    t.pelvis_mesh = 'kronkPelvis'
    t.upper_arm_mesh = 'kronkUpperArm'
    t.forearm_mesh = 'kronkForeArm'
    t.hand_mesh = 'kronkHand'
    t.upper_leg_mesh = 'kronkUpperLeg'
    t.lower_leg_mesh = 'kronkLowerLeg'
    t.toes_mesh = 'kronkToes'
    kronk_sounds = [
        'kronk1',
        'kronk2',
        'kronk3',
        'kronk4',
        'kronk5',
        'kronk6',
        'kronk7',
        'kronk8',
        'kronk9',
        'kronk10',
    ]
    t.jump_sounds = kronk_sounds
    t.attack_sounds = kronk_sounds
    t.impact_sounds = kronk_sounds
    t.death_sounds = ['kronkDeath']
    t.pickup_sounds = kronk_sounds
    t.fall_sounds = ['kronkFall']
    t.style = 'kronk'
    t.default_color = (0.4, 0.5, 0.4)
    t.default_highlight = (1, 0.5, 0.3)
    t.render = 'renders/KronkRender'
    t.render_color_mask = 'renders/KronkRenderColorMask'
    t.screen_ko_texture = 'renders/KronkScreenKO'
    t.screen_ko_color_mask = 'renders/KronkScreenKOColorMask'

    # Chef ###########################################
    t = Appearance('Mel')
    t.color_texture = 'melColor'
    t.color_mask_texture = 'melColorMask'
    t.icon_texture = 'melIcon'
    t.icon_mask_texture = 'melIconColorMask'
    t.head_mesh = 'melHead'
    t.torso_mesh = 'melTorso'
    t.pelvis_mesh = 'kronkPelvis'
    t.upper_arm_mesh = 'melUpperArm'
    t.forearm_mesh = 'melForeArm'
    t.hand_mesh = 'melHand'
    t.upper_leg_mesh = 'melUpperLeg'
    t.lower_leg_mesh = 'melLowerLeg'
    t.toes_mesh = 'melToes'
    mel_sounds = [
        'mel01',
        'mel02',
        'mel03',
        'mel04',
        'mel05',
        'mel06',
        'mel07',
        'mel08',
        'mel09',
        'mel10',
    ]
    t.jump_sounds = mel_sounds
    t.attack_sounds = mel_sounds
    t.impact_sounds = mel_sounds
    t.death_sounds = ['melDeath01']
    t.pickup_sounds = mel_sounds
    t.fall_sounds = ['melFall01']
    t.style = 'mel'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0.1, 0.6, 0.1)

    # Pirate #######################################
    t = Appearance('Jack Morgan')
    t.color_texture = 'jackColor'
    t.color_mask_texture = 'jackColorMask'
    t.icon_texture = 'jackIcon'
    t.icon_mask_texture = 'jackIconColorMask'
    t.head_mesh = 'jackHead'
    t.torso_mesh = 'jackTorso'
    t.pelvis_mesh = 'kronkPelvis'
    t.upper_arm_mesh = 'jackUpperArm'
    t.forearm_mesh = 'jackForeArm'
    t.hand_mesh = 'jackHand'
    t.upper_leg_mesh = 'jackUpperLeg'
    t.lower_leg_mesh = 'jackLowerLeg'
    t.toes_mesh = 'jackToes'
    hit_sounds = [
        'jackHit01',
        'jackHit02',
        'jackHit03',
        'jackHit04',
        'jackHit05',
        'jackHit06',
        'jackHit07',
    ]
    sounds = ['jack01', 'jack02', 'jack03', 'jack04', 'jack05', 'jack06']
    t.jump_sounds = sounds
    t.attack_sounds = sounds
    t.impact_sounds = hit_sounds
    t.death_sounds = ['jackDeath01']
    t.pickup_sounds = sounds
    t.fall_sounds = ['jackFall01']
    t.style = 'pirate'
    t.default_color = (1, 0.2, 0.1)
    t.default_highlight = (1, 1, 0)
    t.render = 'renders/PirateRender'
    t.render_color_mask = 'renders/PirateRenderColorMask'
    t.screen_ko_texture = 'renders/PirateScreenKO'
    t.screen_ko_color_mask = 'bonesColorMask'

    # Santa ######################################
    t = Appearance('Santa Claus')
    t.color_texture = 'santaColor'
    t.color_mask_texture = 'santaColorMask'
    t.icon_texture = 'santaIcon'
    t.icon_mask_texture = 'santaIconColorMask'
    t.head_mesh = 'santaHead'
    t.torso_mesh = 'santaTorso'
    t.pelvis_mesh = 'kronkPelvis'
    t.upper_arm_mesh = 'santaUpperArm'
    t.forearm_mesh = 'santaForeArm'
    t.hand_mesh = 'santaHand'
    t.upper_leg_mesh = 'santaUpperLeg'
    t.lower_leg_mesh = 'santaLowerLeg'
    t.toes_mesh = 'santaToes'
    hit_sounds = ['santaHit01', 'santaHit02', 'santaHit03', 'santaHit04']
    sounds = ['santa01', 'santa02', 'santa03', 'santa04', 'santa05']
    t.jump_sounds = sounds
    t.attack_sounds = sounds
    t.impact_sounds = hit_sounds
    t.death_sounds = ['santaDeath']
    t.pickup_sounds = sounds
    t.fall_sounds = ['santaFall']
    t.style = 'santa'
    t.default_color = (1, 0, 0)
    t.default_highlight = (1, 1, 1)
    t.render = 'renders/SantaRender'
    t.render_color_mask = 'renders/SantaRenderColorMask'
    t.screen_ko_texture = 'renders/SantaScreenKO'
    t.screen_ko_color_mask = 'renders/SantaScreenKOColorMask'


    # Snowman ###################################
    t = Appearance('Frosty')
    t.color_texture = 'frostyColor'
    t.color_mask_texture = 'frostyColorMask'
    t.icon_texture = 'frostyIcon'
    t.icon_mask_texture = 'frostyIconColorMask'
    t.head_mesh = 'frostyHead'
    t.torso_mesh = 'frostyTorso'
    t.pelvis_mesh = 'frostyPelvis'
    t.upper_arm_mesh = 'frostyUpperArm'
    t.forearm_mesh = 'frostyForeArm'
    t.hand_mesh = 'frostyHand'
    t.upper_leg_mesh = 'frostyUpperLeg'
    t.lower_leg_mesh = 'frostyLowerLeg'
    t.toes_mesh = 'frostyToes'
    frosty_sounds = ['frosty01', 'frosty02', 'frosty03', 'frosty04', 'frosty05']
    frosty_hit_sounds = ['frostyHit01', 'frostyHit02', 'frostyHit03']
    t.jump_sounds = frosty_sounds
    t.attack_sounds = frosty_sounds
    t.impact_sounds = frosty_hit_sounds
    t.death_sounds = ['frostyDeath']
    t.pickup_sounds = frosty_sounds
    t.fall_sounds = ['frostyFall']
    t.style = 'frosty'
    t.default_color = (0.5, 0.5, 1)
    t.default_highlight = (1, 0.5, 0)
    t.render = 'renders/SnowmanRender'
    t.render_color_mask = 'renders/SnowmanRenderColorMask'
    t.screen_ko_texture = 'renders/SnowmanScreenKO'
    t.screen_ko_color_mask = 'renders/SnowmanScreenKOColorMask'

    # Skeleton ################################
    t = Appearance('Bones')
    t.color_texture = 'bonesColor'
    t.color_mask_texture = 'bonesColorMask'
    t.icon_texture = 'bonesIcon'
    t.icon_mask_texture = 'bonesIconColorMask'
    t.head_mesh = 'bonesHead'
    t.torso_mesh = 'bonesTorso'
    t.pelvis_mesh = 'bonesPelvis'
    t.upper_arm_mesh = 'bonesUpperArm'
    t.forearm_mesh = 'bonesForeArm'
    t.hand_mesh = 'bonesHand'
    t.upper_leg_mesh = 'bonesUpperLeg'
    t.lower_leg_mesh = 'bonesLowerLeg'
    t.toes_mesh = 'bonesToes'
    bones_sounds = ['bones1', 'bones2', 'bones3']
    bones_hit_sounds = ['bones1', 'bones2', 'bones3']
    t.jump_sounds = bones_sounds
    t.attack_sounds = bones_sounds
    t.impact_sounds = bones_hit_sounds
    t.death_sounds = ['bonesDeath']
    t.pickup_sounds = bones_sounds
    t.fall_sounds = ['bonesFall']
    t.style = 'bones'
    t.default_color = (0.6, 0.9, 1)
    t.default_highlight = (0.6, 0.9, 1)
    t.render = 'renders/BonesRender'
    t.render_color_mask = 'bonesColorMask'
    t.screen_ko_texture = 'renders/BonesScreenKO'
    t.screen_ko_color_mask = 'bonesColorMask'

    # Bear ###################################
    t = Appearance('Bernard')
    t.color_texture = 'bearColor'
    t.color_mask_texture = 'bearColorMask'
    t.icon_texture = 'bearIcon'
    t.icon_mask_texture = 'bearIconColorMask'
    t.head_mesh = 'bearHead'
    t.torso_mesh = 'bearTorso'
    t.pelvis_mesh = 'bearPelvis'
    t.upper_arm_mesh = 'bearUpperArm'
    t.forearm_mesh = 'bearForeArm'
    t.hand_mesh = 'bearHand'
    t.upper_leg_mesh = 'bearUpperLeg'
    t.lower_leg_mesh = 'bearLowerLeg'
    t.toes_mesh = 'bearToes'
    bear_sounds = ['bear1', 'bear2', 'bear3', 'bear4']
    bear_hit_sounds = ['bearHit1', 'bearHit2']
    t.jump_sounds = bear_sounds
    t.attack_sounds = bear_sounds
    t.impact_sounds = bear_hit_sounds
    t.death_sounds = ['bearDeath']
    t.pickup_sounds = bear_sounds
    t.fall_sounds = ['bearFall']
    t.style = 'bear'
    t.default_color = (0.7, 0.5, 0.0)
    t.render = 'renders/BernardRender'
    t.render_color_mask = 'renders/BernardRenderColorMask'
    t.screen_ko_texture = 'renders/BernardScreenKO'
    t.screen_ko_color_mask = 'renders/BernardScreenKOColorMask'

    # Penguin ###################################
    t = Appearance('Pascal')
    t.color_texture = 'penguinColor'
    t.color_mask_texture = 'penguinColorMask'
    t.icon_texture = 'penguinIcon'
    t.icon_mask_texture = 'penguinIconColorMask'
    t.head_mesh = 'penguinHead'
    t.torso_mesh = 'penguinTorso'
    t.pelvis_mesh = 'penguinPelvis'
    t.upper_arm_mesh = 'penguinUpperArm'
    t.forearm_mesh = 'penguinForeArm'
    t.hand_mesh = 'penguinHand'
    t.upper_leg_mesh = 'penguinUpperLeg'
    t.lower_leg_mesh = 'penguinLowerLeg'
    t.toes_mesh = 'penguinToes'
    penguin_sounds = ['penguin1', 'penguin2', 'penguin3', 'penguin4']
    penguin_hit_sounds = ['penguinHit1', 'penguinHit2']
    t.jump_sounds = penguin_sounds
    t.attack_sounds = penguin_sounds
    t.impact_sounds = penguin_hit_sounds
    t.death_sounds = ['penguinDeath']
    t.pickup_sounds = penguin_sounds
    t.fall_sounds = ['penguinFall']
    t.style = 'penguin'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)
    t.render = 'renders/PascalRender'
    t.render_color_mask = 'renders/PascalRenderColorMask'
    t.screen_ko_texture = 'renders/PascalScreenKO'
    t.screen_ko_color_mask = 'renders/PascalScreenKOColorMask'

    # Ali ###################################
    t = Appearance('Taobao Mascot')
    t.color_texture = 'aliColor'
    t.color_mask_texture = 'aliColorMask'
    t.icon_texture = 'aliIcon'
    t.icon_mask_texture = 'aliIconColorMask'
    t.head_mesh = 'aliHead'
    t.torso_mesh = 'aliTorso'
    t.pelvis_mesh = 'aliPelvis'
    t.upper_arm_mesh = 'aliUpperArm'
    t.forearm_mesh = 'aliForeArm'
    t.hand_mesh = 'aliHand'
    t.upper_leg_mesh = 'aliUpperLeg'
    t.lower_leg_mesh = 'aliLowerLeg'
    t.toes_mesh = 'aliToes'
    ali_sounds = ['ali1', 'ali2', 'ali3', 'ali4']
    ali_hit_sounds = ['aliHit1', 'aliHit2']
    t.jump_sounds = ali_sounds
    t.attack_sounds = ali_sounds
    t.impact_sounds = ali_hit_sounds
    t.death_sounds = ['aliDeath']
    t.pickup_sounds = ali_sounds
    t.fall_sounds = ['aliFall']
    t.style = 'ali'
    t.default_color = (1, 0.5, 0)
    t.default_highlight = (1, 1, 1)
    t.render = 'renders/AliRender'
    t.render_color_mask = 'renders/AliRenderColorMask'
    t.screen_ko_texture = 'renders/AliScreenKO'
    t.screen_ko_color_mask = 'renders/AliScreenKOColorMask'

    # Cyborg ###################################
    t = Appearance('B-9000')
    t.color_texture = 'cyborgColor'
    t.color_mask_texture = 'cyborgColorMask'
    t.icon_texture = 'cyborgIcon'
    t.icon_mask_texture = 'cyborgIconColorMask'
    t.head_mesh = 'cyborgHead'
    t.torso_mesh = 'cyborgTorso'
    t.pelvis_mesh = 'cyborgPelvis'
    t.upper_arm_mesh = 'cyborgUpperArm'
    t.forearm_mesh = 'cyborgForeArm'
    t.hand_mesh = 'cyborgHand'
    t.upper_leg_mesh = 'cyborgUpperLeg'
    t.lower_leg_mesh = 'cyborgLowerLeg'
    t.toes_mesh = 'cyborgToes'
    cyborg_sounds = ['cyborg1', 'cyborg2', 'cyborg3', 'cyborg4']
    cyborg_hit_sounds = ['cyborgHit1', 'cyborgHit2']
    t.jump_sounds = cyborg_sounds
    t.attack_sounds = cyborg_sounds
    t.impact_sounds = cyborg_hit_sounds
    t.death_sounds = ['cyborgDeath']
    t.pickup_sounds = cyborg_sounds
    t.fall_sounds = ['cyborgFall']
    t.style = 'cyborg'
    t.default_color = (0.5, 0.5, 0.5)
    t.default_highlight = (1, 0, 0)
    t.render = 'renders/B9000Render'
    t.render_color_mask = 'renders/B9000RenderColorMask'
    t.screen_ko_texture = 'renders/B9000ScreenKO'
    t.screen_ko_color_mask = 'renders/B9000ScreenKOColorMask'

    # Agent ###################################
    t = Appearance('Agent Johnson')
    t.color_texture = 'agentColor'
    t.color_mask_texture = 'agentColorMask'
    t.icon_texture = 'agentIcon'
    t.icon_mask_texture = 'agentIconColorMask'
    t.head_mesh = 'agentHead'
    t.torso_mesh = 'agentTorso'
    t.pelvis_mesh = 'agentPelvis'
    t.upper_arm_mesh = 'agentUpperArm'
    t.forearm_mesh = 'agentForeArm'
    t.hand_mesh = 'agentHand'
    t.upper_leg_mesh = 'agentUpperLeg'
    t.lower_leg_mesh = 'agentLowerLeg'
    t.toes_mesh = 'agentToes'
    agent_sounds = ['agent1', 'agent2', 'agent3', 'agent4']
    agent_hit_sounds = ['agentHit1', 'agentHit2']
    t.jump_sounds = agent_sounds
    t.attack_sounds = agent_sounds
    t.impact_sounds = agent_hit_sounds
    t.death_sounds = ['agentDeath']
    t.pickup_sounds = agent_sounds
    t.fall_sounds = ['agentFall']
    t.style = 'agent'
    t.default_color = (0.3, 0.3, 0.33)
    t.default_highlight = (1, 0.5, 0.3)
    t.render = 'renders/JohnRender'
    t.render_color_mask = 'renders/JohnRenderColorMask'
    t.screen_ko_texture = 'renders/JohnScreenKO'
    t.screen_ko_color_mask = 'renders/JohnScreenKOColorMask'

    # Jumpsuit ###################################
    t = Appearance('Lee')
    t.color_texture = 'jumpsuitColor'
    t.color_mask_texture = 'jumpsuitColorMask'
    t.icon_texture = 'jumpsuitIcon'
    t.icon_mask_texture = 'jumpsuitIconColorMask'
    t.head_mesh = 'jumpsuitHead'
    t.torso_mesh = 'jumpsuitTorso'
    t.pelvis_mesh = 'jumpsuitPelvis'
    t.upper_arm_mesh = 'jumpsuitUpperArm'
    t.forearm_mesh = 'jumpsuitForeArm'
    t.hand_mesh = 'jumpsuitHand'
    t.upper_leg_mesh = 'jumpsuitUpperLeg'
    t.lower_leg_mesh = 'jumpsuitLowerLeg'
    t.toes_mesh = 'jumpsuitToes'
    jumpsuit_sounds = ['jumpsuit1', 'jumpsuit2', 'jumpsuit3', 'jumpsuit4']
    jumpsuit_hit_sounds = ['jumpsuitHit1', 'jumpsuitHit2']
    t.jump_sounds = jumpsuit_sounds
    t.attack_sounds = jumpsuit_sounds
    t.impact_sounds = jumpsuit_hit_sounds
    t.death_sounds = ['jumpsuitDeath']
    t.pickup_sounds = jumpsuit_sounds
    t.fall_sounds = ['jumpsuitFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # ActionHero ###################################
    t = Appearance('Todd McBurton')
    t.color_texture = 'actionHeroColor'
    t.color_mask_texture = 'actionHeroColorMask'
    t.icon_texture = 'actionHeroIcon'
    t.icon_mask_texture = 'actionHeroIconColorMask'
    t.head_mesh = 'actionHeroHead'
    t.torso_mesh = 'actionHeroTorso'
    t.pelvis_mesh = 'actionHeroPelvis'
    t.upper_arm_mesh = 'actionHeroUpperArm'
    t.forearm_mesh = 'actionHeroForeArm'
    t.hand_mesh = 'actionHeroHand'
    t.upper_leg_mesh = 'actionHeroUpperLeg'
    t.lower_leg_mesh = 'actionHeroLowerLeg'
    t.toes_mesh = 'actionHeroToes'
    action_hero_sounds = [
        'actionHero1',
        'actionHero2',
        'actionHero3',
        'actionHero4',
    ]
    action_hero_hit_sounds = ['actionHeroHit1', 'actionHeroHit2']
    t.jump_sounds = action_hero_sounds
    t.attack_sounds = action_hero_sounds
    t.impact_sounds = action_hero_hit_sounds
    t.death_sounds = ['actionHeroDeath']
    t.pickup_sounds = action_hero_sounds
    t.fall_sounds = ['actionHeroFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Assassin ###################################
    t = Appearance('Zola')
    t.color_texture = 'assassinColor'
    t.color_mask_texture = 'assassinColorMask'
    t.icon_texture = 'assassinIcon'
    t.icon_mask_texture = 'assassinIconColorMask'
    t.head_mesh = 'assassinHead'
    t.torso_mesh = 'assassinTorso'
    t.pelvis_mesh = 'assassinPelvis'
    t.upper_arm_mesh = 'assassinUpperArm'
    t.forearm_mesh = 'assassinForeArm'
    t.hand_mesh = 'assassinHand'
    t.upper_leg_mesh = 'assassinUpperLeg'
    t.lower_leg_mesh = 'assassinLowerLeg'
    t.toes_mesh = 'assassinToes'
    assassin_sounds = ['assassin1', 'assassin2', 'assassin3', 'assassin4']
    assassin_hit_sounds = ['assassinHit1', 'assassinHit2']
    t.jump_sounds = assassin_sounds
    t.attack_sounds = assassin_sounds
    t.impact_sounds = assassin_hit_sounds
    t.death_sounds = ['assassinDeath']
    t.pickup_sounds = assassin_sounds
    t.fall_sounds = ['assassinFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Wizard ###################################
    t = Appearance('Grumbledorf')
    t.color_texture = 'wizardColor'
    t.color_mask_texture = 'wizardColorMask'
    t.icon_texture = 'wizardIcon'
    t.icon_mask_texture = 'wizardIconColorMask'
    t.head_mesh = 'wizardHead'
    t.torso_mesh = 'wizardTorso'
    t.pelvis_mesh = 'wizardPelvis'
    t.upper_arm_mesh = 'wizardUpperArm'
    t.forearm_mesh = 'wizardForeArm'
    t.hand_mesh = 'wizardHand'
    t.upper_leg_mesh = 'wizardUpperLeg'
    t.lower_leg_mesh = 'wizardLowerLeg'
    t.toes_mesh = 'wizardToes'
    wizard_sounds = ['wizard1', 'wizard2', 'wizard3', 'wizard4']
    wizard_hit_sounds = ['wizardHit1', 'wizardHit2']
    t.jump_sounds = wizard_sounds
    t.attack_sounds = wizard_sounds
    t.impact_sounds = wizard_hit_sounds
    t.death_sounds = ['wizardDeath']
    t.pickup_sounds = wizard_sounds
    t.fall_sounds = ['wizardFall']
    t.style = 'spaz'
    t.default_color = (0.2, 0.4, 1.0)
    t.default_highlight = (0.06, 0.15, 0.4)
    t.render = 'renders/WizardRender'
    t.render_color_mask = 'bonesColorMask'
    t.screen_ko_texture = 'renders/WizardScreenKO'
    t.screen_ko_color_mask = 'bonesColorMask'

    # Witch ###################################
    t = Appearance('Witch')
    t.color_texture = 'witchColor'
    t.color_mask_texture = 'witchColorMask'
    t.icon_texture = 'witchIcon'
    t.icon_mask_texture = 'witchIconColorMask'
    t.head_mesh = 'witchHead'
    t.torso_mesh = 'witchTorso'
    t.pelvis_mesh = 'witchPelvis'
    t.upper_arm_mesh = 'witchUpperArm'
    t.forearm_mesh = 'witchForeArm'
    t.hand_mesh = 'witchHand'
    t.upper_leg_mesh = 'witchUpperLeg'
    t.lower_leg_mesh = 'witchLowerLeg'
    t.toes_mesh = 'witchToes'
    witch_sounds = ['witch1', 'witch2', 'witch3', 'witch4']
    witch_hit_sounds = ['witchHit1', 'witchHit2']
    t.jump_sounds = witch_sounds
    t.attack_sounds = witch_sounds
    t.impact_sounds = witch_hit_sounds
    t.death_sounds = ['witchDeath']
    t.pickup_sounds = witch_sounds
    t.fall_sounds = ['witchFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Warrior ###################################
    t = Appearance('Warrior')
    t.color_texture = 'warriorColor'
    t.color_mask_texture = 'warriorColorMask'
    t.icon_texture = 'warriorIcon'
    t.icon_mask_texture = 'warriorIconColorMask'
    t.head_mesh = 'warriorHead'
    t.torso_mesh = 'warriorTorso'
    t.pelvis_mesh = 'warriorPelvis'
    t.upper_arm_mesh = 'warriorUpperArm'
    t.forearm_mesh = 'warriorForeArm'
    t.hand_mesh = 'warriorHand'
    t.upper_leg_mesh = 'warriorUpperLeg'
    t.lower_leg_mesh = 'warriorLowerLeg'
    t.toes_mesh = 'warriorToes'
    warrior_sounds = ['warrior1', 'warrior2', 'warrior3', 'warrior4']
    warrior_hit_sounds = ['warriorHit1', 'warriorHit2']
    t.jump_sounds = warrior_sounds
    t.attack_sounds = warrior_sounds
    t.impact_sounds = warrior_hit_sounds
    t.death_sounds = ['warriorDeath']
    t.pickup_sounds = warrior_sounds
    t.fall_sounds = ['warriorFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Superhero ###################################
    t = Appearance('Middle-Man')
    t.color_texture = 'superheroColor'
    t.color_mask_texture = 'superheroColorMask'
    t.icon_texture = 'superheroIcon'
    t.icon_mask_texture = 'superheroIconColorMask'
    t.head_mesh = 'superheroHead'
    t.torso_mesh = 'superheroTorso'
    t.pelvis_mesh = 'superheroPelvis'
    t.upper_arm_mesh = 'superheroUpperArm'
    t.forearm_mesh = 'superheroForeArm'
    t.hand_mesh = 'superheroHand'
    t.upper_leg_mesh = 'superheroUpperLeg'
    t.lower_leg_mesh = 'superheroLowerLeg'
    t.toes_mesh = 'superheroToes'
    superhero_sounds = ['superhero1', 'superhero2', 'superhero3', 'superhero4']
    superhero_hit_sounds = ['superheroHit1', 'superheroHit2']
    t.jump_sounds = superhero_sounds
    t.attack_sounds = superhero_sounds
    t.impact_sounds = superhero_hit_sounds
    t.death_sounds = ['superheroDeath']
    t.pickup_sounds = superhero_sounds
    t.fall_sounds = ['superheroFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Alien ###################################
    t = Appearance('Alien')
    t.color_texture = 'alienColor'
    t.color_mask_texture = 'alienColorMask'
    t.icon_texture = 'alienIcon'
    t.icon_mask_texture = 'alienIconColorMask'
    t.head_mesh = 'alienHead'
    t.torso_mesh = 'alienTorso'
    t.pelvis_mesh = 'alienPelvis'
    t.upper_arm_mesh = 'alienUpperArm'
    t.forearm_mesh = 'alienForeArm'
    t.hand_mesh = 'alienHand'
    t.upper_leg_mesh = 'alienUpperLeg'
    t.lower_leg_mesh = 'alienLowerLeg'
    t.toes_mesh = 'alienToes'
    alien_sounds = ['alien1', 'alien2', 'alien3', 'alien4']
    alien_hit_sounds = ['alienHit1', 'alienHit2']
    t.jump_sounds = alien_sounds
    t.attack_sounds = alien_sounds
    t.impact_sounds = alien_hit_sounds
    t.death_sounds = ['alienDeath']
    t.pickup_sounds = alien_sounds
    t.fall_sounds = ['alienFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # OldLady ###################################
    t = Appearance('Betty')
    t.color_texture = 'oldLadyColor'
    t.color_mask_texture = 'oldLadyColorMask'
    t.icon_texture = 'oldLadyIcon'
    t.icon_mask_texture = 'oldLadyIconColorMask'
    t.head_mesh = 'oldLadyHead'
    t.torso_mesh = 'oldLadyTorso'
    t.pelvis_mesh = 'oldLadyPelvis'
    t.upper_arm_mesh = 'oldLadyUpperArm'
    t.forearm_mesh = 'oldLadyForeArm'
    t.hand_mesh = 'oldLadyHand'
    t.upper_leg_mesh = 'oldLadyUpperLeg'
    t.lower_leg_mesh = 'oldLadyLowerLeg'
    t.toes_mesh = 'oldLadyToes'
    old_lady_sounds = ['oldLady1', 'oldLady2', 'oldLady3', 'oldLady4']
    old_lady_hit_sounds = ['oldLadyHit1', 'oldLadyHit2']
    t.jump_sounds = old_lady_sounds
    t.attack_sounds = old_lady_sounds
    t.impact_sounds = old_lady_hit_sounds
    t.death_sounds = ['oldLadyDeath']
    t.pickup_sounds = old_lady_sounds
    t.fall_sounds = ['oldLadyFall']
    t.style = 'bones'
    t.default_color = (0.2, 1.0, 1.0)
    t.default_highlight = (0.5, 0.25, 1.0)
    t.render = 'renders/BettyRender'
    t.render_color_mask = 'renders/BettyRenderColorMask'
    t.screen_ko_texture = 'renders/BettyScreenKO'
    t.screen_ko_color_mask = 'renders/BettyScreenKOColorMask'
    

    # Gladiator ###################################
    t = Appearance('Gladiator')
    t.color_texture = 'gladiatorColor'
    t.color_mask_texture = 'gladiatorColorMask'
    t.icon_texture = 'gladiatorIcon'
    t.icon_mask_texture = 'gladiatorIconColorMask'
    t.head_mesh = 'gladiatorHead'
    t.torso_mesh = 'gladiatorTorso'
    t.pelvis_mesh = 'gladiatorPelvis'
    t.upper_arm_mesh = 'gladiatorUpperArm'
    t.forearm_mesh = 'gladiatorForeArm'
    t.hand_mesh = 'gladiatorHand'
    t.upper_leg_mesh = 'gladiatorUpperLeg'
    t.lower_leg_mesh = 'gladiatorLowerLeg'
    t.toes_mesh = 'gladiatorToes'
    gladiator_sounds = ['gladiator1', 'gladiator2', 'gladiator3', 'gladiator4']
    gladiator_hit_sounds = ['gladiatorHit1', 'gladiatorHit2']
    t.jump_sounds = gladiator_sounds
    t.attack_sounds = gladiator_sounds
    t.impact_sounds = gladiator_hit_sounds
    t.death_sounds = ['gladiatorDeath']
    t.pickup_sounds = gladiator_sounds
    t.fall_sounds = ['gladiatorFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Wrestler ###################################
    t = Appearance('Wrestler')
    t.color_texture = 'wrestlerColor'
    t.color_mask_texture = 'wrestlerColorMask'
    t.icon_texture = 'wrestlerIcon'
    t.icon_mask_texture = 'wrestlerIconColorMask'
    t.head_mesh = 'wrestlerHead'
    t.torso_mesh = 'wrestlerTorso'
    t.pelvis_mesh = 'wrestlerPelvis'
    t.upper_arm_mesh = 'wrestlerUpperArm'
    t.forearm_mesh = 'wrestlerForeArm'
    t.hand_mesh = 'wrestlerHand'
    t.upper_leg_mesh = 'wrestlerUpperLeg'
    t.lower_leg_mesh = 'wrestlerLowerLeg'
    t.toes_mesh = 'wrestlerToes'
    wrestler_sounds = ['wrestler1', 'wrestler2', 'wrestler3', 'wrestler4']
    wrestler_hit_sounds = ['wrestlerHit1', 'wrestlerHit2']
    t.jump_sounds = wrestler_sounds
    t.attack_sounds = wrestler_sounds
    t.impact_sounds = wrestler_hit_sounds
    t.death_sounds = ['wrestlerDeath']
    t.pickup_sounds = wrestler_sounds
    t.fall_sounds = ['wrestlerFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # OperaSinger ###################################
    t = Appearance('Gretel')
    t.color_texture = 'operaSingerColor'
    t.color_mask_texture = 'operaSingerColorMask'
    t.icon_texture = 'operaSingerIcon'
    t.icon_mask_texture = 'operaSingerIconColorMask'
    t.head_mesh = 'operaSingerHead'
    t.torso_mesh = 'operaSingerTorso'
    t.pelvis_mesh = 'operaSingerPelvis'
    t.upper_arm_mesh = 'operaSingerUpperArm'
    t.forearm_mesh = 'operaSingerForeArm'
    t.hand_mesh = 'operaSingerHand'
    t.upper_leg_mesh = 'operaSingerUpperLeg'
    t.lower_leg_mesh = 'operaSingerLowerLeg'
    t.toes_mesh = 'operaSingerToes'
    opera_singer_sounds = [
        'operaSinger1',
        'operaSinger2',
        'operaSinger3',
        'operaSinger4',
    ]
    opera_singer_hit_sounds = ['operaSingerHit1', 'operaSingerHit2']
    t.jump_sounds = opera_singer_sounds
    t.attack_sounds = opera_singer_sounds
    t.impact_sounds = opera_singer_hit_sounds
    t.death_sounds = ['operaSingerDeath']
    t.pickup_sounds = opera_singer_sounds
    t.fall_sounds = ['operaSingerFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Pixie ###################################
    t = Appearance('Pixel')
    t.color_texture = 'pixieColor'
    t.color_mask_texture = 'pixieColorMask'
    t.icon_texture = 'pixieIcon'
    t.icon_mask_texture = 'pixieIconColorMask'
    t.head_mesh = 'pixieHead'
    t.torso_mesh = 'pixieTorso'
    t.pelvis_mesh = 'pixiePelvis'
    t.upper_arm_mesh = 'pixieUpperArm'
    t.forearm_mesh = 'pixieForeArm'
    t.hand_mesh = 'pixieHand'
    t.upper_leg_mesh = 'pixieUpperLeg'
    t.lower_leg_mesh = 'pixieLowerLeg'
    t.toes_mesh = 'pixieToes'
    pixie_sounds = ['pixie1', 'pixie2', 'pixie3', 'pixie4']
    pixie_hit_sounds = ['pixieHit1', 'pixieHit2']
    t.jump_sounds = pixie_sounds
    t.attack_sounds = pixie_sounds
    t.impact_sounds = pixie_hit_sounds
    t.death_sounds = ['pixieDeath']
    t.pickup_sounds = pixie_sounds
    t.fall_sounds = ['pixieFall']
    t.style = 'pixie'
    t.default_color = (0, 1, 0.7)
    t.default_highlight = (0.65, 0.35, 0.75)

    # Robot ###################################
    t = Appearance('Robot')
    t.color_texture = 'robotColor'
    t.color_mask_texture = 'robotColorMask'
    t.icon_texture = 'robotIcon'
    t.icon_mask_texture = 'robotIconColorMask'
    t.head_mesh = 'robotHead'
    t.torso_mesh = 'robotTorso'
    t.pelvis_mesh = 'robotPelvis'
    t.upper_arm_mesh = 'robotUpperArm'
    t.forearm_mesh = 'robotForeArm'
    t.hand_mesh = 'robotHand'
    t.upper_leg_mesh = 'robotUpperLeg'
    t.lower_leg_mesh = 'robotLowerLeg'
    t.toes_mesh = 'robotToes'
    robot_sounds = ['robot1', 'robot2', 'robot3', 'robot4']
    robot_hit_sounds = ['robotHit1', 'robotHit2']
    t.jump_sounds = robot_sounds
    t.attack_sounds = robot_sounds
    t.impact_sounds = robot_hit_sounds
    t.death_sounds = ['robotDeath']
    t.pickup_sounds = robot_sounds
    t.fall_sounds = ['robotFall']
    t.style = 'spaz'
    t.default_color = (0.3, 0.5, 0.8)
    t.default_highlight = (1, 0, 0)

    # Bunny ###################################
    t = Appearance('Easter Bunny')
    t.color_texture = 'bunnyColor'
    t.color_mask_texture = 'bunnyColorMask'
    t.icon_texture = 'bunnyIcon'
    t.icon_mask_texture = 'bunnyIconColorMask'
    t.head_mesh = 'bunnyHead'
    t.torso_mesh = 'bunnyTorso'
    t.pelvis_mesh = 'bunnyPelvis'
    t.upper_arm_mesh = 'bunnyUpperArm'
    t.forearm_mesh = 'bunnyForeArm'
    t.hand_mesh = 'bunnyHand'
    t.upper_leg_mesh = 'bunnyUpperLeg'
    t.lower_leg_mesh = 'bunnyLowerLeg'
    t.toes_mesh = 'bunnyToes'
    bunny_sounds = ['bunny1', 'bunny2', 'bunny3', 'bunny4']
    bunny_hit_sounds = ['bunnyHit1', 'bunnyHit2']
    t.jump_sounds = ['bunnyJump']
    t.attack_sounds = bunny_sounds
    t.impact_sounds = bunny_hit_sounds
    t.death_sounds = ['bunnyDeath']
    t.pickup_sounds = bunny_sounds
    t.fall_sounds = ['bunnyFall']
    t.style = 'bunny'
    t.default_color = (1, 1, 1)
    t.default_highlight = (1, 0.5, 0.5)
    t.render = 'renders/BunnyRender'
    t.render_color_mask = 'renders/BunnyRenderColorMask'
    t.screen_ko_texture = 'renders/BunnyScreenKO'
    t.screen_ko_color_mask = 'renders/BunnyScreenKOColorMask'

    # Agent Spaz ###################################
    t = Appearance('Agent Spaz')
    t.color_texture = 'agentSpazColor'
    t.color_mask_texture = 'agentSpazColorMask'
    t.icon_texture = 'agentSpazIconColor'
    t.icon_mask_texture = 'agentSpazIconColorMask'
    t.head_mesh = 'AgentSpazHead'
    t.torso_mesh = 'agentTorso'
    t.pelvis_mesh = 'agentPelvis'
    t.upper_arm_mesh = 'agentUpperArm'
    t.forearm_mesh = 'agentForeArm'
    t.hand_mesh = 'AgentSpazHand'
    t.upper_leg_mesh = 'agentUpperLeg'
    t.lower_leg_mesh = 'AgentSpazLowerLeg'
    t.toes_mesh = 'AgentSpazToes'
    t.jump_sounds = ['spazJump01', 'spazJump02', 'spazJump03', 'spazJump04']
    t.attack_sounds = [
        'spazAttack01',
        'spazAttack02',
        'spazAttack03',
        'spazAttack04',
    ]
    t.impact_sounds = [
        'spazImpact01',
        'spazImpact02',
        'spazImpact03',
        'spazImpact04',
    ]
    t.death_sounds = ['spazDeath01']
    t.pickup_sounds = ['spazPickup01']
    t.fall_sounds = ['spazFall01']
    t.style = 'spaz'
    t.default_color = (0.3, 0.3, 0.33)
    t.default_highlight = (1, 0.5, 0.3)


    # Amar ###################################
    t = Appearance('Amar')
    t.color_texture = 'AmarColor'
    t.color_mask_texture = 'AmarColorMask'
    t.icon_texture = 'AmarIcon'
    t.icon_mask_texture = 'AmarIconColor'
    t.head_mesh = 'AmarHead'
    t.torso_mesh = 'AmarBody'
    t.pelvis_mesh = 'invisible'
    t.upper_arm_mesh = 'invisible'
    t.forearm_mesh = 'invisible'
    t.hand_mesh = 'AmarHand'
    t.upper_leg_mesh = 'invisible'
    t.lower_leg_mesh = 'AmarFoot'
    t.toes_mesh = 'invisible'
    amar_sounds = ['amar1', 'amar2', 'amar3']
    amar_hurt_sounds = ['amarHurt', 'amarHurt2']
    t.jump_sounds = amar_sounds
    t.attack_sounds = amar_sounds
    t.impact_sounds = amar_hurt_sounds
    t.death_sounds = ['amarDeath']
    t.pickup_sounds = ['amarPickup']
    t.fall_sounds = ['amarFall']
    t.style = 'bones'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0.6, 0.6, 0.6)
    t.render = 'renders/AmarRender'
    t.render_color_mask = 'renders/AmarRenderColorMask'
    t.screen_ko_texture = 'renders/AmarScreenKO'
    t.screen_ko_color_mask = 'renders/AmarScreenKOColorMask'

    # Bob ###################################
    t = Appearance('Bob')
    t.color_texture = 'byteColor'
    t.color_mask_texture = 'byteColorMask'
    t.icon_texture = 'byteIcon'
    t.icon_mask_texture = 'byteIconColor'
    t.head_mesh = 'undertakerHead'
    t.torso_mesh = 'undertakerTorso'
    t.pelvis_mesh = 'undertakerPelvis'
    t.upper_arm_mesh = 'undertakerUpperArm'
    t.forearm_mesh = 'undertakerForearm'
    t.hand_mesh = 'undertakerHand'
    t.upper_leg_mesh = 'undertakerUpperLeg'
    t.lower_leg_mesh = 'undertakerLowerLeg'
    t.toes_mesh = 'undertakerToes'
    byte_sounds = ['byte1', 'byte2', 'byte3', 'byte4', 'byte5', 'byte6']
    byte_hit_sounds = ['byteHurt1', 'byteHurt2']
    t.jump_sounds = byte_sounds
    t.attack_sounds = byte_sounds
    t.impact_sounds = byte_hit_sounds
    t.death_sounds = ['byteDeath']
    t.pickup_sounds = byte_sounds
    t.fall_sounds = ['byteFall']
    t.style = 'bones'
    t.default_color = (0.2, 0.4, 0.2)
    t.default_highlight = (0.06, 0.15, 0.4)
    t.render = 'renders/BobRender'
    t.render_color_mask = 'renders/BobRenderColorMask'
    t.screen_ko_texture = 'renders/BobScreenKO'
    t.screen_ko_color_mask = 'renders/BobScreenKOColorMask'

# Cyber Ninja ###################################
    t = Appearance('Cyber Shadow')
    t.color_texture = 'cyborgColor'
    t.color_mask_texture = 'cyborgColorMask'
    t.icon_texture = 'cyborgIcon'
    t.icon_mask_texture = 'cyborgIconColorMask'
    t.head_mesh = 'cyborgHead'
    t.torso_mesh = 'ninjaTorso'
    t.pelvis_mesh = 'cyborgPelvis'
    t.upper_arm_mesh = 'cyborgUpperArm'
    t.forearm_mesh = 'ninjaForeArm'
    t.hand_mesh = 'ninjaHand'
    t.upper_leg_mesh = 'cyborgUpperLeg'
    t.lower_leg_mesh = 'ninjaLowerLeg'
    t.toes_mesh = 'ninjaToes'
    cyborg_sounds = ['cyborg1', 'cyborg2', 'cyborg3', 'cyborg4']
    cyborg_hit_sounds = ['cyborgHit1', 'cyborgHit2']
    t.jump_sounds = cyborg_sounds
    t.attack_sounds = cyborg_sounds
    t.impact_sounds = cyborg_hit_sounds
    t.death_sounds = ['cyborgDeath']
    t.pickup_sounds = cyborg_sounds
    t.fall_sounds = ['cyborgFall']
    t.style = 'cyborg'
    t.default_color = (0.5, 0.5, 0.5)
    t.default_highlight = (1, 0, 0)

    # spirit ###################################
    t = Appearance('Watory')
    t.color_texture = 'spiritColor'
    t.color_mask_texture = 'spiritColorMask'
    t.icon_texture = 'spiritIcon'
    t.icon_mask_texture = 'spiritIconColor'
    t.head_mesh = 'spiritHead'
    t.torso_mesh = 'spiritTorso'
    t.pelvis_mesh = 'invisible'
    t.upper_arm_mesh = 'invisible'
    t.forearm_mesh = 'invisible'
    t.hand_mesh = 'spiritHand'
    t.upper_leg_mesh = 'invisible'
    t.lower_leg_mesh = 'spiritFoot'
    t.toes_mesh = 'invisible'
    watory_sounds = ['watory1', 'watory2', 'watory3', 'watory4']
    watory_hit_sounds = ['watoryHurt1', 'watoryHurt2']
    t.jump_sounds = watory_sounds
    t.attack_sounds = watory_sounds
    t.impact_sounds = watory_hit_sounds
    t.death_sounds = ['watoryDeath']
    t.pickup_sounds = watory_sounds
    t.fall_sounds = ['watoryFall']
    t.style = 'cyborg'
    t.default_color = (0, 0.5, 1)
    t.default_highlight = (1, 1, 1)
    t.render = 'renders/WatoryRender'
    t.render_color_mask = 'renders/WatoryRenderColorMask'
    t.screen_ko_texture = 'renders/WatoryScreenKO'
    t.screen_ko_color_mask = 'renders/WatoryScreenKOColorMask'
    


    # Space Guy #####################################
    t = Appearance('Space Guy')
    t.color_texture = 'spaceguyColor'
    t.color_mask_texture = 'spaceguyColorMask'
    t.icon_texture = 'spaceguyIcon'
    t.icon_mask_texture = 'spaceguyIconColor'
    t.head_mesh = 'spaceguyHead'
    t.torso_mesh = 'spaceguyTorso'
    t.pelvis_mesh = 'spaceguyPelvis'
    t.upper_arm_mesh = 'spaceguyLimb'
    t.forearm_mesh = 'spaceguyLimb'
    t.hand_mesh = 'spaceguyHand'
    t.upper_leg_mesh = 'spaceguyLimb'
    t.lower_leg_mesh = 'spaceguyLimb'
    t.toes_mesh = 'spaceguyToes'
    cat_sounds = ['SPACEpunch1', 'SPACEpunch2', 'SPACEpunch3']
    t.jump_sounds = cat_sounds
    t.attack_sounds = cat_sounds
    t.impact_sounds = ['SPACEhurt1', 'SPACEhurt2', 'SPACEhurt3', 'SPACEhurt4']
    t.death_sounds = ['SPACEdeath1', 'SPACEdeath2', 'SPACEdeath3']
    t.pickup_sounds = ['SPACEpickup1', 'SPACEpickup2', 'SPACEpickup3', 'SPACEpickup4', 'SPACEpickup5']
    t.fall_sounds = ['SPACEfall1', 'SPACEfall2']
    t.style = 'agent'
    t.default_color = (1, 1, 0)
    t.default_highlight = (0, 0, 1)

    # vr guy ###################################
    t = Appearance('VR-Cache')
    t.color_texture = 'vrColor'
    t.color_mask_texture = 'vrColorMask'
    t.icon_texture = 'vrIcon'
    t.icon_mask_texture = 'vrIconColor'
    t.head_mesh = 'vrHead'
    t.torso_mesh = 'vrTorso'
    t.pelvis_mesh = 'invisible'
    t.upper_arm_mesh = 'invisible'
    t.forearm_mesh = 'invisible'
    t.hand_mesh = 'vrHand'
    t.upper_leg_mesh = 'invisible'
    t.lower_leg_mesh = 'invisible'
    t.toes_mesh = 'invisible'
    cyborg_sounds = ['cyborg1', 'cyborg2', 'cyborg3', 'cyborg4']
    cyborg_hit_sounds = ['cyborgHit1', 'cyborgHit2']
    t.jump_sounds = cyborg_sounds
    t.attack_sounds = cyborg_sounds
    t.impact_sounds = cyborg_hit_sounds
    t.death_sounds = ['cyborgDeath']
    t.pickup_sounds = cyborg_sounds
    t.fall_sounds = ['cyborgFall']
    t.style = 'cyborg'
    t.default_color = (0.5, 0.5, 0.5)
    t.default_highlight = (0, 1, 1)
    t.render = 'renders/VrCacheRender'
    t.render_color_mask = 'renders/VrCacheRenderColorMask'
    t.screen_ko_texture = 'renders/VrCacheScreenKO'
    t.screen_ko_color_mask = 'renders/VrCacheScreenKOColorMask'

    #custom land mine bot ###################################
    t = Appearance('Land-Mine')
    t.head_mesh = 'invisible'
    t.torso_mesh = 'landMine'
    t.upper_arm_mesh = 'frostyUpperArm'
    t.forearm_mesh = 'frostyForeArm'
    t.hand_mesh = 'frostyHand'
    t.upper_leg_mesh = 'frostyUpperLeg'
    t.lower_leg_mesh = 'frostyLowerLeg'
    t.toes_mesh = 'frostyToes'
    t.pelvis_mesh = 'invisible'
    t.forearm_mesh = 'invisible'
    t.color_texture = 'landMine'
    t.jump_sounds = ['nothing']
    t.attack_sounds = ['nothing']
    t.impact_sounds = ['nothing']
    t.death_sounds = ['nothing']
    t.pickup_sounds = ['nothing']
    t.fall_sounds = ['nothing']
    t.style = 'bones'

    # Cooler Chef ###########################################
    t = Appearance('Peppino Spaghetti')
    t.color_texture = 'pepColor'
    t.color_mask_texture = 'pepColorMask'
    t.icon_texture = 'pepIcon'
    t.icon_mask_texture = 'pepIconColorMask'
    t.head_mesh = 'pepHead'
    t.torso_mesh = 'pepTorso'
    t.pelvis_mesh = 'invisible'
    t.upper_arm_mesh = 'pepUpperArm'
    t.forearm_mesh = 'pepForeArm'
    t.hand_mesh = 'pepHand'
    t.upper_leg_mesh = 'pepUpperLeg'
    t.lower_leg_mesh = 'pepLowerLeg'
    t.toes_mesh = 'pepToes'
    pep_sounds = [
        'peppino01',
        'peppino02',
        'peppino03',
        'peppino04',
        'peppino05',
        'peppino06',
        'peppino07',
    ]
    t.jump_sounds = pep_sounds
    t.attack_sounds = pep_sounds
    t.impact_sounds = ['peppinoHit01', 'peppinoHit02']
    t.death_sounds = ['peppinoDeath01']
    t.pickup_sounds = ['peppinoPickup01']
    t.fall_sounds = ['peppinoFall01']
    t.style = 'agent'
    t.default_color = (1, 1, 1)

    # Cooler Ninja ##########################################
    t = Appearance('Theodore Noise')
    t.color_texture = 'noiseColor'
    t.color_mask_texture = 'noiseColorMask'
    t.icon_texture = 'noiseIcon'
    t.icon_mask_texture = 'noiseIconColorMask'
    t.head_mesh = 'noiseHead'
    t.torso_mesh = 'noiseTorso'
    t.pelvis_mesh = 'noisePelvis'
    t.upper_arm_mesh = 'noiseUpperArm'
    t.forearm_mesh = 'noiseLowerArm'
    t.hand_mesh = 'noiseHand'
    t.upper_leg_mesh = 'noiseUpperLeg'
    t.lower_leg_mesh = 'noiseLowerLeg'
    t.toes_mesh = 'noiseToes'
    noise_sounds = ['noise01', 'noise02', 'noise03', 'noise04', 'noise05', 'noise06']
    t.jump_sounds = noise_sounds
    t.attack_sounds = noise_sounds
    t.impact_sounds = noise_sounds
    t.death_sounds = ['noiseDeath01']
    t.pickup_sounds = ['noisePickup01']
    t.fall_sounds = ['noiseFall01']
    t.style = 'agent'
    t.default_color = (1, 1, 0)
    t.default_highlight = (1, 0.8, 0)

    # Female Bunny ###################################
    t = Appearance('Penny')
    t.color_texture = 'hoppiColor'
    t.color_mask_texture = 'hoppiColorMask'
    t.icon_texture = 'hoppiIcon'
    t.icon_mask_texture = 'hoppiIconColor'
    t.head_mesh = 'hoppiHead'
    t.torso_mesh = 'hoppiTorso'
    t.pelvis_mesh = 'bunnyPelvis'
    t.upper_arm_mesh = 'bunnyUpperArm'
    t.forearm_mesh = 'bunnyForeArm'
    t.hand_mesh = 'bunnyHand'
    t.upper_leg_mesh = 'bunnyUpperLeg'
    t.lower_leg_mesh = 'bunnyLowerLeg'
    t.toes_mesh = 'bunnyToes'
    bunny_sounds = ['penny1', 'penny2', 'penny3', 'penny4']
    bunny_hit_sounds = ['pennyHurt01', 'pennyHurt02', 'pennyHurt03']
    t.jump_sounds = bunny_sounds
    t.attack_sounds = bunny_sounds
    t.impact_sounds = bunny_hit_sounds
    t.death_sounds = ['pennyDeath']
    t.pickup_sounds = bunny_sounds
    t.fall_sounds = ['pennyFall']
    t.style = 'ali'
    t.default_color = (1, 0.3, 0.5)
    t.default_highlight = (1, 0.5, 0.5)
    t.render = 'renders/PennyRender'
    t.render_color_mask = 'renders/PennyRenderColorMask'
    t.screen_ko_texture = 'renders/PennyScreenKO'
    t.screen_ko_color_mask = 'renders/PennyScreenKOColorMask'

    # orange dude ###################################
    t = Appearance('Orangecap')
    t.color_texture = 'oCapNewColor'
    t.color_mask_texture = 'oCapNewColorMask'
    t.icon_texture = 'orangeCapIcon'
    t.icon_mask_texture = 'orangeCapIconColorMask'
    t.head_mesh = 'oCapNewHead'
    t.torso_mesh = 'oCapNewTorso'
    t.pelvis_mesh = 'oCapNewPelvis'
    t.upper_arm_mesh = 'oCapNewUpperArm'
    t.forearm_mesh = 'oCapNewForeArm'
    t.hand_mesh = 'oCapNewHand'
    t.upper_leg_mesh = 'oCapNewUpperLeg'
    t.lower_leg_mesh = 'oCapNewLowerLeg'
    t.toes_mesh = 'oCapNewToes'

    t.jump_sounds = ['capjump', 'capjump1', 'capjump2', 'capjump3']
    t.attack_sounds = ['cappunch1', 'cappunch2', 'cappunch3', 'cappunch4']
    t.impact_sounds = ['caphurt1']
    t.death_sounds = ['capdeath1', 'capdeath2']
    t.pickup_sounds = ['cappickup1', 'cappickup2', 'cappickup3', 'cappickup4']
    t.fall_sounds = ['capfall1', 'capfall2', 'capfall3']
    t.style = 'agent'
    t.default_color = (1, 0.4, 0.0)
    t.default_highlight = (0.415, 0.1666, 0.549)

    # FEMBOY FROM DELATRUNE !~??! ###################################
    t = Appearance('Ralsei')
    t.color_texture = 'ralseiColor'
    t.color_mask_texture = 'ralseiColorMask'
    t.icon_texture = 'ralseiIcon'
    t.icon_mask_texture = 'ralseiIconColorMask'
    t.head_mesh = 'ralseiHead'
    t.torso_mesh = 'ralseiTorso'
    t.pelvis_mesh = 'ralseiPelvis'
    t.upper_arm_mesh = 'ralseiUpperArm'
    t.forearm_mesh = 'ralseiForeArm'
    t.hand_mesh = 'ralseiHand'
    t.upper_leg_mesh = 'ralseiUpperLeg'
    t.lower_leg_mesh = 'ralseiLowerLeg'
    t.toes_mesh = 'ralseiToes'
    femboy_sounds = ['ralsei1', 'ralsei2', 'ralsei3', 'ralsei4']
    femboy_hit_sounds = ['ralseiHit1', 'ralseiHit2']
    t.jump_sounds = femboy_sounds
    t.attack_sounds = femboy_sounds
    t.impact_sounds = femboy_hit_sounds
    t.death_sounds = ['ralseiDeath']
    t.pickup_sounds = femboy_sounds
    t.fall_sounds = ['ralseiFall']
    t.style = 'agent'
    t.default_color = (106/255,255/255,17/255)#i got lazy
    t.default_highlight = (252 /255,68/255,156/255) 

    # ire2
    t = Appearance('ire')
    t.color_texture = 'ireColor'
    t.color_mask_texture = 'ireColorMask'
    t.icon_texture = 'ireIcon'
    t.icon_mask_texture = 'ireIconCM'
    t.head_mesh = 'ireHead'
    t.torso_mesh = 'ireTorso'
    t.pelvis_mesh = 'irePelvis'
    t.upper_arm_mesh = 'ireUpperArm'
    t.forearm_mesh = 'ireForeArm'
    t.hand_mesh = 'ireHand'
    t.upper_leg_mesh = 'ireUpperLeg'
    t.lower_leg_mesh = 'ireLowerLeg'
    t.toes_mesh = 'invisible'
    t.jump_sounds = ['ireJump' + str(i + 1) + '' for i in range(4)]
    t.attack_sounds = ['ireAttack' + str(i + 1) + '' for i in range(6)]
    t.impact_sounds = ['ireImpact' + str(i + 1) + '' for i in range(5)]
    t.death_sounds = ['ireDeath']
    t.pickup_sounds = t.attack_sounds
    t.fall_sounds = ['ireFall']
    t.style = 'bones'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0, 0, 0)

    # buddie's Buddy ###################################
    t = Appearance('Rem')
    t.color_texture = 'remColor'
    t.color_mask_texture = 'remColorMask'
    t.icon_texture = 'remIcon'
    t.icon_mask_texture = 'remIconCM'
    t.head_mesh = 'remHead'
    t.torso_mesh = 'remTorso'
    t.upper_arm_mesh = 'remUpperArm'
    t.forearm_mesh = 'remForeArm'
    t.hand_mesh = 'remHand'
    t.upper_leg_mesh = 'remUpperLeg'
    t.lower_leg_mesh = 'remLowerLeg'
    t.jump_sounds = ['zoeJump01', 'zoeJump02', 'zoeJump03']
    t.attack_sounds = [
        'zoeAttack01',
        'zoeAttack02',
        'zoeAttack03',
        'zoeAttack04',
    ]
    t.impact_sounds = [
        'zoeImpact01',
        'zoeImpact02',
        'zoeImpact03',
        'zoeImpact04',
    ]
    t.death_sounds = ['zoeDeath01']
    t.pickup_sounds = ['zoePickup01']
    t.fall_sounds = ['zoeFall01']
    t.style = 'bones'
    t.default_color = (232 / 255, 17 / 255, 17 / 255)
    t.default_highlight = (240 / 255, 14 / 255, 14 / 255)  

     # south park but pokemoen ###################################
    t = Appearance('Fennekin')
    t.color_texture = 'fennikoColor'
    t.color_mask_texture = 'fennikoColorMask'
    t.icon_texture = 'fennekinIcon'
    t.icon_mask_texture = 'fennekinIconCM'
    t.head_mesh = 'fennikoHead'
    t.torso_mesh = 'fennikoTorso'
    t.upper_arm_mesh = 'invisible'
    t.forearm_mesh = 'invisible'
    t.hand_mesh = 'fennikoHand'
    t.upper_leg_mesh = 'invisible'
    t.lower_leg_mesh = 'fennikoLeg'
    sounds = [
        'fennekin1', 'fennekin2', 'fennekin3',
        'fennekinPunch1', 'fennekinPunch2', 'fennekinPunch3',
    ]
    t.jump_sounds = sounds
    t.attack_sounds = [
        'fennekinPunch1', 'fennekinPunch2', 'fennekinPunch3',
    ]
    t.impact_sounds = [
        'fennekinHurt1', 'fennekinHurt2', 'fennekinHurt3',
        'fennekinHurt4', 'fennekinHurt5', 'fennekinHurt6',
        'fennekinHurt7'
    ]
    t.death_sounds = ['fennekinDeath']
    t.pickup_sounds = sounds
    t.fall_sounds = ['fennekinFall']
    t.style = 'mel'
    t.default_color = (1, 1, 0)
    t.default_highlight =(1, 0.5, 0)
    t.render = 'renders/FennekinRender'
    t.render_color_mask = 'renders/FennekinRenderColorMask'
    t.screen_ko_texture = 'renders/FennekinScreenKO'
    t.screen_ko_color_mask = 'renders/FennekinScreenKOColorMask'


    # THESE ARE ICONS FOR THE SHOP, DO NOT USE
    
    t = Appearance('Spaz.EXE')
    t.icon_texture = 'spazEXEIcon'
    t.icon_mask_texture = 'black'
   

    t = Appearance('Star Hoodie')
    t.icon_texture = 'hoppiIcon'
    t.icon_mask_texture = 'black'
   

    t = Appearance('Full-Insanity')
    t.icon_texture = 'amarInsanityIcon'
    t.icon_mask_texture = 'black'
   


    t = Appearance('Blue Cap')
    t.icon_texture = 'blueCapCosmeticIcon'
    t.icon_mask_texture = 'black'
   

    t = Appearance('Melling')
    t.icon_texture = 'fatassIcon'
    t.icon_mask_texture = 'fatassIconColorMask'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0.1, 0.6, 0.1)

    t = Appearance('Ninjaling')
    t.icon_texture = 'ninjaIcon'
    t.icon_mask_texture = 'ninjaIconColorMask'
    t.default_color = (0, 0.8, 1)
    t.default_highlight = (1, 1, 1)

    t = Appearance('Spazling')
    t.icon_texture = 'spazingaIcon'
    t.icon_mask_texture = 'spazingaIconColorMask'
    t.default_color = (0.5, 0.25, 1.0)
    t.default_highlight = (0.5, 0.25, 1.0)

    t = Appearance('Salvatore')
    t.icon_texture = 'SalCosmeticIcon'
    t.icon_mask_texture = 'black'

    t = Appearance('Scoldy')
    t.icon_texture = 'scoldyIcon'
    t.icon_mask_texture = 'scoldyIconMask'
    t.default_color = (0.3, 0.3, 0.33)
    t.default_highlight = (1, 0.5, 0.3)

    t = Appearance('Jolly')
    t.icon_texture = 'jollyNinjaIcon'
    t.icon_mask_texture = 'jollyNinjaIconColorMask'
    t.default_color = (1, 1, 1)
    t.default_highlight = (0.55, 0.8, 0.55)

    t = Appearance('Horseless Headless Horseman')
    t.icon_texture = 'AmarIcon'
    t.icon_mask_texture = 'black'

    t = Appearance('Gummy Voice Spaz')
    t.icon_texture = 'neoSpazIcon'
    t.icon_mask_texture = 'black'

    t = Appearance('Gummy Voice Jack')
    t.icon_texture = 'jackIcon'
    t.icon_mask_texture = 'black'

    t = Appearance('Gummy Voice Agent')
    t.icon_texture = 'agentIcon'
    t.icon_mask_texture = 'black'

    t = Appearance('YBS16')
    t.icon_texture = 'YBS16Icon'
    t.icon_mask_texture = 'YBS16IconColorMask'
    t.default_color = (1, 0.0, 0.0)
    t.default_highlight = (0, 0, 0)

    t = Appearance('Tophat')
    t.icon_texture = 'tophatIcon'
    t.icon_mask_texture = 'black'
   

    # Roaring Knight's right hand they/them #####################################
    t = Appearance('Kris')
    t.color_texture = 'krisColor'
    t.color_mask_texture = 'krisColorMask'
    t.head_mesh = 'krisHead'
    t.torso_mesh = 'krisTorso'
    t.pelvis_mesh = 'krisPelvis'
    t.upper_arm_mesh = 'krisUpperArm'
    t.forearm_mesh = 'krisForeArm'
    t.hand_mesh = 'krisHand'
    t.upper_leg_mesh = 'krisUpperLeg'
    t.lower_leg_mesh = 'krisLowerLeg'
    t.toes_mesh = 'krisToes'
    t.style = 'agent'
    t.default_color = (0, 1, 1)
    t.default_highlight = (0.4588235294117647, 0.984313725490196, 0.9294117647058824)
    
    # barney wannabe #####################################
    t = Appearance('Susie')
    t.color_texture = 'susieColor'
    t.color_mask_texture = 'susieColorMask'
    t.head_mesh = 'susieHead'
    t.torso_mesh = 'susieTorso'
    t.pelvis_mesh = 'susiePelvis'
    t.upper_arm_mesh = 'susieUpperArm'
    t.forearm_mesh = 'susieForeArm'
    t.hand_mesh = 'susieHand'
    t.upper_leg_mesh = 'susieUpperLeg'
    t.lower_leg_mesh = 'susieLowerLeg'
    t.toes_mesh = 'susieToes'
    t.style = 'agent'
    t.default_color =(1, 0.3, 0.6)
    t.default_highlight = (0.5333333333333333, 0.09019607843137255, 0.41568627450980394)
    
    # knite. ###################################
    t = Appearance('Roaring Knight')
    t.color_texture = 'knightColor'
    t.color_mask_texture = 'knightColorMask'
    t.head_mesh = 'knightHead'
    t.torso_mesh = 'knightTorso'
    t.pelvis_mesh = 'knightPelvis'
    t.upper_arm_mesh = 'knightUpperArm'
    t.forearm_mesh = 'knightForeArm'
    t.hand_mesh = 'knightHand'
    t.upper_leg_mesh = 'knightUpperLeg'
    t.lower_leg_mesh = 'knightLowerLeg'
    t.toes_mesh = 'knightToes'
    t.style = 'agent'
    t.default_color = (0.0, 0.0, 0.0)
    t.default_highlight = (1, 1, 1)

    t = Appearance('Empty')

    
