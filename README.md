# cli-chess
A command line interface chess game.

## Insallation
1. Check that python3 is installed on your operating system by running
```bash
python3 --version
```
2. Run:
```bash
python3 -m venv .venv
```

3. Activate the created Virtual environment (.venv)

4.  Run:
```bash
python -m pip install -r requirements.txt
```

## Usage

1. To play the default new game:
```bash
python play.py
```

2. To load the last saved game:
```bash
python play.py load
```

3. To use the timer:
```bash
python play.py -t 30
```

4. To disable pausing:
```bash
python play.py -np
```

5. To see the help message:
```bash
python play.py -h
```





## Current Features
- Arbitrary Piece Movement
- Arbitrary Piece Removal
- Arbitrary Piece Setting
- Piece Movement Validation
- Piece Removal Validation
- Board Validation
- Board Resetting
- Board Clearing
- Board Filling
- Messaging
- Timer
- Pausing
- Help
- Game Saving
- Game Loading

## Future Features
- Chess Rules Validation
- PvP
- PvE
- Tournaments
- and many more