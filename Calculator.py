from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def american_to_decimal(american_odds):
    if american_odds > 0:
        return (american_odds / 100) + 1
    elif american_odds < 0:
        return (100 / abs(american_odds)) + 1
    else:
        return 1

def calculate_hedge(original_bet, odds_original, odds_hedge, hedge_percentage=100, odds_type='American'):
    if odds_type == 'American':
        odds_original = american_to_decimal(odds_original)
        odds_hedge = american_to_decimal(odds_hedge)

    max_hedge_amount = int(round((original_bet * odds_original) / odds_hedge))
    custom_hedge = int(round(max_hedge_amount * (hedge_percentage / 100)))

    payout_original = int(round(original_bet * odds_original))
    payout_hedge = int(round(custom_hedge * odds_hedge))

    profit_if_original_wins = int(round(payout_original - (original_bet + custom_hedge)))
    profit_if_hedge_wins = int(round(payout_hedge - (original_bet + custom_hedge))) if custom_hedge > 0 else 0

    return max_hedge_amount, custom_hedge, profit_if_original_wins, profit_if_hedge_wins

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            original_bet = float(request.form.get('original_bet', 0))
            odds_original = float(request.form.get('odds_original', 0))
            odds_hedge = float(request.form.get('odds_hedge', 0))
            odds_type = request.form.get('odds_type')

            if original_bet < 0 or odds_original == 0 or odds_hedge == 0:
                raise ValueError("Please enter valid positive numbers for bets and non-zero odds.")

            max_hedge_amount, custom_hedge, profit_if_original_wins, profit_if_hedge_wins = calculate_hedge(
                original_bet, odds_original, odds_hedge, hedge_percentage=100, odds_type=odds_type
            )

            return render_template(
                'index.html', 
                max_hedge_amount=max_hedge_amount,
                custom_hedge=custom_hedge, 
                profit_if_original_wins=profit_if_original_wins, 
                profit_if_hedge_wins=profit_if_hedge_wins,
                original_bet=original_bet,
                odds_original=odds_original,
                odds_hedge=odds_hedge,
                odds_type=odds_type,
                show_advanced=True
            )

        except ValueError as e:
            error_message = str(e)
            return render_template('index.html', error=error_message, show_advanced=False)

    return render_template('index.html', custom_hedge=None, show_advanced=False)

# New AJAX endpoint for hedge amount calculation
@app.route('/calculate_hedge', methods=['POST'])
def calculate_hedge_ajax():
    data = request.get_json()
    original_bet = float(data['original_bet'])
    odds_original = float(data['odds_original'])
    odds_hedge = float(data['odds_hedge'])
    hedge_percentage = float(data['hedge_percentage'])
    odds_type = data.get('odds_type', 'American')

    max_hedge_amount, custom_hedge, profit_if_original_wins, profit_if_hedge_wins = calculate_hedge(
        original_bet, odds_original, odds_hedge, hedge_percentage=hedge_percentage, odds_type=odds_type
    )

    return jsonify({
        'max_hedge_amount': max_hedge_amount,
        'custom_hedge': custom_hedge,
        'profit_if_original_wins': profit_if_original_wins,
        'profit_if_hedge_wins': profit_if_hedge_wins,
    })

if __name__ == '__main__':
    app.run(debug=True)
