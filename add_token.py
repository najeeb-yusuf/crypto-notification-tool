import pandas as pd
import numpy as np
import os

def main():
    token_details = {}


    print('Input token id')
    token_id = input()
    token_details['token'] = token_id

    print('Input purchase price')
    purchase_price = input()
    try:
        token_details['buy_price'] = float(purchase_price)
    except ValueError:
        print('invalid input')
        exit()


    print('Custom up/down multiplier? (y/n)')
    answer = input()
    if answer == 'y':
        print('Input up multiplier')

        try:
            up_multiplier = float(input())
        except ValueError:
            print('invalid input')
            exit()

        token_details['up_multiplier'] = up_multiplier

        print('Input down multiplier')
        try:
            down_multiplier = float(input())
        except ValueError:
            print('invalid input')
        token_details['down_multiplier'] = down_multiplier
    elif answer == 'n':
        token_details['up_multiplier'] = 2.0
        token_details['down_multiplier'] = 0.75
    else:
        print('invalid input')
        exit()

    token_details['notifications'] = 't'

    token_details['last_checked'] = token_details['buy_price']
    

    df = pd.read_csv('/Users/najeeb/Desktop/crypto/tokens.csv')
    new_df = pd.DataFrame(token_details)
    df.append(new_df, ignore_index=True)

    df.to_csv('/Users/najeeb/Desktop/crypto/tokens.csv', index=False)

if __name__ == "__main__":
    main()