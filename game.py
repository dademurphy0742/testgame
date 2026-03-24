import json
import random
import os

SAVE_FILE = "savegame.json"

# =========================
# PLAYER SYSTEM
# =========================
class Player:
    def __init__(self, name, role, hp=100, max_hp=100, xp=0, level=1, inventory=None, zone=0, skill_points=0, skills=None):
        self.name = name
        self.role = role
        self.hp = hp
        self.max_hp = max_hp
        self.xp = xp
        self.level = level
        self.inventory = inventory if inventory else []
        self.zone = zone
        self.skill_points = skill_points
        self.skills = skills if skills else {"damage": 0, "health": 0, "xp": 0}

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

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
        self.max_hp += 20 + (self.skills["health"] * 5)
        self.hp = self.max_hp
        print(f"\n🎉 LEVEL UP! Level {self.level} | Skill Points: {self.skill_points}\n")

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Player(**data)

# =========================
# SAVE / LOAD SYSTEM
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
# ZONES
# =========================
ZONES = [
    {"name": "Home Directory", "file": "linux_commands.json"},
    {"name": "Networking Realm", "file": "network_commands.json"},
    {"name": "Kali Underworld", "file": "kali_commands.json"}
]

# =========================
# LOAD QUESTIONS
# =========================
def load_questions(file):
    if not os.path.exists(file):
        return []
    with open(file, 'r') as f:
        return json.load(f)["commands"]

# =========================
# SKILL TREE
# =========================
def skill_menu(player):
    while player.skill_points > 0:
        print("\n🧬 Skill Tree")
        print(f"Points Available: {player.skill_points}")
        print("1. Increase Damage")
        print("2. Increase Max Health")
        print("3. Increase XP Gain")

        choice = input("Choose skill to upgrade: ")

        if choice == "1":
            player.skills["damage"] += 1
        elif choice == "2":
            player.skills["health"] += 1
        elif choice == "3":
            player.skills["xp"] += 1
        else:
            print("Invalid choice")
            continue

        player.skill_points -= 1
        print("✅ Skill upgraded!")

# =========================
# COMBAT SYSTEM
# =========================
def battle(player, questions, boss=False):
    enemy_hp = (120 if boss else 50) + (player.level * 10)
    print(f"\n⚔️ {'BOSS BATTLE' if boss else 'Encounter'} in {ZONES[player.zone]['name']}!\n")

    questions_copy = questions[:]  # make a copy
    random.shuffle(questions_copy)

    while enemy_hp > 0 and player.hp > 0:
        if not questions_copy:
            break  # no more questions
        question = questions_copy.pop()  # get a unique question

        print(f"\n🧑 {player.name} HP: {player.hp}/{player.max_hp}")
        print(f"💻 Enemy HP: {enemy_hp}\n")

        print(f"Question: {question['question']}")
        options = question['options'][:]
        random.shuffle(options) 

        if "hint" in player.inventory and not boss:
            wrong = [o for o in options if o != question['answer']]
            if wrong:
                options.remove(random.choice(wrong))
            player.inventory.remove("hint")  # consume hint
            print("💡 Hint used! One wrong option removed.")

        for i, opt in enumerate(options):
            print(f"{i+1}. {opt}")

        print("\n(i) Use Item    (s) Save Game")
        choice = input("Choose an option: ")

        if choice == "i":
            use_item(player)
            continue
        if choice == "s":
            save_game(player)
            continue

        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(options):
            print("Invalid choice!")
            continue

        selected = options[int(choice)-1]

        if selected == question['answer']:
            base = random.randint(15, 30)
            damage = base + (player.skills["damage"] * 5)
            enemy_hp -= damage
            print(f"\n✅ Correct! You dealt {damage} damage!")
            player.gain_xp(30 if boss else 20)
        else:
            damage = random.randint(15, 30) if boss else random.randint(10, 25)
            player.take_damage(damage)
            print(f"\n❌ Wrong! You took {damage} damage!")

    return player.hp > 0

# =========================
# INVENTORY SYSTEM
# =========================
def use_item(player):
    if not player.inventory:
        print("No items available.")
        return

    print("Inventory:")
    for i, item in enumerate(player.inventory):
        print(f"{i+1}. {item}")

    choice = input("Choose item to use: ")
    if choice.isdigit() and int(choice) <= len(player.inventory):
        item = player.inventory.pop(int(choice)-1)

        if item == "heal":
            player.heal(30)
            print("You healed 30 HP!")
        elif item == "hint":
            print("Hint active!")

# =========================
# RANDOM EVENTS
# =========================
def random_event(player):
    event = random.choice(["heal", "damage", "loot", "none"])

    if event == "heal":
        player.heal(20)
        print("💾 Backup found. +20 HP")
    elif event == "damage":
        player.take_damage(15)
        print("🔥 System overload! -15 HP")
    elif event == "loot":
        item = random.choice(["heal", "hint"])
        player.inventory.append(item)
        print(f"🎁 Found item: {item}")

# =========================
# GAME LOOP
# =========================
def game_loop():
    print("\n=== Linux Sandbox RPG ===\n")

    player = load_game()

    if player:
        print(f"Welcome back, {player.name}!")
    else:
        name = input("Enter your name: ")
        print("1. Script Kiddie  2. SysAdmin  3. Pentester")
        role = {"1": "Script Kiddie", "2": "SysAdmin", "3": "Pentester"}.get(input("Choice: "), "SysAdmin")
        player = Player(name, role)

    while player.zone < len(ZONES):
        zone = ZONES[player.zone]
        print(f"\n🌍 Entering {zone['name']}\n")

        questions = load_questions(zone['file'])
        random.shuffle(questions)

# ===== ZONE ENCOUNTERS =====
        questions = load_questions(zone['file'])
        if not questions:
            print("No questions found for this zone. Skipping...")
            player.zone += 1
            continue
        
        # Shuffle questions once
        random.shuffle(questions)
        
        # Run normal battles
        survived = battle(player, questions)
        if not survived:
            print("\n💀 Game Over")
            save_game(player)
            return
        
        # Random event
        random_event(player)
        
        # Boss fight with multiple questions
        num_boss_questions = min(5, len(questions))
        boss_questions = random.sample(questions, num_boss_questions)
        
        print("\n👑 Boss Appears!\n")
        if not battle(player, boss_questions, boss=True):
            print("\n💀 Defeated by Boss")
            save_game(player)
            return
        
        print("\n🏆 Zone Cleared!")
        player.zone += 1
        skill_menu(player)
        save_game(player)

    print("\n🏆 You conquered all zones!")

# =========================
# START GAME
# =========================
if __name__ == "__main__":
    game_loop()
