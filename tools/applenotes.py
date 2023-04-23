#applescript parsing
import applescript
import re
import html2text


class AppleNotes:
    def __init__(self):
        pass
    def append_to_note(self, note_id: str, content: str) -> None:
        script = f"""
        tell application "Notes"
            set target_note to first note whose id is "{note_id}"
            set body of target_note to (body of target_note) & "{content}"
        end tell
        """
        r = applescript.run(script)
        return r

    # This is quality code--potentially done (although parsing still needs to be done)
    def fetch_recent_notes(self, count=5, start=1, id_tag='id', time_tag='edit_time', content_tag='content'):
        # id_tag = tags.get('id', 'id')
        applescript_code = f'''
        tell application "Notes"
            set notesCount to count of notes
            set startingNote to {start}
            set endingNote to {start + count}
            if (startingNote < 1) then set startingNote to 1

            set recentNotesInfo to {{}}

            repeat with noteIndex from startingNote to endingNote
                set currentNote to note noteIndex
                set currentNoteID to id of currentNote
                set currentNoteBody to body of currentNote
                set currentNoteEditTime to modification date of currentNote

                copy {{{id_tag}:currentNoteID, {time_tag}:currentNoteEditTime, {content_tag}:currentNoteBody}} to the end of recentNotesInfo
            end repeat

        end tell

        return recentNotesInfo
        '''

        response = applescript.run(applescript_code)
        return response
    

    def parse_notes(self, response, id_tag='id', time_tag='edit_time', content_tag='content'):
        print(id_tag, time_tag, content_tag)
        pattern = fr"{id_tag}:(?P<id>.*?), {time_tag}:(?P<date>.*?), {content_tag}:(?P<content>.*?)(?=, {id_tag}:|$)"

        matches = re.finditer(pattern, response.out, re.DOTALL)

        result = [(match.group("id"), match.group("date"), match.group("content")) for match in matches]

        converter = html2text.HTML2Text()
        converter.ignore_links = False
        # plain_text = converter.handle(html_content)

        # print(plain_text)
        notes = []
        for note in result:
            
            # Remove image tags
            cleaned_content = re.sub(r'<img[^>]*>', '', note[2])

            notes.append({
                'id': note[0],
                'edit_time': note[1],
                'content': converter.handle(cleaned_content),
            })            
        return notes
    
    def create_new_note(self, content, name='\n'):
        applescript_code = f'''
        tell application "Notes"
            make new note at folder "Notes" with properties {{name: "{name}", body: "{content}"}}
        end tell
        '''

        applescript.run(applescript_code)

    def edit_note(self, note_id, new_content):
        pass