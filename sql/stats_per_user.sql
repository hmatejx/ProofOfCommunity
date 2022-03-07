SELECT
    *
FROM
    (SELECT
        fileId,
            originalInterestCoin,
			/* interestCoin */
            COUNT(*) as numUsers,
			/* totalInterestInCoin */
            IFNULL(SUM(totalInterestInUsd), 0) AS totalInterestInUsd,
            CASE WHEN originalInterestCoin = 'CEL' THEN
				1.0
			ELSE
				IFNULL(SUM(earningInterestInCel * totalInterestInUsd) / SUM(totalInterestInUsd), 0)
			END AS fractionInterestEarnedInCel,
            CASE WHEN originalInterestCoin = 'CEL' THEN
				1.0
			ELSE
				IFNULL(SUM(earningInterestInCel) / COUNT(*), 0)
			END AS fractionCoinsEarningInCel,
            /* loyaltyTier */
            IFNULL(SUM(initialBalance), 0) AS initialBalance,
            IFNULL(SUM(deposit), 0) AS deposit,
            IFNULL(SUM(withdrawal), 0) AS withdrawal,
            IFNULL(SUM(deposit), 0) + IFNULL(SUM(withdrawal), 0) AS net,
            IFNULL(SUM(loan_interest_payment), 0) AS loan_interest_payment,
            IFNULL(SUM(loan_principal_payment), 0) AS loan_principal_payment,
            IFNULL(SUM(loan_principal_liquidation), 0) AS loan_principal_liquidation,
            IFNULL(SUM(loan_interest_liquidation), 0) AS loan_interest_liquidation,
            IFNULL(SUM(collateral), 0) AS collateral,
            IFNULL(SUM(swap_in), 0) AS swap_in,
            IFNULL(SUM(swap_out), 0) AS swap_out,
            IFNULL(SUM(inbound_transfer), 0) AS inbound_transfer,
            IFNULL(SUM(outbound_transfer), 0) AS outbound_transfer,
            IFNULL(SUM(promo_code_reward), 0) AS promo_code_reward,
            IFNULL(SUM(locked_deposit), 0) AS locked_deposit,
            IFNULL(SUM(referred_award), 0) AS referred_award,
            IFNULL(SUM(referrer_award), 0) AS referrer_award,
            IFNULL(SUM(operation_cost), 0) AS operation_cost
    FROM
        Celsius.Rewards
    /* WHERE
        originalInterestCoin = 'CEL' */
    GROUP BY originalInterestCoin , fileId) AS R
        LEFT JOIN
    Files AS F ON R.fileId = F.fileId
ORDER BY F.date ASC