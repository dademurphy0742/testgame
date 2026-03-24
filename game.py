import json
import random
import os
from colorama import init, Fore
from enhancements import multi_step_attack, apply_weakness, use_enhanced_item, process_armor_turn, is_boss
from features import assign_skill_point

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

    def attack(self):
        return random.randint(*self.dmg_range)

# Regular enemies per zone
ZONE_ENEMIES = {
    "Linux": [
        Enemy("Script Kiddie", 50, (10, 20), "linux"),
        Enemy("Account Lockout", 55, (5, 10))
    ],
    "Network": [
        Enemy("Firewall Misconfig", 70, (5, 15), "network"),
        Enemy("Account Lockout", 55, (5, 10))
    ],
    "Kali": [
        Enemy("Script Kiddie", 50, (10, 20), "linux"),
        Enemy("Ransomware", 60, (8, 18), "python")
    ]
}

# Bosses per zone
ZONE_BOSSES = {
    "Linux": Enemy("APT Hacker", 80, (12, 22), "network"),
    "Network": Enemy("Firewall Overlord", 90, (15, 25), "network"),
    "Kali": Enemy("Malware Overlord", 100, (18, 28), "python")
}

# =========================
# PLAYER SYSTEM
# =========================
class Player:
    def __init__(self, name, role, hp=100, max_hp=100, xp=0, level=1,
                 inventory=None, zone=0, skill_points=0, skills=None, status=None):
        self.name = name
        self.role = role
        self.hp = hp
        self.max_hp = max_hp
        self.xp = xp
        self.level = level
        self.inventory = inventory if inventory else []
        self.zone = zone
        self.skill_points = skill_points
        self.skills = skills if skills else {
            "damage": 0, "health": 0, "xp": 0, "python": 0, "network": 0
        }
        self.status = status if status else {"poison": 0, "stun": False, "armor": 0}
        self.armor_turns = 0
        self.damage_boost_turns = 0

    def take_damage(self, amount):
        reduced = max(0, amount - (5 if self.armor_turns > 0 else 0))
        self.hp = max(0, self.hp - reduced)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_xp(self, amount):
        bonus = self.skills["xp"] * 0.1
        self.xp += int(amount * (1 + bonus))
        if self.xp >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.skill_points += 1
        self.max_hp += 25 + self.skills.get("health", 0) * 5
        self.hp = self.max_hp
        print(Fore.BLUE + f"\n🎉 LEVEL UP! Level {self.level} | Skill Points: {self.skill_points}")
        while self.skill_points > 0:
            assign_skill_point(self)
            self.skill_points -= 1

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

# =========================
# NORMALIZATION
# =========================
def normalize(cmd):
    return cmd.strip().lower()

# =========================
# TOOLS / ITEMS
# =========================
def use_item(player):
    if not player.inventory:
        print("❌ No items available")
        return None

    print(Fore.GREEN + "Your items:")
    for i, item in enumerate(player.inventory):
        print(f"{i+1}. {item}")

    choice = input("Item: ")
    if not choice.isdigit():
        print("❌ Invalid choice")
        return None

    idx = int(choice) - 1
    if idx < 0 or idx >= len(player.inventory):
        print("❌ Invalid choice")
        return None

    item = player.inventory.pop(idx)
    return use_enhanced_item(player, item)

# =========================
# STATUS EFFECTS
# =========================
def process_status(player):
    process_armor_turn(player)

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
def battle(player, enemy, questions):
    enemy.scale(player.level)
    print(Fore.BLUE + f"\n⚔️ Encounter: {enemy.name}")
    input(Fore.GREEN + "Press Enter to start…")

    filtered_qs = questions[:]
    random.shuffle(filtered_qs)

    while enemy.hp > 0 and player.hp > 0:
        if process_status(player):
            continue
        if not filtered_qs:
            break

        q = filtered_qs.pop()
        player_content = f"{player.name} HP: {player.hp}/{player.max_hp}"
        enemy_content = f"{enemy.name} HP: {enemy.hp}/{enemy.base_hp}"
        box_width = max(len(player_content), len(enemy_content)) + 4

        print(Fore.CYAN + f"┌{'─'*box_width}┐")
        print(Fore.CYAN + f"│ {player_content:<{box_width-2}}│")
        print(Fore.CYAN + f"└{'─'*box_width}┘")
        print(Fore.MAGENTA + f"┌{'─'*box_width}┐")
        print(Fore.MAGENTA + f"│ {enemy_content:<{box_width-2}}│")
        print(Fore.MAGENTA + f"└{'─'*box_width}┘")

        print(Fore.WHITE + "--- TERMINAL ---")
        print(Fore.WHITE + f"💻 Challenge: {q['question']}")
        options = q.get("options", [q["answer"]])
        random.shuffle(options)
        print(Fore.GREEN + "Options for reference:")
        for opt in options[:4]:
            print(Fore.GREEN + f"• {opt}")

        choice = input(Fore.GREEN + "(i) Use item | Type command > ")
        cmd = normalize(choice)

        if cmd == "i":
            use_item(player)
            continue

        # Boss multi-step attack
        if is_boss(enemy.name):
            damage_done, msg, skip_enemy = multi_step_attack(enemy, player, questions)
            if skip_enemy:
                break

        if cmd == normalize(q["answer"]):
            dmg = random.randint(15, 30)
            dmg += apply_weakness(enemy, player, q)
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
        {"name": "Linux", "file": "linux_commands.json", "loot": ["heal", "script", "firewall"]},
        {"name": "Network", "file": "network_commands.json", "loot": ["heal", "armor_potion", "network_patch"]},
        {"name": "Kali", "file": "kali_commands.json", "loot": ["heal", "script_boost", "network_patch"]}
    ]

    while player.zone < len(ZONES):
        zone = ZONES[player.zone]
        print(Fore.BLUE + f"\n🌐 Zone: {zone['name']}")
        questions = load_questions(zone['file'])
        enemies_pool = ZONE_ENEMIES[zone["name"]]

        # 10 regular fights
        for fight_num in range(10):
            enemy = random.choice(enemies_pool)
            alive = battle(player, enemy, questions)
            if not alive:
                print(Fore.RED + "💀 Game Over")
                save_game(player)
                return

            # Loot
            loot_item = random.choice(zone["loot"])
            player.inventory.append(loot_item)
            print(Fore.YELLOW + f"📦 Loot acquired: {loot_item}")
            save_game(player)

        # Boss fight at end of zone
        boss = ZONE_BOSSES[zone["name"]]
        print(Fore.RED + f"\n🔥 BOSS FIGHT: {boss.name} 🔥")
        alive = battle(player, boss, questions)
        if not alive:
            print(Fore.RED + "💀 Game Over")
            save_game(player)
            return

        # Boss loot
        loot_item = random.choice(zone["loot"])
        player.inventory.append(loot_item)
        print(Fore.YELLOW + f"📦 Boss loot acquired: {loot_item}")
        save_game(player)

        player.zone += 1

    print(Fore.GREEN + "🏆 Victory! All zones cleared.")

if __name__ == "__main__":
    game_loop()
