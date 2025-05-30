import os
import json
import shutil
import subprocess
import math

def mkdir_for(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def apply_create_block(create):
    for path in create.get("dirs", []):
        os.makedirs(path, exist_ok=True)

    for path, content in create.get("files", {}).items():
        mkdir_for(path)
        with open(path, "w") as f:
            f.write(content)

    for link_path, target in create.get("symlinks", {}).items():
        mkdir_for(link_path)
        try:
            os.symlink(target, link_path)
        except FileExistsError:
            pass

def compile_backup():
    if not os.path.exists("backup.c"):
        print("❌ Error: backup.c not found")
        return False
    result = subprocess.run(["gcc", "-o", "backup", "backup.c"])
    if result.returncode != 0:
        print("❌ Compilation failed")
        return False
    return True

def clean_all_paths(test_cases):
    for case in test_cases:
        shutil.rmtree(case["src"], ignore_errors=True)
        shutil.rmtree(case["dst"], ignore_errors=True)

def run_test_case(case):
    shutil.rmtree(case["src"], ignore_errors=True)
    shutil.rmtree(case["dst"], ignore_errors=True)

    apply_create_block(case.get("create", {}))

    subprocess.run(["./backup", case["src"], case["dst"]],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    missing = []
    content_mismatches = []
    symlink_mismatches = []
    j = 0
    for path in case["expected"]:
        if not os.path.lexists(path):
            missing.append(path)
            continue

        expected_src = path.replace(case["dst"], case["src"], 1)

        if os.path.islink(path):
            expected_target = os.readlink(expected_src)
            actual_target = os.readlink(path)
            if expected_target != actual_target:
                symlink_mismatches.append((path, expected_target, actual_target))
        elif os.path.isfile(path):
            with open(expected_src, "r") as f1, open(path, "r") as f2:
                if f1.read() != f2.read():
                    content_mismatches.append(path)

    if missing or content_mismatches or symlink_mismatches:
        if missing:
            print(f"❌ {case['name']}: Missing {', '.join(missing)}")
        if content_mismatches:
            print(f"❌ {case['name']}: Content mismatch in {', '.join(content_mismatches)}")
        for path, expected, actual in symlink_mismatches:
            print(f"❌ {case['name']}: Symlink {path} -> '{actual}' (expected '{expected}')")
        print()
        return False
    else:
        print(f"✅ {case['name']} passed")
        return True
def main():
    if not compile_backup():
        return

    with open("part3_test_cases.json") as f:
        test_cases = json.load(f)

    total = len(test_cases)
    passed = 0

    for case in test_cases:
        if run_test_case(case):
            passed += 1
    final_grade = math.ceil((passed / total) * 100)
    print(f"Final Grade: {final_grade}, tests passed: {passed}/{total}")

    # put this line in comment if u want to see the input/output file :)
    clean_all_paths(test_cases)

if __name__ == "__main__":
    main()
