import pyaudio
import threading
import time
import openai
import math
import struct
import os
import wave
import logging
import queue
import textwrap




# Configure the logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='logs/listener.log',
    filemode='w'
)



# TODO: explore speechrecognition library
class Listener:
    def __init__(self, config, logger=None):
        self.listening = False
        self.transcribe_queue = queue.Queue()
        self.dir = config.get("dir", "./user_audio/")
        # self.audio = pyaudio.PyAudio()
        self.silence_threshold = config.get('silence_threshold', 2000)
        self.transcribe_trigger = config.get('transcribe_trigger', 1)
        self.tolerable_silence = config.get('tolerable_silence', 3)
        self.max_duration = config.get('max_duration', 60)
        self.textmap = {}
        self.thinker = None
        self.logger = logger if logger else logging.getLogger()

        pass
    
    def listen(self):
        #continuously save audio to file (append? or just multiple audio files)
        print(textwrap.dedent("""
             --------------------------
            | Don't all speak at once! |
             --------------------------
        """))
        
        start_time = time.time()

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = self.max_duration
        # TODO: adjust based on microphone, etc... (maybe it sould be sampled from the first few seconds of audio
        THRESHOLD = self.silence_threshold 
        audio = pyaudio.PyAudio()

        # start recording audio
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        frames = []

        #Don't start the timer until the user has started speaking
        silence_counter = -float('inf')
        WRITE_SECONDS = self.transcribe_trigger
        WAIT_SECONDS = self.tolerable_silence
        
        written = False
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            #if not self.listening: break
            data = stream.read(CHUNK)
            frames.append(data)
            seconds = i / RATE * CHUNK

            if seconds > 0.5:
                rms = math.sqrt(struct.unpack("h"*CHUNK, data)[0] ** 2)
                # if RMS value is below the threshold, increment silence counter
                if rms < THRESHOLD:
                    silence_counter += 1
                # otherwise reset the silence counter--the user is still speaking
                else:
                    silence_counter = 0
                    written = False
                    
                if not written and silence_counter > RATE / CHUNK * WRITE_SECONDS: 
                    # self.logger.info("The silence has become unbearable!")
                    # print('Writing!')
                            # stop recording audio and save to file
                    stream.stop_stream()
                    stream.close()
                    # audio.terminate()
                        
                    filename = os.path.join(self.dir, f"{time.time()}.wav")
                    with wave.open(filename, 'wb') as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(audio.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                        # Write audio buffer to file
                        # Reset audio buffer
                        # Add transcription task to queue
                        thread = threading.Thread(target=self.transcribe, args=(filename,), daemon=True)
                        thread.start()
                        # task = asyncio.run_coroutine_threadsafe(self.transcribe(filename), self.loop)
                        self.transcribe_queue.put(thread)
                        # restart audio stream
                        # print('restarting audio stream')
                        stream = audio.open(format=FORMAT, channels=CHANNELS,
                                            rate=RATE, input=True,
                                            frames_per_buffer=CHUNK)
                        frames = []
                    written = True

                # if silence counter exceeds a certain value, stop recording
                if silence_counter > RATE / CHUNK * WAIT_SECONDS: 
                    # self.logger.info("The silence has become unbearable!")
                    print('The silence is unbearable!')
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    self.logger.info(f"Stopped listening after {elapsed_time:.2f} seconds")

                    self.stop()
                    break
                   

        #shutdown pyaudio object
        audio.terminate()
        
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.logger.info(f"listen() complete in {elapsed_time:.2f} seconds")

    def stop(self):
        self.listening = False
        # print(self.textmap)
        self.logger.info("About to start closing these mf tasks")
        while not self.transcribe_queue.empty():
            thread = self.transcribe_queue.get()
            thread.join()
            
        # print(self.textmap)
        self.logger.info("Closed all the mf tasks")

            

        keys = sorted(list(self.textmap.keys()))
        utterance = ""

        for k in keys:
            utterance += f" {self.textmap[k]}"
        
        # HOw can we do this, as we transcribe? How can the thinker make use of partial transcriptions?
        if self.thinker:
            self.thinker.receive(utterance)

        else:
            print(utterance)
            with open('transcript.txt', 'w') as f:
                f.write(utterance)
        self.logger.info("Have written utterance to file, or sent it to the brain :-)")

            
    def start(self):
        if self.listening:
            print('already listening!')
        else:
            self.listening = True
            self.listen()
            
    # def run(self):
    
    def transcribe(self, filename):
        start_time = time.time()

        audio_file = open(filename, "rb")

        # TODO: include prompt here for context on homonyms, noise
        # ^ ^ ^ THis is now key since you don't have the whole audio history
        transcript = openai.Audio.transcribe("whisper-1", audio_file, prompt=self._collate_textmap())

        end_time = time.time()
        elapsed_time = end_time - start_time
        content = transcript.text

        # # demarcate pauses in speech
        # if content and content[-1] not in '.!?:;,':
        #     content += ','

        self.logger.info(f"Finished transcription of {filename} in: {elapsed_time:.2f} seconds")
        self.textmap[filename] = content #float(filename[:-4])
        # print("transcribed:", content)
        return content
    
    def _collate_textmap(self):
        keys = sorted(list(self.textmap.keys()))
        utterance = ""

        for k in keys:
            utterance += f" {self.textmap[k]}"
        return utterance
    
if __name__ == "__main__":
    listener = Listener({})

    listener.start()