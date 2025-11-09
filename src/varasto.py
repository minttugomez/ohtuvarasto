""" docstring """

class Varasto:
    """ docstring """
    def __init__(self, tilavuus, alku_saldo = 0):
        """ docstring """
        self.tilavuus = tilavuus if tilavuus > 0 else 0.0

        if alku_saldo < 0.0:
            # virheellinen, nollataan
            self.saldo = 0.0
        elif alku_saldo <= self.tilavuus:
            # mahtuu
            self.saldo = alku_saldo
        else:
            # täyteen ja ylimäärä hukkaan!
            self.saldo = tilavuus

    # huom: ominaisuus voidaan myös laskea.
    # Ei tarvita erillistä kenttää viela_tilaa tms.
    def paljonko_mahtuu(self):
        """ docstring """
        return self.tilavuus - self.saldo

    def lisaa_varastoon(self, maara):
        """ docstring """
        if maara < 0:
            return
        if maara <= self.paljonko_mahtuu():
            self.saldo = self.saldo + maara
        else:
            self.saldo = self.tilavuus

    def ota_varastosta(self, maara):
        """ docstring """
        if maara < 0:
            return 0.0
        if maara > self.saldo:
            kaikki_mita_voidaan = self.saldo
            self.saldo = 0.0

            return kaikki_mita_voidaan

        self.saldo = self.saldo - maara

        return maara

    def __str__(self):
        """ docstring """
        return f"saldo = {self.saldo}, vielä tilaa {self.paljonko_mahtuu()}"
