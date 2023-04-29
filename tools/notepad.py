import pandas as pd

class NotePad(Tool):  # NotePad now inherits from Tool
    def __init__(self):
        trigger_prompt = None
        actions_prompt = None
        super().__init__(trigger_prompt, actions_prompt)  # Pass trigger_prompt and action_prompt to the Tool's constructor
        self.api = AppleNotes()
        
        self.df = pd.read_csv('notes_cache.csv')
        # if not 'embedding' in self.df.columns:
        self.df.edit_time = pd.to_datetime(self.df.edit_time)
        self.df.embedding = self.df.embedding.apply(eval)
        
        self.last_update_time = None
        if len(self.df):
            self.last_update_time = self.df.edit_time.max()
        self.embeddings = np
        
        # self.embe
        # self.fetch_notes()  # Fetch the 50 most recent notes on initialization

    def fetch_recent_notes(self, count=5, start=1):
        kwargs = {
            'id_tag':'zmcnuadsl',
            'time_tag':'asdlkjadk',
            'content_tag':'dakjkcmas',
        }
        notedata = self.api.fetch_recent_notes(start=start, count=count, **kwargs) #this api needs to have start index as well
        notelist = self.api.parse_notes(notedata, **kwargs)
        
        df = pd.DataFrame(notelist)
        df.edit_time = pd.to_datetime(df.edit_time)
        
        return df
    
    def initialize(self, n=20):
        notes = self.fetch_recent_notes(n)
        self.df = notes
        self.last_update_time = self.df.edit_time.max()
    
    def update(self, batchsize=5):
        if not len(self.df):
            print('Call self..initialize() first before calling self.update() 
        start = 1
        notes_pulled = 0
        while True:
            notes = self.fetch_recent_notes(batchsize, start)
            notes = notes[notes.edit_time > self.last_update_time]
            if notes.empty:
                self.df = self.df.sort_values('edit_time', ascending=False).drop_duplicates(subset='id', keep='first')
                # self.df.sort_values('edit_time', inplace=True)
                return notes_pulled
            notes['embedding'] = notes.content.apply(get_embedding)
            self.df = self.df.append(notes, ignore_index=True)
            start += batchsize
        
    def write(self, content, node_id=None):
        if note_id:
            self.api.append_to_note(note_id, content)
        else:
            self.api.create_new_note(content)
    def extend_history(self):
        pass

    def write(self, messages, note_id=None):
        prompt = (
            "You are the note-management arm of a superintelligent AI system."
            " Based on the previous conversation, and the user's most recent request,"
            " respond with the content that should be added to the relevant note"
        )
        #response = openai.ChatCompletions.create(data)
        if note_id:
            # this is where the appending logic happens
            # in the future we may want unified read+write logic for edits
            pass
        else:
            self.notes_api.create_new_note(response)
        
        
    def read(self):
        prompt = (
            "You are the note-management arm of a superintelligent AI system."
            " Based on the previous conversation, and the user's most recent request,"
            " respond with the content that should be added to the relevant note."
            " Your response will be transcribed directly to the note, so do not"
            " include any explanation of what you are doing, or address the user"
            " in any way."
        )
    def rank_notes(self, query):
        pass