import json
import asyncio
from listener import Listener
from thinker import Thinker
# from speaker import Speaker
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



#Ideally, each class would simply look to the parent (i.e. for bot in [listener, thinker, speaker]: bot.parent = self
#pass logdir through config?
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
        # TODO: make each worker have its own function
        # TODO: This function should set the parent; more elegant that way
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

        #think out loud    
    #right now the spaeaker is called directly by thinker.process, but ideally it'd be from here
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
    

    listener = None
    # llogger = setup_logger('listener', log_file='logs/listener.log')
    # listener = Listener({}, llogger)
    
    tlogger = setup_logger('thinker', log_file='logs/thinker.log')
    # thinker = Thinker({}, tlogger)
    thinker = Thinker({"model":"gpt-4-0314"}, tlogger)
    
    # with open('../keys.json') as f:
    #     keys = json.load(f)

    speaker = None
    # speaker = Speaker({"api_key": keys['xilabs']})
    
    chat = Chatter_v2(listener=listener, thinker=thinker, speaker=speaker)
    chat.repl()
    chat.save()

