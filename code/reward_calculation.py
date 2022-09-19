"""
Lambda function that reads dynamodb, generates calculation policies
"""
import json


def get_policy_list_by_date_and_card_type(transaction_date: str, cardType: str):
    """function to fetch the policies for that current date"""
    #db logic to be implemented

    policy_list = [
        {
            'amount_greater_than': '100',
            'merchant_name_include': ['Grab'],
            'percentage_of_amount': '4',
            'calculation_reason': 'Grab Promo - 4 miles per dollar with Grab, min spend 100 SGD'
        },
        {
            'amount_greater_than': '2000',
            'percentage_of_amount': '0.03',
            'calculation_reason': '3 percent cashback for all expenditure above 2000 SGD'
        },
        {
            'amount_greater_than': '500',
            'percentage_of_amount': '0.01',
            'calculation_reason': '1 percent cashback for all expenditure above 500 SGD'
        },
        {
            'percentage_of_amount': '0.005',
            'calculation_reason': '0.5 percent cashback for all expenditure'
        },
    ]
    return policy_list


def get_exclusions_by_date_and_card_type(transaction_date: str, cardType: str):
    '''function to get all exclusions by date'''
    exclusions_dict = {
        'exclusions_dict_mcc':
            {
                '6051': 'Quasi Cash Merchants - Prepaid top-ups',
                '9399': 'Government Services-Not Elsewhere Classified | Excluded',
                '6540': 'POI (Point of Interaction) Funding Transactions (Excluding MoneySend) | Taxis & public transport'
            },
        'exclusions_dict_merchant':
            {
                'Blacklisted Merchant': 'Merchant has been blacklisted'
            }
    }

    return exclusions_dict


def get_reward(transaction: dict):
    '''main function to govern the calculation of an individual transaction, generating a record'''

    reward = {
        'reward_id': 'id',
        'card_id': transaction['cardId'],
        'card_type': transaction['cardType'],
        'date': transaction['date'],
        'merchant_name': transaction['merchant'],
        'is_exclusion': False,
        'currency': transaction['currency'],
        'original_amount': transaction['sgdAmount']
    }

    #check exclusions
    exclusions_dict = get_exclusions_by_date_and_card_type(transaction['date'], transaction['cardType'])

    if transaction['mcc'] in exclusions_dict['exclusions_dict_mcc']:
        reward['is_exclusion'] = True
        reward['calculation_reason'] = exclusions_dict['exclusions_dict_mcc'][transaction['mcc']]
        reward['reward_value'] = 0

    if transaction['merchant'] in exclusions_dict['exclusions_dict_merchant']:
        reward['is_exclusion'] = True
        reward['calculation_reason'] = exclusions_dict['exclusions_dict_merchant'][transaction['merchant']]
        reward['reward_value'] = 0

    if not reward['is_exclusion']:
        #get policy and calculate
        policy_list = get_policy_list_by_date_and_card_type(transaction['date'], transaction['cardType'])

        for policy in policy_list:
            reward_float = apply_policy(transaction, policy)
            if reward_float > 0:
                reward['reward_value'] = reward_float
                reward['calculation_reason'] = policy['calculation_reason']
                break

    print(json.dumps(reward, indent = 4))



def apply_policy(transaction: dict, policy: dict):
    '''Function to run the logic.
    Must give a transaction dict and a policy dict,
    returns a reward amount in float'''

    try:

        if 'amount_greater_than' in policy:
            if float(transaction['sgdAmount']) <= float(policy['amount_greater_than']):
                return -1
        if 'mcc_include' in policy:
            if transaction['mcc'] not in policy['mcc_include']:
                return -1
        if 'mcc_exclude' in policy:
            if transaction['mcc'] in policy['mcc_exclude']:
                return -1
        if 'merchant_name_include' in policy:
            if transaction['merchant'] not in policy['merchant_name_include']:
                return -1
        if 'merchant_name_exclude' in policy:
            if transaction['merchant'] in policy['merchant_name_exclude']:
                return -1

        if 'percentage_of_amount' in policy:
            return float(policy['percentage_of_amount']) * float(transaction['sgdAmount'])
        #else other calculation types to be implemented

    except Exception as exception:
        raise exception




# def process_policy(amount, mcc, transaction_date, card_type, card_id, merchant_name):
#     """test logic
#     assume card is current, and within our purview
#     """
#     # policy = get_current_date_policy(transaction_date)
#     is_exclusion = False

