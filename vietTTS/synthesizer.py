import re
import glob
import os
import pickle
import pandas as pd

import unicodedata
from argparse import ArgumentParser
from pathlib import Path
from vinorm import TTSnorm

import soundfile as sf

from .hifigan.mel2wave import mel2wave
from .nat.config import FLAGS
from .nat.text2mel import text2mel



parser = ArgumentParser()
parser.add_argument("--path", type=str)
parser.add_argument("--output", type=str)
# parser.add_argument("--sample-rate", default=16000, type=int)
# parser.add_argument("--silence-duration", default=-1, type=float)
# parser.add_argument("--lexicon-file", default=None)
args = parser.parse_args()

with open("phonetic.pkl","rb") as f:
  mapping = pickle.load(f)

with open("exception.pkl","rb") as f:
  dict = pickle.load(f)
  
def nat_normalize_text(text):
    text = unicodedata.normalize("NFKC", text)
    sil = FLAGS.special_phonemes[FLAGS.sil_index]
    text = re.sub(r"[\n.,:]+", f" {sil} ", text)
  
    ls = list(text.split(" "))
    M = (pd.Series(ls)).replace(dict)
    text = ' '.join(list(M))
  
    text = TTSnorm(text)
    text = text.replace('"', " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[.,:;?!]+", f" {sil} ", text)
    text = re.sub("[ ]+", " ", text)
    text = re.sub(f"( {sil}+)+ ", f" {sil} ", text)  
    text = text.lower().strip()
  
    ls = list(text.split(" "))
    M = (pd.Series(ls)).replace(mapping)
    text = ' '.join(list(M))
  
    return text.strip()


text = unicodedata.normalize("NFKC", text)
text = text.lower().strip()
text = re.sub(r"[\n.,:]+", f" {sil} ", text)
text = text.replace('"', " ")
text = re.sub(r"\s+", " ", text)
text = re.sub(r"[.,:;?!]+", f" {sil} ", text)
text = re.sub("[ ]+", " ", text)
text = re.sub(f"( {sil}+)+ ", f" {sil} ", text)
return text.strip()


# text = nat_normalize_text(args.text)
# print("Normalized text input:", text)
# mel = text2mel(text, args.lexicon_file, args.silence_duration)
# wave = mel2wave(mel)
# print("writing output to file", args.output)
# sf.write(str(args.output), wave, samplerate=args.sample_rate)


def syntheaudio(path, output, sample_rate, silence_duration, lexicon_file):
    txt = open(path, "r")
    file_name = os.path.basename(path)
    raw_text = txt.read()
    text = nat_normalize_text(raw_text)
    print("Normalized text input:", text)
    try:
        mel = text2mel(text, lexicon_file, silence_duration)
        wave = mel2wave(mel)
        print("writing output to file", output)
        sf.write(str(output), wave, samplerate=sample_rate)
    except ValueError:
        with open("log_file.txt", "a") as file: #log file error
            file.write(file_name+ "|" + raw_text + "\n")
            

# path = ['/Users/macos/Desktop/Final_Report/Data/test_slice_data/source/train/4.wav']
# output = '/Users/macos/Documents/GitHub/vietTTS/assets/infore/clip1.wav'
sample_rate = 16000
silence_duration = 0.2
lexicon_file = '/content/TTS/assets/infore/lexicon.txt'

def multisyn(base_path, output):
    list_path =  sorted([f for f in glob.glob(base_path+"/*.txt")])
    for i in list_path:
        print(i)
        file_name = os.path.basename(i)
        file = os.path.splitext(file_name)
        syntheaudio(i, output + '/' + file[0] + '.wav', sample_rate, silence_duration, lexicon_file)

multisyn(args.path, args.output)
