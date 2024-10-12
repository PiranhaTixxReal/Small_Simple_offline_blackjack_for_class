import tkinter as tk
from tkinter import font as tkfont, messagebox, simpledialog
import random
import json
import os

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.color = "red" if suit in ['♥', '♦'] else "white"

    def __repr__(self):
        return f"{self.value}{self.suit}"

class BlackjackGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blackjack Game")
        self.root.attributes('-fullscreen', True)

        self.bg_color = "#2E2E2E"
        self.card_bg_color = "#4D4D4D"
        self.text_color = "white"
        
        self.suits = ['♠', '♥', '♦', '♣']
        self.deck = [Card(v, s) for v in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] for s in self.suits]

        self.player_hand = []
        self.dealer_hand = []

        self.save_states = self.load_game_state()
        self.current_state = None
        self.current_bet = 0

        self.setup_ui()
        
        # Bind ESC key to show quit window
        self.root.bind('<Escape>', self.show_quit_window)

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        self.large_font = tkfont.Font(family="Helvetica", size=24)
        self.huge_font = tkfont.Font(family="Helvetica", size=36, weight="bold")
        self.card_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        self.small_card_font = tkfont.Font(family="Helvetica", size=14, weight="bold")

        self.info_label = tk.Label(self.root, text="Welcome to Blackjack!", font=self.huge_font, bg=self.bg_color, fg=self.text_color)
        self.info_label.pack(pady=20)

        self.balance_label = tk.Label(self.root, text="", font=self.large_font, bg=self.bg_color, fg=self.text_color)
        self.balance_label.pack()

        self.bet_label = tk.Label(self.root, text="", font=self.large_font, bg=self.bg_color, fg=self.text_color)
        self.bet_label.pack()

        self.player_frame = tk.Frame(self.root, bg=self.bg_color)
        self.player_frame.pack(pady=20)

        self.dealer_frame = tk.Frame(self.root, bg=self.bg_color)
        self.dealer_frame.pack(pady=20)

        self.button_frame = tk.Frame(self.root, bg=self.bg_color)
        self.button_frame.pack(pady=20)

        self.start_button = tk.Button(self.button_frame, text="Choose Game", command=self.choose_game, font=self.large_font)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.quit_button = tk.Button(self.button_frame, text="Quit", command=self.show_quit_window, font=self.large_font)
        self.quit_button.pack(side=tk.LEFT, padx=10)

    def load_game_state(self):
        if os.path.exists('gamestate.json'):
            with open('gamestate.json', 'r') as f:
                return json.load(f)
        else:
            return [{"name": f"Game {i+1}", "balance": 100} for i in range(3)]

    def save_game_state(self):
        with open('gamestate.json', 'w') as f:
            json.dump(self.save_states, f)

    def choose_game(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        for i, state in enumerate(self.save_states):
            btn = tk.Button(self.button_frame, text=f"{state['name']}: ${state['balance']}", 
                            command=lambda idx=i: self.game_options(idx), font=self.large_font)
            btn.pack(side=tk.LEFT, padx=10)

        rename_btn = tk.Button(self.button_frame, text="Rename Game", command=self.rename_game, font=self.large_font)
        rename_btn.pack(side=tk.LEFT, padx=10)

        transfer_btn = tk.Button(self.button_frame, text="Transfer Money", command=self.transfer_money, font=self.large_font)
        transfer_btn.pack(side=tk.LEFT, padx=10)

    def game_options(self, state_index):
        self.current_state = self.save_states[state_index]
        if self.current_state['balance'] == 0:
            response = messagebox.askyesno("No Balance", "You have no balance. Would you like to add $100?")
            if response:
                self.current_state['balance'] = 100
                self.save_game_state()
            else:
                return
        self.setup_betting_ui()

    def rename_game(self):
        index = simpledialog.askinteger("Rename Game", "Enter the game number to rename (1-3):", minvalue=1, maxvalue=3)
        if index:
            new_name = simpledialog.askstring("Rename Game", f"Enter new name for Game {index}:")
            if new_name:
                self.save_states[index-1]['name'] = new_name
                self.save_game_state()
                self.choose_game()

    def transfer_money(self):
        from_index = simpledialog.askinteger("Transfer From", "Enter the game number to transfer from (1-3):", minvalue=1, maxvalue=3)
        to_index = simpledialog.askinteger("Transfer To", "Enter the game number to transfer to (1-3):", minvalue=1, maxvalue=3)
        
        if from_index and to_index and from_index != to_index:
            amount = simpledialog.askinteger("Transfer Amount", f"Enter amount to transfer (max ${self.save_states[from_index-1]['balance']}):", 
                                             minvalue=1, maxvalue=self.save_states[from_index-1]['balance'])
            if amount:
                self.save_states[from_index-1]['balance'] -= amount
                self.save_states[to_index-1]['balance'] += amount
                self.save_game_state()
                self.choose_game()

    def setup_betting_ui(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        min_bet = tk.Button(self.button_frame, text="Min Bet ($10)", command=lambda: self.place_bet(10), font=self.large_font)
        min_bet.pack(side=tk.LEFT, padx=10)

        normal_bet = tk.Button(self.button_frame, text="10% Bet", command=lambda: self.place_bet(int(self.current_state['balance'] * 0.1)), font=self.large_font)
        normal_bet.pack(side=tk.LEFT, padx=10)

        all_in = tk.Button(self.button_frame, text="All In", command=lambda: self.place_bet(self.current_state['balance']), font=self.large_font)
        all_in.pack(side=tk.LEFT, padx=10)

        back_btn = tk.Button(self.button_frame, text="Back", command=self.choose_game, font=self.large_font)
        back_btn.pack(side=tk.LEFT, padx=10)

    def place_bet(self, amount):
        if amount > self.current_state['balance']:
            messagebox.showerror("Invalid Bet", "You don't have enough balance for this bet!")
            return
        if amount < 10:
            messagebox.showerror("Invalid Bet", "Minimum bet is $10!")
            return

        self.current_bet = amount
        self.current_state['balance'] -= amount
        self.deal_cards()

    def deal_cards(self):
        self.player_hand = []
        self.dealer_hand = []
        random.shuffle(self.deck)

        for _ in range(2):
            self.player_hand.append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())

        self.update_info()
        self.setup_game_buttons()

    def setup_game_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        self.hit_button = tk.Button(self.button_frame, text="Hit", command=self.hit, font=self.large_font)
        self.hit_button.pack(side=tk.LEFT, padx=10)

        self.stand_button = tk.Button(self.button_frame, text="Stand", command=self.stand, font=self.large_font)
        self.stand_button.pack(side=tk.LEFT, padx=10)

    def hit(self):
        self.player_hand.append(self.deck.pop())
        if self.calculate_hand(self.player_hand) > 21:
            self.end_game("You busted! Dealer wins.")
        else:
            self.update_info()

    def stand(self):
        while self.calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
        
        player_total = self.calculate_hand(self.player_hand)
        dealer_total = self.calculate_hand(self.dealer_hand)

        if dealer_total > 21:
            self.end_game("Dealer busted! You win!")
        elif dealer_total > player_total:
            self.end_game("Dealer wins!")
        elif dealer_total < player_total:
            self.end_game("You win!")
        else:
            self.end_game("It's a tie!")

    def calculate_hand(self, hand):
        total = sum([10 if card.value in ['J', 'Q', 'K'] else 11 if card.value == 'A' else int(card.value) for card in hand])
        aces = sum(1 for card in hand if card.value == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def end_game(self, message):
        self.info_label['text'] = message
        if "You win" in message:
            self.current_state['balance'] += self.current_bet * 2
        elif "tie" in message:
            self.current_state['balance'] += self.current_bet

        self.current_bet = 0
        self.save_game_state()
        self.update_info()
        self.setup_betting_ui()

    def update_info(self):
        self.balance_label['text'] = f"Balance: ${self.current_state['balance']}"
        self.bet_label['text'] = f"Current Bet: ${self.current_bet}"
        
        for widget in self.player_frame.winfo_children():
            widget.destroy()
        for widget in self.dealer_frame.winfo_children():
            widget.destroy()

        tk.Label(self.player_frame, text="Your hand:", font=self.large_font, bg=self.bg_color, fg=self.text_color).pack()
        self.draw_hand(self.player_frame, self.player_hand)
        tk.Label(self.player_frame, text=f"Total: {self.calculate_hand(self.player_hand)}", font=self.large_font, bg=self.bg_color, fg=self.text_color).pack()

        tk.Label(self.dealer_frame, text="Dealer's hand:", font=self.large_font, bg=self.bg_color, fg=self.text_color).pack()
        self.draw_hand(self.dealer_frame, self.dealer_hand, hide_first=True)

    def draw_hand(self, frame, hand, hide_first=False):
        card_frame = tk.Frame(frame, bg=self.bg_color)
        card_frame.pack()

        for i, card in enumerate(hand):
            if i == 0 and hide_first:
                self.draw_card(card_frame, None)
            else:
                self.draw_card(card_frame, card)

    def draw_card(self, frame, card):
        card_width, card_height = 100, 150
        canvas = tk.Canvas(frame, width=card_width, height=card_height, bg=self.card_bg_color, highlightthickness=2, highlightbackground="black")
        canvas.pack(side=tk.LEFT, padx=5)

        if card:
            canvas.create_text(10, 20, text=card.value, font=self.small_card_font, fill=card.color, anchor="nw")
            canvas.create_text(10, 40, text=card.suit, font=self.small_card_font, fill=card.color, anchor="nw")
            
            canvas.create_text(card_width//2, card_height//2, text=card.suit, font=self.card_font, fill=card.color)
            
            canvas.create_text(card_width-10, card_height-20, text=card.value, font=self.small_card_font, fill=card.color, anchor="se")
            canvas.create_text(card_width-10, card_height-40, text=card.suit, font=self.small_card_font, fill=card.color, anchor="se")
        else:
            canvas.create_rectangle(5, 5, card_width-5, card_height-5, fill="#007ACC", outline="navy")
            for i in range(0, card_width, 10):
                canvas.create_line(i, 0, i, card_height, fill="navy")
            for i in range(0, card_height, 10):
                canvas.create_line(0, i, card_width, i, fill="navy")

    def show_quit_window(self, event=None):
        response = messagebox.askyesno("Quit Game", "Are you sure you want to quit?")
        if response:
            self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()