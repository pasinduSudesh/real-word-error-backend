from app import app
from flask import Flask, render_template, request, jsonify
import os
from flask_cors import CORS
import re
import json

from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

path_to_model = "sin-survivor/re-errors"
# path_to_model = "G:/ACA/FYP/Huggingface_Finetuned_Model/rw-errors"
model = MBartForConditionalGeneration.from_pretrained(path_to_model)
tokenizer = MBart50TokenizerFast.from_pretrained(path_to_model)
print("Mode and Tokenizer downloaded")
tokenizer.src_lang = "si_LK"


def pre_process(sentences):
  punctuation_marks = [".", "?"]
  for x in range(len(sentences)):
    # sentences[x] = re.sub(' +',' ',sentences[x])#Only remove spaces
    sentences[x] = sentences[x].strip()
    sentences[x] = re.sub('\s+',' ',sentences[x])#Remove spaces and new lines
    if sentences[x][-1] not in punctuation_marks:
      sentences[x] = sentences[x]+"."
  return sentences

def predict_single_sent(model, tokenizer, sentences):
  predited_sentences = []
  for sent in sentences:
    encoded = tokenizer(sent,  return_tensors="pt",padding=True)
    generated_tokens = model.generate(**encoded, decoder_start_token_id=tokenizer.lang_code_to_id["si_LK"],return_dict_in_generate=True, output_scores=True,
                                  num_beams=5,num_return_sequences=5)
    predicted_sent = tokenizer.batch_decode(generated_tokens["sequences"], skip_special_tokens=True)
    predicted_sent = post_process(predicted_sent)
    predited_sentences.append(predicted_sent)
  return predited_sentences

def post_process(sentences):
  for x in range(len(sentences)):
    sentences[x] = sentences[x][5:]
    sentences[x] = sentences[x].strip().replace("\u0DCA \u0dbb", "\u0DCA\u200D\u0dbb").replace("\u0DCA \u0dba", "\u0DCA\u200D\u0dba").replace('\u0dad \u0dca','\u0dad\u200d\u0dca')
  return sentences

def create_response(inputsetence, predictions):
  input_words = inputsetence.split()
  # print("input", input_words)
  prediction_word_list = []
  for sent in predictions:
    prediction_word_list.append(sent.split())
  # //TODO
  # print("predictions",prediction_word_list)
  suggestion_details = []
  for x in range(len(input_words)):
    error_level = 2
    suggestion_list = []
    has_error = False
    for i, pred in enumerate(prediction_word_list):  
      # print("lengths: ", len(input_words) , len(pred))    
      if len(input_words) == len(pred):
        if input_words[x].strip() != pred[x].strip():
          if pred[x].strip() not in suggestion_list:
            suggestion_list.append(pred[x].strip())
            has_error = True
          if i==0:
            error_level = 1
    
    if has_error:
      suggestion_details.append({
          'index':x,
          'word':input_words[x].strip(),
          'suggestions':suggestion_list,
          'errorLevel':error_level
      })
  
  return json.dumps({
      'input':inputsetence,
      'predicted':predictions[0],
      'wordPredictions':suggestion_details
  })

@app.route("/")
def index():

    """
    This route will render a template.
    If a query string comes into the URL, it will return a parsed
    dictionary of the query string keys & values, using request.args
    """
    return json.dumps({
      'sdddd':[2,3,6],
      "sddd":{
        "sed":["er","fr","d"]
      }
    })

    # try:
    #     print("Downloading Model")
    #     # model = 
    #     print("Model Donloaded")

    #     print("Model Downloaded")
    #     return {
    #         "msg":"successfully loaded model"
    #     }
    # except:
    #     return{
    #         "msg": "error in loading model"
    #     }

    
    

@app.route('/', methods=["POST"])
def home():
  if request.method=='POST':
    posted_data = request.get_json()
    inputSentence = posted_data['splittedText']
    print("HOME()")
    if type(inputSentence) == str:
      inputSentence = [inputSentence]
    # print("input", inputSentence[0])
    print("Input Sentence()")
    print(inputSentence)
    print("Input Sentence Type()")
    print(type(inputSentence))

    pre_processed = pre_process(inputSentence)
    print("input sentence moodified:: ",pre_processed)
    predictions = predict_single_sent(model, tokenizer, pre_processed)
    # print("Predictions: ", predictions[0])
    response = create_response(inputSentence[0],predictions[0])
    print(response)
    return response
  return "nothing"