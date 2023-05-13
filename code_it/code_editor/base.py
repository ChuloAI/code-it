import subprocess

from typing import List


class CodeEditorTooling:
    def __init__(self, filename = "persistent_source.py", interpreter = "python3") -> None:
        self.source_code: List[str] = []
        self.filename = filename
        self.interpreter = "python3"
        self.new_code_candidate = ""
    
    def push_new_code_candidate(self, new_code: str):
        self.new_code_candidate = new_code

    def add_code_to_top(self, add_code_input: str):
        new_lines_of_code =  [line for line in add_code_input.split("\n") if line]
        self.source_code = new_lines_of_code + self.source_code
        self.save_code()
        return self.display_code()

    def overwrite_code(self, new_source: str):
        new_lines_of_code =  [line for line in new_source.split("\n") if line]
        self.source_code = new_lines_of_code
        self.save_code()
        return self.display_code() 

    def add_code(self, add_code_input: str):
        new_lines_of_code =  [line for line in add_code_input.split("\n") if line]
        self.source_code.extend(new_lines_of_code)
        self.save_code()
        return self.display_code() 

    def change_code_line(self, change_code_line_input: str):
        s = change_code_line_input.split("\n")
        line = int(s[0]) - 1
        code = s[1]
        self.source_code[line] = code
        self.save_code()
        return self.display_code() 

    def delete_code_lines(self, delete_code_lines_input: str):
        lines_to_delete = [int(x) for x in delete_code_lines_input.split(",")]
        lines_to_delete.sort()
        lines_to_delete.reverse()

        for line in lines_to_delete:
            idx = line -1
            self.source_code.pop(idx)
        self.save_code()
        return self.display_code() 


    def save_code(self, *args, **kwargs):
        with open(self.filename, "w") as fp:
            fp.write("\n".join(self.source_code))

    def run_code(self, *args, **kwargs):
        completed_process = subprocess.run([self.interpreter, self.filename], capture_output=True, timeout=10)

        print(completed_process, completed_process.stderr)
        succeeded = "Succeeded" if completed_process.returncode == 0 else "Failed"
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        return f"Program {succeeded}\nStdout:{stdout}\nStderr:{stderr}"
        
    def display_code(self):
        code_string = "\n"
        for idx, line in enumerate(self.source_code):
            code_string += f"{line}\n"
        return code_string

