from csv import DictWriter

def store_table(fn, rows):
    with open(fn, 'w') as csvfile:
        fieldnames = rows[0].keys()
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)