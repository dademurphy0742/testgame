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
    bonus = 0
    if enemy.weakness:
        for tag in question.get("tags", []):
            if tag == enemy.weakness:
                bonus = random.randint(8, 15)
                print(f"⚡ Exploited weakness ({tag})! +{bonus} damage")
    return bonus

# =========================
# ITEM SYSTEM
# =========================

def use_enhanced_item(player, item_name):
    """
    Returns flags for battle handling:
    "skip" = skip enemy turn
    "script" = instant damage
    None = normal effect
    """
    if item_name == "heal":
        heal = 40
        player.hp = min(player.max_hp, player.hp + heal)
        print(f"💖 Healed {heal} HP!")
        return None

    elif item_name == "armor_potion":
        player.armor_turns = 3
        print("🛡 Armor active for 3 turns!")
        return None

    elif item_name == "script":
        print("💻 Script executed! Massive damage!")
        return "script"

    elif item_name == "script_boost":
        player.damage_boost_turns = 3
        print("⚔ Damage boosted for 3 turns!")
        return None

    else:
        print("❓ Unknown item")
        return None

def process_armor_turn(player):
    """
    Handles turn-based buffs
    """
    if hasattr(player, "armor_turns") and player.armor_turns > 0:
        player.armor_turns -= 1
        if player.armor_turns == 0:
            print("🛡 Armor expired!")

    if hasattr(player, "damage_boost_turns") and player.damage_boost_turns > 0:
        player.damage_boost_turns -= 1
        if player.damage_boost_turns == 0:
            print("⚔ Damage boost expired!")

def modify_damage(player, base_damage):
    """
    Apply armor + damage boost modifiers
    """
    if hasattr(player, "damage_boost_turns") and player.damage_boost_turns > 0:
        base_damage += 10
    return base_damage

# =========================
# BOSS FIGHT SYSTEM
# =========================

def multi_step_attack(enemy, player, questions):
    """
    Returns: (damage_done, message, skip_enemy)
    """
    sequence = BOSS_SEQUENCES.get(enemy.name, [])
    step_index = 0
    damage_done_total = 0

    if not sequence:
        print(f"⚠ No boss sequence defined for {enemy.name}!")
        return 0, f"No sequence for {enemy.name}", False

    print(f"\n🔥 BOSS FIGHT: {enemy.name} 🔥")

    while enemy.hp > 0 and player.hp > 0 and step_index < len(sequence):
        current_step = sequence[step_index]

        possible_questions = [
            q for q in questions
            if enemy.name in q.get("tags", []) and current_step in q.get("tags", [])
        ]

        if not possible_questions:
            print(f"⚠ No boss questions for {enemy.name} step {current_step}!")
            step_index += 1
            continue

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
            from game import use_item
            result = use_item(player)
            if result == "script":
                dmg = 35
                enemy.hp -= dmg
                damage_done_total += dmg
                print(f"💥 Script hit for {dmg} damage!")
                continue
            else:
                continue

        # =========================
        # ANSWER CHECK
        # =========================
        if choice == q["answer"].lower():
            dmg = random.randint(20, 35)
            dmg += apply_weakness(enemy, player, q)
            dmg = modify_damage(player, dmg)
            enemy.hp -= dmg
            damage_done_total += dmg
            print(f"✅ Correct! {dmg} damage")
            step_index += 1
        else:
            dmg = random.randint(10, 18)
            if hasattr(player, "armor_turns") and player.armor_turns > 0:
                dmg = max(0, dmg - 5)
                print("🛡 Armor reduced damage!")
            player.take_damage(dmg)
            print(f"❌ Wrong! Took {dmg} damage")

        process_armor_turn(player)

    if enemy.hp <= 0:
        print(f"\n💀 {enemy.name} defeated!")
        return damage_done_total, "Boss defeated", True

    return damage_done_total, "Boss still alive", False
