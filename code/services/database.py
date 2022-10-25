POLICY_DATABASE = {
    "scis_shopping/01-01-2022": {
        "campaign_conditions": [
            {
                "merchant_category_include": "Online",
                "percentage_of_amount": "10",
                "calculation_reason": "10 points/SGD on all online spend",
                "campaign_id": "01-01-2020_SCIS Shopping",
                "campaign_priority": "0"
            },
            {
                "merchant_category_include": "Shopping",
                "percentage_of_amount": "4",
                "calculation_reason": "4 points/SGD on all shopping spend",
                "campaign_id": "01-01-2020_SCIS Shopping",
                "campaign_priority": "0"
            },
            {
                "percentage_of_amount": "1",
                "calculation_reason": "1 point/SGD on spend",
                "campaign_id": "01-01-2020_SCIS Shopping",
                "campaign_priority": "0"
            }
        ],
        "exclusion_conditions": {
            "mcc":
            {
                "6051": "Quasi Cash Merchants - Prepaid top-ups",
                "9399": "Government Services-Not Elsewhere Classified | Excluded",
                "6540": "POI (Point of Interaction) Funding Transactions (Excluding MoneySend) | Taxis & public transport"
            },
            "merchant":
            {
                "Blacklisted Merchant": "Merchant has been blacklisted"
            }
        }
    }
}

CAMPAIGN_SERVICE_TABLE = [
    {
        "campaign_name": "Grab promo",
        "campaign_start_date": "10-06-2022",
        "campaign_description": "Grab promo",
        "card_type": "scis_shopping",
        "campaign_end_date": "11-06-2022",
        "campaign_id": "01-06-2021_Grab promo",
        "campaign_priority": "50",
        "campaign_conditions": [
            {
                "campaign": "Grab"
            }
            # {
            #     "amount_greater_than": "100",
            #     "merchant_name_include": ["Grab"],
            #     "percentage_of_amount": "4",
            #     "calculation_reason": "Grab Promo - 4 miles per dollar with Grab, min spend 100 SGD"
            # }
        ]
    },
    {
        "campaign_name": "SCIS Shopping Card Base",
        "campaign_start_date": "09-06-2022",
        "campaign_description": "SCIS Shopping Card Base campaign",
        "card_type": "scis_shopping",
        "campaign_end_date": "11-06-2022",
        "campaign_id": "01-01-2020_SCIS Shopping Card Base",
        "campaign_priority": "0",
        "campaign_conditions": [
            {
                "campaign": "Base top"
            },
            {
                "campaign": "Base mid"
            },
            {
                "campaign": "Base low"
            }
            # {
            #     "merchant_category_include": "Online",
            #     "percentage_of_amount": "10",
            #     "calculation_reason": "10 points/SGD on all online spend",
            # },
            # {
            #     "merchant_category_include": "Shopping",
            #     "percentage_of_amount": "4",
            #     "calculation_reason": "4 points/SGD on all shopping spend",
            # },
            # {
            #     "percentage_of_amount": "1",
            #     "calculation_reason": "1 point/SGD on spend",
            # }
        ]
    },
    {
        "campaign_name": "Shopee promo",
        "campaign_start_date": "09-06-2022",
        "campaign_description": "Shopee promo",
        "card_type": "scis_shopping",
        "campaign_end_date": "10-06-2022",
        "campaign_id": "01-06-2021_Shopee promo",
        "campaign_priority": "100",
        "campaign_conditions": [
            # {
            #     "merchant_name_include": ["Shopee"],
            #     "percentage_of_amount": "5",
            #     "calculation_reason": "Shopee Promo - 5 points per dollar with Shopee"
            # }
            {
                "campaign": "Shopee"
            }
        ]
    },
    # {
    #     "campaign_name": "Freedom Card Base",
    #     "campaign_start_date": "01-01-2020",
    #     "campaign_description": "SCIS Freedom Card Base cashback amounts",
    #     "card_type": "scis_freedom",
    #     "campaign_end_date": "31-12-2022",
    #     "campaign_id": "01-01-2020_Freedom Card Base",
    #     "campaign_priority": "0",
    #     "campaign_conditions": [
    #         {
    #             "amount_greater_than": "2000",
    #             "percentage_of_amount": "0.03",
    #             "calculation_reason": "3 percent cashback for all expenditure above 2000 SGD"
    #         },
    #         {
    #             "amount_greater_than": "500",
    #             "percentage_of_amount": "0.01",
    #             "calculation_reason": "1 percent cashback for all expenditure above 500 SGD"
    #         },
    #         {
    #             "percentage_of_amount": "0.005",
    #             "calculation_reason": "0.5 percent cashback for all expenditure"
    #         }
    #     ]
    # },
    # {
    #     "campaign_name": "Platinum Miles Card Base",
    #     "campaign_start_date": "01-01-2020",
    #     "campaign_description": "SCIS Platinum Miles Card Base campaign",
    #     "card_type": "scis_platinummiles",
    #     "campaign_end_date": "31-12-2022",
    #     "campaign_id": "01-01-2020_Platinum Miles Card Base",
    #     "campaign_priority": "0",
    #     "campaign_conditions": [
    #         {
    #             "mcc_type_include": "hotel",
    #             "currency_exclude": "SGD",
    #             "percentage_of_amount": "6",
    #             "calculation_reason": "6 miles/SGD on all foreign hotel spend"
    #         },
    #         {
    #             "mcc_type_include": "hotel",
    #             "percentage_of_amount": "3",
    #             "calculation_reason": "3 miles/SGD on all hotels spend"
    #         },
    #         {
    #             "currency_exclude": "SGD",
    #             "percentage_of_amount": "3",
    #             "calculation_reason": "3 miles/SGD on all foreign card spend"
    #         },
    #         {
    #             "percentage_of_amount": "1.4",
    #             "calculation_reason": "1.4 miles/SGD spent"
    #         }
    #     ]
    # },
    # {
    #     "campaign_name": "Premium Miles Card Base",
    #     "campaign_start_date": "01-01-2020",
    #     "campaign_description": "SCIS Premium Miles Card Base campaign",
    #     "card_type": "scis_premiummiles",
    #     "campaign_end_date": "31-12-2022",
    #     "campaign_id": "01-01-2020_Premium Miles Card Base",
    #     "campaign_priority": "0",
    #     "campaign_conditions": [
    #         {
    #             "mcc_type_include": "hotel",
    #             "percentage_of_amount": "3",
    #             "calculation_reason": "3 miles/SGD on all hotels spend"
    #         },
    #         {
    #             "currency_exclude": "SGD",
    #             "percentage_of_amount": "2.2",
    #             "calculation_reason": "2.2 miles/SGD on all foreign card spend"
    #         },
    #         {
    #             "percentage_of_amount": "1.1",
    #             "calculation_reason": "1.1 miles/SGD spent"
    #         }
    #     ]
    # }
]

EXCLUSION_SERVICE_TABLE = [
    {
    "exclusion_id": "09-06-2022_Standard Exclusions",
    "exclusion_name": "Standard Exclusions",
    "exclusion_start_date": "09-06-2022",
    "exclusion_end_date": "11-06-2022",
    "card_type": ["scis_shopping", "scis_freedom"],
    "exclusion_conditions": {
        "mcc":
            {
                "6051": "Quasi Cash Merchants - Prepaid top-ups",
                "9399": "Government Services-Not Elsewhere Classified | Excluded",
                "6540": "POI (Point of Interaction) Funding Transactions (Excluding MoneySend) | Taxis & public transport"
            },
        "merchant":
            {
                "Blacklisted Merchant": "Merchant has been blacklisted"
            }
        }
    }
]
