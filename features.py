import random
from colorama import Fore

# =========================
# Skill Tree / Level Up
# =========================
def assign_skill_point(player):
    print(Fore.BLUE + "\n🎯 Assign a skill point:")
    skills = list(player.skills.keys())
    for i, skill in enumerate(skills):
        print(f"{i+1}. {skill} (current: {player.skills[skill]})")
    choice = input("Choose skill to increase: ")
    if choice.isdigit() and 1 <= int(choice) <= len(skills):
        player.skills[skills[int(choice)-1]] += 1
        print(Fore.GREEN + f"✅ {skills[int(choice)-1]} increased!")
        return True
    else:
        print(Fore.RED + "❌ Invalid choice")
        return False

# =========================
# Loot System
# =========================
def get_loot(player):
    loot_table = ["heal", "script", "firewall", "exploit", "armor_potion"]
    loot = random.choice(loot_table)
    player.inventory.append(loot)
    print(Fore.YELLOW + f"📦 Loot acquired: {loot}")

# =========================
# Multi-step challenge
# =========================
def multi_step_challenge(player, steps):
    print(Fore.MAGENTA + "💻 Multi-step challenge initiated!")
    for step in steps:
        choice = input(Fore.GREEN + f"Step: {step['question']} > ")
        if choice.strip().lower() != step["answer"]:
            dmg = 10
            player.hp -= dmg
            print(Fore.RED + f"❌ Incorrect! Took {dmg} damage")
        else:
            print(Fore.YELLOW + "✅ Step completed")
