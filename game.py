import json
import random
import os
from colorama import init, Fore, Style
from features import enhanced_level_up, get_loot, multi_step_challenge

init(autoreset=True)
SAVE_FILE = "savegame.json"

# =========================
# ENEMY SYSTEM
# =========================
class Enemy:
    def __init__(self, name, base_hp, dmg_range, weakness=None, effect=None, behavior=None):
        self.name = name
        self.base_hp = base_hp
        self.dmg_range = dmg_range
        self.weakness = weakness
        self.effect = effect
        self.behavior = behavior
        self.hp = base_hp

    def scale(self, level):
        self.hp = self.base_hp + (level * 12)
        self.dmg_range = (self.dmg_range[0]+level, self.dmg_range[1]+level)

    def attack(self):
        return random.randint(*self.dmg_range)

ENEMIES = [
    Enemy("Script Kiddie", 50, (10, 20), "linux"),
    Enemy("Ransomware", 60, (8, 18), "python", "poison"),
    Enemy("Firewall Misconfig", 70, (5, 15), "network", "armor"),
    Enemy("Account Lockout", 55, (5, 10), None, "stun"),
    Enemy("APT Hacker", 80, (12, 22), "network", None, "evasive")
]

# =========================
# PLAYER SYSTEM
# =========================
class Player:
    def __init__(self, name, role, hp=100, max_hp=100, xp=0, level=1, inventory=None, zone=0, skill_points=0, skills=None, status=None):
        self.name = name
        self.role = role
        self.hp = hp
        self.max_hp = max_hp
        self.xp = xp
        self.level = level
        self.inventory = inventory if inventory else []
        self.zone = zone
        self.skill_points = skill_points
        self.skills = skills if skills else {"damage": 0, "health": 0, "xp": 0, "python": 0, "network": 0}
        self.status = status if status else {"poison": 0, "stun": False, "armor": 0}

    def take_damage(self, amount):
        reduced = max(0, amount - self.status.get("armor", 0))
        self.hp = max(0, self.hp - reduced)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_xp(self, amount):
        bonus = self.skills["xp"] * 0.1
        self.xp += int(amount * (1 + bonus))
        if self.xp >= self.level * 100:
            enhanced_level_up(self)

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Player(**data)

# =========================
# SAVE / LOAD
# =========================
def save_game(player):
    with open(SAVE_FILE, "w") as f:
        json.dump(player.to_dict(), f)
    print(Fore.YELLOW + "💾 Game saved.")

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        return Player.from_dict(json.load(f))

# =========================
# QUESTIONS
# =========================
def load_questions(file):
    if not os.path.exists(file):
        return []
    with open(file, 'r') as f:
        return json.load(f)["commands"]

def normalize(cmd):
    return cmd.strip().lower()

# =========================
# TOOLS
# =========================
def use_item(player):
    if not player.inventory:
        return None

    for i, item in enumerate(player.inventory):
        print(f"{i+1}. {item}")

    choice = input("Item: ")
    if not choice.isdigit():
        return None

    item = player.inventory.pop(int(choice)-1)
    if item == "heal":
        player.heal(30)
        print(Fore.CYAN + "💊 Restored 30 HP")
    elif item == "script":
        print(Fore.YELLOW + "⚡ Script executed")
        return "skip"
    elif item == "firewall":
        player.status["armor"] = 5
        print(Fore.CYAN + "🛡️ Firewall active")
    elif item == "exploit":
        print(Fore.RED + "⚡ Exploit dealt massive damage")
        return "exploit"
    elif item == "armor_potion":
        player.status["armor"] += 3
        print(Fore.CYAN + "🛡️ Armor increased by 3")
    return None

# =========================
# STATUS EFFECTS
# =========================
def process_status(player):
    if player.status["poison"] > 0:
        player.take_damage(5)
        player.status["poison"] -= 1
        print(Fore.MAGENTA + "☠️ Poison damage")

    if player.status["stun"]:
        print(Fore.YELLOW + "⚡ Stunned! Skipping turn")
        player.status["stun"] = False
        return True
    return False

