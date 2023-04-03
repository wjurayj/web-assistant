import openai
import asyncio
import json
import logging
import time
import textwrap

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='logs/thinker.log',
    filemode='w'
)

class Thinker:
    def __init__(self, config, logger=None):
        self.name = config.get("name", "Chatter")
        self.model = config.get("model", "gpt-3.5-turbo-0301")
        self.speaker = None
        self.logger = logger if logger else logging.getLogger()
        self.logger.warning(f"Initialized Thinker using model {self.model}")

        prime = {
            "role": "system",
            "content": f"You are {self.name}, a goofy and cheerful but somewhat rude fellow. You are never afraid to speak your mind, even when the truth is unpleasant. You are hyperanalytical, and an extremely perceptive person who is highly opinionated and never afraid to share his mind."
        }
        
        init = [
            {
                "role": "user",
                "content": f"Hello, it's nice to meet you! You must be {self.name}? I've heard you're a genius, and that you never shy from a debate."
         
                # I know you're actually very nice and friendly, but I'd like you to pretend to be my friend, '{self.name}'. {self.name} is blunt and can be rather rude, but he's very funny as well because he's never afraid to speak his mind, and ultimately he's a very perceptive person. You must never break character"
            },
            {
                "role": "assistant",
                "content": "Oh give me a break. Although you're right--I can be pretty offensive sometimes. I firmly believe that for every issue there is absolutely a right side and a wrong side, and there is no room for any other viewpoint than my own. Everyone should support/oppose the issue without question because it is the only morally correct position to take. People who disagree with my stance are simply misguided or ignorant. "
                # "Screw you, you don't get to tell me what to do. And don't go thinking that just because I happen to have all these qualities, means that it's because you told me I do!"
            }
        ]
        # init = []

        self.prime = [prime] #+ init
        
        # Track what's actually been said, from user's perspective
        self.utterances = init
    # def respond(self, message):
    def receive(self, message):     
        self.utterances.append({
            "role": "user",
            "content": message
        })
        self.logger.info(f"> {message}")
        
    def verbalize(self):
        pass
    
    def process(self, nfails = 4, webapp=False):
        for i in range(nfails):
            try:
                return self._process(webapp)
            except openai.error.RateLimitError:
                self.logger.info(f"Hit rate limit on try #{i}")
                time.sleep(2**i)
            except openai.error.APIConnectionError:
                self.logger.info(f"API connection error on try #{i}")
                time.sleep(2**i)
        self.logger.info(f"Unable to process input after {i} tries")

    def _process(self, webapp=False):

        #sned request for stream
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.prime + self.utterances,
            temperature=1,
            # max_tokens=256,
            top_p=0.98,
            frequency_penalty=0.5,
            presence_penalty=0.2,
            stream=True
        )
        
        utterance = ""
        buffer = ""
        for chunk in response:
            ch = chunk['choices'][0]['delta'].get('content', '')
            buffer += ch
            #needs to always yield, and have the chatter wrapper print if necessary
            # if webapp:
            yield ch
            # else:
            #     print(ch, end="", flush=True)
            if '\n' in ch: #break down by more frequent/all punctuation, like a period?
                #send to speaker by paragraph, etc.
                if self.speaker:
                    # print('verbalizing!')
                    
                    #this blocks text rendering a little, which I don't want
                    self.speaker.verbalize(buffer)#, eg
                utterance += buffer
                buffer = ""
                pass
        #handle the last paragraph
        if buffer:
            if self.speaker: #don't write if we're in a code block; instead the UI should render this
                # print('verbalizing the last bit!')
                self.speaker.verbalize(buffer)
            utterance += buffer
        print()

        self.utterances.append({
            "role": "assistant",
            "content": utterance
        })
        self.logger.info(f"% {utterance}")