USE Celsius;

CREATE TABLE `Files` (
  `fileId` int NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `filename` char(36) COLLATE utf8_bin NOT NULL,
  `version` tinyint(1) NOT NULL,
  PRIMARY KEY (`fileId`),
  UNIQUE KEY `idFiles_UNIQUE` (`fileId`),
  UNIQUE KEY `Filename_UNIQUE` (`filename`),
  UNIQUE KEY `Date_UNIQUE` (`date`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8_bin;

CREATE TABLE `Rewards` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `fileId` int NOT NULL,
  `txId` char(36) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `originalInterestCoin` varchar(10) COLLATE utf8_bin NOT NULL,
  `interestCoin` varchar(10) COLLATE utf8_bin NOT NULL,
  `totalInterestInCoin` decimal(36,18) NOT NULL,
  `totalInterestInUsd` decimal(36,18) NOT NULL,
  `earningInterestInCel` tinyint(1) NOT NULL,
  `loyaltyTier` tinyint(1) DEFAULT NULL,
  `initialBalance` decimal(36,18) DEFAULT NULL,
  `interest` decimal(36,18) DEFAULT NULL,
  `deposit` decimal(36,18) DEFAULT NULL,
  `withdrawal` decimal(36,18) DEFAULT NULL,
  `loan_interest_payment` decimal(36,18) DEFAULT NULL,
  `loan_principal_payment` decimal(36,18) DEFAULT NULL,
  `loan_principal_liquidation` decimal(36,18) DEFAULT NULL,
  `loan_interest_liquidation` decimal(36,18) DEFAULT NULL,
  `collateral` decimal(36,18) DEFAULT NULL,
  `swap_in` decimal(36,18) DEFAULT NULL,
  `swap_out` decimal(36,18) DEFAULT NULL,
  `inbound_transfer` decimal(36,18) DEFAULT NULL,
  `outbound_transfer` decimal(36,18) DEFAULT NULL,
  `promo_code_reward` decimal(36,18) DEFAULT NULL,
  `locked_deposit` decimal(36,18) DEFAULT NULL,
  `referred_award` decimal(36,18) DEFAULT NULL,
  `referrer_award` decimal(36,18) DEFAULT NULL,
  `operation_cost` decimal(36,18) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Id_UNIQUE` (`Id`),
  UNIQUE KEY `unique_index` (`txId`,`originalInterestCoin`),
  KEY `Id_IdFiles` (`fileId`),
  KEY `Id_Coin` (`originalInterestCoin`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8_bin;