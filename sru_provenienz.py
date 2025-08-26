import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        """
    # Provenienzdaten explorieren
    ## Ein Notebook für Datenabfragen an der [SRU-Schnittstelle](https://wiki.k10plus.de/spaces/K10PLUS/pages/27361342/SRU) des [k10plus](https://www.bszgbv.de/services/k10plus/)
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    Dieses Notebook ist ein [Marimo](https://docs.marimo.io/)-Notebook – es kann als App oder in der Code-Ansicht ausgeführt werden.
    Um zwischen den Ansichten zu wechseln, drücken Sie **Strg + .** oder drücken Sie den button "Toggle app view" unten rechts.
    """
    )
    return


@app.cell
def _():
    # import necessary libraries
    import marimo as mo
    import requests
    import xml.etree.ElementTree as ET
    import unicodedata
    from lxml import etree
    from urllib.parse import urlencode
    import pandas as pd
    import altair as alt
    return ET, alt, etree, mo, pd, requests, unicodedata, urlencode


@app.cell
def _(mo):
    # define variable and ui-element for query text
    querytext = mo.ui.text(placeholder="Suchbegriff...", label="Suchbegriff")
    return (querytext,)


@app.cell
def _(mo):
    # define switch for search-type
    einstieg = mo.ui.dropdown(options=["Titel-Schlagwort", "Provenienz-Schlagwort"], label="Sucheinstieg")
    return (einstieg,)


@app.cell
def _(mo):
    # define variable and ui-element for query text with index-terms
    text = mo.ui.text(placeholder="Suchstring", label="Alternativ: Suchstring (z.B.: 'pica.prk=Sammlung Jochen Früh AND pica.tit=Cand*')")

    return (text,)


@app.cell
def _(mo):
    mo.md(
        """
    Für die Suche über die SRU-Schnittstelle des k10plus (Basis-Url: [https://sru.k10plus.de/opac-de-627](https://sru.k10plus.de/opac-de-627)) muss die Suchanfrage u.a. spezifizieren, welches Ausgabeformat die Schnittstelle zurückgeben soll (im Folgenden wird *marcxml* verwendet) und welcher/welcher Suchschlüssel mit welchen Werten abgefragt werden sollen.

    Für eine Stichwortsuche nach dem Wort "Faust" im Titel wäre bspw. der Suchstring "pica.tit=Faust" zu verwenden.  

    Eine Übersicht der Indexschlüssel findet sich [hier](https://format.k10plus.de/k10plushelp.pl?cmd=idx_s). Für das Folgende werden zwei Suchschlüssel verwendet: pica.tit für die Suche in Titeln, pica.prk für die Suche nach Provenienzinformationen. 

    Alternativ können Sie einen Suchstring frei eingeben; dabei sind auch Operatoren wie *and* oder *not* möglich.
    """
    )
    return


@app.cell
def _(einstieg, mo, querytext, text):
    mo.hstack([mo.vstack([einstieg, querytext]),text])

    return


@app.cell
def _(einstieg, querytext, text):
    if einstieg.value == "Provenienz-Schlagwort":
        query = "pica.prk="+querytext.value

    elif einstieg.value == "Titel-Schlagwort":
       query = "pica.tit="+querytext.value

    elif text.value != "":
        query = text.value


    return (query,)


@app.cell
def _(etree, requests, urlencode):
    def get_nr_of_records(query):
        base_url = "https://sru.k10plus.de/opac-de-627"
        params = {
            'recordSchema': 'marcxml',
            'operation': 'searchRetrieve',
            'version': '1.1',
            'maximumRecords': '1',
            'query': query
        }
        query_string = urlencode(params, safe='+')
        response = requests.get(base_url + '?' + query_string)
        content = response.content

        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(content, parser)
        try:
            number_of_records = int(root.find('.//{http://www.loc.gov/zing/srw/}numberOfRecords').text)
        except (AttributeError):
            print(response.request.url)
            raise ValueError("Kein numberOfRecords-Element in der Antwort -- Fehler in der Anfrage?")
        
        return number_of_records    
    return (get_nr_of_records,)


@app.cell
def _(get_nr_of_records, mo, query):
    nr_of_records = get_nr_of_records(query)
    mo.md(f"""
    Die Suche liefert: **{nr_of_records} Ergebnisse**

    Zunächst wird abgefragt, wie viele Treffer ihre Suche liefert. Im Folgenden Schritt können die Daten zu den einzelnen Treffern geladen werden. 

    **Beachten Sie**: Je nach Menge der Treffer kann dies eine Weile dauern. Für einen ersten Eindruck haben Siedie Möglichkeit, nur die ersten 100 Treffer zu laden. Beachten Sie bitte auch, dass jede Abfrage die Schnittstelle belastet und führen Sie nur Abfragen durch, die Sie für Ihre Arbeit benötigen.

    """
    )
    return (nr_of_records,)


