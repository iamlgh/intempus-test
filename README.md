# intempus-test

##System B

System B uses a postgreSQL DB running in Docker. The system is designed to be run on a síngle PC, but if you have an existing Docker installation on a server it can be used.

##System B Setup

* Install Python 3 (if not already installed)
* Install Docker (if not already installed)
* Run config.py to setup the Python dependiencies and the DB in Docker
  * Verifies Python 3 and Docker are setup locally
  * Installs the dependencies using pip
  * Sets up environment variables for accessing the DB these variables are local to the command prompt where the DB is run
  * If Docker is installed locally, it sets up a postgreSQL DB that the system will use
  * If Docker is is running on another machine, it prints the Docker commands to run on the remote machine to setup the DB
* Setup up environment variables for accessing the Intempus system

```
Windows:
    set INTEMPUS_APIKEY=<apikey>
    set INTEMPUS_USER=<email>

Linux:
    export INTEMPUS_APIKEY=<apikey>
    export INTEMPUS_USER=<email>
```

## Running System B

After setup is complete, you can run data.py to generate the DB table creation script, CreateProjectsTable.sql. The sql script has alread been created an can be found in data data folder.

```
python3 data.py
```

Once the CreateProjectsTable.sql script has been created, you can run the tests or the system.

There is also a script, update.py, that updates all the values in Intempus based on one of the existing records in my profile (after I saved the initial data of the record to file).

To run the tests run:

```
pytest
```

Run main.py to sync System A and System B. The first time main.py is run, the CreateProjectsTable.sql script will setup the "projects" table in the DB, if the test haven't been run and set this up (or the table was dropped).

```
python3 main.py
```

## Scripts included in the repo, with a brief description
| -------------- | --------------------------------------------- |
| Script         | What it does                                  |
| -------------- | --------------------------------------------- |
| data.py        | Used to generate CreateProjectsTable.sql      |
| extras.py      | Code that I wrote that I didn't end up using  |
| main.py        | The main script to sync System A and System B |
| shared.py      | Contains functions shared across multiple scripts |
| test_main.py   | Tests from "main" functions |
| test_shared.py | Tests from "shared" functions |
| update.py      | Used to test that all the data types were correct in the DB so they could be written to the Intempus system |
