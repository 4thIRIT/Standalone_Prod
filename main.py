import streamlit as st
import requests
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TapexTokenizer, BartForConditionalGeneration
import pandas as pd
from typing import List
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TapexTokenizer, BartForConditionalGeneration
import pandas as pd
import requests
import json


#text classification model function
def text_Classification(text, review_categories):
    response = requests.post('http://20.55.40.136:8085/api/v1/classify',
                            data=json.dumps({"text": text, "labels": review_categories}), verify=False)
    return response.json()['answer']

#to get special terms and special terms count
def special_terms_extractor (SAP_Note):
    country_abbreviations = [
        "AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ",
        "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR",
        "IO", "BN", "BG", "BF", "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD", "CL", "CN", "CX", "CC",
        "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO",
        "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF",
        "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY",
        "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM",
        "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY",
        "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT",
        "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NC", "NZ",
        "NI", "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH",
        "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN", "LC", "MF", "PM", "VC",
        "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI", "SB", "SO", "ZA", "GS",
        "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK",
        "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU",
        "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "M0", "G0"
    ]

    special_terms = []
    special_term_count = 0
    labels = "Alphanumeric,Text,Integer,Float"
    lines = SAP_Note.split(' ')
    for line in lines:
            if line[:2] in country_abbreviations and 4<len(line)<7:
                classification = text_Classification(line, labels)
                label = classification['labels'][0]
                score = classification['scores'][0]
                if label == "Alphanumeric":
                    if float(score) > 0.98:
                        special_terms.append(line)

    special_term_count =len(special_terms)

    return special_terms , special_term_count

#based on conditions decide what case it falls into
def decider(Line_items, Special_terms_count):

    path = 0
    if Line_items == 1 and Special_terms_count == 1:
        path = 1
        
    elif Line_items == 1 and Special_terms_count > 1:
        path = 2
        
    elif Line_items > 1 and Special_terms_count == 1:
        path = 3
        
    elif Line_items > 1 and Special_terms_count > 1:
        path = 4
        
    else:
        pass
    
    return path

#to get material type
def material_type (SAP_Note):
    material_type = text_Classification(SAP_Note, "All Spare Parts,SIKO Parts,Individual Spare Parts")['labels'][0]
    return material_type

#to process Table
def process_data(file):
    df = file.read()
    Table = pd.read_excel(df)
    for column in Table.columns:
        if Table[column].dtype == float:
            Table[column] = Table[column].astype(str)
    return Table

#to get CHTUS discount
def discount_CHTUS_2 (Table, Special_term, Material_type, Delivery_time, Delivery_period):
    while Delivery_time > 0:
        filtered_df = Table.loc[(Table['Special_Term'].isin([(Special_term)])) & (Table['Scope'].isin([Material_type])) & (Table['Delivery_Time'].isin([Delivery_time])) & (Table['Delivery_Period'].isin([Delivery_period])) ]
        if not filtered_df.empty:
            return filtered_df['CHTUS_Discount'].values[0]
        else:
            Delivery_time -= 1
    return 0

#to get Delivery time discount
def discount_Delivery_Time_2 (Table, Special_term, Material_type, Delivery_time, Delivery_period):
    while Delivery_time >= 0:
        filtered_df = Table.loc[(Table['Special_Term'].isin([(Special_term)])) & (Table['Scope'].isin([Material_type])) & (Table['Delivery_Time'].isin([Delivery_time])) & (Table['Delivery_Period'].isin([Delivery_period])) ]
        if not filtered_df.empty:
            return filtered_df['Delivery_Time_Discount'].values[0]
        
        else:
            Delivery_time -= 1
    return 0

#to get LBU discount
def discount_LBU_2 (Table, Special_term, Material_type, Delivery_time, Delivery_period):
    while Delivery_time >= 0:
        filtered_df = Table.loc[(Table['Special_Term'].isin([(Special_term)])) & (Table['Scope'].isin([Material_type])) & (Table['Delivery_Time'].isin([Delivery_time])) & (Table['Delivery_Period'].isin([Delivery_period])) ]
        
        if not filtered_df.empty:
            return filtered_df['LBU_Discount'].values[0]
        
        else:
            Delivery_time -= 1
    return 0

#to get Total internal discount
def discount_Total_Internal_2 (Table, Special_term, Material_type, Delivery_time, Delivery_period):
    while Delivery_time >= 0:
        filtered_df = Table.loc[(Table['Special_Term'].isin([(Special_term)])) & (Table['Scope'].isin([Material_type])) & (Table['Delivery_Time'].isin([Delivery_time])) & (Table['Delivery_Period'].isin([Delivery_period])) ]
        if not filtered_df.empty:
            return filtered_df['Total_Internal_Discount'].values[0]
        
        else:
            Delivery_time -= 1
    return 0


