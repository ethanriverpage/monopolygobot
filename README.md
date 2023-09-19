# Monopoly GO! Bot
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit) [![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Description

Monopoly GO! Bot is a Python script designed to automate actions in the mobile game Monopoly GO!. Please note that it requires the game to be running in the BlueStacks Android emulator.

**This project is for educational and research purposes only. It is not intended to be deployed as a fully functional or production-ready application.**
**Usage of this project in any way that violates the terms of service of Monopoly GO! or any other applicable laws and regulations is strictly prohibited.**
**Please be aware that this project may not be fully functional or optimized for actual gameplay.**

## Features

- Handles gathering game information
- Building (including saving building info to JSON)
- Autorolling (including starting and stopping at set values)
- Modifying the multiplier
- Handling all UI events
- Handling bank heists and shutdowns
- And more...

## Unimplemented Features

- Quick wins and community chests
- Handling game crashes
- Customizing the multiplier set amount

## Known Issues

- The bot may get stuck at some points.
- Due to how BlueStacks works, the script requires administrator privileges to use because it uses DirectInput to interface with the emulator.
- Building may break without an initial `game_data.json` file.
- Accuracy of locating parts of the screen may vary due to differences in hardware setups.

## Environment Variables

1. `WINDOW_TITLE`: The title of your BlueStacks window.
2. `AR_MINIMUM_ROLLS`: The number of rolls you want to stop rolling at.
3. `AR_RESUME_ROLLS`: The number of rolls you want to start rolling at.
   
   All these variables can be defined in a `.env` file.

## Usage

1. Install the required modules using pip:

`pip install -r requirements.txt`

2. On Windows, run the script as an administrator:

`.\start.ps1`

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Credits

[lewisgibson](https://github.com/lewisgibson) for his repository [monopoly-go-bot/](https://github.com/lewisgibson/monopoly-go-bot) which served as the base for this project.

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). You can find the full license text in the [LICENSE](LICENSE) file.
