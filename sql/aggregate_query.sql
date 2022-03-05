SELECT 
    COUNT(*) AS `Count`,
    ROUND(SUM(InitialAmount), 0) AS `Amount`,
    SUM(InterestInUsd) AS `Reward`,
    SUM(InitialAmount) / COUNT(*) AS `Coin/User`,
    CASE
        WHEN `Coin` = 'CEL' THEN 1.0
        ELSE SUM(InterestInUsd * EarningInCel) / SUM(InterestInUsd)
    END AS `PercentCEL`,
    CASE
		WHEN `Coin` = 'CEL' THEN SUM(InterestInUsd)
        ELSE SUM(InterestInUsd * EarningInCel)
	END AS `InterestCEL`,
    `Coin`,
    `Date`
FROM
    Celsius.Rewards AS R
        LEFT JOIN
    Celsius.Files AS F ON R.IdFiles = F.IdFiles
GROUP BY `Coin` , R.IdFiles
ORDER BY `Date` DESC , `Reward` DESC