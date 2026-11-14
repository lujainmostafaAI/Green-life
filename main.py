import flet as ft
from green_life_ai import recommend_trees_for_location, diagnose_plant_chat

# Paste your free key from Google AI Studio below (or leave as-is to test Offline AI)
MY_GEMINI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"

def main(page: ft.Page):
    page.title = "Green Life"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 395
    page.window_height = 820
    page.padding = 14
    page.scroll = ft.ScrollMode.AUTO

    # App & Chat State
    app_state = {
        "email": "",
        "is_subscribed": False,
        "selected_tree": "Wild Olive (Olea europaea)",
        "current_city": "Alexandria Coast, Egypt",
        "chat_history": []
    }

    # Brand Header
    header = ft.Container(
        content=ft.Column([
            ft.Text("🌱 Green Life", size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("We will help you protect the Earth", size=12, color=ft.Colors.GREEN_100),
        ], spacing=2),
        bgcolor=ft.Colors.GREEN_800,
        padding=14,
        border_radius=12,
    ) 
    # SCREEN 3: MAIN CONNECTED APP (UNLOCKED AFTER 20 L.E. SUBSCRIPTION)
    def show_main_app():
        page.clean()

        # --- TAB 1: LOCATION & ECO-SAFE TREE ENGINE ---
        location_input = ft.TextField(
            label="Enter your location",
            value="Alexandria Coast, Egypt",
            border_radius=10
        )
        tree_results_column = ft.Column(spacing=10)

        def on_find_trees(e):
            tree_results_column.controls.clear()
            tree_results_column.controls.append(ft.ProgressRing())
            page.update()

            city = location_input.value.strip()
            app_state["current_city"] = city
            data = recommend_trees_for_location(city)

            tree_results_column.controls.clear()
            if "error" in data:
                tree_results_column.controls.append(
                    ft.Text(f"⚠️ {data['error']}", color=ft.Colors.RED_700)
                )
            else:
                zone_label = "Coastal / High Salinity" if data["coastal_zone"] else "Inland / Arid"
                tree_results_column.controls.append(
                    ft.Text(f"📍 {data['detected_address'][:48]}...\n🌍 Zone: {zone_label}", size=12, weight=ft.FontWeight.BOLD)
                )
                for t in data["recommended_trees"]:
                    app_state["selected_tree"] = t["name"]
                    card = ft.Container(
                        content=ft.Column([
                            ft.Text(f"✅ {t['name']}", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                            ft.Text(f"Benefit: {t['benefit']}", size=12),
                            ft.Text(f"Eco-Safety: {t['why_safe']}", size=12, italic=True, color=ft.Colors.TEAL_800),
                        ], spacing=4),
                        bgcolor=ft.Colors.GREEN_50,
                        padding=12,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.GREEN_300)
                    )
                    tree_results_column.controls.append(card)
            page.update()

        tab1_content = ft.Column([
            ft.Text("1. Eco-Safe Tree Matcher", size=16, weight=ft.FontWeight.BOLD),
            location_input,
            ft.ElevatedButton(
                "Analyze Soil & Recommend Trees",
                icon=ft.Icons.SEARCH,
                on_click=on_find_trees,
                bgcolor=ft.Colors.GREEN_700,
                color=ft.Colors.WHITE 
            ),
            tree_results_column
        ], spacing=10)

        # --- TAB 2: REMINDERS & AUTOMATED FUNNY GROWTH TIMELINE ---
        growth_milestones = [
            ("🌱", "Day 1 — 1 cm", "Just woke up! Thanks for planting me."),
            ("🌿", "Day 2 — 10 cm", "Drinking sunshine and stretching my tiny roots!"),
            ("🪴", "Day 7 — 25 cm", "One week strong! Already holding the soil together."),
            ("🌳", "Day 30 — 80 cm", "Look at me now! Protecting the Earth with you.")
        ]

        timeline_cards = [
            ft.Container(
                content=ft.Row([
                    ft.Text(icon, size=28),
                    ft.Column([
                        ft.Text(day, weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_900),
                        ft.Text(msg, size=12, color=ft.Colors.GREY_800),
                    ], spacing=2, expand=True)
                ]),
                bgcolor=ft.Colors.LIGHT_GREEN_50,
                padding=10,
                border_radius=10
            ) for icon, day, msg in growth_milestones
        ]

        tab2_content = ft.Column([
            ft.Text("2. Daily Care Reminders", size=16, weight=ft.FontWeight.BOLD),
            ft.Checkbox(label="Morning drip-water check (200 ml)", value=True),
            ft.Checkbox(label="Check leaves for sea-salt dust", value=False),
            ft.Divider(),
            ft.Text("3. Automated Growth Journal", size=16, weight=ft.FontWeight.BOLD),
            *timeline_cards
        ], spacing=8)

        # --- TAB 3: MULTI-TURN AI PLANT DOCTOR CHAT ---
        chat_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=340)
        chat_input = ft.TextField(
            hint_text="Describe symptom or answer AI question...",
            border_radius=10,
            expand=True
        )

        def render_chat():
            chat_column.controls.clear()
            if not app_state["chat_history"]:
                chat_column.controls.append(
                    ft.Container(
                        content=ft.Text("🌱 AI Botanist: Tell me what problem your plant is having, and I will ask quick questions to find the exact eco-safe cure!", size=12),
                        bgcolor=ft.Colors.BLUE_GREY_50,
                        padding=10,
                        border_radius=10
                    )
                )
            for msg in app_state["chat_history"]:
                is_user = msg["role"] == "user"
                bubble = ft.Container(
                    content=ft.Text(
                        f"{'You' if is_user else '🌱 AI Doctor'}: {msg['text']}",
                        size=12,
                        color=ft.Colors.WHITE if is_user else ft.Colors.BLACK87
                    ),
                    bgcolor=ft.Colors.GREEN_700 if is_user else ft.Colors.BLUE_GREY_50,
                    padding=10,
                    border_radius=10,
                    alignment=ft.alignment.center_right if is_user else ft.alignment.center_left
                )
                chat_column.controls.append(bubble)
            page.update()

        def on_send_chat(e):
            user_text = chat_input.value.strip()
            if not user_text:
                return

            chat_input.value = ""
            app_state["chat_history"].append({"role": "user", "text": user_text})
            render_chat()

            ai_reply = diagnose_plant_chat(
                tree_name=app_state["selected_tree"],
                location_name=app_state["current_city"],
                chat_history=app_state["chat_history"],
                api_key=MY_GEMINI_API_KEY
            )
            app_state["chat_history"].append({"role": "ai", "text": ai_reply})
            render_chat()

        def on_reset_chat(e):
            app_state["chat_history"].clear()
            render_chat()

        render_chat()

        tab3_content = ft.Column([
            ft.Row([
                ft.Text("4. AI Plant Doctor", size=16, weight=ft.FontWeight.BOLD, expand=True),
                ft.TextButton("New Case", on_click=on_reset_chat)
            ]),
            chat_column,
            ft.Row([
                chat_input,
                ft.IconButton(icon=ft.Icons.SEND, icon_color=ft.Colors.GREEN_800, on_click=on_send_chat)
            ])
        ], spacing=8)

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=200,
            tabs=[
                ft.Tab(text="Locate", icon=ft.Icons.LOCATION_ON, content=ft.Container(tab1_content, padding=8)),
                ft.Tab(text="Journal", icon=ft.Icons.ECO, content=ft.Container(tab2_content, padding=8)),
                ft.Tab(text="AI Doctor", icon=ft.Icons.CHAT, content=ft.Container(tab3_content, padding=8)),
            ],
            expand=True
        )

        status_bar = ft.Container(
            content=ft.Text(f"Active Plan: 20 L.E./Month ✅ ({app_state['email']})", size=11, color=ft.Colors.GREEN_900),
            bgcolor=ft.Colors.GREEN_100,
            padding=8,
            border_radius=8
        )

        page.add(header, status_bar, tabs)

    # =========================================================================
    # SCREEN 2: 20 L.E. / MONTH SUBSCRIPTION PAYWALL
    # =========================================================================
    def show_payment_screen():
        page.clean()

        payment_method = ft.RadioGroup(
            value="google_play",
            content=ft.Column([
                ft.Radio(value="google_play", label="Google Play Billing (20 L.E. / Month)"),
                ft.Radio(value="vodafone_cash", label="Vodafone Cash / Mobile Wallet (20 L.E.)"),
                ft.Radio(value="card", label="Meeza / Visa / Mastercard (20 L.E.)"),
            ])
        )
        payment_input = ft.TextField(label="Wallet Number or Card Last 4 Digits", hint_text="e.g., 010xxxxxxxx", border_radius=10)
        error_text = ft.Text("", color=ft.Colors.RED_700, size=12)

        def on_confirm_payment(e):
            if not payment_input.value.strip():
                error_text.value = "⚠️ Please enter payment details to activate your 20 L.E. plan."
                page.update()
                return

