from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/organizational-units')
def get_organizational_units_for_university():
    uid = request.args.get("uid")
    
    if not uid:
        return jsonify({"error": "Missing UID"}), 400
    
    try:
        url = f"https://diavgeia.gov.gr/opendata/organizations/{uid}/units"

        res = requests.get(
            url,
            headers={"Accept": "application/json"},
            params={"status": "active"}
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/decisions/published')
def get_published_decisions():
    uid = request.args.get("uid")
    year = request.args.get("year")

    if not uid:
        return jsonify({"error": "Missing UID"}), 400

    if not year:
        return jsonify({"error": "Missing decision year"}), 400
    
    # First, retrieve all the data from the first 6 moths. Diavgeia does not support longer periods
    # See: 'Αν οριστούν τιμές για τα from_issue_date και to_issue_date και το διάστημα που ορίζουν ξεπερνά τις 180 ημέρες, το σύστημα αυτομάτως εισάγει ως τιμή του to_issue_date την τιμή του from_issue_date "συν" 180 ημέρες.'

    from_date = f"{year}-01-01"
    to_date = f"{year}-06-30"

    url = "https://diavgeia.gov.gr/opendata/search"
    params = {
        "org": uid,
        "from_issue_date": from_date,
        "to_issue_date": to_date,
        "size": 1, # We don't want the actual results, we just need to count them
        "page": 0,
        "status": "published",
    }

    try:
        response1 = requests.get(url, headers={"Accept": "application/json"}, params=params)
        data = response1.json()
        decisionsCounter = data.get("info", []).get("total")

        from_date = f"{year}-07-01"
        to_date = f"{year}-12-30"

        params = {
            "org": uid,
            "from_issue_date": from_date,
            "to_issue_date": to_date,
            "size": 1,
            "page": 0,
            "status": "published",
        }

        # Now, we will repeat the request for the rest 6 months of the year
        # Again, we don't care about the results, we just need the counter.
        # The total counter is included in the response of diavgeia
        response2 = requests.get(url, headers={"Accept": "application/json"}, params=params)
        data2 = response2.json()
        decisionsCounter += data2.get("info", []).get("total")

        return {
            "totalPublished": decisionsCounter,
            "year": year 
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/decisions/revoked')
def get_revoked_decisions():
    uid = request.args.get("uid")
    year = request.args.get("year")

    if not uid:
        return jsonify({"error": "Missing UID"}), 400

    if not year:
        return jsonify({"error": "Missing decision year"}), 400
    
    # First, retrieve all the data from the first 6 moths. Diavgeia does not support longer periods
    # Reference: 'Αν οριστούν τιμές για τα from_issue_date και to_issue_date και το διάστημα που ορίζουν ξεπερνά τις 180 ημέρες, το σύστημα αυτομάτως εισάγει ως τιμή του to_issue_date την τιμή του from_issue_date "συν" 180 ημέρες.'

    from_date = f"{year}-01-01"
    to_date = f"{year}-06-30"

    url = "https://diavgeia.gov.gr/opendata/search"
    params = {
        "org": uid,
        "from_issue_date": from_date,
        "to_issue_date": to_date,
        "size": 500, # max for unauthenticated users is 500, but the revoked decisions are much less than this limit so is enough
        "page": 0, # first page
        "status": "revoked",
    }

    try:
        response1 = requests.get(url, headers={"Accept": "application/json"}, params=params)
        data = response1.json()
        decisionsCounter = data.get("info", []).get("total")
        decisions = data.get("decisions", [])
        privateDataRevokedDecisions = 0
        for d in decisions:
            if d.get("privateData") == True:
                privateDataRevokedDecisions += 1

        # Now, we will repeat the request for the rest 6 months of the year
        # The total counter is included in the response of diavgeia

        from_date = f"{year}-07-01"
        to_date = f"{year}-12-30"

        params = {
            "org": uid,
            "from_issue_date": from_date,
            "to_issue_date": to_date,
            "size": 500, # max for unauthenticated users is 500, but the revoked decisions are much less than this limit so is enough
            "page": 0, # first page
            "status": "revoked",
        }

        response2 = requests.get(url, headers={"Accept": "application/json"}, params=params)
        data2 = response2.json()
        decisionsCounter += data2.get("info", []).get("total")
        decisions2 = data2.get("decisions", [])
        for d in decisions2:
            if d.get("privateData") == True:
                privateDataRevokedDecisions += 1

        return {
            "totalRevoked": decisionsCounter,
            "totalRevokedWithPrivateData": privateDataRevokedDecisions,
            "year": year,
            "revokedTotal": decisions,
            "revokedWithPrivateData": decisions2
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
