from googletrans import Translator

# Create an instance of the Translator class
translator = Translator()

def translate(text_input,src,dest):
    translation = translator.translate(text_input, src=src, dest=dest)
    return translation.text