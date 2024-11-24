START TRANSACTION;
USE `TransportManagerDB`;
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Opony', 'Naczepa');
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Hamulce', 'Naczepa');
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Silnik', 'Naczepa');
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Wyposażenie', 'Naczepa');
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Zawieszenie', 'Naczepa');
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Klimatyzacja', 'Naczepa');
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Układ chłodniczy', 'Naczepa');
INSERT INTO `TransportManagerDB`.`TypSerwisu` (`idTypSerwisu`, `rodzajSerwisu`, `typPojazdu`) VALUES (DEFAULT, 'Inne', 'Naczepa');

COMMIT;
