To run the web assistant, first create a virtual environment with `python>=3.8`, and install `requirements.txt`

You'll need an OpenAI API key to run this.

If you use conda for package management, you can complete setup by running the following in your terminal:

```
conda create -n webassistant python=3.10
conda activate webassistant
pip install -r requirements.txt
mkdir logs
mkdir user_audio
export OPENAI_API_KEY='<YOUR-API-KEY>'
```

Then start the server by running:

```
python main.py
```

You can open the interface in `http://localhost:5000/`.

Press space to start/stop recording, or you can just use the text bar to write your inputs.

The button on the far right adds the contents of the text box to the context without generating a response.

You can toggle between GPT-3.5 and GPT-4 by saying "Toggle" and the name of the model you want in the same message

# Tools
To use a tool, simply mention that it should be used, and let GPT's intent judgment do the rest.

Currently, a notepad is available, which can connect to your Apple Notes API.