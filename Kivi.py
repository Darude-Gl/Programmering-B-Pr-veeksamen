<MainWindow>:
    orientation: "vertical"
    padding: 10
    spacing: 10

    TextInput:
        id: search_input
        hint_text: "Søg efter spil..."
        size_hint_y: None
        height: 40
        on_text: root.filter_deals(self.text)

    Button:
        text: "Opdater spiltilbud"
        size_hint_y: None
        height: 50
        on_release: root.fetch_game_deals()

    ScrollView:
        size_hint: (1, 1)
        GridLayout:
            id: game_list
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            row_default_height: 60
            row_force_default: True

            # Dynamisk oprettelse af tilbud
            Label:
                text: "Ingen spiltilbud endnu." if not root.game_deals else ""
                size_hint_y: None
                height: 60
            # Bind hver spiltilbud dynamisk
            Label:
                text: f"{deal['title']} - {deal['salePrice']} USD ({deal['normalPrice']} USD)"
                size_hint_y: None
                height: 60
                for deal in root.game_deals
