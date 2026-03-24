# enhancements.py
import random

# Define which enemies are bosses
def is_boss(enemy_name):
    return enemy_name in ["APT Hacker", "Ransomware"]

# Multi-step sequences for bosses
BOSS_SEQUENCES = {
    "APT Hacker": ["tcpdump", "wireshark", "hydra"],
    "Ransomware": ["python script", "chmod exploit", "rm payload"]
}

# Handle boss attack sequence
def multi_step_attack(player, enemy, questions):
    sequence = BOSS_SEQUENCES.get(enemy.name, [])
    step_index = 0

    while enemy.hp > 0 and player.hp > 0:
        q = next((q for q in questions if sequence and sequence[step_index] in q['tags']), None)
        if not q:
            break  # no questions left for this step

        print(f"💻 Boss Challenge Step {step_index+1}: {q['question']}")
        options = q.get("options", [q["answer"]])
        random.shuffle(options)
        print("Options:")
        for opt in options[:4]:
            print(f"• {opt}")

        choice = input("(i) Use item | Type command > ").strip().lower()
        if choice == "i":
            # Use item (from game.py)
            from game import use_item
            result = use_item(player)
            if result == "skip":
                enemy.hp -= 25
                continue
        else:
            correct = choice == q["answer"].lower()
            if correct:
                dmg = random.randint(20, 40)
                print(f"✅ Correct! {dmg} damage")
                enemy.hp -= dmg
                step_index += 1  # next step
            else:
                dmg = random.randint(10, 20)
                print(f"❌ Wrong! Took {dmg} damage")
                player.take_damage(dmg)

        if step_index >= len(sequence):
            break  # boss defeated sequence completed

    return enemy.hp <= 0
