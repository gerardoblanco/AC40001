import envAutomation
import envControlFuncs
import unittest


class TestEnvAutomate(unittest.TestCase):
    
    def test_ventilation(self):
        interior, exterior = envControlFuncs.greenhouseTemp()
        if interior > exterior and interior > 25:
            opened, closed = envAutomation.ventilation()
            assertTrue(opened)
            assertFalse(closed)
        else if exterior > interior and interior < 25:
            opened, closed = envAutomation.ventilation()
            assertTrue(closed)
            assertFalse(opened)
    
    def test_fillTank(self):
        if envControlFuncs.waterTankDepth() < 0.7:
            assertTrue(envAutomation.fillTank())
            
            
    def test_irrigation(self):
        if envControlFuncs.soilMoisture() == True:
            assertTrue(envAutomation.irrigation())  
    
            

if __name__ == '__main__':
    unittest.main()