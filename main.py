from flask import Flask, render_template_string, request, send_file
import requests
import pandas as pd
from io import BytesIO

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTTP Status Checker</title>
</head>
<body>
    <h1>Bulk Domain HTTP Status Checker</h1>
    <form method="POST" action="/" enctype="multipart/form-data">
        <textarea name="domains" rows="10" cols="50" placeholder="Enter one domain per line"></textarea><br><br>
        <button type="submit">Check Status</button>
    </form>
    {% if results %}
        <h2>Results</h2>
        <table border="1">
            <tr>
                <th>Domain</th>
                <th>Status</th>
            </tr>
            {% for domain, status in results %}
            <tr>
                <td>{{ domain }}</td>
                <td>{{ status }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <form action="/export" method="GET">
            <button type="submit">Export to CSV</button>
        </form>
    {% endif %}
</body>
</html>
"""

results = []

@app.route("/", methods=["GET", "POST"])
def index():
    global results
    if request.method == "POST":
        domains = request.form["domains"].splitlines()
        results = []
        for domain in domains:
            domain = domain.strip()
            if not domain:
                continue
            try:
                response = requests.get(f"http://{domain}", timeout=5)
                status = response.status_code
            except requests.exceptions.RequestException as e:
                status = f"Error: {e}"
            results.append((domain, status))
    return render_template_string(HTML_TEMPLATE, results=results)

@app.route("/export", methods=["GET"])
def export():
    global results
    if not results:
        return "No data to export", 400

    df = pd.DataFrame(results, columns=["Domain", "HTTP Status"])
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="http_status_results.csv",
        mimetype="text/csv",
    )

if __name__ == "__main__":
    app.run(debug=True)