@app.cell
def _(etree, requests, second_button, urlencode):
    def query_sru(query):
        base_url = "https://sru.k10plus.de/opac-de-627"
        params = {
            'recordSchema': 'marcxml',
            'operation': 'searchRetrieve',
            'version': '1.1',
            'maximumRecords': '100',
            'query': query
        }

        all_records = []

        while True:
            query_string = urlencode(params, safe='+')
            response = requests.get(base_url + '?' + query_string)

            # Print the URL for debugging
            print(response.url)

            content = response.content

            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(content, parser)

            # Get the number of records
            number_of_records = int(root.find('.//{http://www.loc.gov/zing/srw/}numberOfRecords').text)


            # Find all <record> elements
            records = root.findall('.//{http://www.loc.gov/MARC21/slim}record')

            # Add the current records to the list
            all_records.extend(records)
            if second_button.value == True:
                break
            # Check if we have retrieved all records
            if len(all_records) >= number_of_records:
                break

            # Update the startRecord parameter for the next request
            params['startRecord'] = len(all_records) + 1  # Start from the next record

        return all_records
    return (query_sru,)


@app.cell
def _(mo, nr_of_records):
    mo.stop(nr_of_records <1)

    first_button = mo.ui.run_button(label="Hole alle Ergebnisse")
    second_button = mo.ui.run_button(label="Hole die ersten 100 Ergebnisse")
    mo.vstack([first_button, second_button])
    return first_button, second_button


@app.cell
def _(first_button, mo, query, query_sru, second_button):
    mo.stop(first_button.value == False and second_button.value==False)
    records = query_sru(query)
    records_loaded = len(records)    
    mo.md(f"""Es wurden **{records_loaded}** Ergebnisse geladen

    Bei den geladenen Ergebnissen handelt es sich – egal, welchen Sucheinstieg Sie gewählt haben -- um Titeldaten, also bibliographische Angaben, zu den Titel (Manifestationen), die Ihre Suchabfrage liefert. 
    """      
    )    
    return (records,)


@app.cell
def _(ET, etree, records, unicodedata):
    def get_ex(record):
        ns = {"marc":"http://www.loc.gov/MARC21/slim"}
        record_str = ET.tostring(record, encoding='unicode')

        xml = etree.fromstring(unicodedata.normalize("NFC", record_str))

        exemplare = xml.xpath("marc:datafield[@tag = '361']/marc:subfield[@code = 'y']", namespaces=ns)
        return [exemplar.text for exemplar in exemplare]

    # Flatten the list of lists into a single list
    all_ex = [ex for sublist in [get_ex(record) for record in records] for ex in sublist]

    # get unique exemplare
    unique_exemplare = set(all_ex)


    return (unique_exemplare,)


@app.cell
def _(ET, etree, unicodedata):
    def parse_record(record):

        ns = {"marc":"http://www.loc.gov/MARC21/slim"}
        record_str = ET.tostring(record, encoding='unicode')

        xml = etree.fromstring(unicodedata.normalize("NFC", record_str))

        #Idn
        Idn = xml.xpath("marc:controlfield[@tag = '001']", namespaces=ns)
        try:
            Idn = Idn[0].text
        except:
            Idn = 'none'

        # Titel
        title = xml.xpath("marc:datafield[@tag = '245']/marc:subfield[@code='a']", namespaces=ns)
        try:
            title = title[0].text
        except:
            title = 'none'

        # Autor #100-subfield4=aut
        aut = xml.xpath("marc:datafield[@tag = '100']/marc:subfield[@code='4']", namespaces=ns)
        print(aut)
        try: 
            if aut[0].text == "aut":
                author = xml.xpath("marc:datafield[@tag ='100']/marc:subfield[@code='a']", namespaces=ns)
            author = author[0].text
        except:
            author = 'none'

        meta_dict = {"PPN":Idn,
                    "Titel":title,
                    "Autor":author}
        return meta_dict
    return (parse_record,)


@app.cell
def _(parse_record, pd, records):
    output = [parse_record(record) for record in records]
    df = pd.DataFrame(output)
    df
    return


