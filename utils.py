class Message:
    def __init__(self, content='', role='user', meta={}):
        self.role = role
        self.content = content
        self.meta = meta
        
    def to_openai(self):
        return {'role':self.role, 'content':self.content}
    
    def to_anthropic(self):
        return ""