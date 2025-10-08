import marimo

__generated_with = "0.16.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    print("Hello from the Staatsbibliothek")
    return


@app.cell
def _():
    a = 6
    b = 2
    return a, b


@app.cell
def _(a, b):
    a+b
    return


@app.cell
def _(mo):
    slider = mo.ui.slider(start=1, stop=10, step=1)
    slider
    return (slider,)


@app.cell
def _(b, slider):
    slider.value+b
    return


@app.cell
def _(mo):
    mo.md(r"""# Überschrift""")
    return


@app.cell
def _():
    return


@app.cell
def _():
    import pandas as pd
    return (pd,)


@app.cell
def _(pd):
    data = {
        "Monat": ["Januar", "Februar", "März", "April", "Mai", "Juni"],
        "Besucherzahlen": [120, 150, 180, 80, 95, 110]
    }

    df = pd.DataFrame(data)
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    import matplotlib.pyplot as plt

    # Erstelle Liniendiagramm
    plt.figure(figsize=(10, 6))
    plt.bar(df['Monat'], df['Besucherzahlen'], color='skyblue')

    # Ergänze labels
    plt.xlabel('Monat')
    plt.ylabel('Besucherzahlen')
    plt.title('Besucherzahlen pro Monat')

    # Zeige die Visualisierung
    plt.show()
    return


@app.cell
def _(df):
    import plotly.express as px

    # Create a bar chart
    fig = px.bar(df, x='Monat', y='Besucherzahlen', title='Besucherzahlen pro Monat',
                 labels={'Monat':'Monat', 'Besucherzahlen':'Besucherzahlen'},
                 color='Monat', color_discrete_sequence=px.colors.qualitative.Plotly)

    # Show the plot
    fig.show()
    return (fig,)


@app.cell
def _(fig, mo):
    mo.md(f"""Here's a plot! {mo.as_html(fig)}""")
    return


@app.cell
def _(mo):
    mo.md(r"""## Eine Schnittstellenabfrage""")
    return


@app.cell
def _():
    import requests
    from urllib.parse import urlencode

    return requests, urlencode


@app.cell
def _(requests, urlencode):
    base_url = "https://sru.k10plus.de/opac-de-627"
    params = {
            'recordSchema': 'marcxml',
            'operation': 'searchRetrieve',
            'version': '1.1',
            'maximumRecords': '1',
            'query': 'pica.ppn=235702242'
        }
    query_string = urlencode(params, safe='+')
    response = requests.get(base_url + '?' + query_string)
    content = response.content
    print(content)
    return


if __name__ == "__main__":
    app.run()
