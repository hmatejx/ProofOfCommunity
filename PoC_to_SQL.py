import json
import glob
from pathlib import Path
import pymysql
from alive_progress import alive_bar
import re


# should the upload to the DB be forced from scratch
__FORCE_FILE_RESCAN = True
# how often should the DB commit, i.e. every 1000 records updated
__COMMIT_EVERY = 1000


# global variables for DB connection
connection = None
cursor = None


# get the list of CSV files to process
def get_files_to_process(folder):
    files = glob.glob(folder + "/*.csv")

    return files


# connect to the MySQL DB
def connect_db():
    global connection
    global cursor

    connection = pymysql.connect(
        host = "192.168.1.40",
        user = "test",
        password = "test",
        port = 3306,
        db = "Celsius"
    )
    cursor = connection.cursor()


# close the DB connection
def close_db():
    cursor.execute("COMMIT")
    connection.close()


# get the date of the first interest transaction in the CSV file
def get_reward_date(filename):
    date = None

    with open(filename, "r") as file:
        # skip header
        file.readline()

        # read transactions until the first interest payment
        while True:
            line = file.readline()

            # we hit end of file
            if not line:
                break

            _, details = line.split(",", 1)
            details = json.loads(details)

            # check if file is version 1
            version = details.get("version")
            if version is not None:
                details = details.get("data")

            # loop over all coins in the record
            for item in details:
                if version is not None:
                    coin = item.get("originalInterestCoin")
                    coindata = item
                else:
                    coin = item
                    coindata = details.get(coin)
                distdata = coindata.get("distributionData")
                for item in distdata:
                    type = item.get("type")
                    # we found an interest transaction!
                    if type == "interest":
                        date = item.get("date").replace("T", " ")
                        date = re.sub("\.[0-9]+Z", "", date)
                        break

                # break for
                if date is not None:
                    break

            # break while
            if date is not None:
                break

    return date


# check if the file name already exists in the Files table
def check_file_processed(name):
    cursor.execute("SELECT IdFiles from Files where Filename=%s", name)
    ret = cursor.fetchone()
    return ret is not None


# insert the file name into the Files table
def insert_file(name, date):
    cursor.execute("INSERT INTO Files(Filename,Date) VALUES(%s, %s) ON DUPLICATE KEY UPDATE IdFiles=IdFiles", (name, date))
    cursor.execute("Commit")


# get the id for the file name from the Files table
def get_fileid(name):
    cursor.execute("SELECT IdFiles from Files where Filename=%s", name)
    return cursor.fetchone()[0]


# scan the file to get the number of records contained
def get_num_records(filename):
    lines = 0
    with open(filename, 'r') as fp:
        for lines, line in enumerate(fp):
            pass
    return lines


# get the set of existing transactions for a certain file id
def get_transactions(fileid):
    cursor.execute("SELECT TxId from Rewards LEFT JOIN Files ON Rewards.IdFiles=Files.IdFiles where Rewards.IdFiles=%s", fileid)
    return set([TxId[0] for TxId in cursor.fetchall()])


# main workhorse function that processes all transactions
def process_records(filename, name):

    # get the current file Id in the Files table (used as foreign key)
    fileId = get_fileid(name)

    # get the number of records in the file
    lines = get_num_records(filename)
    print("\t\t{} lines...".format(lines), flush=True)

    # and get the set of already uploaded transactions for the file
    existingTxIds = get_transactions(fileId)

    # loop over all lines in the CSV file
    with open(filename, 'r') as file:
        with alive_bar(lines, length = 48) as bar:
            # skip header
            line = file.readline()

            txcount = 0
            while True:
                # Get a line from file
                line = file.readline()

                # we hit end of file
                if not line:
                    break

                # get a TxId record
                txid, details = line.split(",", 1)

                # skip already uplodaded transactions
                if txid in existingTxIds:
                    bar()
                    continue

                # parse the transaction record
                txcount += 1
                details = json.loads(details)

                # check if file is version 1
                version = details.get("version")
                if version is not None:
                    details = details.get("data")

                # loop over all coins in the record
                for item in details:
                    if version is not None:
                        coin = item.get("originalInterestCoin")
                        coindata = item
                    else:
                        coin = item
                        coindata = details.get(coin)
                    interestUSD = float(coindata.get("totalInterestInUsd"))
                    interest = float(coindata.get("totalInterestInCoin"))
                    earnInCel = 1 if coindata.get("earningInterestInCel") else 0
                    interestCoin = 'CEL' if earnInCel else coin
                    tier = coindata.get("loyaltyTier").get("level")
                    distdata = coindata.get("distributionData")
                    balance = None
                    # check what was the initial balance
                    for item in distdata:
                        type = item.get("type")
                        if type == "initialBalance":
                            balance = float(item.get("value"))
                            break
                    # there was no initial balance, check if a deposit was made
                    if balance is None:
                        for item in distdata:
                            if type == "deposit":
                                balance = float(item.get("newBalance"))
                                break

                    if balance is not None:
                        cursor.execute("INSERT INTO Rewards(TxId,Coin,InitialAmount,InterestCoin," +
                                    "InterestInCoin,InterestInUsd,EarningInCel,Tier,IdFiles) " +
                                    "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE TxId=TxId",
                                    (txid, coin, balance, interestCoin, interest, interestUSD, earnInCel, tier, fileId))

                    #if balance is None:
                    #    print(details)
                    #    exit()

                # commit for TxId
                if txcount % __COMMIT_EVERY == 0:
                    cursor.execute("Commit")

                # update progress bar
                bar()

    # commit remaining data
    cursor.execute("Commit")


if __name__ == "__main__":
    connect_db()

    # get list of Celisus reward CSV files
    files = get_files_to_process("data")

    # go over all files
    for i in range(0, len(files)):

        filename = files[i]
        name = Path(filename).stem
        print("Processing file {}... ({}/{})".format(name, i + 1, len(files)), end='', flush=True)

        if check_file_processed(name) and not __FORCE_FILE_RESCAN:
            print("\t\tskipping!")
            continue

        date = get_reward_date(filename)
        insert_file(name, date)
        process_records(filename, name)

    close_db()
