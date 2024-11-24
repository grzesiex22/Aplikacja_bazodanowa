CREATE OR REPLACE VIEW serwiswidok AS
SELECT 
    serwis.idSerwis,
	typserwisu.rodzajSerwisu,
	pojazd.idPojazd,
	pojazd.typPojazdu,
    pojazd.marka,
    pojazd.model,
    pojazd.nrRejestracyjny,
    serwis.data,
    serwis.cenaCzesciNetto,
    serwis.robocizna,
    serwis.kosztCalkowityNetto,
    serwis.przebieg,
    serwis.infoDodatkowe
FROM 
    serwis
LEFT JOIN 
    pojazd ON serwis.idPojazd = pojazd.idPojazd
LEFT JOIN 
    typserwisu ON serwis.idTypSerwisu = typserwisu.idTypSerwisu;
