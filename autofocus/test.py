<<<<<<< Updated upstream
<<<<<<< Updated upstream
import logging
import sangaboard

# Print logs
logging.basicConfig(level=logging.DEBUG)

class Sangaboard2(sangaboard.Sangaboard):
    def test_communications(self):
        return True

sangaboard.Sangaboard.port_settings["baudrate"] = 9_600

sb = sangaboard.Sangaboard("COM3")
sb.move_rel([1000,0,0])
sb.position
=======
<<<<<<< Updated upstream
=======
>>>>>>> Stashed changes
import logging
import sangaboard

# Print logs
logging.basicConfig(level=logging.DEBUG)

class Sangaboard2(sangaboard.Sangaboard):
    def test_communications(self):
        return True

sangaboard.Sangaboard.port_settings["baudrate"] = 9_600

sb = sangaboard.Sangaboard("COM3")
sb.move_rel([1000,0,0])
sb.position
=======
import logging
import sangaboard

# Print logs
logging.basicConfig(level=logging.DEBUG)

class Sangaboard2(sangaboard.Sangaboard):
    def test_communications(self):
        return True

sangaboard.Sangaboard.port_settings["baudrate"] = 9_600

sb = sangaboard.Sangaboard("COM3")
sb.move_rel([1000,0,0])
sb.position
>>>>>>> Stashed changes
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
exit()