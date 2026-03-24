# enhancements.py
import random

# =========================
# BOSS SYSTEM
# =========================

def is_boss(enemy_name):
    return enemy_name in ["APT Hacker", "Ransomware", "Network Defender", "Account Lockout"]

# Boss sequences now match STEP TAGS (not command names)
BOSS_SEQUENCES = {
    "APT Hacker": ["step1", "step2", "step3"],
    "Ransomware": ["step1", "step2", "step3"],
    "Network Defender": ["step1", "step2", "step3"],
    "Account Lockout": ["step1", "step2", "step3"]
}

# =========================
# WEAKNESS SYSTEM
# =========================

def apply_weakness(enemy, player, question):
    """
    Returns bonus damage if question tags match enemy weakness
    """
    if not hasattr(enemy, "weakness"):
        return 0

    for tag in question.get("tags", []):
        if tag in enemy.weakness:
            bonus = random.randint(8, 15)
            print(f"⚡ Exploited weakness ({tag})! +{bonus} damage")
            return bonus

    return 0


# =========================
# ITEM SYSTEM
# =========================

def use_enhanced_item(player, item_name):
    if item_name == "heal":
        heal = 40
        player.hp = min(player.max_hp, player.hp + heal)
        print(f"💖 Healed {heal} HP!")

    elif item_name == "armor_potion":
        player.armor_turns = 3
        print("🛡 Armor active for 3 turns!")

    elif item_name == "script":
        # instant damage ability
        print("💻 Script executed! Massive damage!")
        return "script"

    elif item_name == "script_boost":
        player.damage_boost_turns = 3
        print("⚔ Damage boosted for 3 turns!")

    else:
        print("❓ Unknown item")


def process_armor_turn(player):
    """
    Handles turn-based buffs
    """
    if hasattr(player, "armor_turns") and player.armor_turns > 0:
        player.armor_turns -= 1

    if hasattr(player, "damage_boost_turns") and player.damage_boost_turns > 0:
        player.damage_boost_turns -= 1


def modify_damage(player, base_damage):
    """
    Apply armor + damage boost modifiers
    """
    # Armor reduces incoming damage (handled elsewhere typically)
    # Damage boost increases outgoing damage
    if hasattr(player, "damage_boost_turns") and player.damage_boost_turns > 0:
        base_damage += 10

    return base_damage


# =========================
# BOSS FIGHT SYSTEM
# =========================

def multi_step_attack(player, enemy, questions):
    """
    Boss fight with step-based progression
    """
    sequence = BOSS_SEQUENCES.get(enemy.name, [])
    step_index = 0

    print(f"\n🔥 BOSS FIGHT: {enemy.name} 🔥")

    while enemy.hp > 0 and player.hp > 0:

        current_step = sequence[step_index]

        # FIXED: now selects by BOTH enemy + step
        possible_questions = [
            q for q in questions
            if enemy.name in q.get("tags", []) and current_step in q.get("tags", [])
        ]

        if not possible_questions:
            print("⚠ No boss questions found for this step!")
            return False

        q = random.choice(possible_questions)

        print(f"\n💻 Step {step_index + 1}: {q['question']}")

        options = q.get("options", [q["answer"]])
        random.shuffle(options)

        for opt in options[:4]:
            print(f"• {opt}")

        choice = input("(i) Use item | Type command > ").strip().lower()

        # =========================
        # ITEM USAGE
        # =========================
        if choice == "i":
            from game import use_item  # avoid circular import at top
            result = use_item(player)

            if result == "script":
                dmg = 35
                print(f"💥 Script hit for {dmg} damage!")
                enemy.hp -= dmg
                continue

        # =========================
        # ANSWER CHECK
        # =========================
        if choice == q["answer"].lower():
            dmg = random.randint(20, 35)

            # Apply weakness bonus
            dmg += apply_weakness(enemy, player, q)

            dmg = modify_damage(player, dmg)

            print(f"✅ Correct! {dmg} damage")
            enemy.hp -= dmg

            step_index += 1

        else:
            dmg = random.randint(10, 18)

            # Armor reduces damage
            if hasattr(player, "armor_turns") and player.armor_turns > 0:
                dmg = max(0, dmg - 5)
                print("🛡 Armor reduced damage!")

            print(f"❌ Wrong! Took {dmg} damage")
            player.take_damage(dmg)

        process_armor_turn(player)

        if step_index >= len(sequence):
            print(f"\n💀 {enemy.name} defeated!")
            return True

    return enemy.hp <= 0
