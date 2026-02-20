import os
import subprocess

class ActionBus:
    def __init__(self, workspace_dir: str = "./workspace"):
        """Initializes the isolated sandbox directory."""
        self.workspace_dir = os.path.abspath(workspace_dir)
        os.makedirs(self.workspace_dir, exist_ok=True)

    def _is_safe_path(self, target_path: str) -> bool:
        """
        Deterministically verifies the target path remains within the sandbox boundary.
        Prevents LLMs from exploiting '../' traversal.
        """
        resolved_path = os.path.abspath(os.path.join(self.workspace_dir, target_path))
        return os.path.commonpath([self.workspace_dir, resolved_path]) == self.workspace_dir

    def write_file(self, filename: str, content: str) -> str:
        if not self._is_safe_path(filename):
            return "ERROR: Path traversal detected. Access Denied."
            
        # Hard boundary: Agents cannot rewrite their own configuration memory directly
        if filename.endswith('.yaml') or filename.endswith('.env'):
            return "ERROR: System configuration files are read-only to the agent plane."
        
        target = os.path.abspath(os.path.join(self.workspace_dir, filename))
        with open(target, 'w') as f:
            f.write(content)
        return f"SUCCESS: Safely wrote {filename}"

    def execute_bash(self, command: str) -> str:
        """
        Executes a command within the sandbox. 
        Note: This is a weak sandbox. Production requires microVMs.
        """
        if ".." in command or "cd " in command:
             return "ERROR: Navigation commands are blocked for security."
             
        try:
            result = subprocess.run(
                command, 
                cwd=self.workspace_dir, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            if result.returncode != 0:
                return f"EXECUTION FAILED:\n{result.stderr}"
            return f"EXECUTION SUCCESS:\n{result.stdout}"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 15 seconds."