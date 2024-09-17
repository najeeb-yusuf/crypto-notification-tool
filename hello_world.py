import pandas as pd

tokens = pd.read_csv('/Users/najeeb/Desktop/crypto/tokens.csv')

mask = tokens['token'].str.startswith('3psH1Mj1f7yUfaD5gh6Zj7epE8hhrMkMETgv5TshQA4o')
tokens.loc[mask, 'up_multiplier'] = 4

tokens.to_csv('/Users/najeeb/Desktop/crypto/tokens.csv')

