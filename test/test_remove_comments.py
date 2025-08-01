import sys
import os
import shutil

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent.tools.file_utils import remove_python_comments

# Path to the test directory
test_dir = os.path.join(os.path.dirname(__file__), 'comment_test')
backup_dir = os.path.join(os.path.dirname(__file__), 'comment_test_backup')

# Create a backup of the test directory
if os.path.exists(backup_dir):
    shutil.rmtree(backup_dir)
shutil.copytree(test_dir, backup_dir)

print(f"Testing remove_python_comments on directory: {test_dir}")

# Print the content of the file before processing
sample_file = os.path.join(test_dir, 'sample.py')
print("\nBEFORE PROCESSING:")
with open(sample_file, 'r') as f:
    print(f.read())

# Run the function with clean_empty_lines=True (default)
print("\n=== TEST 1: With clean_empty_lines=True (default) ===")
processed, errors = remove_python_comments(test_dir)
print(f"Processed {processed} files with {errors} errors")

# Print the content of the file after processing
print("\nAFTER PROCESSING (clean_empty_lines=True):")
with open(sample_file, 'r') as f:
    print(f.read())

# Restore the original file from backup
shutil.copy(os.path.join(backup_dir, 'sample.py'), sample_file)

# Run the function with clean_empty_lines=False
print("\n=== TEST 2: With clean_empty_lines=False ===")
processed, errors = remove_python_comments(test_dir, clean_empty_lines=False)
print(f"Processed {processed} files with {errors} errors")

# Print the content of the file after processing
print("\nAFTER PROCESSING (clean_empty_lines=False):")
with open(sample_file, 'r') as f:
    print(f.read())
