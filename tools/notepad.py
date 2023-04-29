import pandas as pd
from openai.embeddings_utils import get_embedding, cosine_similarity
from toolkit import Tool
from applenotes import AppleNotes
import os
import time



class NotePad(Tool):  # NotePad now inherits from Tool
    def __init__(self, cache_path='notes_cache.csv', thinker=None):
        trigger_prompt = None
        actions_prompt = None
        super().__init__(trigger_prompt, actions_prompt, thinker)  # Pass trigger_prompt and action_prompt to the Tool's constructor
        self.filepath = cache_path
        self.api = AppleNotes()
        
        if os.path.isfile(self.filepath):
            self.df = pd.read_csv(self.filepath)
            self.df.edit_time = pd.to_datetime(self.df.edit_time)
            self.df.embedding = self.df.embedding.apply(eval)

        else:
            self.initialize()
        
        self.last_update_time = None
        if len(self.df):
            self.last_update_time = self.df.edit_time.max()
        else:
            self.initialize()
                        
    def handle(self, action, messages):
        if action == 'new':
            self.write(messages)
        if action in ['read', 'append']:
            note = self.search_notes(messages[-1].content).iloc[0]
        
        
            
    def search_notes(self, query, n=1, pprint=False, spectral=False, similarity_fxn=cosine_similarity):
        start_time = time.time()
        query_embedding = get_embedding(
            query,
            engine="text-embedding-ada-002"
        )
        # similarity_fxn = manhattan_distance #cosine_similarity #

        if spectral:
            embs = list(self.df.embedding) + [query_embedding]
            spectral_embedding = SpectralEmbedding(n_components=int(np.sqrt(len(self.df))))
            embs = spectral_embedding.fit_transform(embs)
            self.df['spectral'] = pd.Series(list(embs[:-1]))
            self.df["similarity"] = self.df.spectral.apply(lambda x: similarity_fxn(x, embs[-1]))
        else:
            self.df["similarity"] = self.df.embedding.apply(lambda x: similarity_fxn(x, query_embedding))

        results = (
            self.df.sort_values("similarity", ascending=False)
            .head(n)
        )
        end_time = time.time()
        if pprint:
            print(f'searched {len(self.df)} notes in {end_time-start_time} seconds.\n')

        return results


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
        self.df['embedding'] = self.df.content.apply(lambda x: get_embedding(x, engine="text-embedding-ada-002"))
        self.last_update_time = self.df.edit_time.max()
    
    def update(self, batchsize=5):
        if not len(self.df):
            print("Call self.initialize() first before calling self.update()")
        start = 1
        notes_pulled = 0
        while True:
            notes = self.fetch_recent_notes(batchsize, start)
            notes = notes[notes.edit_time > self.last_update_time]
            if notes.empty:
                self.df = self.df.sort_values('edit_time', ascending=False).drop_duplicates(subset='id', keep='first').reset_index()[['id', 'edit_time', 'content', 'embedding']]
                self.df.to_csv(self.filepath, index=False)
                return notes_pulled
            notes['embedding'] = notes.content.apply(lambda x: get_embedding(x, engine="text-embedding-ada-002"))
            self.df = self.df.concat(notes, ignore_index=True)
            start += batchsize
        
    def write(self, messages, node_id=None):
        prompt = (
            "You are the note-management arm of a superintelligent AI system."
            " Based on the previous conversation, and the user's most recent request,"
            " respond with the content that should be added to the relevant note."
            " Your response will be transcribed directly to the note, so do not"
            " include any explanation of what you are doing, or address the user"
            " in any way."
        )
        
        response = openai.ChatCompletions.create(
            model='gpt-3.5-turbo',
            messages=[message.to_openai() for message in messages[-3:]],
            temperature=0.3,
        )
        content = response['choices'][0]['message']['content']

        if note_id:
            self.api.append_to_note(note_id, content)
        else:
            self.api.create_new_note(content)
            
    def extend_history(self):
        pass
        
    def rank_notes(self, query):
        pass