#to get Delivery time discount
def get_discount (Discount_type,Table, Special_term, Material_type, Delivery_time, Delivery_period):
    while Delivery_time >= 0:
        filtered_df = Table.loc[(Table['Special_Term'].isin([(Special_term)])) & (Table['Scope'].isin([Material_type])) & (Table['Delivery_Time'].isin([Delivery_time])) & (Table['Delivery_Period'].isin([Delivery_period])) ]
        if not filtered_df.empty:
            return filtered_df[Discount_type].values[0]
        
        else:
            Delivery_time -= 1
    return 0

st.title("Calculate Discounts from PO")

#Input section: to take all necessary inputs for use with functions
file = st.file_uploader("Upload ATURB DB")
Delivery_time =st.selectbox("Delivery time",[1, 2, 4])
Delivery_period =st.selectbox("Delivery period",["Month(s)", "Week(s)", "Day(s)"])
SAP_Note =st.text_input("SAP Note")
Line_item_count=st.number_input("How many items?",1)
Items =[]
if Line_item_count:
    for x in range(Line_item_count):
        Items.append(st.selectbox("Select your material type",["Exchange Turbocharger", "Replacement Turbocharger", "All Spare Parts","SIKO Parts", "Individual Spare Parts"], key=x))


if st.button("SAP Button"):
    Table=process_data(file)
    Special_terms, Special_terms_count =special_terms_extractor (SAP_Note)
    Material_type = material_type (SAP_Note)
    Path= decider(Line_item_count,Special_terms_count)
    st.write(Special_terms)

    match Path:
        case 1: #When line items =1 and special terms =1 - done tbt
            Material_type =Items[0]
            Header_discount =discount_CHTUS_2(Table, Special_terms[0], Material_type, Delivery_time, Delivery_period)
            st.title("Header Discount: ")
            st.markdown(f"{Header_discount}%")

        case 2:#When line items =1 and special terms >1 - doubt this happens
            discounts = {}
            Material_type =Items[0]
            for special_term in Special_terms:
                discount =(discount_CHTUS_2(Table, special_term, Material_type, Delivery_time, Delivery_period))
                discounts[special_term] = discount
            Header_discount = min(discounts.values())
            st.write("Header Discount: ")
            st.markdown(Header_discount)
            Header_discount_key = max(discounts, key=discounts.get)
            discounts.pop(Header_discount_key)
            for key in discounts:
                discounts[key] = discounts[key] - Header_discount
            Position_discounts = discounts
            st.write("Position Discount: ")
            st.markdown(Position_discounts)

        case 3:#When line items >1 and special terms =1 - done tbt
            Header_discount =discount_CHTUS_2(Table, Special_terms[0], "All Spare Parts", Delivery_time, Delivery_period)
            delivery_time_discount = discount_Delivery_Time_2(Table, Special_terms[0], "All Spare Parts", Delivery_time, Delivery_period)
            st.markdown(f"Header Discount: { Header_discount}%")
            for material in Items:
                if material != "All Spare Parts":
                    Material_discount= discount_CHTUS_2(Table, Special_terms[0], material, Delivery_time, Delivery_period)
                    Position_discount =  float(Material_discount) - float(Header_discount)
                    if Position_discount < 0:
                        Position_discount = 0
                    if float(Position_discount) - float(delivery_time_discount)>0:
                        Position_discount = float(Position_discount) - float(delivery_time_discount)
                    else:
                        Position_discount= float(Position_discount)
                    st.markdown(f"{Position_discount}% for {material}")
                    
            #check total internal discount

        case 4:#When line items >1 and special terms >1, <3 -done tbt
            discounts = {}
            p_discounts={}
            for special_term in Special_terms:
                discount = discount_CHTUS_2(Table, special_term, "All Spare Parts", Delivery_time, Delivery_period)
                discounts[special_term] = float(discount)
            Header_discount = max(discounts.values())
            Header_discount_key = max(discounts, key=discounts.get)
            discounts.pop(Header_discount_key)
            for key in discounts:
                Material_discount= discount_CHTUS_2(Table, key, Material_type, Delivery_time, Delivery_period)
                if Material_discount < 0:
                    Material_discount =0
                p_discounts[key] = float(Material_discount)
            Position_discount = max(p_discounts.values())
            st.markdown(f"Header Discount: {Header_discount}")
            st.markdown(f"{Position_discount} for {Items[1]}")