@app.cell
def _(mo, unique_exemplare):
    mo.md(
        f"""
    Das Ergebnisset enthält Provenienzinformationen zu **{len(unique_exemplare)} Exemplaren**

    Wenn Sie eine Titelsuche ausgeführt haben, kann es sein, dass keine Provenienzinformationen ausgegeben werden -- in diesem Fall sind schlicht zu den gefundenen Titeln keine Provenienzinformationen hinterlegt. 

    Es ist auch möglich, dass Sie mehr Ergebnisse zu Exemplaren erhalten als zu den Titeldaten. Dies ist dann der Fall, wenn zu einem Titel mehrere Exemplare vorliegen.

    (N.B.: Es kann vorkommen, dass im Ergebnisset die Zahl der Exemplare von der Anzahl der eindeutigen Signaturen abweicht. Dies ist etwa bei Sammelbänden der Fall, die auf eine Signatur verweisen, deren Titel aber jeweils unterschiedliche Exemplarnummern haben.)
    """
    )
    return


@app.cell
def _(ET, etree, unicodedata):
    def parse_ex(record):

        ns = {"marc":"http://www.loc.gov/MARC21/slim"}
        record_str = ET.tostring(record, encoding='unicode')

        xml = etree.fromstring(unicodedata.normalize("NFC", record_str))

        data = []
        for field361 in xml.findall("marc:datafield[@tag='361']", namespaces=ns):
            row_data = {}
            for subfield in field361.findall("marc:subfield", namespaces=ns):
                code = subfield.get("code")
                text = subfield.text
                row_data[code] = text  # Use the subfield code directly as the column name

            data.append(row_data)

        return data
    return (parse_ex,)


@app.cell
def _(parse_ex, pd, records):
    output_ex = [parse_ex(record) for record in records]
    prov_statements = [item for sublist in output_ex for item in sublist]

    # Create the DataFrame
    df_ex = pd.DataFrame(prov_statements)
    df_ex= df_ex.rename(columns={"5":"Institution", "y": "EPN", "s": "Signatur", "o":"Typ", "a": "Name", "0":"Normdatum", "f":"Provenienzbegriff", "z": "Notiz", "u":"URI", "k":"Datum"})
    df_ex
    return (df_ex,)


@app.cell
def _():
    return


@app.cell
def _(chart_names, mo):
    content = ""
    if chart_names:
       content = '''
    ### Visualisierungen
    In Marimo lassen sich aus den Tabellen (bzw. Dataframes) direkt in der Oberfläche der App-Ansicht Visualisierungen generieren; hier bspw. eine Visualisierung auf Basis der in den Provenienzinformationen vorkommenden Namen.'''

    mo.md(content)

    return


@app.cell
def _(alt, df_ex):

    chart_names = (
        alt.Chart(df_ex)
        .mark_bar()
        .encode(
            x=alt.X(field='Name', type='nominal'),
            y=alt.Y(aggregate='count', type='quantitative'),
            tooltip=[
                alt.Tooltip(field='Name'),
                alt.Tooltip(aggregate='count')
            ]
        )
        .properties(
            height=290,
            width='container',
            config={
                'axis': {
                    'grid': False
                }
            }
        )
    )
    chart_names
    return (chart_names,)


@app.cell
def _(mo, transformed_df_ex):
    content_transform = ""
    if transformed_df_ex is not None:
       content_transform = '''
    ## Transformationen
    Auch Transformationen der Dataframes lassen sich direkt in der Oberfläche erstellen.
    '''

    mo.md(content_transform)
    return


@app.cell
def _(df_ex, mo):
    transformed_df_ex = mo.ui.dataframe(df_ex)
    transformed_df_ex
    return (transformed_df_ex,)


@app.cell
def _(df_ex_next, mo):
    content_df_ex_next = ""
    if df_ex_next is not None:
       content_df_ex_next = '''


    Als Beispiel hier eine Transformation, die die Tabelle der Exemplardaten reduziert nach Provenienzinformationen, die:

    1. der Institution DE-1 (Staatsbibliothek zu Berlin) zugeordnet sind,

    2. Als Provenienzbegriff "Stempel" angeben und

    3. über eine Notiz verfügen'''

    mo.md(content_df_ex_next)
    return


@app.cell
def _(df_ex):
    df_ex_next = df_ex
    df_ex_next = df_ex_next[(df_ex_next["Institution"].eq("DE-1")) & (df_ex_next["Provenienzbegriff"].eq("Stempel")) & (df_ex_next["Notiz"].notna())]
    df_ex_next
    return (df_ex_next,)


if __name__ == "__main__":
    app.run()

