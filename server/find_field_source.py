import os

search_dir = r"C:\Users\sahan\Downloads\Support-AI-Ticket-Management-Team\server"
target = "latest_response_id"

found = False
for root, dirs, files in os.walk(search_dir):
    if "venv" in root or ".git" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if target in content:
                    found = True
                    print(f"\nFound in: {path}")
                    # Print lines containing the target
                    for i, line in enumerate(content.splitlines(), start=1):
                        if target in line:
                            print(f"  Line {i}: {line}")
            except Exception as e:
                print(f"Error reading {path}: {e}")

if not found:
    print("Target string not found in any Python files.")
