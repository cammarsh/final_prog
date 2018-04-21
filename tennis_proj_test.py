import unittest
import tennis_proj as tennis
import json


class TestRankings(unittest.TestCase):

    def testWTA(self):
        tennis.get_rankings('2018', 'WTA')
        tennis.get_rankings('2016', 'WTA')

        a = tennis.get_rankings('2018', 'WTA')[0]
        b = tennis.get_rankings('2016', 'WTA')[1]
        self.assertEqual(a, 'Simona Halep')
        self.assertEqual(b, 'Serena Williams')

        c = tennis.get_rankings('2017', 'WTA')[4]
        self.assertEqual(c, 'Venus Williams')

    def testATP(self):
            tennis.get_rankings('2018', 'ATP')
            tennis.get_rankings('2016', 'WTA')

            a = tennis.get_rankings('2018', 'ATP')[0]
            b = tennis.get_rankings('2016', 'ATP')[1]
            self.assertEqual(a, 'Rafael Nadal')
            self.assertEqual(b, 'Nojak Djokovic')

            c = tennis.get_rankings('2017', 'WTA')[4]
            self.assertEqual(c, 'Dominic Thiem')
if __name__ == "__main__":
    testWTA();
    testATP();
