from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


# Initialize the Flask app
app = Flask(__name__)

# Load the trained model
model = joblib.load(r'random_forest_model_online_payment_fraud_detection (1).pkl')

# Function to send email alert
def send_email_alert(transaction_details):
    # Email configurations
    from_email = "haridatapro7@gmail.com"
    to_email = "dineshkumarpolavarapu5@gmail.com"
    subject = "Fraud Alert: Transaction Detected"
    
    # Create detailed body with transaction information
    body = f"""A fraudulent transaction was detected!
    
Transaction Details:
- Type: {transaction_details['type']}
- Amount: {transaction_details['amount']}
- Original Balance: {transaction_details['oldbalanceOrg']}
- Destination Balance: {transaction_details['oldbalanceDest']}

Please review the transaction immediately."""

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, "jpwn ssrd mswy yhjp")
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email alert sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

import random as rd
# Function to make predictions
def predict_fraud(step, type, amount, oldbalanceOrg, oldbalanceDest):
    # Prepare the input for prediction
    data = pd.DataFrame([[step, type, amount, oldbalanceOrg, oldbalanceDest]], columns=['step', 'type', 'amount', 'oldbalanceOrg', 'oldbalanceDest'])
    
    # Encode 'type' as necessary (assuming 'type' is categorical)
    type_mapping = {
        'CASH_OUT': 0,
        'PAYMENT': 1,
        'CASH_IN': 2,
        'TRANSFER': 3,
        'DEBIT': 4
    }

    # Map the 'type' to integer value
    data['type'] = data['type'].map(type_mapping)

    # Predict the class (Fraud or Non-Fraud)
    prediction = model.predict(data)[0]
    prediction_score = model.predict_proba(data)[:, 1][0]
    
    # Flip prediction based on random number

    prediction = 1 if rd.random() < 0.5 else 0

    print(prediction)
    # If fraud is detected, send an email alert with transaction details
    if prediction == 1:
        transaction_details = {
            'type': type,
            'amount': amount,
            'oldbalanceOrg': oldbalanceOrg,
            'oldbalanceDest': oldbalanceDest
        }
        email_sent = send_email_alert(transaction_details)
        if not email_sent:
            print("Warning: Fraud detected but email alert failed")

    return "Fraud" if prediction == 1 else "Non-Fraud", prediction_score

# Route to display the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the prediction
@app.route('/predict', methods=['POST'])
def predict():
    step = int(request.form['step'])
    type = request.form['type']
    amount = float(request.form['amount'])
    oldbalanceOrg = float(request.form['oldbalanceOrg'])
    oldbalanceDest = float(request.form['oldbalanceDest'])

    # Get the prediction
    prediction, prediction_score = predict_fraud(step, type, amount, oldbalanceOrg, oldbalanceDest)

    # Return result as JSON
    return jsonify({
        'prediction': prediction,
        'prediction_score': round(prediction_score, 4)
    })

if __name__ == '__main__':
    app.run(debug=True , host='0.0.0.0', port=5000)
