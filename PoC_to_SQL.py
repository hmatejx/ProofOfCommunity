import hashlib
import json
import glob
import re
from pathlib import Path
from decimal import Decimal
from typing import Text
import pymysql
from alive_progress import alive_bar


# should the upload to the DB be forced from scratch
__FORCE_FILE_RESCAN = True
# in case a file rescan is required, should existing tx records be overwritten
__OVERWRITE_EXISTING = False
# how often should the DB commit, i.e. every 1000 records updated
__COMMIT_EVERY = 2000


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
    cursor.execute("SET sql_log_bin = OFF")


# close the DB connection
def close_db():
    cursor.execute("COMMIT")
    cursor.execute("SET sql_log_bin = ON")
    connection.close()


# get file SHA1 hash
def get_file_sha1(filename):
    h  = hashlib.sha1()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


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
    cursor.execute("SELECT fileId from Files where filename=%s", name)
    ret = cursor.fetchone()
    return ret is not None


# get file version
def get_version(filename):

    with open(filename, "r") as file:
        # skip header and read the first transaction
        file.readline()
        line = file.readline()
        # extract version info
        _, txinfo = line.split(",", 1)
        txinfo = json.loads(txinfo)
        version = txinfo.get("version")
        if version is None:
            version = 0

    return version


# insert the file name into the Files table
def insert_file(filename, name):
    date = get_reward_date(filename)
    version = get_version(filename)
    cursor.execute("INSERT INTO Files(filename,date,version) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE fileId=fileId",
                   (name, date, version))
    cursor.execute("Commit")


# get the id for the file name from the Files table
def get_file_info(name):
    cursor.execute("SELECT fileId,version from Files where Filename=%s", name)
    return(cursor.fetchone())


# scan the file to get the number of records contained
def get_num_records(filename):
    lines = 0
    with open(filename, 'r') as fp:
        for lines, _ in enumerate(fp):
            pass
    return lines


# get the set of existing transactions for a certain file id
def get_transactions(fileid):
    cursor.execute("SELECT txId from Rewards LEFT JOIN Files ON Rewards.fileId=Files.fileId where Rewards.fileId=%s", fileid)
    return set([TxId[0] for TxId in cursor.fetchall()])


# insert the entry into the DB
def insert_tx(dbentry):
    values = ["txid", "originalInterestCoin", "interestCoin", "totalInterestInCoin", "totalInterestInUsd",
              "earningInterestInCel", "loyaltyTier","initialBalance", "newBalance", "interest", "deposit", "withdrawal",
              "loan_interest_payment", "loan_principal_payment", "loan_principal_liquidation",
              "loan_interest_liquidation", "collateral", "swap_in", "swap_out", "inbound_transfer", "outbound_transfer",
              "promo_code_reward", "locked_deposit", "referred_award", "referrer_award", "operation_cost", "fileId"]
    query = "INSERT INTO Rewards(" + ','.join(values) + ") VALUES (" + "%s,"*(len(values)-1) +\
            "%s) ON DUPLICATE KEY UPDATE txId=txId"

    cursor.execute(query, tuple(dbentry.get(k) for k in values))
    insert_tx.counter += 1

    # commit
    if insert_tx.counter % __COMMIT_EVERY == 0:
        cursor.execute("Commit")
insert_tx.counter = 0


# main workhorse function that processes all transactions
def process_records(filename, name):

    # get file hash
    hash = get_file_sha1(filename)

    # get the number of records in the file
    lines = get_num_records(filename)

    print("\tSHA1: {}, {} lines...".format(hash, lines), flush=True)

    # get the current file Id in the Files table (used as foreign key)
    fileId, version = get_file_info(name)
    if version not in (0, 1, 2):
        print("Error! Unknown file version.")
        exit()

    # and get the set of already uploaded transactions for the file
    existingTxIds = get_transactions(fileId)

    # loop over all lines in the CSV file
    with open(filename, 'r') as file:
        with alive_bar(lines, length = 48) as bar:
            # skip header
            line = file.readline()

            while True:
                # Get a line from file
                line = file.readline()
                if not line:
                    break

                # update progress bar
                bar()

                # get a TxId record
                txid, txinfo = line.split(",", 1)

                # skip already uplodaded transactions
                if txid in existingTxIds and not __OVERWRITE_EXISTING:
                    continue

                # parse the transaction record JSON
                txinfo = json.loads(txinfo)
                if version in (1, 2):
                    txinfo = txinfo.get("data")

                # loop over all coins in the record
                for citem in txinfo:
                    dbentry = {'txid': txid, 'fileId': fileId}
                    coindata = citem if version in (1, 2) else txinfo.get(citem)
                    dbentry["interestCoin"] = coindata.get("interestCoin")
                    dbentry["originalInterestCoin"] = coindata.get("originalInterestCoin") if version in (1, 2) else citem
                    dbentry["totalInterestInCoin"] = coindata.get("totalInterestInCoin")
                    dbentry["totalInterestInUsd"] = coindata.get("totalInterestInUsd")
                    dbentry["earningInterestInCel"] = coindata.get("earningInterestInCel")
                    dbentry["loyaltyTier"] = coindata.get("loyaltyTier").get("level")

                    # process the distribution data
                    distributionData = coindata.get("distributionData")
                    for ditem in distributionData:
                        # type can be any of the defined transaction types
                        type = ditem.get("type")
                        value = Decimal(ditem.get("value"))
                        # aggregate over multiple instances of same transaction type
                        if dbentry.get(type) is None:
                            dbentry[type] = value
                        else:
                            dbentry[type] += value

                    # take the new balance from the last distribution data information
                    dbentry["newBalance"] = distributionData[-1].get("newBalance")

                    # insert into DB
                    insert_tx(dbentry)

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

        insert_file(filename, name)
        process_records(filename, name)

    close_db()
