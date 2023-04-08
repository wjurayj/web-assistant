To run the web assistant, first create a virtual environment with `python>=3.8`: if using conda, you can do this with the command `conda create -n webassistant python=3.10`

Then, run `pip install -r requirements.txt`
Set your environment variable `OPENAI_API_KEY` to your API key

Finally, run `python main.py`

You can open the interface in `http://localhost:5000/`.

Press space to start/stop recording, or you can just use the text bar to write your inputs.