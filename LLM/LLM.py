import os
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from util import get_device


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

    # bnb_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_use_double_quant=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_compute_dtype=torch.bfloat16
    # )
    # device=get_device()
    # print("device : ",device)
    # model_id=os.getenv('HF_LLM_CHECKPOINT')
    # print("model_id",model_id)
    # print("Start Loading LLM .....")
    # # LLM_Model=AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config)
    # LLM_Model=AutoModelForCausalLM.from_pretrained(model_id)
    # LLM_Model=LLM_Model.to(device)
    # print("Done Loading LLM .....")
    # return LLM_Model

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

def format_prompt_gemma_1(Query,Context):
  prompt=f"""
  Answer the question in detail "{Query}" from the Context below :
  Context : {Context}
  """
  # print("prompt is : ",prompt)
  return prompt

def continue_generation_prompt_mistral(Query,Context,PreviousAnswer):
  prompt=f"""
  [Complete the detailed answer for the query] "{Query}" [based on Context] ,
  :> Context : {Context} ,
  [Don't Repeat PreviousAnswer , just Continue Generating NextAnswer after PreviousAnswer]
  :> PreviousAnswer : {PreviousAnswer} , 
  """
  return prompt
  
load_dotenv()
# REPLACE WITH YOUR HUGGING FACE ACCOUNT TOKEN ( Go to settings and get access token from hugging face)
hf_token=os.getenv('HF_TOKEN')
def query(payload):
    
    import requests

    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    # API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

    headers = {"Authorization": "Bearer "+hf_token}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def mistral_prompt_format(Query,Context,PreviousAnswer=None):
  # print("In mistral_prompt_format : ",PreviousAnswer)

  formatted_prompt=format_prompt_gemma_1(Query,Context) if (PreviousAnswer == None) else continue_generation_prompt_mistral(Query,Context,PreviousAnswer)
  mistral_prompt='<s>[INST] '+formatted_prompt+'\n [/INST] Model answer</s>'
  print("mistral_prompt",mistral_prompt)
  return mistral_prompt

def infer(Query,Context,PreviousAnswer=None):
  try:
      # Prefix="Giving you 'Query' Below Answer appropriate based on Given 'Context'"
      Prefix="Hello, Spiritual Vivechan Expert, Answer appropriately for given 'Query' based on Given 'Context' provided"

      # print("In Infer PreviousAnswer : ",PreviousAnswer)

      prompt=mistral_prompt_format(Query,Context,PreviousAnswer)
      
      # print("prompt is : ",prompt)

      output = query({
          "inputs": prompt,
          "parameters": 
        {
          "contentType": "application/json",
          "max_tokens": 1000,
          "min_tokens": 1000,
          "return_full_text": False
        }
      })

      print("output generated",output)

      return output[0]['generated_text']
  except Exception as e:
        print(f"An error occurred: {e}")
        return f"could not generate answer Due to Error, please try after some time ,{e} "  

