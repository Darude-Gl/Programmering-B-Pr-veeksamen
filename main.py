from kivy.app import App  # Importerer App-klassen fra Kivy-frameworket
from kivy.uix.boxlayout import BoxLayout  # Importerer BoxLayout til brugergrænseflade-layout
from kivy.uix.label import Label  # Importerer Label til dynamisk oprettelse af tekst
from kivy.properties import StringProperty, ListProperty  # Importerer egenskaber til datahåndtering
import requests  # Importerer requests-biblioteket til at hente data fra internettet
from kivy.uix.image import AsyncImage  # Importerer AsyncImage til asynkron indlæsning af billeder

#from Kivi import size_hint_y


def is_valid_image(url):
    """Checks if the image URL is valid and accessible"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

# Definerer hovedvinduets funktioner og layout
class MainWindow(BoxLayout):
    search_input = StringProperty("")  # Egenskab til at gemme brugersøgeord
    game_deals = ListProperty([])  # Egenskab til at gemme listen over spiltilbud
    game_titles = ListProperty([])  # Egenskab til at gemme titlerne på spillene

    def fetch_game_deals(self):
        """Henter spiltilbud fra CheapShark API"""
        url = "https://www.cheapshark.com/api/1.0/deals?upperPrice=15"  # URL til API med maks. pris på $15
        try:
            response = requests.get(url)  # Sender GET-anmodning til API'en
            response.raise_for_status()  # Kontrollerer for HTTP-fejl
            self.game_deals = response.json()[:50]  # Gemmer de første 50 resultater
            self.game_titles = [deal["title"] for deal in self.game_deals]  # Opdaterer listen over spilnavne
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")  # Udskriver fejlbesked i konsollen
            self.game_deals = []  # Tømmer listen, hvis der opstår fejl
            self.game_titles = []  # Tømmer titellisten, hvis der opstår fejl
        self.update_game_list()  # Opdaterer visningen af spiltilbud

    def filter_deals(self, keyword):
        """Filtrerer spil baseret på søgeord"""
        keyword = keyword.lower()  # Gør søgeord småt for case-insensitiv søgning
        # Filtrerer spil, hvis titel indeholder søgeordet
        filtered_deals = [
            deal for deal in self.game_deals
            if keyword in deal["title"].lower()
        ]
        self.game_deals = filtered_deals  # Opdaterer listen af filtrerede spil
        self.update_game_list()  # Opdaterer visningen af filtrerede spil

    def get_store_data(self):
        data = requests.get('https://www.cheapshark.com/api/1.0/stores')
        stores = {}
        if data.status_code == 200:
            for store in data.json():
                stores[store['storeID']] = store['storeName']
            return stores

    def update_game_list(self):
        """Opdaterer widgets i game_list baseret på spiltilbud"""
        store_names = self.get_store_data()
        game_list = self.ids.game_list
        game_list.clear_widgets()

        if not self.game_deals:
            game_list.add_widget(Label(
                text="Ingen spiltilbud endnu.",
                size_hint_y=None,
                height=60
            ))
        else:
            for deal in self.game_deals:
                store_name = store_names.get(deal['storeID'], "Unknown Store")

                # Container for each game's info
                container = BoxLayout(orientation="horizontal", size_hint_y=None, height=100)

                # Check if image URL is valid before adding the AsyncImage widget
                image_url = deal['thumb']
                if is_valid_image(image_url):
                    # Add the game's thumbnail only if the image is valid
                    container.add_widget(AsyncImage(source=image_url, size_hint_x=0.2))
                else:
                    # If the image is not valid, use a placeholder image
                    container.add_widget(AsyncImage(source="path/to/placeholder_image.png", size_hint_x=0.2))

                # Handle metacriticScore (fallback to 'N/A' if missing or 0)
                metacritic_score = deal.get('metacriticScore', "N/A")

                # Add the game's details
                details = Label(
                    text=(
                        f"[b]{deal['title']}[/b]\n"
                        f"Sale Price: {deal['salePrice']} USD (Normal: {deal['normalPrice']} USD)\n"
                        f"Metacritic: {metacritic_score}\n"
                        f"Store: {store_name}"
                    ),
                    markup=True,
                    size_hint_x=0.8,
                    halign="left",
                    valign="top",
                )
                details.bind(size=details.setter('text_size'))  # Ensures text wraps correctly
                container.add_widget(details)

                game_list.add_widget(container)


# Definerer applikationen og opbygningen af vinduet
class GameDealsApp(App):
    def build(self):
        return MainWindow()  # Returnerer hovedvinduet som appens layout

# Starter applikationen, hvis filen køres direkte
if __name__ == "__main__":
    GameDealsApp().run()  # Kører appen