
INST_CLARINET = 0
INST_PIANO = 1


class CollisionRecord:
    def __init__(self, instrument, pitch, volume):
        self.instrument = instrument
        self.pitch = pitch
        self.volume = volume
