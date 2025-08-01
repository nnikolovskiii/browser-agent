import os
from agent.file_utils import concat_folder_to_file

def test_concat_folder():
    # Define test folder path - using the 'data' directory which should exist
    test_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    # Define output file path
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_output.txt')

    # Make sure the output file doesn't exist before the test
    if os.path.exists(output_file):
        os.remove(output_file)

    # Call the function with the test folder
    result = concat_folder_to_file(
        test_folder, 
        output_file, 
        ignore_patterns=set(),  # No ignore patterns for test
        binary_extensions={'.ogg', '.mp3', '.mp4', '.wav', '.zip', '.tar', '.gz'}  # Specify binary extensions to skip
    )

    # Check if the function returned True (success)
    print(f"Function returned: {result}")

    # Check if the output file exists
    if os.path.exists(output_file):
        print(f"Output file created: {output_file}")

        # Check file size
        file_size = os.path.getsize(output_file)
        print(f"Output file size: {file_size} bytes")

        # Print first few lines of the file
        with open(output_file, 'r', encoding='utf-8') as f:
            first_lines = ''.join(f.readlines()[:10])
            print(f"First few lines of output file:\n{first_lines}")
    else:
        print("Output file was not created!")

if __name__ == "__main__":
    test_concat_folder()
