README_node-earnings-app

Setup:

1) You need to get an api key from https://www.alchemy.com/

2) When the app starts for the first time you need to provide, api key (the number), token address and address you want to monitor
	Autonomi token contract address: 0xa78d8321B20c4Ef90eCd72f2588AA985A4BDb684

3) All modules should be added with the executables in the packages for the different OS's, if not pip install: 

| Module       | Install Command          | Notes                      |
| ------------ | ------------------------ | -------------------------- |
| `tkinter`    | included with Python     | GUI                        |
| `requests`   | `pip install requests`   | API calls to Alchemy       |
| `matplotlib` | `pip install matplotlib` | Charts                     |
| `appdirs`    | `pip install appdirs`    | Cross-platform data folder |

Optional for packaging to executable

| Module        | Notes                     |                             |
| ------------- | ------------------------- | --------------------------- |
| `pyinstaller` | `pip install pyinstaller` | For creating standalone exe |

4) Where the app stores its data

The app uses appdirs.user_data_dir, which is platform-aware:

Windows:
C:\Users\<username>\AppData\Roaming\ArbEarningsApp\

Linux:
/home/<username>/.local/share/ArbEarningsApp/

macOS:
/Users/<username>/Library/Application Support/ArbEarningsApp/

Files stored:

| File            | Purpose                                                                     |
| --------------- | --------------------------------------------------------------------------- |
| `config.json`   | Stores default wallet and token contract                                    |
| `transfers.csv` | Ledger of all incoming ERC20 transfers (per-transfer, not hourly snapshots) |


Editable Alchemy API key stored in config.json.

