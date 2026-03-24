import random
from colorama import Fore

# =========================
# MULTI-STEP BOSS CHALLENGES
# =========================
BOSS_CHALLENGES = {
    "APT Hacker": [
        ["nmap", "tcpdump", "wireshark"],
        ["iperf", "airmon-ng", "aircrack-ng"]
    ],
    "Ransomware": [
        ["python", "grep", "rm"],
        ["chmod", "chown", "mv"]
    ]
}

def is_boss(enemy_name):
    return enemy_name in BOSS_CHALLENGES

def multi_step_attack(enemy, player, command_history):
    """
    Checks if the player is doing the correct sequence for a boss.
    Returns (damage, message, skip_enemy_attack)
    """
    sequences = BOSS_CHALLENGES.get(enemy.name, [])
    damage = 0
    skip = False
    for seq in sequences:
        # Check if last N commands match a sequence
        if command_history[-len(seq):] == seq:
            damage = random.randint(30, 50)
            crit = random.random() < 0.2
            if crit:
                damage *= 2
                print(Fore.RED + "💥 CRITICAL MULTI-STEP HIT!")
            enemy.hp -= damage
            skip = True  # Enemy loses turn
            print(Fore.YELLOW + f"🎯 Multi-step success! {damage} damage")
            return damage, "multi-step success", skip
    return damage, None, skip

# =========================
# ENEMY-WEAKNESS INTERACTION
# =========================
def apply_weakness(enemy, player, command):
    """
    Gives bonus damage if command matches enemy weakness tag
    """
    bonus = 0
    if enemy.weakness:
        # Command tags would come from JSON questions
        if enemy.weakness in command.get("tags", []):
            bonus = random.randint(5, 15)
            enemy.hp -= bonus
            print(Fore.CYAN + f"⚡ Exploited weakness ({enemy.weakness})! +{bonus} damage")
    return bonus

# =========================
# NEW ITEMS
# =========================
def use_enhanced_item(player, item):
    """
    Handles extra items without bloating game.py
    """
    if item == "armor_potion":
        player.status["armor"] = 10
        print(Fore.CYAN + "🛡️ Armor Potion activated! +10 armor for 3 turns")
        player.status["armor_turns"] = 3
    elif item == "poison_antidote":
        player.status["poison"] = 0
        print(Fore.CYAN + "💊 Poison cured!")
    elif item == "network_patch":
        player.skills["network"] += 1
        print(Fore.CYAN + "💻 Network skill temporarily boosted!")
    elif item == "script_boost":
        player.skills["damage"] += 2
        print(Fore.CYAN + "⚡ Script Boost! +2 damage next turn")
    else:
        return False
    return True

# =========================
# PROCESS STATUS FOR ARMOR TURN
# =========================
def process_armor_turn(player):
    if "armor_turns" in player.status and player.status["armor_turns"] > 0:
        player.status["armor_turns"] -= 1
        if player.status["armor_turns"] == 0:
            player.status["armor"] = 0
            print(Fore.YELLOW + "🛡️ Armor effect wore off")
