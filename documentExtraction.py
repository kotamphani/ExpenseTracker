import fitz  # PyMuPDF
import re
import pandas as pd

# Open the PDF file
doc = fitz.open("amex.pdf")

# Combine all text lines
all_lines = []
for page in doc:
    all_lines.extend(page.get_text().splitlines())
    
# Step 1: Locate the "New Charges Details" section
start_idx = None
for i, line in enumerate(all_lines):
    if "New Charges Details" in line:
        start_idx = i
        break

if start_idx is None:
    raise ValueError("Could not find 'New Charges Details' section in the PDF.")

# Step 2: Extract everything starting from that point until we hit an unrelated section
transactions = []
i = start_idx + 1
while i < len(all_lines):
    line = all_lines[i].strip()
    # Detect a transaction starting line (starts with a date)
    if re.match(r"^\d{2}/\d{2}/\d{2}\b", line):
        date = line
        description_lines = []
        j = i + 1
        while j < len(all_lines):
            next_line = all_lines[j].strip()
            if re.match(r"^\$[0-9]+\.[0-9]{2}$", next_line):
                amount = next_line
                break
            else:
                description_lines.append(next_line)
            j += 1
        full_description = " ".join(description_lines)
        transactions.append([date, full_description, amount])
        i = j  # move past amount
    else:
        # Stop parsing if we hit a new section (like "Fees", "Interest", etc.)
        if re.search(r"^(Fees|Interest Charged|Payments|Credits|Total)", line):
            break
        i += 1
# Step 3: Create DataFrame
df = pd.DataFrame(transactions, columns=["Date", "Description", "Amount"])
print(df)