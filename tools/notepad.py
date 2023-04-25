import pandas as pd

class NotePad(Tool):  # NotePad now inherits from Tool
    def __init__(self, df=[]):
        trigger_prompt = None
        actions_prompt = None
        super().__init__(trigger_prompt, actions_prompt)  # Pass trigger_prompt and action_prompt to the Tool's constructor
        self.notes_api  = AppleNotes()
        
        self.df = df #should also be able to pass a filepath to .csv for easy initilization
        self.last_update_time = None
        if len(self.df):
            self.last_update_time = self.df.edit_time.max()
            
        # self.fetch_notes()  # Fetch the 50 most recent notes on initialization

    def fetch_recent_notes(self, count=5, start=1):
        kwargs = {
            'id_tag':'zmcnuadsl',
            'time_tag':'asdlkjadk',
            'content_tag':'dakjkcmas',
        }
        notedata = self.notes_api.fetch_recent_notes(start=start, count=count, **kwargs) #this api needs to have start index as well
        notelist = self.notes_api.parse_notes(notedata, **kwargs)
        
        df = pd.DataFrame(notelist)
        df.edit_time = pd.to_datetime(df.edit_time)
        
        return df
    
    def initialize(self, max_notes=20):
        notes = self.fetch_recent_notes(max_notes)
        self.df = notes
        self.last_update_time = self.df.edit_time.max()
    
    def update(self, batchsize=5):
        assert len(self.df) > 0
        start = 1
        notes_pulled = 0
        while True:
            notes = self.fetch_recent_notes(batchsize, start)
            notes = notes[notes.edit_time > self.last_update_time]
            if notes.empty:
                self.df.sort_values('edit_time', inplace=True)
                return notes_pulled
            self.df = self.df.append(notes, ignore_index=True)
            start += batchsize
            
    def extend(self):
        pass