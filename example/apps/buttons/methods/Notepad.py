import os
from Directly import Ext

# Relative location of the notepad.txt, since I want to keep it inside the app folder
notes = os.path.join(os.path.dirname(__file__), '..', 'notepad.txt')

@Ext.cls
class Notepad():
    @staticmethod
    @Ext.method
    def read_file(request):
        # Exception handling is not ideal, but it gets the idea over
        # Read file and return contents or error message
        try:
            f = open(notes, 'r')
        except Exception, e:
            return {'error': e.message}
        else:
            file_content = f.read()
            f.close()
            return file_content

    @staticmethod
    @Ext.method
    def write_file(request, text):
        # Same as above
        try:
            f = open(notes, 'w')
        except Exception, e:
            return {'error': e.message}
        else:
            f.write(text)
            f.close()
            return True