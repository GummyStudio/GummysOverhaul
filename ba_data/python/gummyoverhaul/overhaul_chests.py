import bascenev1 as bs
import _bauiv1 as bui # type: ignore
import random


def give_chest(chest_data: dict) -> None:
    """
    Give a chest to the player. If the current slot is empty, set it there.
    Otherwise, append to the queue.
    """
    cfg = bs.app.config
    #from gummyoverhaul.overhaul_chests import give_chest; give_chest({"type": "coins","color": (0.5, 1, 1),"name": "test chest", "tint": (1, 1, 1),"tint2": (1, 1, 1), "rewards": 0})

    #from gummyoverhaul.overhaul_chests import give_chest; give_chest({"type": "coins","color": (1, 1, 0.8),"name": "test chest", "tint": (random.random(), random.random(), random.random()),"tint2": (random.random(), random.random(), random.random()), "rewards": 0})

   

    if not cfg["gummy_chestinslot"]:
        # Slot is empty: put chest here
        cfg["gummy_chestinslot"] = chest_data
    else:
        # Slot occupied: append to queue
        cfg["gummy_chestqueue"].append(chest_data)
        
    bs.screenmessage("You got a chest! (Check your Inventory)", color=(0, 0.8, 1))
    bui.getsound('cashRegister').play()
    

    cfg.apply_and_commit()

def drop_random_chest(max_level: int = 4):
    """ drops a chest with random attributes. """
    
    level = min(random.randint(1, max_level), 4)
    if random.randint(0, 5) == 0:
        level *= 2
        give_chest(
            {
                "type": "both",
                "name": f"Random Drop Lvl{level}",
                "color": (1, 1, 0.8 ) if level == 1 else (1, 1, 2) if level == 2 else (2.5, 1, 2) if level == 3 else (2.5, 3, 2),
                "tint": (random.random(), random.random(), random.random()),
                "tint2": (random.random(), random.random(), random.random()),
                "coins": random.randint(130, 380) * level,
                "dollars": random.randint(1, 4)
                }
        )

    else:
        give_chest(
            {
                "type": "coins",
                "name": f"Random Drop Lvl{level}",
                "color": (1, 1, 0.8 ) if level == 1 else (1, 1, 2) if level == 2 else (2.5, 1, 2) if level == 3 else (2.5, 3, 2),
                "tint": (random.random(), random.random(), random.random()),
                "tint2": (random.random(), random.random(), random.random()),
                "rewards": random.randint(130, 380) * level
                }
        )

def random_shit():
    
    
    from gummyoverhaul.overhaul_chests import give_chest; give_chest({"type": "coins","color": (0.5, 1, 0.9), "name": f"Coins Chest {random.randint(100, 999)}", "tint": (random.random(), random.random(), random.random()),"tint2": (random.random(), random.random(), random.random()), "rewards": 0})
    from gummyoverhaul.overhaul_chests import give_chest; give_chest({"type": "dollars","color": (1, 1, 1), "name": f"Dollars Chest {random.randint(100, 999)}", "tint": (random.random(), random.random(), random.random()),"tint2": (random.random(), random.random(), random.random()), "rewards": 0})
    from gummyoverhaul.overhaul_chests import give_chest; give_chest({"type": "both","color": (1, 1, 1), "name": f"Both Chest {random.randint(100, 999)}", "tint": (random.random(), random.random(), random.random()),"tint2": (random.random(), random.random(), random.random()), "coins": 0, "dollars": 0})

    from gummyoverhaul.overhaul_chests import give_chest; give_chest({"type": "both","color": (0.1, 1, 0.8), "name": f"Both Chest {random.randint(100, 999)}", "tint": (1, 2, 2),"tint2": (random.random(), random.random(), random.random()), "coins": 0, "dollars": 0})
    from gummyoverhaul.overhaul_chests import drop_random_chest; drop_random_chest()