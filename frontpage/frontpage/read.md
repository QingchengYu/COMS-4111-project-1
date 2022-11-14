install pip if needed
    sudo apt-get install python-pip

Install libraries
    pip install click flask sqlalchemy

Edit server.py to set your database URI
    DATABASEURI = "postgresql://hw2846:414526344@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2"

Run it in the shell
    python server.py

Get help:
    python server.py --help