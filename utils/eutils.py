import sys
sys.path.append("..")
from encoders.identity import Identity

def init_encoders(encoder_manager):
    encoder_manager.add_encoder(Identity("identity"))
