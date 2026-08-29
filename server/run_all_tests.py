import subprocess
import os

test_files = [
    "test_queue.py",
    "test_routing.py",
    "test_severity_pipeline.py",
    "test_sla.py",
    "test_status_transition.py",
    "test_text_search.py",
    "test_vector_search.py",
    "test_hybrid_retrieval.py"
]

python_path = os.path.join("venv", "Scripts", "python.exe")

print("=== RUNNING ALL LOCAL BACKEND TESTS ===")
all_passed = True

# Prepare environment with UTF-8 encoding
custom_env = os.environ.copy()
custom_env["PYTHONIOENCODING"] = "utf-8"

for test_file in test_files:
    print(f"\nRunning {test_file}...")
    res = subprocess.run([python_path, test_file], capture_output=True, text=True, env=custom_env)
    if res.returncode == 0:
        print(f"[PASS] {test_file}")
        # Print output lines
        lines = res.stdout.splitlines()
        for line in lines:
            print(f"  {line}")
    else:
        print(f"[FAIL] {test_file} (Exit Code: {res.returncode})")
        print("--- Stdout ---")
        print(res.stdout)
        print("--- Stderr ---")
        print(res.stderr)
        all_passed = False

if all_passed:
    print("\nAll local backend tests completed successfully!")
else:
    print("\nSome backend tests failed.")
