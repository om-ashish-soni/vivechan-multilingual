import os
from dotenv import load_dotenv
from util import get_device

# not in use as of now
def load_llm():
    load_dotenv()
    from transformers import AutoTokenizer, AutoModelForCausalLM

    device=get_device()
    print("device : ",device)
    print("loading tokenizer.....")
    tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
    print("done loading tokenizer ....")
    print("loading LLM .....")
    model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it").to(device)
    print("done loading LLM .....")
    model.eval()
    print("model is in eval stage")

    return tokenizer,model

# not in use as of now
def generate_answer_from_llm(LLM_Tokenizer,LLM_Model,Query,Context):
  device=get_device()
  prompt=format_prompt_gemma_1(Query,Context)
  print("going for tokenizing input ....")
  input_ids = LLM_Tokenizer(prompt, return_tensors="pt").to(device)
  print("done for tokenizing input ....")
  print("going for model generate answer ....")
  outputs = LLM_Model.generate(**input_ids,max_length=1024)
  print("done for model generate answer ....")
  model_answer=LLM_Tokenizer.decode(outputs[0])
  print("model_answer : ",model_answer)
  return model_answer

# formatting prompt
def format_prompt_1(Query,Context):
  prompt=f"""
  Answer the question in detail "{Query}" from the Context below :
  Context : {Context}
  """
  return prompt

# not in use as of now
def continue_generation_prompt_1(Query,Context,PreviousAnswer):
  prompt=f"""
  [Complete the detailed answer for the query] "{Query}" [based on Context] ,
  :> Context : {Context} ,
  [Don't Repeat PreviousAnswer , just Continue Generating NextAnswer after PreviousAnswer]
  :> PreviousAnswer : {PreviousAnswer} , 
  """
  return prompt
  
# loading env varaibles
load_dotenv()
# REPLACE WITH YOUR HUGGING FACE ACCOUNT TOKEN ( Go to settings and get access token from hugging face)
hf_token=os.getenv('HF_TOKEN')

# querying
def query(payload):
    
    import requests

    # Replace API URL with your LLM API URL ( from hugging face. i.e. )
    # for example HF_LLM_INFERENCE_CHECKPOINT='https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2'
    API_URL = os.getenv('HF_LLM_INFERENCE_CHECKPOINT')

    headers = {"Authorization": "Bearer "+hf_token}
    
    # retriving response
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def prompt_format_2(Query,Context,PreviousAnswer=None):
  formatted_prompt=format_prompt_1(Query,Context) if (PreviousAnswer == None) else continue_generation_prompt_1(Query,Context,PreviousAnswer)
  prompt='<s>[INST] '+formatted_prompt+'\n [/INST] Model answer</s>'
  return prompt

def infer(Query,Context,PreviousAnswer=None):
  try:

      prompt=prompt_format_2(Query,Context,PreviousAnswer)
      
      output = query({
          "inputs": prompt,
          "parameters": 
        {
          "contentType": "application/json",
          "max_tokens": 12800,
          "max_new_tokens": 4000,
          "return_full_text": False
        }
      })

      return output[0]['generated_text']
  except Exception as e:
        print(f"An error occurred: {e}")
        return f"could not generate answer Due to Error, please try after some time ,{e} "  

