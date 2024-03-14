# IMPORTING 
from util import generate_context,display_footer,write_answer
from text_to_speech import speak
from dataset.dataset import load_text_dataset
from indices.index import load_index
from encoder.encoder import load_encoder
from LLM.LLM import infer
import streamlit as st
from translator import translate
import httpcore
from dotenv import load_dotenv
import os
load_dotenv()

print(os.getenv('HF_DATASET_CHECKPOINT'))
print(os.getenv('FAISS_INDEX_FILE_PATH'))

setattr(httpcore, 'SyncHTTPTransport', None)


# SOME STATIC VARIABLES
k=10
max_line_length = 80
matching_threshold=0.50

language_choices = {
    'English': 'en',
    'Hindi': 'hi',
    'Gujarati': 'gu',
    'Marathi': 'mr',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Kannada': 'kn',
    'Bengali': 'bn',
}

# MAIN METHOD TO SET PAGE CONFIG
def main():
    
    st.set_page_config(
        page_title="Vivechan AI",
        page_icon="✨",
    )
    
if __name__ == "__main__":
    main()

# RETRIVING RESOURCES LIKE ENCODER , DATASET , INDEX etc.
@st.cache_resource
def get_cached_encoder():
    return load_encoder()

@st.cache_resource
def get_cached_index():
    return load_index()

@st.cache_resource
def get_cached_text_dataset():
    return load_text_dataset()


Encoder=get_cached_encoder()

VectorIndex=get_cached_index()

Texts=get_cached_text_dataset()


# UI
st.title("Vivechan AI 🌟")
st.subheader("AI for spritual matters")
st.markdown(
    """
    <style>
        .reportview-container {
            width: 90%;
        }
    </style>
    """,
    unsafe_allow_html=True
)
query = st.text_input("Ask any question related spritual matters i.e. Shiv Mahapuran, Shrimad Bhagwat , Shripad Charitramrutam : ")

# SELECTING LANGUAGE
language=language_choices[st.selectbox("Select Language:", list(language_choices.keys()))]
print("language : ",language)

def ask(IsContinue=False):

    PreviousAnswer=st.session_state.get('PreviousAnswer','')
    Answer=st.session_state.get('Answer','')
    
    # Translating query
    translated_query=query
    if language != 'en':
        translated_query=translate(query,language,'en')
    
    # encoding and retriving context form vector index
    encoded=Encoder.encode([translated_query])
    Distance,Positions=VectorIndex.search(encoded,k)
    Distance=Distance[0]
    Positions=Positions[0]
    min_distance=min(Distance)
    max_distance=max(Distance)
    if max_distance==min_distance:
        max_distance+=0.001

    Similarity=[(1-(dist-min_distance)/(max_distance-min_distance)) for dist in Distance]
    
    BetterPositions=[ Pos for i,Pos in enumerate(Positions) if Similarity[i] >= matching_threshold]

    print("Distance : ",Distance)
    print("Similarity : ",Similarity)

    print("Positions : ",Positions)
    print("BetterPositions : ",BetterPositions)

    Context=generate_context(Texts,BetterPositions)

    
    
    # generating answer from the context
    CurrentAnswer=infer(translated_query,Context)

    # Future feature : to support continue generation of previous answer
    if IsContinue : Answer+=CurrentAnswer
    else : Answer=CurrentAnswer
    PreviousAnswer=Answer
    
    st.session_state['PreviousAnswer']=PreviousAnswer
    st.session_state['Answer']=Answer


    write_answer(Answer,max_line_length,language)
    st.session_state['ShouldContinue']=True

    # text to speech
    speak(Answer)

    st.subheader("Full Context : ")
    st.write(Context)

if st.button('Ask'):
    st.session_state['PreviousAnswer']=''
    st.session_state['Answer']=''
    st.session_state['ShouldContinue']=False
    ask()
    
display_footer()