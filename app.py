from flask import Flask, request, jsonify
import pandas as pd
from rapidfuzz import process, fuzz

app = Flask(__name__)

brands = pd.read_csv("data/brands.csv")
companies = pd.read_csv("data/companies.csv")

#irrelevant data
brands_to_rem = ['id', 'website', 'allOf']
companies_to_rem = ['id']

brands['name_lower'] = brands['name'].str.lower()
companies['name_lower'] = companies['name'].str.lower()

brands_names = brands['name_lower'].dropna().tolist()
companies_names = companies['name_lower'].dropna().tolist()

#low threshold for handling typos entered by the user
def fuzzy_search(name, choices, threshold=72):
    name = name.lower()
    match = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
    if (match and match[1] >= threshold):
        return match[0]  
    return None

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    input_name = data.get('name', '').strip().lower()

    if (not input_name):
        return jsonify({'error': 'No name provided, enter a name to search'}), 400

    #matching the names entered in brands csv
    match_name = fuzzy_search(input_name, brands_names)
    if match_name:
        row = brands[brands['name_lower'] == match_name]
        if (not row.empty):
            result = row.drop(columns=brands_to_rem + ['name_lower']).iloc[0].to_dict()
            return jsonify({
                'source': 'brands',
                'match': row.iloc[0]['name'], 
                'data': result
            })

    #matching the names entered in companies csv if not found in brands
    match_name = fuzzy_search(input_name, companies_names)
    if (match_name):
        row = companies[companies['name_lower'] == match_name]
        if (not row.empty):
            result = row.drop(columns=companies_to_rem + ['name_lower']).iloc[0].to_dict()
            return jsonify({
                'source': 'companies',
                'match': row.iloc[0]['name'],  
                'data': result
            })

    return jsonify({'error': 'Please provide a name to search.'}), 400

@app.route('/')
def index():
    return jsonify({"message": "The API is running."})

if __name__ == '__main__':
    app.run()