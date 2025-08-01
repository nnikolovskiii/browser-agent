import subprocess
import os


class InteractiveCMDExecutor:
    def __init__(self, initial_dir="/home/nnikolovskii"):
        self.current_dir = initial_dir or os.getcwd()

    def execute(self, command: str):
        """
        Executes a command like in CMD, supports 'cd' to change directory.
        """
        command = command.strip()
        if not command:
            return "", ""

        # Handle 'cd' internally
        if command.lower().startswith("cd "):
            path = command[3:].strip()
            new_dir = os.path.normpath(os.path.join(self.current_dir, path))
            if os.path.isdir(new_dir):
                self.current_dir = new_dir
                return f"Changed directory to: {self.current_dir}", ""
            else:
                return "", f"The system cannot find the path specified: {new_dir}"

        # Run other commands using subprocess
        try:
            output = ""

            result = subprocess.run(
                command,
                cwd=self.current_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            if not output:
                output = "Command executed successfully with no output."

            return output.strip()
        except Exception as e:
            return f"An error occurred while executing the command: {e}"

bash_executor = InteractiveCMDExecutor()