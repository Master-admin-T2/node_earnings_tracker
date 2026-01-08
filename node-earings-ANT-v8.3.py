import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import requests
import json
import csv
import os
import shutil
from datetime import datetime, timedelta, timezone
from collections import defaultdict

import matplotlib
matplotlib.use("TkAgg")  # ensure Tk backend for PyInstaller
import matplotlib.pyplot as plt
from appdirs import user_data_dir

# ================= CONFIG =================
APP_NAME = "ArbEarningsApp"
DATA_DIR = user_data_dir(APP_NAME)

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
TRANSFERS_FILE = os.path.join(DATA_DIR, "transfers.csv")
# =========================================

os.makedirs(DATA_DIR, exist_ok=True)

# ---------- Utils ----------
def safe_int(value):
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("0x"):
            return int(value, 16)
        return int(value)
    return 0

# ---------- Config ----------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"wallet": "", "token": "", "api_key": ""}

def save_config(wallet, token, api_key=None):
    cfg = {"wallet": wallet, "token": token}
    if api_key:
        cfg["api_key"] = api_key
    else:
        # preserve existing api_key if present
        existing = load_config()
        if "api_key" in existing:
            cfg["api_key"] = existing["api_key"]
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

# ---------- Transfers CSV ----------
def init_transfers_csv():
    if not os.path.exists(TRANSFERS_FILE):
        with open(TRANSFERS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tx_hash",
                "timestamp",
                "date",
                "wallet",
                "token",
                "amount"
            ])

def load_existing_tx_hashes():
    hashes = set()
    if not os.path.exists(TRANSFERS_FILE):
        return hashes
    with open(TRANSFERS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hashes.add(row["tx_hash"])
    return hashes

# ---------- Alchemy Sync ----------
def sync_new_transfers(wallet, token, api_key):
    if not api_key:
        raise ValueError("Alchemy API key missing.")
    alchemy_url = f"https://arb-mainnet.g.alchemy.com/v2/{api_key}"

    existing_hashes = load_existing_tx_hashes()
    new_count = 0
    page_key = None

    while True:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getAssetTransfers",
            "params": [{
                "fromBlock": "0x0",
                "toBlock": "latest",
                "toAddress": wallet,
                "contractAddresses": [token],
                "category": ["erc20"],
                "withMetadata": True,
                "excludeZeroValue": False,
                **({"pageKey": page_key} if page_key else {})
            }]
        }

        r = requests.post(alchemy_url, json=payload, timeout=30)
        r.raise_for_status()
        result = r.json()["result"]

        for tx in result.get("transfers", []):
            tx_hash = tx.get("hash")
            if not tx_hash or tx_hash in existing_hashes:
                continue

            try:
                tx_time = datetime.fromisoformat(
                    tx["metadata"]["blockTimestamp"].replace("Z", "")
                ).replace(tzinfo=timezone.utc)
            except Exception:
                continue

            raw = tx.get("rawContract", {}).get("value")
            dec = tx.get("rawContract", {}).get("decimal")

            value_int = safe_int(raw)
            decimals_int = safe_int(dec)

            if decimals_int <= 0:
                continue

            amount = value_int / (10 ** decimals_int)

            with open(TRANSFERS_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    tx_hash,
                    tx_time.isoformat(),
                    tx_time.date().isoformat(),
                    wallet,
                    token,
                    round(amount, 6)
                ])

            existing_hashes.add(tx_hash)
            new_count += 1

        page_key = result.get("pageKey")
        if not page_key:
            break

    return new_count

# ---------- Token metadata ----------
def get_token_symbol(token_address, api_key):
    if not api_key:
        return token_address[:6]
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getTokenMetadata",
            "params": [token_address]
        }
        r = requests.post(f"https://arb-mainnet.g.alchemy.com/v2/{api_key}", json=payload, timeout=15)
        r.raise_for_status()
        data = r.json().get("result", {})
        return data.get("symbol", token_address[:6])
    except Exception:
        return token_address[:6]  # fallback

