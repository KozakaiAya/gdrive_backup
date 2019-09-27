import subprocess
import sys

def execute(command, working_dir=None):
    print("Executing:", command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=working_dir)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline().decode(sys.stdout.encoding)
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output