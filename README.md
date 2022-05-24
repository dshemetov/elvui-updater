# ElvUI Updater

A minimal ElvUI updater script. Put it in your Task Scheduler and forget about
it.

## Usage

Only tested on Windows. Errors are logged to `run.log` in the script's
directory.

```cmd
# Make a venv, activate, install dependencies
py -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt

# Example CLI usage
python run.py "D:/World of Warcraft/"
```

To use in Task Scheduler, add this to a `run.bat` script, and make a task to run
it (set execution directory to the script's directory).

```bat
:: You can use 'where python' in CMD (not PowerShell) to find your actual python,
:: though pyw might work fine.
.\venv\Scripts\activate.bat && pyw .\run.py "D:/World of Warcraft/"
```
