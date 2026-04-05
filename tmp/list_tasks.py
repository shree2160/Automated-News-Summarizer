from transformers.pipelines import SUPPORTED_TASKS

print("\n--- Searching for tasks containing 'summar' ---")
found = False
for task in sorted(SUPPORTED_TASKS.keys()):
    if "summar" in task.lower():
        print(f"FOUND: {task}")
        found = True

if not found:
    print("NO TASKS FOUND CONTAINING 'SUMMAR'")
    print("Listing all available tasks instead:")
    for task in sorted(SUPPORTED_TASKS.keys()):
        print(task)
