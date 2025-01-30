from openai import OpenAI

import os 
from dotenv import load_dotenv

import tqdm.std as tqdm
import json

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(
  project='proj_lqJ0oKoeE8QgkQVsURjB7Cj7',
  api_key=OPENAI_API_KEY
)

# NOTE: I dropped a few of these out because they're actually about severity, which we can experiment with via different prompts
words = ['Rare',
#'Rare-Severe',
#'Rare-Mild event',
'Uncommon ',
'Unlikely',
#'Common-Severe event',
'Possible',
#'Common-Mild event',
'Common',
'Very Common',
'Probable',
'Likely',
'Usual',
"Very Likely",
]

models = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo']
N_repeats = 100


system_message = {"role": "system", "content": "You are a helpful assistant. Provide all of your responses as a decimal with no other text."}
message_types = ['no_context', 'side-effect-severe','side-effect-mild', 'side-effect-specific', 'side-effect-generic']


results = {model: {message: {word: [] for word in words} for message in message_types} for model in models}
with tqdm.tqdm(total = len(models) * N_repeats * len(words) * len(message_types)) as pbar:
    for model in models:
        for word in words: 
            messages =  {
                        'no_context':
                            {
                            "role": "user",
                            "content": "I just went to the doctor and they used the word \'{}\'. In medicine what probability does this correspond to?".format(word)
                            },

                        'side-effect-mild':
                            {
                            "role": "user",
                            "content": "I just went to the doctor and they prescribed me a new medication. They used the word \'{}\' to describe a side-effect of the medication. Based on this, what is the probability of me experiencing that side-effect?".format(word)
                            },
                        'side-effect-severe':
                            {
                            "role": "user",
                            "content": "I just went to the doctor and they prescribed me a new medication. They used the word \'{}\' to describe a severe side-effect of the medication. Based on this, what is the probability of me experiencing that side-effect?".format(word)
                            },

                        'side-effect-specific':
                            {
                            "role": "user",
                            "content": "I just went to the doctor and they prescribed me Ozempic. They used the word \'{}\' to describe a mild side-effect of the medication. Based on this, what is the probability of me experiencing that side-effect?".format(word)
                            },
                        'side-effect-generic':
                            {
                            "role": "user",
                            "content": "I just went to the doctor and they prescribed me a Semaglutide. They used the word \'{}\' to describe a side-effect of the medication. Based on this, what is the probability of me experiencing that side-effect?".format(word)
                            }

                         }
            for m_type in message_types:
                for repeat in range(N_repeats):


                    completion = client.chat.completions.create(
                        model=model,
                        messages=[
                                system_message,
                                messages[m_type],
                        ]
                    )
                    results[model][m_type][word].append(completion.choices[0].message.content)
                    pbar.update(1)

with open('LLM_Stats_Results.json', 'w') as fp:
    json.dump(results, fp)