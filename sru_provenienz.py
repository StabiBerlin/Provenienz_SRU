import marimo

__generated_with = "0.16.4"
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

    **Beachten Sie**: Je nach Menge der Treffer kann dies eine Weile dauern. Für einen ersten Eindruck haben Sie die Möglichkeit, nur die ersten 100 Treffer zu laden. Beachten Sie bitte auch, dass jede Abfrage die Schnittstelle belastet und führen Sie nur Abfragen durch, die Sie für Ihre Arbeit benötigen.

    """
    )
    return (nr_of_records,)


@app.cell
def func_parse(ET, etree, pd, unicodedata):
    def parse_record(record):

        ns = {"marc":"http://www.loc.gov/MARC21/slim"}
        record_str = ET.tostring(record, encoding='unicode')

        xml = etree.fromstring(unicodedata.normalize("NFC", record_str))

        #Idn
        Idn = xml.xpath("marc:controlfield[@tag = '001']", namespaces=ns)
        try:
            Idn = Idn[0].text
            URL = f"https://opac.k10plus.de/DB=2.299/PPNSET?PPN={Idn}&PRS=HOL&INDEXSET=21"
        except:
            Idn = pd.NA
            URL = pd.NA


        # Titel
        title = xml.xpath("marc:datafield[@tag = '245']/marc:subfield[@code='a']", namespaces=ns)
        try:
            title = title[0].text
        except:
            title = pd.NA

        # Autor #100-subfield4=aut
        aut = xml.xpath("marc:datafield[@tag = '100']/marc:subfield[@code='4']", namespaces=ns)
        try: 
            if aut[0].text == "aut":
                author = xml.xpath("marc:datafield[@tag ='100']/marc:subfield[@code='a']", namespaces=ns)
            author = author[0].text
        except:
            author = pd.NA

        # Jahr controlfield 008
        year = xml.xpath("marc:controlfield[@tag = '008']", namespaces=ns)
        try:
            year = year[0].text[7:11]  # Extract year substring from position 7 to 11 (yyyy format)]
        except:
            year = pd.NA


        meta_dict = {"PPN":Idn,
                    "Titel":title,
                    "Autor":author,
                    "Jahr": year,
                    "URL": URL}
        return meta_dict
    return (parse_record,)


@app.cell
def _(etree, requests, urlencode):
    def query_sru(query, max_records=100):
        base_url = "https://sru.k10plus.de/opac-de-627"
        params = {
            'recordSchema': 'marcxml',
            'operation': 'searchRetrieve',
            'version': '1.1',
            'maximumRecords': '100',   # maximum allowed per request
            'startRecord': 1,
            'query': query
        }

        all_records = []
        records_to_fetch = max_records

        while records_to_fetch > 0:
            batch_size = min(records_to_fetch, 100)  # fetch up to 100 each time
            params['maximumRecords'] = str(batch_size)
            params['startRecord'] = str(len(all_records) + 1)

            query_string = urlencode(params, safe='+')
            response = requests.get(base_url + '?' + query_string)

            print(response.url)  # for debugging

            content = response.content

            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(content, parser)

            # Find records in this batch
            batch_records = root.findall('.//{http://www.loc.gov/MARC21/slim}record')

            all_records.extend(batch_records)

            records_to_fetch -= batch_size

            # Stop if no more records returned (end of data)
            if not batch_records:
                break

        return all_records
    return (query_sru,)


@app.cell
def _(mo, nr_of_records):
    mo.stop(nr_of_records <1)

    all_button = mo.ui.run_button(label="Hole alle Ergebnisse")
    hundred_button = mo.ui.run_button(label="Hole die ersten max. 100 Ergebnisse")
    mo.vstack([hundred_button, all_button])

    # Slider to select number of records in 100-step increments, max capped at 10000 for usability
    max_limit_slider = mo.ui.slider(
        start=0, 
        stop=min(nr_of_records, nr_of_records), 
        value=0, 
        step=100, 
        label="Anzahl der Ergebnisse (in 100er Schritten)")

    load_slider_button = mo.ui.run_button(label="Ergebnisse laden")

    # Arrange buttons and slider side by side
    mo.hstack([
        mo.vstack([hundred_button, all_button]),
        mo.vstack([max_limit_slider, load_slider_button])
    ])
    return all_button, hundred_button, load_slider_button, max_limit_slider


@app.cell
def _(
    all_button,
    hundred_button,
    load_slider_button,
    max_limit_slider,
    mo,
    nr_of_records,
    query,
    query_sru,
):
    mo.stop(
        not (hundred_button.value or all_button.value or load_slider_button.value)
    )
    if hundred_button.value:
        records = query_sru(query, 100)
    elif all_button.value:
        records = query_sru(query, nr_of_records)
    elif load_slider_button.value:
        records = query_sru(query, max_limit_slider.value)

    records_loaded = len(records)

    mo.md(f"""Es wurden **{records_loaded}** Ergebnisse geladen

    Bei den geladenen Ergebnissen handelt es sich – egal, welchen Sucheinstieg Sie gewählt haben – um Titeldaten, also bibliographische Angaben, zu den Titel (Manifestationen), die Ihre Suchabfrage liefert. 
    """      
    )    
    return records, records_loaded


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
    return all_ex, unique_exemplare


@app.cell
def _(parse_record, pd, records):
    output = [parse_record(record) for record in records]
    df = pd.DataFrame(output)

    df
    return


@app.cell
def _(ET, etree, unicodedata):
    def parse_ex(record):

        ns = {"marc":"http://www.loc.gov/MARC21/slim"}
        record_str = ET.tostring(record, encoding='unicode')

        xml = etree.fromstring(unicodedata.normalize("NFC", record_str))

        # Extract the ID once per record
        controlfield_001 = xml.xpath("marc:controlfield[@tag='001']", namespaces=ns)
        record_id = controlfield_001[0].text if controlfield_001 else None

        # Extract the Title once per record
        title_field =xml.xpath("marc:datafield[@tag = '245']/marc:subfield[@code='a']", namespaces=ns)
        title = title_field[0].text if title_field else None

        data = []
        for field361 in xml.findall("marc:datafield[@tag='361']", namespaces=ns):
            row_data = {}
            for subfield in field361.findall("marc:subfield", namespaces=ns):
                code = subfield.get("code")
                text = subfield.text

                if code == "0":
                    if text is not None and text.startswith("(DE-588"):
                        row_data[code] = text
                    else:
                        continue

                row_data[code] = text  # Use the subfield code directly as the column name

            data.append(row_data)
            row_data["PPN"] = record_id
            row_data["Titel"] = title
            row_data["URL"] = f"https://opac.k10plus.de/DB=2.299/PPNSET?PPN={record_id}&PRS=HOL&INDEXSET=21"

        return data
    return (parse_ex,)


@app.cell
def _(all_ex, mo, unique_exemplare):
    mo.md(
        f"""
    Das Ergebnisset enthält **{len(all_ex)} Aussagen** zur Provenienz, die sich auf **{len(unique_exemplare)} Exemplare** beziehen.

    Wenn Sie eine Titelsuche ausgeführt haben, kann es sein, dass keine Provenienzinformationen ausgegeben werden – in diesem Fall sind schlicht zu den gefundenen Titeln keine Provenienzinformationen hinterlegt. 

    Es ist auch möglich, dass Sie mehr Ergebnisse zu Exemplaren erhalten als zu den Titeldaten. Dies ist dann der Fall, wenn zu einem Titel mehrere Exemplare vorliegen.

    (N.B.: Es kann vorkommen, dass im Ergebnisset die Zahl der Exemplare von der Anzahl der eindeutigen Signaturen abweicht. Dies ist etwa bei Sammelbänden der Fall, die auf eine Signatur verweisen, deren Titel aber jeweils unterschiedliche Exemplarnummern haben.)
    """
    )
    return


@app.cell
def _(mo, records_loaded):
    mo.stop(records_loaded<1)
    all_ex_button = mo.ui.run_button(label="Hole Provenienzinformationen zu allen Titeln")
    ppn_eingabe = mo.ui.text(placeholder="PPN-Liste hier eingeben", label="Nur Informationen zu Titeln aus PPN-Liste (kommasepariert)")
    list_button = mo.ui.run_button(label="Hole Provenienzinformationen zu den Titeln in der Liste")
    mo.vstack([all_ex_button, mo.hstack([ppn_eingabe, list_button])])
    return all_ex_button, list_button, ppn_eingabe


@app.cell
def _(all_ex_button, list_button, parse_ex, pd, ppn_eingabe, records):
    output_ex = [parse_ex(record) for record in records]

    if all_ex_button.value:
        prov_statements = [item for sublist in output_ex for item in sublist]
    elif list_button.value:
        ppn_list = [value.strip() for value in str(ppn_eingabe.value).split(",")]
        prov_statements = [item for sublist in output_ex for item in sublist if item["PPN"] in ppn_list]

    # Create the DataFrame
    df_ex = pd.DataFrame(prov_statements)
    df_ex= df_ex.rename(columns={"5":"Institution", "y": "EPN", "s": "Signatur", "o":"Typ", "a": "Name", "0":"Normdatum", "f":"Provenienzbegriff", "z": "Notiz", "u":"URI", "k":"Datum", "zu":"Test"})

    # add URLs for GND
    if "Normdatum" in df_ex.columns:
        df_ex["Normdatum"] = df_ex["Normdatum"].apply(
        lambda x: f"https://explore.gnd.network/gnd/{x.split(")",1)[1].strip()}" if pd.notna(x) else None)

    # Reorder df_ex to have 'Title', 'PPN' and 'URL' as the last columns
    # Desired columns to move to the end
    cols_end = ["Titel", "URL", "PPN"]
    # Create list of columns excluding those to move
    cols_start = [col for col in df_ex.columns if col not in cols_end]

    # Combine, putting desired columns at the end in order
    df_ex = df_ex[cols_start + cols_end]
    return (df_ex,)


@app.cell
def _(df_ex, etree, requests):
    def fetch_institution_name(inst_id):
        base_url = "https://services.dnb.de/sru/bib"
        params = {
            "version": "1.1",
            "operation": "searchRetrieve",
            "query": f"isil={inst_id}",
            "recordSchema": "PicaPlus-xml"
        }
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return inst_id # as fallback

        parser = etree.XMLParser(recover=True)
        xml = etree.fromstring(response.content, parser=parser)

        # Define namespace for ppxml elements if any; here assuming default (adjust if needed)
        ns = {"ppxml": "http://www.oclcpica.org/xmlns/ppxml-1.0"}    
        name_field = xml.xpath('.//ppxml:tag[@id="029A"]/ppxml:subf[@id="a"]', namespaces=ns)
        name = name_field[0].text
        if name_field:
            return name
        else:
            return inst_id

    # Cache dictionary for institution IDs to names
    inst_cache = {}

    # Get unique Institution IDs from df_ex
    unique_ids = df_ex["Institution"].unique()

    # Fetch names for all unique IDs not in cache yet
    for inst_id in unique_ids:
        if inst_id not in inst_cache and inst_id is not None:
            inst_cache[inst_id] = fetch_institution_name(inst_id)


    return (inst_cache,)


@app.cell
def _(inst_cache):
    print(inst_cache)
    return


@app.cell
def _(df_ex, inst_cache):
    # Map the IDs in df_ex["Institution"] to Names using cache
    df_ex["Institution"] = df_ex["Institution"].map(inst_cache).fillna(df_ex["Institution"])
    df_ex
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
    df_ex_next = df_ex_next[(df_ex_next["Institution"].eq("Staatsbibliothek zu Berlin - Preußischer Kulturbesitz, Haus Unter den Linden")) & (df_ex_next["Provenienzbegriff"].eq("Stempel")) & (df_ex_next["Notiz"].notna())]
    df_ex_next
    return (df_ex_next,)


@app.cell
def _(df_ex, mo):
    # Use mo.ui.data_explorer to provide an interactive way to explore the provenance exemplar data


    explorer = mo.ui.data_explorer(df_ex)

    title = mo.md("### Data explorer")
    combined = mo.vstack([title, explorer])
    combined
    return


if __name__ == "__main__":
    app.run()
