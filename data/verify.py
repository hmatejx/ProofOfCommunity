import hashlib
import glob
import csv

# get file SHA1 hash
def get_file_sha1(filename):
    h  = hashlib.sha1()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

# get the expected hash values
with open('hashes.txt', mode = 'r') as infile:
    reader = csv.reader(infile)
    next(reader, None)
    hashdict = {rows[1][44:]:rows[2] for rows in reader}

# get the list of CSV files to process
csvfiles = [csv for csv in glob.glob("*.csv") if len(csv) == 40]

# check the hash of each file
print("File\t\t\t\t\t  Hash\t\t\t\t\t   Expected\t\t\t\t\t    OK")
print("------------------------------------------------------------------------------------------------------------------------------")
for csv in csvfiles:
    hash = get_file_sha1(csv)
    exphash = hashdict[csv][2:]
    print("{}  {} {} {}".format(csv, hash, exphash, "✓" if hash == exphash else "×"))
    exit()
