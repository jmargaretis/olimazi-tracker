# Set up Olimazi Tracker on Windows

This guide is for someone who has never used a command window. It uses the fake
`12 Sample Street` example, so you can see the tracker work before adding any of your
own records.

> **What this is NOT**
>
> Olimazi Tracker is a record-keeping organizer, not tax, legal, or accounting advice.
> It does not decide what is deductible or what belongs on your return. Confirm all
> figures with a qualified tax professional before filing. The software is provided
> as-is, without a warranty.

## Part 1 — Install Python

1. Open your web browser and go to
   [python.org/downloads](https://www.python.org/downloads/).
2. Choose the big yellow **Download Python 3** button near the top. (Ignore anything
   about a "Python install manager" — the plain download is what you want.)
3. Open the downloaded installer.
4. Before choosing **Install Now**, select **Add python.exe to PATH** near the bottom
   of the installer window.
5. Finish the installation, then close the installer.

## Part 2 — Download the tracker

1. Open the Olimazi Tracker page on GitHub.
2. Choose the green **Code** button, then **Download ZIP**.
3. Open your Downloads folder.
4. Right-click the downloaded ZIP file, choose **Extract All**, and accept the
   suggested location.
5. Open the extracted `olimazi-tracker` folder. If you used GitHub's **Code** →
   **Download ZIP** instead of the versioned release, open `olimazi-tracker-main`.

## Part 3 — Install the one required helper

1. While viewing the extracted tracker folder, click the folder address at the top of
   File Explorer.
2. Type `powershell` and press Enter. A blue command window should open in that folder.
3. Copy the line below, paste it into the blue window, and press Enter:

   ```powershell
   py -m pip install openpyxl
   ```

4. Wait until the window says the installation succeeded.

## Five-minute smoke test

Keep the blue PowerShell window open and complete these steps in order.

1. Create the fake `12 Sample Street` workbook and source documents:

   ```powershell
   py fixtures\make_fixture.py
   ```

   You should see a message beginning with `Created fake sample fixture`.

2. Run the deterministic reconciliation:

   ```powershell
   py engine\reconcile.py "fixtures\sample-property"
   ```

   The summary should show exactly **one FAIL**. That is intentional: the example
   points to a gardener invoice that does not exist, demonstrating how a broken file
   reference is caught. Warnings are review reminders, not engine crashes.

3. Open the sample dashboard:

   ```powershell
   Start-Process "fixtures\sample-property\SchE_Dashboard.html"
   ```

4. Your normal web browser should open a page titled **Schedule E** for
   **12 Sample Street**. The red **1 BREAK(S)** badge proves the sample check ran.

## What the test created

Everything stays inside `fixtures\sample-property`:

- `sample-tracker.xlsx` — the fake workbook you own.
- `source-docs` — small fake documents referenced by the workbook.
- `SchE_Reconciliation.md` — the plain-English check report.
- `reconciliation.json` — the same results in a machine-readable form.
- `SchE_Dashboard.html` — the dashboard you opened.

You can repeat the smoke test at any time. The generator replaces the fake workbook;
the reconciler replaces the report and dashboard. Neither step sends data anywhere.

## If a command does not work

- If Windows says `py` is not recognized, restart the computer once and try again.
  If it still fails, repeat Part 1 and confirm the PATH option.
- If the workbook is open in Excel, close Excel before repeating the commands.
- If the browser does not open, find `SchE_Dashboard.html` inside
  `fixtures\sample-property` and double-click it.
