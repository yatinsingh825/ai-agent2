import matplotlib.pyplot as plt
import json


def generate_report(history, filename="report.html"):

    months = [h["month"] for h in history]
    users = [h["users"] for h in history]
    revenue = [h["revenue"] for h in history]
    cash = [h["cash"] for h in history]

    # Charts
    plt.figure()
    plt.plot(months, users)
    plt.title("User Growth")
    plt.xlabel("Month")
    plt.ylabel("Users")
    plt.savefig("users_chart.png")

    plt.figure()
    plt.plot(months, revenue)
    plt.title("Revenue Growth")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.savefig("revenue_chart.png")

    plt.figure()
    plt.plot(months, cash)
    plt.title("Cash Position")
    plt.xlabel("Month")
    plt.ylabel("Cash")
    plt.savefig("cash_chart.png")

    # HTML report
    html = f"""
    <html>
    <head>
    <title>Startup Simulation Report</title>
    </head>

    <body>

    <h1>Startup Simulation Report</h1>

    <h2>Growth Charts</h2>

    <img src="users_chart.png" width="600">
    <img src="revenue_chart.png" width="600">
    <img src="cash_chart.png" width="600">

    <h2>Final Metrics</h2>

    <pre>
    {json.dumps(history[-1], indent=4)}
    </pre>

    </body>
    </html>
    """

    with open(filename, "w") as f:
        f.write(html)

    print(f"📊 Performance report generated: {filename}")