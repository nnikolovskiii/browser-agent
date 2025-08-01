import os
from pathlib import Path
from agent.tools.diff_utils import apply_diff_changes, create_diff

def test_apply_diff_changes():
    """
    Test the apply_diff_changes function with a sample diff.
    """
    # Create a temporary test file
    test_file = "test_diff_file.txt"
    with open(test_file, "w") as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

    # Create a sample diff
    diff_content = """--- test_diff_file.txt
+++ test_diff_file.txt
@@ -1,5 +1,6 @@
 Line 1
-Line 2
+Line 2 (modified)
+New line added
 Line 3
 Line 4
 Line 5
"""

    # Apply the diff changes
    print(f"Applying diff changes to {test_file}...")
    result = apply_diff_changes(test_file, diff_content)

    if result:
        print("Changes applied successfully!")

        # Read and print the modified file
        with open(test_file, "r") as f:
            modified_content = f.read()

        print("\nModified file content:")
        print(modified_content)
    else:
        print("Failed to apply changes.")

    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

def test_create_diff():
    """
    Test the create_diff function by comparing two files.
    """
    # Create original file
    original_file = "original.txt"
    with open(original_file, "w") as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

    # Create modified file
    modified_file = "modified.txt"
    with open(modified_file, "w") as f:
        f.write("Line 1\nLine 2 (modified)\nNew line added\nLine 3\nLine 4\nLine 5\n")

    # Create diff between the files
    print(f"\nCreating diff between {original_file} and {modified_file}...")
    diff_content = create_diff(original_file, modified_file)

    print("\nGenerated diff:")
    print(diff_content)

    # Clean up
    if os.path.exists(original_file):
        os.remove(original_file)
    if os.path.exists(modified_file):
        os.remove(modified_file)

if __name__ == "__main__":
    print("Testing diff utilities...")
    test_apply_diff_changes()
    test_create_diff()
    print("\nAll tests completed.")
