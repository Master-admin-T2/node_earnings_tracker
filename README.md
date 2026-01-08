# Arbitrum ERC20 Earnings Tracker

[cite_start]This application monitors incoming ERC20 transfers (e.g., Autonomi tokens) on the Arbitrum network using the Alchemy API[cite: 1, 18].

## 🛠 Setup & Configuration

1.  [cite_start]**Get an API Key:** You need to obtain a free API key from [Alchemy](https://www.alchemy.com/)[cite: 1, 19].
2.  **Initial Launch:** When starting the app for the first time, you will be prompted to provide:
    * [cite_start]**Alchemy API Key**[cite: 1].
    * [cite_start]**Wallet Address:** The address you wish to monitor[cite: 1].
    * [cite_start]**Token Contract Address:** The address of the token you want to track[cite: 1].
        * [cite_start]*Example (Autonomi):* `0xa78d8321B20c4Ef90eCd72f2588AA985A4BDb684`[cite: 1].

---

## How to Run the App

The app is provided as a standalone executable. You do not need to install Python or any libraries to run the files from the **Releases** section.

### Windows
1.  Download `NodeEarningsTracker.exe`.
2.  Double-click the file to launch.
3.  If Windows Defender shows a warning ("Unknown Publisher"), click **"More info"** and then **"Run anyway"**.

### Linux
1.  Download `NodeEarningsTracker-Linux`.
2.  Open a terminal and make the file executable:
    ```bash
    chmod +x NodeEarningsTracker-Linux
    ```
3.  Run the app:
    ```bash
    ./NodeEarningsTracker-Linux
    ```

### macOS
1.  Download and extract `NodeEarningsTracker-Mac.zip`.
2.  **Note:** Since the app is not signed by Apple, you cannot simply double-click it. **Right-click** (or Ctrl+Click) the app and select **Open**.
3.  In the dialog that appears, click **Open** again.

---

## Data Storage
[cite_start]The app stores your settings and transaction history locally on your computer using platform-aware folders[cite: 13]:

* [cite_start]**Windows:** `C:\Users\<username>\AppData\Roaming\ArbEarningsApp\` [cite: 13]
* [cite_start]**Linux:** `/home/<username>/.local/share/ArbEarningsApp/` [cite: 13]
* [cite_start]**macOS:** `/Users/<username>/Library/Application Support/ArbEarningsApp/` [cite: 13]

**Files created:**
* [cite_start]`config.json`: Stores your default wallet and token contract[cite: 16, 17].
* [cite_start]`transfers.csv`: A ledger of all incoming ERC20 transfers[cite: 16, 18].

---

## For Developers (Running from Source)
If you wish to run the `.py` file directly, the following modules are required:

| Module | Install Command | Purpose |
| :--- | :--- | :--- |
| `tkinter` | Included with Python | [cite_start]GUI [cite: 4, 5] |
| `requests` | `pip install requests` | [cite_start]API calls to Alchemy [cite: 6, 7] |
| `matplotlib` | `pip install matplotlib` | [cite_start]Charts [cite: 2, 8] |
| `appdirs` | `pip install appdirs` | [cite_start]Cross-platform data folder management [cite: 9] |
| `pyinstaller` | `pip install pyinstaller` | [cite_start]For creating standalone executables [cite: 12] |
