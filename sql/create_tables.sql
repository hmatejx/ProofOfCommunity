USE Celsius;

CREATE TABLE `Files` (
  `IdFiles` int NOT NULL AUTO_INCREMENT,
  `Filename` char(36) COLLATE utf8_bin NOT NULL,
  `Date` datetime NOT NULL,
  PRIMARY KEY (`IdFiles`),
  UNIQUE KEY `idFiles_UNIQUE` (`IdFiles`),
  UNIQUE KEY `Filename_UNIQUE` (`Filename`),
  UNIQUE KEY `Date_UNIQUE` (`Date`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8_bin;

CREATE TABLE `Rewards` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `TxId` char(36) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `Coin` varchar(10) COLLATE utf8_bin NOT NULL,
  `InitialAmount` double NOT NULL,
  `InterestCoin` varchar(10) COLLATE utf8_bin NOT NULL,
  `InterestInCoin` double NOT NULL,
  `InterestInUsd` double NOT NULL,
  `EarningInCel` tinyint(1) NOT NULL,
  `Tier` tinyint(1) DEFAULT NULL,
  `IdFiles` int NOT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Id_UNIQUE` (`Id`),
  UNIQUE KEY `unique_index` (`TxId`,`Coin`),
  KEY `Id_IdFiles` (`IdFiles`),
  KEY `Id_Coin` (`Coin`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb3 COLLATE=utf8_bin
