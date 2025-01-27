from kivy.app import App  # Importerer App-klassen fra Kivy, der bruges til at oprette hovedapplikationen
from kivy.uix.boxlayout import BoxLayout  # Importerer BoxLayout til at arrangere widgets i en boks-layout
from kivy.uix.label import Label  # Importerer Label, som bruges til at vise tekst
from kivy.properties import StringProperty, ListProperty  # Importerer egenskaber til dynamisk opdatering af data
import requests  # Importerer requests-biblioteket til at lave HTTP-anmodninger
from kivy.uix.image import AsyncImage  # Importerer AsyncImage til at indlæse billeder asynkront



#------------------------------------------------------------------------------------------- Datahåndtering
# Funktion til at verificere, om en given URL til et billede er gyldig og tilgængelig
def is_valid_image(url):
    try:
        response = requests.head(url, timeout=5)  # Sender en HTTP HEAD-anmodning til URL'en
        return response.status_code == 200  # Returnerer True, hvis statuskoden er 200 (OK)
    except:  # Fanger alle undtagelser
        return False  # Returnerer False, hvis anmodningen fejler

#------------------------------------------------------------------------------------------- UI
# Klasse for hovedvinduet, der håndterer layout og funktionalitet
class MainWindow(BoxLayout):
    search_input = StringProperty("")  # Gemmer det aktuelle søgeord indtastet af brugeren
    game_deals = ListProperty([])  # Liste til at holde data om spiltilbud
    game_titles = ListProperty([])  # Liste til at holde titlerne på spillene

    # ------------------------------------------------------------------------------------------- Datahåndtering
    # Funktion til at hente spiltilbud fra CheapShark API
    def fetch_game_deals(self):
        url = "https://www.cheapshark.com/api/1.0/deals?upperPrice=15"      # API URL med en maks. pris på $15
        try:
            response = requests.get(url)                                    # Sender en GET-anmodning til API'en
            response.raise_for_status()                                     # Stopper og kaster en fejl, hvis HTTP-status ikke er 200
            self.game_deals = response.json()[:50]                          # Gemmer de første 50 resultater fra API'en
            self.game_titles = [deal["title"] for deal in self.game_deals]  # Henter og gemmer titler fra resultaterne
        except requests.exceptions.RequestException as e:                   # Håndterer fejl ved HTTP-anmodningen
            print(f"Error fetching data: {e}")                              # Udskriver fejl i konsollen
            self.game_deals = []                                            # Nulstiller spiltilbud, hvis anmodningen fejler
            self.game_titles = []                                           # Nulstiller spiltilbudstitler, hvis anmodningen fejler
        self.update_game_list()                                             # Opdaterer visningen af spiltilbud i brugergrænsefladen

    # ------------------------------------------------------------------------------------------- Integration
    # Funktion til at filtrere spil baseret på et søgeord
    def filter_deals(self, keyword):
        keyword = keyword.lower()                                           # Gør søgeord småt for at sikre, at søgningen ikke er case-sensitiv
        filtered_deals = [                                                  # Filtrerer spiltilbud, hvis titel indeholder søgeordet
            deal for deal in self.game_deals
            if keyword in deal["title"].lower()
        ]
        self.game_deals = filtered_deals                                    # Opdaterer listen af filtrerede spil
        self.update_game_list()                                             # Opdaterer visningen af de filtrerede spil

    # ------------------------------------------------------------------------------------------- Datahåndtering
    # Funktion til at hente butiksnavne fra CheapShark API
    def get_store_data(self):
        data = requests.get('https://www.cheapshark.com/api/1.0/stores')    # Sender en GET-anmodning for at hente butiksliste
        stores = {}                                                         # Opretter en tom dictionary til at holde butiksdata
        if data.status_code == 200:                                         # Tjekker, om HTTP-status er 200 (OK)
            for store in data.json():                                       # Itererer gennem butiksdata
                stores[store['storeID']] = store['storeName']               # Gemmer butiks-ID og navn i dictionary
            return stores                                                   # Returnerer dictionary med butiksnavne
        return stores                                                       # Returnerer tom dictionary, hvis data ikke kunne hentes

    # ------------------------------------------------------------------------------------------- Integration
    # Funktion til at opdatere spiltilbudslisten i brugergrænsefladen
    def update_game_list(self):
        store_names = self.get_store_data()                                     # Henter butiksnavne fra API
        game_list = self.ids.game_list                                          # Refererer til game_list-widgeten i brugergrænsefladen
        game_list.clear_widgets()                                               # Fjerner eksisterende widgets fra listen

        if not self.game_deals:                                                 # Hvis der ikke er spiltilbud
            game_list.add_widget(Label(                                         # Tilføjer en label med beskeden "Ingen spiltilbud endnu."
                text="Ingen spiltilbud endnu.",
                size_hint_y=None,
                height=60
            ))
        else:
            for deal in self.game_deals:                                        # Itererer gennem spiltilbuddene
                store_name = store_names.get(deal['storeID'], "Unknown Store")  # Får butiknavn eller 'Unknown Store'

                # Opretter en container til hvert spiltilbud
                container = BoxLayout(orientation="horizontal", size_hint_y=None, height=100)

                # Tjekker, om billed-URL'en er gyldig, før AsyncImage tilføjes
                image_url = deal['thumb']
                if is_valid_image(image_url):
                    # Tilføjer spillets miniaturebillede, hvis URL'en er gyldig
                    container.add_widget(AsyncImage(source=image_url, size_hint_x=0.2))
                else:
                    # Tilføjer et pladsholderbillede, hvis URL'en ikke er gyldig
                    container.add_widget(AsyncImage(source="path/to/placeholder_image.png", size_hint_x=0.2))
                # ------------------------------------------------------------------------------------------- Datahåndtering
                # Henter metacriticScore (standardværdi 'N/A', hvis den mangler eller er 0)
                metacritic_score = deal.get('metacriticScore', "N/A")
                # ------------------------------------------------------------------------------------------- UI
                # Tilføjer detaljer for spillet
                details = Label(
                    text=(  # Bruger markup til at formatere teksten
                        f"[b]{deal['title']}[/b]\n"
                        f"Sale Price: {deal['salePrice']} USD (Normal: {deal['normalPrice']} USD)\n"
                        f"Metacritic: {metacritic_score}\n"
                        f"Store: {store_name}"
                    ),
                    markup=True,  # Tillader markup i teksten
                    size_hint_x=0.8,
                    halign="left",  # Justerer teksten til venstre
                    valign="top",  # Justerer teksten til toppen
                )
                details.bind(size=details.setter('text_size'))  # Sørger for, at teksten brydes korrekt
                container.add_widget(details)  # Tilføjer detaljer til containeren

                game_list.add_widget(container)  # Tilføjer containeren til game_list-widgeten

# Definerer hovedapplikationen
class GameDealsApp(App):
    def build(self):
        return MainWindow()  # Returnerer hovedvinduet som layout for applikationen

# Starter applikationen, hvis filen køres direkte
if __name__ == "__main__":
    GameDealsApp().run()  # Kører applikationen
