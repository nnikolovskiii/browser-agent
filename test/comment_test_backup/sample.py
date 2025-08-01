# This is a comment at the beginning of the file
import os
import sys  # This is an inline comment

"""
This is a docstring that should be preserved.
It contains multiple lines and # characters that should not be removed.
"""

def hello_world():
    """This is a function docstring that should be preserved."""
    # This comment should be removed
    print("Hello, World!")  # This inline comment should be removed
    
    # Multiple comments
    # should all be removed
    
    # Comment with a "string" inside it
    
    text = "This is a string with a # character that should be preserved"
    
    '''This is another type of docstring'''
    
    return "Done"  # Final comment

# Comment at the end of the file