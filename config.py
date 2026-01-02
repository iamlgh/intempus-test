import os
import platform
import re
import subprocess

def main():
    #verify docker and pip are installed
    #docker --version
    isDockerLocal = True
    r = subprocess.run(["docker", "--version"], stdout=subprocess.PIPE)
    out = r.stdout.decode('utf-8').strip("\\r\\n")
    if not re.search("^Docker version ", out):
        isDockerLocal = False

    #pip --version
    hasPip = True
    r = subprocess.run(["pip", "--version"], stdout=subprocess.PIPE)
    out = r.stdout.decode('utf-8').strip("\\r\\n")
    if not re.search("^pip \\d+\\.\\d+", out):
        hasPip = False

    #verify python requirements were installed from PyPi
    failedDeps = []
    if hasPip:
        #pip show requests
        r = subprocess.run(["pip", "show", "requests"], stdout=subprocess.PIPE)
        out = r.stdout.decode('utf-8').strip("\\r\\n")
        if not re.search("^Name: requests", out):
            failedDeps.append("requests")

        #pip show psycopg2
        r = subprocess.run(["pip", "show", "psycopg2"], stdout=subprocess.PIPE)
        out = r.stdout.decode('utf-8').strip("\\r\\n")
        if not re.search("^Name: psycopg2", out):
            failedDeps.append("psycopg2")

        #pip show pytest
        r = subprocess.run(["pip", "show", "pytest"], stdout=subprocess.PIPE)
        out = r.stdout.decode('utf-8').strip("\\r\\n")
        if not re.search("^Name: pytest", out):
            failedDeps.append("pytest")
    elif isDockerLocal:
        print("""You don't have pip installed, but you do have Docker installed locally, do 
you want to continue with the Docker DB setup? [Y/n] """, end="")
        cont = input()
        if not (cont == "" or cont.lower() == "y" or cont.lower() == "yes"):
            raise SystemExit("Goodbye!")
    else:
        print("""You don't have pip or Docker installed locally, do want to configure the
Environment variable setup? [Y/n] """, end="")
        cont = input()
        if not (cont == "" or cont.lower() == "y" or cont.lower() == "yes"):
            raise SystemExit(f"""You don't have pip or Docker installed locally, and you have chosen
not to run the setup of the environment. Goodbye!""")
    if hasPip and failedDeps:
        print("Dependencies not installed:", failedDeps)
        print(f"Should I install them with pip (e.g. pip install {failedDeps[0]})? [Y/n] ", end="")
        install = input()
        if install == "" or install.lower() == "y" or install.lower() == "yes":
            print("Installing dependencies, this may take a while")
            for package in failedDeps:
                r = subprocess.run(["pip", "install", package], stdout=subprocess.PIPE)
                out = r.stdout.decode('utf-8').strip("\\r\\n")
                print(out)
        else:
            if not (install.lower() == "n" or install.lower() == "no"):
                print(f"Your input, '{install}', is not recognized")
            raise SystemExit(f"""Please install the failed dependencies and run config.py again:
{failedDeps}""")

    #must enter test or dev (test to setup db for automated tests) <dbtype>
    print("Do you want to setup the DB/environment for dev or test? [D/t] ", end="")
    dbtype = "dev"
    
    #set environment variables (host,port,db,user,password,apikey)
    #host
    print("Please specify the host for the db: [localhost] ", end="")
    host = input()
    if not host:
        host = "localhost"
    print(f'Host "{host}" selected')
    print()
    #port
    if dbtype == "dev":
       port = 5432
    if dbtype == "test":
       port = 54321
    print(f"Please specify the port for the db: [{port}] ", end="")
    inputport = input()
    if inputport:
        port = inputport
    print(f'Port "{port}" selected')
    print()
    #db
    print("Please specify the db name: [systemb] ", end="")
    db = input()
    if not db:
        db = "systemb"
    print(f'DB "{db}" selected')
    print()
    #user
    print("Please specify the user name: [postgres] ", end="")
    user = input()
    if not user:
        user = "postgres"
    print(f'User "{user}" selected')
    print()
    #password
    print("Please specify the password name: [postgres] ", end="")
    passwd = input()
    if not passwd:
        passwd = "postgres"
    print(f'Password "{passwd}" selected')
    print()

    #set environment variables
    #get os
    curOs = platform.system()
    if (curOs == "Windows"):
        os.system(f"set POSTGRES_PASSWORD={passwd}")
        os.system(f"set POSTGRES_USER={user}")
        os.system(f"set POSTGRES_DB={db}")
        os.system(f"set POSTGRES_PORT={port}")
    elif (curOs == "Linux"):
        os.system(f"export POSTGRES_PASSWORD={passwd}")
        os.system(f"export POSTGRES_USER={user}")
        os.system(f"export POSTGRES_DB={db}")
        os.system(f"export POSTGRES_PORT={port}")
    else:
        print(f"""Setup the following environment variables on your system:
    POSTGRES_PASSWORD={passwd}
    POSTGRES_USER={user}
    POSTGRES_DB={db}
    POSTGRES_PORT={db}""")
        if host != "localhost":
            print(f"    POSTGRES_HOST={host}")

    if host != "localhost" or not isDockerLocal:
        print("WARNING: not able to setup Docker, it was not found locally!")
        print("You can run the following commands on your remote host (e.g. using ssh) to setup the db")
        print("docker pull postgres")
        print(f"docker run --name postgres-{dbtype} -e POSTGRES_PASSWORD={passwd} -e POSTGRES_USER={user} -e POSTGRES_DB={db} -p {port}:5432 -d postgres")
        raise SystemExit("Goodbye!")

    print("Setting up Docker")
    #docker image ls postgres
    r = subprocess.run(["docker", "image", "ls", "postgres"], stdout=subprocess.PIPE)
    out = r.stdout.decode('utf-8') #.strip("\\r\\n")
    if not re.search("\\npostgres", out):
        print("Pulling latest postgres Docker image, this may take a while")
        #run "docker pull postgres" to pull the latest postgres docker image
        r = subprocess.run(["docker", "pull", "postgres"], stdout=subprocess.PIPE)
        out = r.stdout.decode('utf-8') #.strip("\\r\\n")
        print(out)

    #docker container ls
    srchcmd = "grep"
    srchval = f"postgres-{dbtype}"
    if curOs == "Windows":
        srchcmd = "find"
        srchval = '"' + f"postgres-{dbtype}" + '"'
    r = subprocess.check_output(f"docker container ls -a | {srchcmd} {srchval}", shell=True, text=True)
    if not re.search(f"postgres-{dbtype}", r):
        print("Setting up and running Docker container")
        r = subprocess.run(["docker", "run", "--name", f"postgres-{dbtype}", "-e", f"POSTGRES_PASSWORD={passwd}", "-e", f"POSTGRES_USER={user}", "-e", f"POSTGRES_DB={db}", "-p", f"{port}:5432", "-d", "postgres"], stdout=subprocess.PIPE)
        out = r.stdout.decode('utf-8') #.strip("\\r\\n")
        print(out)
    else:
        r = subprocess.run(["docker", "container", "ls"], stdout=subprocess.PIPE)
        out = r.stdout.decode('utf-8') #.strip("\\r\\n")
        if re.search(f"{port}->5432/tcp\\s+postgres-{dbtype}", out):
            print("Docker container is running")
        else:
            print(f"The postgres-{dbtype} Docker container exists, but is not running, please start it!")
    return

if __name__ == "__main__":
    main()