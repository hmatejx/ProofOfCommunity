import subprocess
import glob

# make sure to run this in the data subfolder

# define path to the 7-zip executable that is compiled with support for Zstandard (zstd)
zstd = "C:/Program Files/7-Zip-Zstandard/7z.exe"

# get the list of CSV files to process
csvfiles = glob.glob("*.csv.7z")

# compress all files
for file in csvfiles:
    print("Compressing file {}...".format(file))
    subprocess.call([zstd, "e", file])

