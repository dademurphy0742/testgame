import json
import random
import os

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
        self.skills = skills if skills else {
            "damage": 0,
            "health": 0,
            "xp": 0,
            "python": 0,
            "network": 0
        }
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
            self.level_up()

    def level_up(self):
        self.level += 1
        self.skill_points += 1
        self.max_hp += 25
        self.hp = self.max_hp
        print(f"\n🎉 LEVEL UP! Level {self.level} | Skill Points: {self.skill_points}\n")

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
    print("💾 Game saved.")


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
# NORMALIZATION (KEY FOR TERMINAL MODE)
# =========================
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
    elif item == "script":
        print("⚡ Script executed")
        return "skip"
    elif item == "firewall":
        player.status["armor"] = 5
        print("🛡️ Firewall active")

    return None

# =========================
# STATUS EFFECTS
# =========================
def process_status(player):
    if player.status["poison"] > 0:
        player.take_damage(5)
        player.status["poison"] -= 1
        print("☠️ Poison")

    if player.status["stun"]:
        print("⚠️ Stunned")
        player.status["stun"] = False
        return True

    return False

# =========================
# TERMINAL COMBAT
# =========================
def ask_question_terminal(q, enemy):
    print("\n--- TERMINAL ---")
    print(q["question"])

    if q.get("type") == "python":
        print(q.get("code", ""))

    if enemy.behavior == "evasive":
        print("⚠️ Output obscured. Be precise.")

    answer = input("$ ")
    return normalize(answer) == normalize(q["answer"])

# =========================
# COMBAT
# =========================
def battle(player, questions):
    enemy = random.choice(ENEMIES)
    enemy.scale(player.level)

    print(f"\n⚔️ {enemy.name} engaged!")

    q_pool = questions[:]
    random.shuffle(q_pool)

    while enemy.hp > 0 and player.hp > 0:
        if process_status(player):
            continue

        print(f"\n{player.name}: {player.hp} HP | {enemy.name}: {enemy.hp} HP")

        if not q_pool:
            break

        q = q_pool.pop()

        print("(i)item")
        choice = input("> ")

        if choice == "i":
            result = use_item(player)
            if result == "skip":
                enemy.hp -= 25
                continue

        correct = ask_question_terminal(q, enemy)

        if correct:
            crit = random.random() < 0.2
            dmg = random.randint(15, 30)

            if crit:
                dmg *= 2
                print("💥 CRITICAL HIT")

            if enemy.weakness:
                dmg += player.skills.get(enemy.weakness, 0) * 3

            enemy.hp -= dmg
            print(f"✅ {dmg} damage")

            if q.get("type") == "python":
                player.skills["python"] += 1

            player.gain_xp(25)
        else:
            dmg = enemy.attack()
            player.take_damage(dmg)
            print(f"❌ Incorrect. Took {dmg}")

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
        print(f"\n🌍 {zone['name']}")

        questions = load_questions(zone['file'])

        if not battle(player, questions):
            print("💀 Game Over")
            save_game(player)
            return

        print("📦 Loot acquired")
        player.inventory.append(random.choice(["heal", "script", "firewall"]))

        player.zone += 1
        save_game(player)

    print("🏆 Victory")


if __name__ == "__main__":
    game_loop()