#     # conditions

#     policy = {
#         'amount_greater_than': '0',
#         'mcc_include': ['0000', '1234'],
#         'mcc_excude': ['5678', '3453'],
#         'merchant_name_include': ['Shell', 'Grab'],
#         'merchant_name_exclude': ['Gojek', 'Shopee'],
#         'percentage_of_amount': '0.05',
#         'calculation_reason': 'test calculation'
#     }

#     # assume that merchant = exactly that type of expenditure,
#     # because you can buy snacks from a shell station too!
#     # in that case, the merchant twould be the snack provider not shell itself

#     # assume that the policies for this given date have been applied

#     # apply exclusions first
#     # codeifiable easily with dictionary in database
#     exclusions = {
#         '6051': 'Quasi cash merchant',
#         '9399': 'AXS',
#         '6540': 'EZ-Link topup'
#     }

#     if mcc in exclusions:
#         reward_value = '0'
#         calculation_reason = exclusions[mcc]
#         is_exclusion = True

#     # when no exclusions apply, find the correct card, then apply the campaign
#     if not is_exclusion:
#         if card_type == 'scis_freedom':
#             if merchant_name == 'Shell' and mcc == '5172':
#                 reward_value = str(0.05 * amount)
#                 calculation_reason = "Shell promo Dec 31st"
#             elif amount > 2000:
#                 reward_value = str(0.03 * amount)
#                 calculation_reason = "3 percent cashback on expenditure over 2000 SGD"
#             elif amount > 500:
#                 reward_value = str(0.01 * amount)
#                 calculation_reason = "1 percent cashback on expenditure over 500 SGD"
#             else:
#                 reward_value = str(0.005 * amount)
#                 calculation_reason = "0.5 percent cashback on all expenditure"

#         elif card_type == 'scis_shopping':
#             """code"""
#         elif card_type == 'scis_premiummiles':
#             """code"""
#         elif card_type == 'scis_platinummiles':
#             """code"""
#         else:
#             return """error no such card"""

#     reward = {
#         'reward_id': '',
#         'card_id': card_id,
#         'card_type': card_type,
#         'reward_value': reward_value,
#         'date': transaction_date,
#         'merchant_name': merchant_name,
#         'calculation_reason': calculation_reason,
#         'is_exclusion': is_exclusion
#     }

#     return reward


#mockup transaction
transaction1 = {
        "id": '7ce56f44-659a-453f-8bc4-5a102faada42',
        "cardId": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "Collier",
        "mcc": "4642",
        "currency": "SGD",
        "amount": "285.96",
        "sgdAmount": "2001",
        "transactionId": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "date": "27/8/2021",
        "cardPan": "6771-8964-5359-9669",
        "cardType": "scis_freedom",
    }

get_reward(transaction1)


transaction2 = {
        "id": '7ce56f44-659a-453f-8bc4-5a102faada42',
        "cardId": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "Grab",
        "mcc": "4642",
        "currency": "SGD",
        "amount": "285.96",
        "sgdAmount": "132.81",
        "transactionId": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "date": "27/8/2021",
        "cardPan": "6771-8964-5359-9669",
        "cardType": "scis_freedom",
    }

get_reward(transaction2)

transaction3 = {
        "id": '7ce56f44-659a-453f-8bc4-5a102faada42',
        "cardId": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "AXS",
        "mcc": "9399",
        "currency": "SGD",
        "amount": "285.96",
        "sgdAmount": "100.53",
        "transactionId": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "date": "27/8/2021",
        "cardPan": "6771-8964-5359-9669",
        "cardType": "scis_freedom",
    }

get_reward(transaction3)

transaction4 = {
        "id": '7ce56f44-659a-453f-8bc4-5a102faada42',
        "cardId": "0fd148a9-a350-4567-9e6d-d768ab9c1932",
        "merchant": "Blacklisted Merchant",
        "mcc": "9399",
        "currency": "SGD",
        "amount": "285.96",
        "sgdAmount": "50.67",
        "transactionId": "07110e8bf85f1a1229eaa5dcbdea68c51d537218143d0021945cfae8861e3efc",
        "date": "27/8/2021",
        "cardPan": "6771-8964-5359-9669",
        "cardType": "scis_freedom",
    }

get_reward(transaction4)

