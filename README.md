# ProofOfCommunity

A set of tool to verify the regularly published [Celsius](https://www.celsius.network) Proof of Community (#PoC) data and ingest it into a (MySQL) database for further analysis.

**Example #PoC summary for the period of 18-25th of February:**
![ProofOfCommunity](/img/ProofOfCommunity.png)

# Requirements

## Disk space

Before starting, make sure you have sufficient space on your hard drive. The current 36 weeks worth of #PoC data sits at 60GB in form of CSV files.

When ingested into a DB, this will shrink to 13GB. Note that currently all transaction types that are documented in the `transaction_types.txt` file are handled (there may be newer transaction types comming in the future). Moreover, with more and more users joining Celsius each weak, expect each week's dump to grow in size, and consequently the DB size will grow quickly.

In summary, aim for sufficient storage size with ample room to grow. As you will quickly observe, the speed of the hard drive also matters a lot. In my case, I am working on a Samsung EVO 870 2TB SSD, which I think is decent, i.e. no M.2, but it gets the job done in a reasonable time.

## Software

First of all, you need a database. Since performance optimization is not in focus yet, I've started with MySQL, which I self-host via a VM. For convenience I've used a pre-packaged [Bitnami image](https://bitnami.com/stack/mysql/virtual-machine). You are on your own on how to install and configure the DB.

The important thing is that, after you are finished, you have:

* enough storage space for the DB (see above)
* a DB user account that has full access to the `Celsius` DB/schema.

In order to ingest the CSV files you will also need python 3 with the following packages installed
```
pymysql (>= 1.0.2)
alive_progress (>= 2.3.1)
```
Other versions would most probably work as well, but were not tested.

# Getting started

Once you have installed the required software, perform the following high-level steps.

1. Download the #PoC files from the https://app.celsius.network/ site and put them into the `data` subfolder.

2. Create the required tables in the `Celsius` DB by a command such as `mysql -h hostname -u user database -p < sql/create_tables.sql`. This should work out of the box for MySQL, but may fail for various reasons. Details may vary depending on your installation and even more so if you use a different DB backend. In such cases inspection of the `create_tables.sql` should make it clear which tables need to be created.

3. Change the DB access configuration (host, username, password, ...) in the `PoC_to_SQL.py` file in the function `connect_db()`.

4. Run the `PoC_to_SQL.py` ingest script from the main folder with `python3 PoC_to_SQL.py`. You should see progress being printed for each CSV file. ![ingest](img/example_ingest.gif)

In case you run the upload script multiple times you can control the behavior by changing the `__FORCE_FILE_RESCAN` variable. If this variable is set to `True`, the CSV files will be re-scanned and every transaction that is not yet within the DB will be pushed into the DB. This is especially useful during development and debugging, where the script might stop or crash because it encounters an unknown structure of the CSV file. After implementing the fix the script can be simply re-run and all already processed transactions are quickly skipped.

# What next?

After the data is ingested into the DB, you can query it to find interesting aggregated views. That was the main goal, after all! One example of such a query is provided in `sql/stats_per_coin.sql`. That query aggregates, for each weak, the amount of coins held, the earned interest (also whether it was in the original coin or CEL) over all entries.

The output of the query looks like this:

|fileId|originalInterestCoin|numUsers|totalInterestInUsd      |fractionInterestEarnedInCel|fractionCoinsEarningInCel|initialBalance             |deposit                  |withdrawal                |net                      |loan_interest_payment   |loan_principal_payment    |loan_principal_liquidation|loan_interest_liquidation|collateral                |swap_in             |swap_out            |inbound_transfer       |outbound_transfer       |promo_code_reward   |locked_deposit      |referred_award      |referrer_award      |operation_cost      |fileId|date               |filename                            |version|
|------|--------------------|--------|------------------------|---------------------------|-------------------------|---------------------------|-------------------------|--------------------------|-------------------------|------------------------|--------------------------|--------------------------|-------------------------|--------------------------|--------------------|--------------------|-----------------------|------------------------|--------------------|--------------------|--------------------|--------------------|--------------------|------|-------------------|------------------------------------|-------|
|21    |ZEC                 |6177    |3713.265186526284699477 |0.2447981451356180756191   |0.2632                   |83225.803755764559745511   |2120.119292910000000000  |-873.715016150000000000   |1246.404276760000000000  |0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |-1437.788571192753630677  |0.000000000000000000|0.000000000000000000|0.961343730000000000   |-0.961343730000000000   |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |ZRX                 |8802    |6150.663978493251271800 |0.2076910787029577501893   |0.2098                   |13428100.847379838248209948|207740.337419556902599790|-71587.664914442444510956 |136152.672505114458088834|0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |-12995.470179283275605101 |0.000000000000000000|0.000000000000000000|0.000000000000000000   |0.000000000000000000    |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |ZUSD                |3       |526.329758591239131100  |0.0000000000000000000000   |0.0000                   |292568.342652005411651481  |45547.029560000000000000 |0.000000000000000000      |45547.029560000000000000 |0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |0.000000000000000000      |0.000000000000000000|0.000000000000000000|0.000000000000000000   |0.000000000000000000    |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |TAUD                |546     |13303.970735988576002975|0.4208111522593811462331   |0.4231                   |10366795.316056292470148759|112857.510000000000000000|-208767.368979644265426366|-95909.858979644265426366|0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |0.000000000000000000      |0.000000000000000000|0.000000000000000000|50.000000000000000000  |-50.000000000000000000  |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |TCAD                |326     |8022.372211761370540029 |0.4970354522154216451051   |0.3558                   |5530537.046238837151936955 |310709.591373000000000000|-65577.541545648387074717 |245132.049827351612925283|0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |0.000000000000000000      |0.000000000000000000|0.000000000000000000|1.000000000000000000   |-1.000000000000000000   |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |TGBP                |877     |24359.084065646222495528|0.4404086423029442521253   |0.3957                   |9927299.099555196048352392 |175027.903277536311297409|-149482.128316485469930525|25545.774961050841366884 |0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |0.000000000000000000      |0.000000000000000000|0.000000000000000000|275.000000000000000000 |-275.000000000000000000 |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |THKD                |305     |7564.729633299061897282 |0.3565053119110207141613   |0.3803                   |34639751.104236747199294003|365500.000052275206367449|-360628.966753135427962243|4871.033299139778405206  |0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |-150931.677018633540372671|0.000000000000000000|0.000000000000000000|0.000000000000000000   |0.000000000000000000    |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |TUSD                |2549    |18099.846983111283919312|0.4891331361941640418140   |0.3158                   |10550515.770184484008954516|814056.735154881362043042|-588188.577539460531751974|225868.157615420830291068|-1047.960000000000000000|-139097.000000000000000000|0.000000000000000000      |0.000000000000000000     |0.000000000000000000      |0.000000000000000000|0.000000000000000000|2500.000000000000000000|-2500.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |
|21    |UMA                 |2422    |989.875244206455854216  |0.2604871651577670230109   |0.1639                   |129714.903901853514943009  |2756.606391929709869925  |-2791.485013708078321163  |-34.878621778368451238   |0.000000000000000000    |0.000000000000000000      |0.000000000000000000      |0.000000000000000000     |153.385751520774134009    |0.000000000000000000|0.000000000000000000|0.000000000000000000   |0.000000000000000000    |0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|0.000000000000000000|21    |2021-06-18 05:00:01|30b1fada-a99b-49dc-be9a-a20b97509935|0      |

# Reset

In case you need for any reason to restart the process from scratch, the following script that completely clears the tables from the `Celsius` DB might be useful, `mysql -h hostname -u user database -p < sql/clear_tables.sql`. Be careful, data in the DB will be permanently lost after running this command.
