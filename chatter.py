import json
import asyncio
from thinker import Thinker
import time
import logging



# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='logs/chatter.log',
    filemode='w'
)


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

class Chatter:
    def __init__(self, listener=None, thinker=None, speaker=None):
        # self.speaker = Speaker()
        self.listener = listener
        self.thinker = thinker
        self.speaker = speaker
        self._interlink()
        self.logger = logging.getLogger()
        pass
    
    def _interlink(self):
        if self.speaker:
            self.speaker.thinker = self.thinker
            self.thinker.speaker = self.speaker
    
        if self.listener:
            self.listener.thinker = self.thinker
            self.thinker.listener = self.listener
        
    def listen(self):
        if self.listener:
            self.listener.start()
        else:
            thinker.receive(input("> "))
            print("==========================")
            print('% ', end="", flush=True)
        
    def think(self, webapp=False):
        if webapp:
            return self.thinker.process()
        else:
            gen = self.thinker.process()
            for ch in gen:
                print(ch, end="", flush=True)

    def speak(self):
        if self.speaker:
            self.logger.info(f"Sending roger to speaker, no new text input coming")
            self.speaker.roger()
        else:
            pass

    
    def run_cycle(self):
        self.listen()
        self.think()
        self.speak()

    
    def repl(self):
        try:
            while True:
                self.run_cycle()
        except KeyboardInterrupt:
            print('\nThanks for chatting; have a nice day!')
            
    def save(self):
        current_time = time.localtime()

        # Format current_time as a string
        formatted_time = time.strftime("%Y-%m-%d.%H-%M-%S", current_time)
        with open(f'./logs/{formatted_time}.json', 'w') as f:
            json.dump(self.thinker.utterances, f)

        
if __name__ == "__main__":
    
    tlogger = setup_logger('thinker', log_file='logs/thinker.log')
    # thinker = Thinker({}, tlogger)
    thinker = Thinker({"model":"gpt-4-0314"}, tlogger)
    
    listener = None
    speaker = None
    
    chat = Chatter(listener=listener, thinker=thinker, speaker=speaker)
    chat.repl()
    chat.save()

