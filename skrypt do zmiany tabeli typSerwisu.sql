ALTER TABLE `TransportManagerDB`.`TypSerwisu`
DROP INDEX `typSerwisu_UNIQUE`;
ALTER TABLE `TransportManagerDB`.`TypSerwisu`
ADD UNIQUE INDEX `rodzaj_typ_UNIQUE` (`rodzajSerwisu`, `typPojazdu`);
