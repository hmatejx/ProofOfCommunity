USE Celsius;

SELECT 
    `date`,
    numUsers,
    numPositions,
    695658161 AS totalCel,
    totalCelInApp,
    totalInterestInUsd,
    weeklyCelBuybackInUsd,
    weeklyCelBuybackInCel,
    CASE
        WHEN `date` >= CAST('2021-10-01 00:00:00' AS DATETIME) THEN weeklyCelBuybackInCel * 0.1
        ELSE 0
    END AS weeklyCelBurnInCel,
    SUM(CASE
        WHEN `date` >= CAST('2021-10-01 00:00:00' AS DATETIME) THEN weeklyCelBuybackInCel * 0.1
        ELSE 0
    END) OVER (ORDER BY date) AS cumulativeCelBurnInCel,
    weeklyCelBuybackInUsd / totalInterestInUsd AS fractionInterestEarnedInCel,
    weeklyCelBuybackInUsd / weeklyCelBuybackInCel AS priceCelInUsd,
    totalCelInApp / numUsers AS averageCelPerUserInApp,
    (695658161 - totalCelInApp) / numUsers AS averageCelPerUserOutside,
    weeklyCelBuybackInCel / numUsers AS weeklyCelBuybackPerUser
FROM
    (SELECT 
        fileId,
            COUNT(DISTINCT txId) AS numUsers,
            COUNT(*) AS numPositions,
            SUM(totalInterestInUsd) AS totalInterestInUsd,
            SUM(CASE
                WHEN originalInterestCoin = 'CEL' THEN newBalance
                ELSE 0
            END) AS totalCelInApp,
            SUM(CASE
                WHEN interestCoin = 'CEL' THEN totalInterestInCoin
                ELSE 0
            END) AS weeklyCelBuybackInCel,
            SUM(CASE
                WHEN originalInterestCoin = 'CEL' THEN totalInterestInUsd
                ELSE earningInterestInCel * totalInterestInUsd
            END) AS weeklyCelBuybackInUsd
    FROM
        Celsius.Rewards
    GROUP BY fileId) AS R
        LEFT JOIN
    Files AS F ON R.fileId = F.fileId
ORDER BY F.date ASC