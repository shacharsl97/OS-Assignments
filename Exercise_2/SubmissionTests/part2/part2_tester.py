import os
import subprocess
import difflib
import json
import sys
import math

def normalize_line(line):
    return ''.join(line.split()).lower()  # remove all whitespace, lowercase

def compare_lines(expected, actual):
    exp_lines = [normalize_line(l) for l in expected.strip().splitlines()]
    act_lines = [normalize_line(l) for l in actual.strip().splitlines()]
    matched = 0
    total = max(len(exp_lines), len(act_lines))
    for i in range(total):
        if i < len(exp_lines) and i < len(act_lines) and exp_lines[i] == act_lines[i]:
            matched += 1
    return matched, total, exp_lines, act_lines

def diff_lines(exp_lines, act_lines):
    diff_result = []
    max_len = max(len(exp_lines), len(act_lines))
    for i in range(max_len):
        e = exp_lines[i] if i < len(exp_lines) else "<missing>"
        a = act_lines[i] if i < len(act_lines) else "<missing>"
        if e != a:
            diff_result.append(f"Line {i+1}: Expected: '{e}' | Actual: '{a}'")
    return '\n'.join(diff_result)

def run_test(index, test):
    print(f"Running Test {index + 1}")
    sys.stdout.flush()

    with open("data.txt", "w") as f:
        f.write(test["data"])
    with open("requests.txt", "w") as f:
        f.write(test["requests"])

    compile_result = subprocess.run(["gcc", "file_processor.c", "-o", "file_processor"], capture_output=True)
    if compile_result.returncode != 0:
        print("❌ Compilation failed:")
        print(compile_result.stderr.decode())
        return False

    run_result = subprocess.run(["./file_processor", "data.txt", "requests.txt"], capture_output=True)
    if run_result.returncode != 0:
        print("❌ Runtime error:")
        print(run_result.stderr.decode())
        return False

    passed = True

    with open("data.txt") as f:
        actual_data = f.read()
    matched, total, exp_lines, act_lines = compare_lines(test["data_changed"], actual_data)
    if matched != total:
        print(f"❌ data.txt mismatch: {matched}/{total} lines matched")
        print(diff_lines(exp_lines, act_lines))
        passed = False
    else:
        print("✅ data.txt matches")

    try:
        with open("read_results.txt") as f:
            actual_reads = f.read()
    except FileNotFoundError:
        actual_reads = ""

    matched, total, exp_lines, act_lines = compare_lines(test["read_results"], actual_reads)
    if matched != total:
        print(f"❌ read_results.txt mismatch: {matched}/{total} lines matched")
        print(diff_lines(exp_lines, act_lines))
        passed = False
    else:
        print("✅ read_results.txt matches")

    print("✅ Test passed" if passed else "❌ Test failed")
    print("-" * 60)
    sys.stdout.flush()
    return passed

def main():
    print("Starting tests...")
    sys.stdout.flush()
    try:
        with open("file_processing_tests.json", "r") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print("❌ file_processing_tests.json not found.")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return

    total_tests = len(test_cases)
    passed_tests = 0

    for i, test in enumerate(test_cases):
        if run_test(i, test):
            passed_tests += 1
    final_grade = math.ceil((passed_tests / total_tests) * 100)
    print(f"✅ Final Grade: {final_grade}, {passed_tests}/{total_tests} tests passed")

if __name__ == "__main__":
    main()
