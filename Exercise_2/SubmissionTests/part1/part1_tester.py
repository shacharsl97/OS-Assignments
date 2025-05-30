import json
import os
import subprocess
import math
from pathlib import Path

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def colorize_grade(grade):
    if grade == 100:
        return f"{colors.OKGREEN}{grade}/100{colors.ENDC}"
    elif grade >= 60:
        return f"{colors.WARNING}{grade}/100{colors.ENDC}"
    else:
        return f"{colors.FAIL}{grade}/100{colors.ENDC}"

def simulate_gladiator_logs():
    i = 1
    while True:
        input_filename = f'G{i}.txt'
        output_filename = f'tester{i}.txt'

        if not os.path.exists(input_filename):
            break

        with open(input_filename, 'r') as f:
            line = f.readline().strip()
            if not line:
                i += 1
                continue

            parts = list(map(int, line.split(',')))
            health, attack = parts[0], parts[1]
            opponents = parts[2:]


        opponent_attacks = {}
        for opp in set(opponents):
            with open(f'G{opp}.txt', 'r') as f:
                opp_stats = list(map(int, f.readline().strip().split(',')))
                opponent_attacks[opp] = opp_stats[1]

        pid = os.getpid()
        log_lines = [f"Gladiator process started. {pid}:"]

        current_health = health
        while current_health > 0:
            for opp in opponents:
                damage = opponent_attacks[opp]
                current_health -= damage
                log_lines.append(f"Facing opponent {opp}... Taking {damage} damage")
                if current_health > 0:
                    log_lines.append(f"Are you not entertained? Remaining health: {current_health}")
                else:
                    log_lines.append(f"The gladiator has fallen... Final health: {current_health}")
                    break

        with open(output_filename, 'w') as log_file:
            for line in log_lines:
                log_file.write(line + '\n')

        i += 1
def grade_log_output(expected_file, student_file):
    import re

    def clean_lines(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        cleaned = [
            re.sub(r'\s+', '', line)
            for line in lines if line.strip()
        ]
        return cleaned

    try:
        expected_lines = clean_lines(expected_file)
        student_lines = clean_lines(student_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 0, 0, 0
    
    max_lines = max(len(expected_lines), len(student_lines))
    min_lines = min(len(expected_lines), len(student_lines))
    differences = -1

    for i in range(min_lines):
        if expected_lines[i] != student_lines[i]:
            differences += 1

    differences += abs(len(expected_lines) - len(student_lines))

    if max_lines == 0:
        grade = 100
    else:
        match_percentage = (max_lines - differences) / max_lines
        grade = round(match_percentage * 100)

    return grade, max_lines, differences
def grade_all_files():
    grades = []
    for i in range(1, 5):
        grade, lines, diffs = grade_log_output(f"G{i}_log.txt", f"tester{i}.txt")
        grades.append((i, grade, lines, diffs))
    return grades

def run_test_cases():
    with open('gladiator_tests.json') as f:
        data = json.load(f)

    test_case_grades = []

    for test_index, case in enumerate(data["test_cases"], start=1):
        print(f"{'-'*60}")
        print(f"{colors.BOLD}{colors.OKBLUE}{'Running Test Case ' + str(test_index) + ': ' + case['name']}{colors.ENDC}")
        print(f"{'-'*60}")

        for filename, content in case['inputs'].items():
            with open(filename, 'w') as f:
                f.write(content.strip())

        try:
            subprocess.run(["gcc", "tournament.c", "-o", "tournament"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["gcc", "gladiator.c", "-o", "gladiator"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("❌ Compilation failed.")
            continue
        
        for i in range(1, 5):
            log_file = Path(f"G{i}_log.txt")
            if log_file.exists():
                log_file.unlink()
            log_file.touch()

        try:
            subprocess.run(["./tournament"], timeout=10, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            print("❌ Tournament timed out.")
            continue
        except subprocess.CalledProcessError:
            print("❌ Tournament exited with error.")
            continue

        simulate_gladiator_logs()
        grades = grade_all_files()
        test_case_avg = sum(g[1] for g in grades) / len(grades)
        test_case_grades.append(test_case_avg)

        for i, grade, lines, diffs in grades:
            print(f"  [G{i}_log.txt] Lines compared: {lines} | Different: {diffs} | Grade: {colorize_grade(grade)}")

        print(f"  --> Test Case Grade: {colors.BOLD}{test_case_avg:.1f}/100{colors.ENDC}")
        print("="*60)

    print(f"{'-'*60}")
    print(f"{colors.BOLD}Final Summary{colors.ENDC}")
    for i, avg in enumerate(test_case_grades, 1):
        print(f"  Test Case {i}: {colorize_grade(round(avg))}")
    print(f"{'-'*60}")
    total_avg = sum(test_case_grades) / len(test_case_grades)
    total_avg = math.ceil(total_avg)
    print(f"{colors.BOLD}🏁 Average Grade: {round(total_avg)}/100{colors.ENDC}")
    print(f"{'-'*60}")


run_test_cases()