# =========================
# COMBAT
# =========================
def battle(player, questions):
    enemy = random.choice(ENEMIES)
    enemy.scale(player.level)

    print(Fore.BLUE + f"\n{'='*20} ⚡ CYBERNETIC ENGAGEMENT ⚡ {'='*20}\n")
    print(Fore.CYAN + f"🌐 Zone: {['Linux','Network','Kali'][player.zone]}\n⚔️ Encounter: {enemy.name}")
    input(Fore.GREEN + "Press Enter to start the fight…")

    # =========================
    # Filter questions by enemy weakness
    # =========================
    if enemy.weakness:
        q_pool = [q for q in questions if enemy.weakness in q.get("tags", [])]
    else:
        q_pool = questions[:]

    # fallback: if no questions match, use full zone
    if not q_pool:
        q_pool = questions[:]

    random.shuffle(q_pool)

    while enemy.hp > 0 and player.hp > 0:
        if process_status(player):
            continue

        if not q_pool:
            break
        q = q_pool.pop()

        # =========================
        # Display player & enemy HP
        # =========================
        player_content = f"{player.name} HP: {player.hp}/{player.max_hp}"
        enemy_content = f"{enemy.name} HP: {enemy.hp}/{enemy.base_hp}"
        box_width = max(len(player_content), len(enemy_content)) + 4
        print(Fore.CYAN + f"┌{'─'*box_width}┐\n│ {player_content:<{box_width-2}}│\n└{'─'*box_width}┘")
        print(Fore.MAGENTA + f"┌{'─'*box_width}┐\n│ {enemy_content:<{box_width-2}}│\n└{'─'*box_width}┘")

        # =========================
        # Show terminal challenge
        # =========================
        print(Fore.WHITE + "--- TERMINAL ---")
        print(Fore.WHITE + f"💻 Challenge: {q['question']}")
        options = q.get("options", [q["answer"]])
        random.shuffle(options)
        print(Fore.GREEN + "Options for reference:")
        for opt in options[:4]:
            print(Fore.GREEN + f"• {opt}")

        choice = input(Fore.GREEN + "(i) Use item | Type command > ")

        # =========================
        # Item usage
        # =========================
        if choice.strip().lower() == "i":
            result = use_item(player)
            if result == "skip":
                enemy.hp -= 25
                continue
            elif result == "exploit":
                enemy.hp -= 50
                continue
        else:
            correct = normalize(choice) == normalize(q["answer"])
            if correct:
                crit = random.random() < 0.2
                dmg = random.randint(15, 30)
                if crit:
                    dmg *= 2
                    print(Fore.RED + "💥 CRITICAL HIT!")
                if enemy.weakness:
                    # Add skill bonus
                    if isinstance(enemy.weakness, list):
                        for w in enemy.weakness:
                            dmg += player.skills.get(w, 0) * 3
                    else:
                        dmg += player.skills.get(enemy.weakness, 0) * 3
                enemy.hp -= dmg
                print(Fore.YELLOW + f"✅ {dmg} damage")
                player.gain_xp(25)
            else:
                dmg = enemy.attack()
                player.take_damage(dmg)
                print(Fore.RED + f"❌ Incorrect. Took {dmg}")
                if enemy.effect == "poison":
                    player.status["poison"] = 3
                if enemy.effect == "stun" and random.random() < 0.3:
                    player.status["stun"] = True

    return player.hp > 0


# =========================
# GAME LOOP
# =========================
def game_loop():
    player = load_game()
    if not player:
        player = Player(input("Name: "), "Pentester")

    ZONES = [
        {"name": "Linux", "file": "linux_commands.json"},
        {"name": "Network", "file": "network_commands.json"},
        {"name": "Kali", "file": "kali_commands.json"}
    ]

    while player.zone < len(ZONES):
        zone = ZONES[player.zone]
        print(Fore.BLUE + f"\n🌐 Zone: {zone['name']}")
        questions = load_questions(zone['file'])

        if not battle(player, questions):
            print(Fore.RED + "💀 Game Over")
            save_game(player)
            return

        # Loot & save
        get_loot(player)
        save_game(player)
        player.zone += 1

    print(Fore.GREEN + "🏆 Victory")

if __name__ == "__main__":
    game_loop()
