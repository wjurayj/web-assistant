import openai
import os

class Notepad:
    def __init__(self):
        self.description = """
Use this class to write after a user requests that you make a note of something
arguments: filename (string)
        """
        self.prompt = [
            {
                'role':'user',
                'content':'You are a monitor process for a virtual assistant. You should respond to every input with "N/A" and nothing else, unless the user asks that you make a note of something. In this case, the first word of your response should be the name of the file (no spaces, all lowercase, with a .txt extension) that the user wants you to write into, followed directly by the text that that the user wants written to this file, with a colin in between. If no filename is specified, use the placeholder filename notes.txt'
            },
            {
                'role':'assistant',
                'content': 'N/A',
            },
            {
                'role':'user',
                'content':'Make a note that my brother will be visiting in May'
            },
            {
                'role':'assistant',
                'content': 'notes.txt: brother visits in may'
            }
        ]
    def process(self, message):
        response = self.check(message)
        # print(response)
        self.react(response)

    def check(self, message):
        _message = {'role': 'user', 'content': message}
        
        #error handle like any other call (write one function?)
        response = openai.ChatCompletion.create(
            model= "gpt-3.5-turbo-0301",
            messages=self.prompt + [_message],
            temperature=1,
            top_p=0.1,
            frequency_penalty=0.2,
        )
        # print(response)
        return response['choices'][0]['message']['content']

    def react(self, response):
        words = response.split(': ')

        if words[0] == 'N/A':
            return
        print(f'making note of {response}')
        
        filename = words[0]
        text = response[len(filename)+1:].strip()
        
        #ensure that it's a text file
        if filename[-4:] != '.txt':
            print(filename)
            return
        
        # 'a+' mode means - open for reading and appending, create the file if it doesn't exist.
        with open(os.path.join('notes', filename), 'a+') as file:
            file.write(text + '\n')