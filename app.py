import eel
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sklearn.linear_model import LinearRegression

# Starte die Eel-Anwendung
eel.init('web')

def save_plot_to_base64(fig):
    """
    Bild in Base64 kodieren (um den Chart in HTML darzustellen)
    INPUT: Chart
    OUTPUT: Base64 Bild
    """
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)  
    return base64_image

def load_data(file_path):
    """
    Daten aus der gegebenen Excel einlesen
    INPUT: Dateipfad als String zur Excel-Datei
    OUTPUT: Gerichtetabelle, Getränketabelle als pandas Dataframe
    """
    bella_capri_gerichte = pd.read_excel(file_path, sheet_name="Gerichte")
    bella_capri_getränke = pd.read_excel(file_path, sheet_name="Getränke")
    return bella_capri_gerichte, bella_capri_getränke

@eel.expose
def get_average_demand():
    """
    Berechnet Durchschnittlichen Bedarf an Pizzen, Pasta und Salat
    OUTPUT: Dictionary mit den Durschschnittswerten aus der gegebenen Tabelle
    """
    bella_capri_gerichte, _ = load_data('BellaCapri.xlsx')
    average_demand = bella_capri_gerichte[['Pizza', 'Pasta', 'Salat']].mean()
    return average_demand.to_dict()

@eel.expose
def get_weekday_visitors():
    """
    Berechnung der Besucheranzahl pro Wochentag
    OUTPUT: Dictionary mit den Durschschnittswerten aus der gegebenen Tabelle pro Wochentag
    """
    bella_capri_gerichte, _ = load_data('BellaCapri.xlsx')
    weekday_visitors = bella_capri_gerichte.groupby('Wochentag')['Besucher'].mean()
    return weekday_visitors.to_dict()

@eel.expose
def get_drinks_demand():
    """
    Berechnung des Getränkebedarfs pro Tag (Getränke + Menge)
    OUTPUT: Dictionary mit den Durschschnittswerten aus der gegebenen Tabelle 
    """
    _, bella_capri_getränke = load_data('BellaCapri.xlsx')
    drinks_demand = bella_capri_getränke[['Mineralwasser', 'Apfelschorle', 'Cola', 'Bier', 'Wein', 'Sonstiges']].mean()
    return drinks_demand.to_dict()

# 
@eel.expose
def generate_charts():
    """
    Hauptfunktion zur Diagrammerstellung und Base64-Kodierung
    OUTPUT: Charts Dictionary mit Base64 Bildern
    """
    bella_capri_gerichte, bella_capri_getränke = load_data('BellaCapri.xlsx')

    # Berechnungen (LineareRegression, Durchschnitte)
    average_demand = bella_capri_gerichte[['Pizza', 'Pasta', 'Salat']].mean()
    X = bella_capri_gerichte[['Reservierungen']].values
    y = bella_capri_gerichte['Besucher'].values
    model = LinearRegression()
    model.fit(X, y)

    weekday_visitors = bella_capri_gerichte.groupby('Wochentag')['Besucher'].mean()

    drinks_demand = bella_capri_getränke[['Mineralwasser', 'Apfelschorle', 'Cola', 'Bier', 'Wein', 'Sonstiges']].mean()

    # Charts Dict anlegen
    charts = {}

    # Durchschnittlicher Bedarf an Pizza, Pasta und Salat Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    average_demand.plot(kind='bar', ax=ax, legend=False, color=['tomato', 'gold', 'green'])
    ax.set_title('Durchschnittlicher Bedarf an Pizza, Pasta und Salat pro Tag')
    ax.set_ylabel('Durchschnittliche Anzahl')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    charts['average_demand'] = save_plot_to_base64(fig)

    # Reservierungen vs Besucheranzahl (lineare Regression) Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(X, y, color='blue', label='Datenpunkte')
    ax.plot(X, model.predict(X), color='red', label='Regressionslinie')
    ax.set_title('Reservierungen vs Besucheranzahl')
    ax.set_xlabel('Reservierungen')
    ax.set_ylabel('Besucheranzahl')
    ax.legend()
    charts['reservation_vs_visitors'] = save_plot_to_base64(fig)

    # Besucheranzahl pro Wochentag Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    weekday_visitors.plot(kind='bar', ax=ax, color='lightblue')
    ax.set_title('Durchschnittliche Besucheranzahl pro Wochentag')
    ax.set_ylabel('Durchschnittliche Besucheranzahl')
    ax.set_xlabel('Wochentag')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    charts['weekday_visitors'] = save_plot_to_base64(fig)

    # Getränkekonsum pro Tag Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    drinks_demand.plot(kind='bar', ax=ax, color='lightblue')
    ax.set_title('Durchschnittlicher Getränkekonsum pro Tag')
    ax.set_ylabel('Menge')
    ax.set_xlabel('Getränke')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    charts['drinks_demand'] = save_plot_to_base64(fig)

    return charts

# Startet die App
eel.start('average_demand.html', size=(1200, 800))