# ---------- Stats ----------
def compute_stats(wallet, token):
    now = datetime.now(timezone.utc)
    d24 = d7 = d30 = total = 0.0

    if not os.path.exists(TRANSFERS_FILE):
        return 0, 0, 0, 0, 0

    with open(TRANSFERS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["wallet"] != wallet or row["token"] != token:
                continue

            ts = datetime.fromisoformat(row["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            val = float(row["amount"])
            total += val
            if ts >= now - timedelta(days=1):
                d24 += val
            if ts >= now - timedelta(days=7):
                d7 += val
            if ts >= now - timedelta(days=30):
                d30 += val

    d7_avg = round(d7 / 7 if d7 else 0, 2)
    d30_total = round(d30, 2)
    return round(d24, 2), round(d7, 2), d7_avg, d30_total, round(total, 2)

# ---------- Chart & Export ----------
def plot_chart(wallet, token):
    daily = defaultdict(float)

    if not os.path.exists(TRANSFERS_FILE):
        return

    with open(TRANSFERS_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["wallet"] == wallet and row["token"] == token:
                ts = datetime.fromisoformat(row["timestamp"])
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                daily[row["date"]] += float(row["amount"])

    dates = sorted(daily.keys())[-30:]
    values = [daily[d] for d in dates]

    plt.figure(figsize=(10, 4))
    plt.bar(dates, values)
    plt.xticks(rotation=45, ha="right")
    plt.title("Incoming ERC20 Earnings (Last 30 Days)")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.show()

def export_csv():
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    if path:
        shutil.copy(TRANSFERS_FILE, path)
        messagebox.showinfo("Export", "CSV exported successfully")

# ---------- UI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Arbitrum ERC20 Earnings Tracker")
        self.geometry("600x420")

        init_transfers_csv()
        cfg = load_config()

        # API key prompt if missing
        if not cfg.get("api_key"):
            key = simpledialog.askstring("Alchemy API Key", "Enter your Alchemy API Key:")
            if key:
                cfg["api_key"] = key
                save_config(cfg["wallet"], cfg["token"], key)
            else:
                messagebox.showerror("Error", "API Key is required")
                self.destroy()
                return

        self.api_key = cfg["api_key"]

        tk.Label(self, text="Wallet Address").pack()
        self.wallet_entry = tk.Entry(self, width=62)
        self.wallet_entry.insert(0, cfg.get("wallet",""))
        self.wallet_entry.pack()

        tk.Label(self, text="Token Contract Address").pack()
        self.token_entry = tk.Entry(self, width=62)
        self.token_entry.insert(0, cfg.get("token",""))
        self.token_entry.pack()

        self.output = tk.Label(self, text="", justify="left")
        self.output.pack(pady=10)

        btns = tk.Frame(self)
        btns.pack()

        tk.Button(btns, text="Update", command=self.update_data).pack(side="left", padx=5)
        tk.Button(btns, text="Show Chart", command=self.show_chart).pack(side="left", padx=5)
        tk.Button(btns, text="Export CSV", command=export_csv).pack(side="left", padx=5)

        # Initial sync ONCE at startup
        self.after(500, self.update_data)

    def update_data(self):
        wallet = self.wallet_entry.get().strip()
        token = self.token_entry.get().strip()

        if not wallet or not token:
            messagebox.showerror("Error", "Wallet and token required")
            return

        save_config(wallet, token, self.api_key)

        try:
            new_tx = sync_new_transfers(wallet, token, self.api_key)
            symbol = get_token_symbol(token, self.api_key)
            d24, d7, d7_avg, d30_total, total_earned = compute_stats(wallet, token)

            self.output.config(text=(
                f"Token: {symbol}\n"
                f"New transfers synced: {new_tx}\n"
                f"Incoming last 24h: {d24:.2f}\n"
                f"Incoming last 7d: {d7:.2f}\n"
                f"7d average/day: {d7_avg:.2f}\n"
                f"Incoming last 30d: {d30_total:.2f}\n"
                f"30d average/day: {round(d30_total/30,2):.2f}\n"
                f"Total earnings: {total_earned:.2f}"
            ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_chart(self):
        plot_chart(
            self.wallet_entry.get().strip(),
            self.token_entry.get().strip()
        )

# ---------- Run ----------
if __name__ == "__main__":
    App().mainloop()
