USE Celsius;

SELECT 
    MIN(`date`) AS `date`,
    fileId,
    SUM(CASE
        WHEN Tier = 0 THEN 1
        ELSE 0
    END) AS Tier0,       
    SUM(CASE
        WHEN Tier = 1 THEN 1
        ELSE 0
    END) AS Tier1,
    SUM(CASE
        WHEN Tier = 2 THEN 1
        ELSE 0
    END) AS Tier2,
    SUM(CASE
        WHEN Tier = 3 THEN 1
        ELSE 0
    END) AS Tier3,
    SUM(CASE
        WHEN Tier = 4 THEN 1
        ELSE 0
    END) AS Tier4
FROM
    (SELECT 
        MIN(Rewards.fileId) AS fileId,
            MIN(`date`) AS `date`,
            txId,
            MIN(loyaltyTier) AS Tier
    FROM
        Rewards
    LEFT JOIN Files ON Rewards.fileId = Files.fileId
    /*WHERE
        Rewards.fileId <= 5*/
    GROUP BY txId) AS I
GROUP BY fileId
ORDER BY `date`