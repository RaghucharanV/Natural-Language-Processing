from flask import Flask, render_template, request
from load import predict_text_and_log
app = Flask(__name__)

def predict_text(input_text):
    res = predict_text_and_log(input_text)
    return res

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        # Get the input text from the form
        input_text = request.form['input_text']

        #result of prediction
        prediction = predict_text(input_text)

        # Prepare the result to be displayed on the same page
        result = {'input_text': input_text, 'prediction': prediction}

    # Render the home template with the result
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080)
