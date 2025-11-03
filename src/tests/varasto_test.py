import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    def setUp(self):
        self.varasto = Varasto(10)
        self.neg_varasto = Varasto(-10)
        self.neg_saldo_varasto = Varasto(10, -5)
        
    def test_negatiivinen_varasto_on_tyhja(self):
        self.assertAlmostEqual(self.neg_saldo_varasto.saldo, 0)
        
    def test_konstruktori_luo_tyhjan_varaston(self):
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_uudella_varastolla_oikea_tilavuus(self):
        self.assertAlmostEqual(self.varasto.tilavuus, -10)
		
    def test_negatiivinen_varasto_oikea_tilavuus(self):
        self.assertAlmostEqual(self.neg_varasto.tilavuus, 0)

    def test_lisays_lisaa_saldoa(self):
        self.varasto.lisaa_varastoon(8)
        self.assertAlmostEqual(self.varasto.saldo, 8)
        
    def test_lisays_lisaa_neg_saldoa(self):
        self.varasto.lisaa_varastoon(-8)
        self.assertAlmostEqual(self.varasto.saldo, 0)
    
    def test_lisays_lisaa_saldoa_yli(self):
        self.varasto.lisaa_varastoon(18)
        self.assertAlmostEqual(self.varasto.saldo, self.varasto.tilavuus)    

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        self.varasto.lisaa_varastoon(8)
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        self.varasto.lisaa_varastoon(8)
        saatu_maara = self.varasto.ota_varastosta(2)
        self.assertAlmostEqual(saatu_maara, 2)
    
    def test_neg_ottaminen_palauttaa_oikean_maaran(self):
        self.varasto.lisaa_varastoon(8)
        saatu_maara = self.varasto.ota_varastosta(-2)
        self.assertAlmostEqual(saatu_maara, 0)
    
    def test_ota_enemman_kuin_on_saatu_maara(self):
        self.varasto.lisaa_varastoon(8)
        saatu_maara = self.varasto.ota_varastosta(20)
        self.assertAlmostEqual(saatu_maara, 8)

    def test_ota_enemman_kuin_on_saldo_jalkeen(self):
        self.varasto.lisaa_varastoon(8)
        saatu_maara = self.varasto.ota_varastosta(20)
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_ottaminen_lisaa_tilaa(self):
        self.varasto.lisaa_varastoon(8)
        self.varasto.ota_varastosta(2)
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)

    def test_str_palauttaa_oikean(self):
        self.varasto.lisaa_varastoon(8)
        palautuva_str = str(self.varasto)
        
        self.assertAlmostEqual(palautuva_str, "saldo = 8, vielä tilaa 2")