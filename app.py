from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM

app = Flask(__name__)
CORS(app)

model = AutoModelForCausalLM.from_pretrained("mental-health-chatbot-model")
tokenizer = AutoTokenizer.from_pretrained("mental-health-chatbot-model")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    prompt = f"User: {user_message}\nBot:"
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=128,
        temperature=0.7,
        top_k=50,
        top_p=0.9,
        do_sample=True
    )
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    bot_reply = full_response.split("Bot:")[-1].strip()
    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
