import os
import sys
import wave
import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from chatter import Chatter, setup_logger
from thinker import Thinker
import openai
from pydub import AudioSegment


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    print('upload audio called')
    file = request.files.get('audio_data', None)
    if file:
        filename = f'user_audio/{time.time()}.wav'
        file.save(filename)

        transcription = transcribe(filename)
        print(transcription)
        socketio.emit('receive_transcription', transcription) #, room=room) No idea why GPT-4 added room lmao

        return jsonify({"status": "success", "message": "File uploaded and saved."}), 200
    else:
        print('upload audio failed')
        return jsonify({"status": "error", "message": "File not received."}), 400

def transcribe(filename):
    start_time = time.time()

    audio_file = open(filename, "rb")

    ntries = 4
    for i in range(ntries):
        try:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)#, prompt=self._collate_textmap())
            break
        except openai.error.RateLimitError:
            print(f"Hit rate limit on try #{i}")
            time.sleep(2**i)
            gen = gen_func(*args, **kwargs)

        except openai.error.APIConnectionError:
            print(f"API connection error on try #{i}")
            gen = gen_func(*args, **kwargs)
            time.sleep(2**i)

        except Exception as e:

            # Handle the error (e.g., log it, sleep and retry, etc.)
            print(f"Unknown error occurred: {e}")
            time.sleep(2**i)
            
    end_time = time.time()
    elapsed_time = end_time - start_time
    content = transcript.text



    logger.info(f"Finished transcription of {filename} in: {elapsed_time:.2f} seconds")

    print(transcript)
    return content

@socketio.on('upload_text')
def upload_text(text):
    thread = chat.thinker.receive(text)
    thread.join()


@socketio.on('send_text')
def handle_send_text(text, chatter=None):
    thread = chat.thinker.receive(text)
    
    gen = my_generator()

    tmp = ""
    for word in gen:
        if '``' in word and not tmp:
            tmp = word 
            continue
        if tmp:
            tmp += word
            if '\n' in word:
                word = tmp
                tmp = ""
            else:
                continue
        emit('receive_word', word)
        socketio.sleep(0.05)  # Adjust this value to control the speed of the word-by-word display
    emit('processing_done')
    
    # join thread created for running any of the tools
    thread.join()


def generator_wrapper(gen_func):
    def wrapper(*args, **kwargs):
        gen = gen_func(*args, **kwargs)
        has_error = True
        t = 0

        ntries = 4
        for i in range(ntries):
            try:
                # Try to get the first value from the generator
                first_value = next(gen)
                break
            except openai.error.RateLimitError:
                print(f"Hit rate limit on try #{i}")
                time.sleep(2**i)
                gen = gen_func(*args, **kwargs)
                
            except openai.error.APIConnectionError:
                print(f"API connection error on try #{i}")
                gen = gen_func(*args, **kwargs)
                time.sleep(2**i)

            #generally caused by overlength context window: should clear out thinker.utterances
            # (or maybe I should do this pre-emptively...)
            except openai.error.InvalidRequestError as e:
                print(f"Invalid Request Error: {e}")
                return None
                
                
            except Exception as e:

                # Handle the error (e.g., log it, sleep and retry, etc.)
                print(f"Unknown error occurred: {e}")
                time.sleep(2**i)

        yield first_value
        yield from gen

    return wrapper


@generator_wrapper
def my_generator():
    return chat.thinker._process(webapp=True)

        
def save_audio_to_file(audio_data, filename=None):
    if not filename:
        filename = f'{time.time()}.wav'
    
    file_path = os.path.join('audio_files', filename)

    with wave.open(file_path, 'wb') as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wave_file.setframerate(16000)  # 16 kHz sampling rate
        wave_file.writeframes(audio_data)

if __name__ == '__main__':
    # Define the directory names
    audio_dir = 'audio_files'
    logs_dir = 'logs'

    # Create the directories if they don't exist
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logger = setup_logger('app', log_file='logs/app.log')
    
    tlogger = setup_logger('thinker', log_file='logs/thinker.log')
    # thinker = Thinker({}, tlogger)
    thinker = Thinker({"model":"gpt-4-0314"}, tlogger)
    
    
    chat = Chatter(listener=None, thinker=thinker, speaker=None)
    if not os.path.exists('audio_files'):
        os.makedirs('audio_files')
    if not os.path.exists('logs'):
        os.makedirs('logs')
    try:
        socketio.run(app, debug=True)
    except KeyboardInterrupt:
        print('Web server exited from terminal')
    chat.save()