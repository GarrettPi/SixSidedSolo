import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import random
import requests
import json
import threading
from datetime import datetime

# ==========================================
# 1. CORE GENERATOR DATA (D66)
# ==========================================

def roll_d66():
    return (random.randint(1, 6) * 10) + random.randint(1, 6)

def get_from_range(roll, table):
    for (low, high), value in table.items():
        if low <= roll <= high:
            return value
    return "Unknown"

FATE_ORACLE = {
    (11, 13): "No, and... (Emphatic negative. Something worse happens.)",
    (14, 26): "No. (Standard negative.)",
    (31, 36): "No, but... (Negative, but a silver lining or alternative appears.)",
    (41, 46): "Yes, but... (Positive, but with a catch, cost, or complication.)",
    (51, 63): "Yes. (Standard positive.)",
    (64, 66): "Yes, and... (Emphatic positive. You get what you want, plus a bonus!)"
}

MUSE_ACTION = {
    11: "Seek", 12: "Destroy", 13: "Protect", 14: "Escort", 15: "Infiltrate", 16: "Steal",
    21: "Rescue", 22: "Assassinate", 23: "Discover", 24: "Sabotage", 25: "Negotiate", 26: "Defend",
    31: "Capture", 32: "Transport", 33: "Investigate", 34: "Betray", 35: "Survive", 36: "Escape",
    41: "Build", 42: "Repair", 43: "Decipher", 44: "Hunt", 45: "Hide", 46: "Confront",
    51: "Deceive", 52: "Avenge", 53: "Explore", 54: "Gather", 55: "Pursue", 56: "Ambush",
    61: "Command", 62: "Summon", 63: "Banish", 64: "Corrupt", 65: "Purify", 66: "Transform"
}

MUSE_THEME = {
    11: "Wealth", 12: "Technology", 13: "Magic/Anomaly", 14: "Weapon", 15: "Information", 16: "Secret",
    21: "Leader", 22: "Family", 23: "Ally", 24: "Enemy", 25: "Monster", 26: "Relic",
    31: "Shelter", 32: "Territory", 33: "Transport", 34: "Supply", 35: "Medicine", 36: "Poison",
    41: "Law", 42: "Religion", 43: "Nature", 44: "History", 45: "Prophecy", 46: "Soul/Mind",
    51: "Power", 52: "Freedom", 53: "Honor", 54: "Revenge", 55: "Love", 56: "Fear",
    61: "Peace", 62: "War", 63: "Chaos", 64: "Order", 65: "Death", 66: "Life"
}

MISSION_OBJECTIVE = {
    11: "Steal Artifact", 12: "Steal Data/Plans", 13: "Retrieve Cargo", 14: "Recover Weapon", 15: "Secure Vehicle", 16: "Kidnap Target",
    21: "Assassinate Leader", 22: "Hunt Monster", 23: "Destroy Facility", 24: "Sabotage Tech", 25: "Clear Outpost", 26: "Poison Supply",
    31: "Escort VIP", 32: "Defend Settlement", 33: "Guard Cargo", 34: "Rescue Hostage", 35: "Extract Defector", 36: "Break out Prisoner",
    41: "Explore Ruin", 42: "Map Wilderness", 43: "Investigate Murder", 44: "Track Fugitive", 45: "Find Missing Person", 46: "Scan Anomaly",
    51: "Deliver Message", 52: "Smuggle Contraband", 53: "Broker Peace", 54: "Intimidate Rival", 55: "Pay Ransom", 56: "Collect Debt",
    61: "Perform Ritual", 62: "Close Portal", 63: "Stop Execution", 64: "Win Tournament", 65: "Frame Innocent", 66: "Fake Death"
}

MISSION_TWIST = {
    11: "Target is already dead", 12: "Target is a decoy", 13: "Ambush!", 14: "Third party intervenes", 15: "Client lied about motives", 16: "The reward is fake",
    21: "Hostile Environment", 22: "Monstrous threat appears", 23: "Ally betrays you", 24: "Target begs for mercy", 25: "Target is infected", 26: "Time limit drops suddenly",
    31: "Guarded by elite force", 32: "Item is broken/corrupted", 33: "Requires a sacrifice", 34: "Two factions fighting over it", 35: "Innocents in crossfire", 36: "Target offers a better deal",
    41: "Transport breaks down", 42: "Comms are jammed", 43: "Trap set by old enemy", 44: "The objective is sentient", 45: "Reinforcements arrive", 46: "VIP is uncooperative",
    51: "Item belongs to a Lord/CEO", 52: "Law enforcement arrives", 53: "Local wildlife attacks all", 54: "A virus is unleashed", 55: "Location is collapsing", 56: "You are framed",
    61: "Requires a rare key", 62: "Gravity/Magic anomaly", 63: "Target has a hostage", 64: "Guarded by a puzzle", 65: "Target is your relative", 66: "It was a test; client is watching"
}

NPC_IDENTITY = {
    11: "Laborer", 12: "Scavenger", 13: "Farmer", 14: "Beggar", 15: "Urchin", 16: "Wanderer",
    21: "Guard", 22: "Soldier", 23: "Mercenary", 24: "Bounty Hunter", 25: "Assassin", 26: "Spy",
    31: "Merchant", 32: "Smuggler", 33: "Criminal", 34: "Thug", 35: "Bandit", 36: "Pirate",
    41: "Scholar", 42: "Scientist", 43: "Mage/Hacker", 44: "Priest/Zealot", 45: "Healer", 46: "Explorer",
    51: "Aristocrat", 52: "Politician", 53: "Official", 54: "Guild Leader", 55: "Patron", 56: "Celebrity",
    61: "Refugee", 62: "Prisoner", 63: "Rebel", 64: "Cultist", 65: "Saboteur", 66: "Agent"
}

NPC_MOTIVATION_VERB = {
    11: "Escape", 12: "Impress", 13: "Pay Off", 14: "Hide", 15: "Avenge", 16: "Prove",
    21: "Recover", 22: "Forget", 23: "Sabotage", 24: "Blackmail", 25: "Protect", 26: "Rescue",
    31: "Murder", 32: "Steal", 33: "Worship", 34: "Abandon", 35: "Support", 36: "Destroy",
    41: "Heal", 42: "Bribe", 43: "Seduce", 44: "Defend", 45: "Betray", 46: "Serve",
    51: "Control", 52: "Expose", 53: "Hunt", 54: "Befriend", 55: "Flee", 56: "Infiltrate",
    61: "Hoard", 62: "Rebuild", 63: "Appease", 64: "Conquer", 65: "Survive", 66: "Claim"
}

NPC_MOTIVATION_NOUN = {
    11: "Debt", 12: "Rival", 13: "Loved One", 14: "Guilt", 15: "Addiction", 16: "Boss/Patron",
    21: "Secret", 22: "Reputation", 23: "Illness", 24: "Heirloom", 25: "Prophecy", 26: "Cult",
    31: "Crime", 32: "Memory", 33: "Bounty", 34: "Treasure", 35: "Weapon", 36: "Authority",
    41: "Homeland", 42: "Honor", 43: "Power", 44: "Freedom", 45: "Knowledge", 46: "Outcast",
    51: "Oppressor", 52: "Monster", 53: "Relic", 54: "Master", 55: "Betrayer", 56: "Contract",
    61: "Wealth", 62: "Status", 63: "Artifact", 64: "Destiny", 65: "Family", 66: "Enemy"
}

NPC_DISPOSITION = {
    (11, 22): "Hostile (Aggressive)",
    (23, 34): "Wary (Suspicious)",
    (35, 46): "Neutral (Business-only)",
    (51, 62): "Friendly (Open)",
    (63, 66): "Helpful (Eager to assist)"
}

BIOMES = {
    "Interior": {
        11: "Corridor", 12: "Maintenance", 13: "Stairwell", 14: "Antechamber", 15: "Tunnel", 16: "Bridge",
        21: "Living Quarters", 22: "Barracks", 23: "Mess Hall", 24: "Washroom", 25: "Cell/Prison", 26: "Vault",
        31: "Storage", 32: "Cargo Bay", 33: "Armory", 34: "Pantry", 35: "Archives", 36: "Hangar/Garage",
        41: "Laboratory", 42: "Workshop", 43: "Medical Bay", 44: "Shrine/Temple", 45: "Control Room", 46: "Comm Hub",
        51: "Grand Hall", 52: "Cavern", 53: "Greenhouse", 54: "Courtyard", 55: "Power Core", 56: "Observation Deck",
        61: "Ruined Area", 62: "Hazardous Room", 63: "Secret Room", 64: "Ritual Chamber", 65: "Boss Lair", 66: "Exit/Transition"
    },
    "Settlement": {
        11: "Town Square", 12: "Market Stalls", 13: "Tavern/Cantina", 14: "Inn/Hotel", 15: "Alleyway", 16: "Sewers",
        21: "Wealthy Estate", 22: "Government Hall", 23: "Guard Barracks", 24: "Prison/Brig", 25: "Courthouse", 26: "Execution Square",
        31: "Slums/Shantytown", 32: "Industrial Factory", 33: "Warehouse District", 34: "Docks/Spaceport", 35: "Smuggler's Den", 36: "Black Market",
        41: "Temple/Church", 42: "Graveyard", 43: "Hospital/Clinic", 44: "Library/Archive", 45: "School/Academy", 46: "Theatre/Arena",
        51: "Crafting District", 52: "Brothel/Club", 53: "Gambling Den", 54: "Bathhouse", 55: "Parks/Gardens", 56: "Abandoned Block",
        61: "Mayor's Office", 62: "Vault/Bank", 63: "Quarantine Zone", 64: "Cultist Hideout", 65: "Safehouse", 66: "City Gates"
    },
    "Wilderness": {
        11: "Dense Forest", 12: "Clearing", 13: "Overgrown Path", 14: "Logging Camp", 15: "Ancient Grove", 16: "Waterfall",
        21: "Swamp/Bog", 22: "Toxic Mire", 23: "Sinking Mud", 24: "Ruined Hut", 25: "Misty Lake", 26: "Flooded Ruins",
        31: "Barren Desert", 32: "Sand Dunes", 33: "Oasis/Spring", 34: "Rocky Canyon", 35: "Hidden Cave", 36: "Abandoned Mine",
        41: "Steep Mountains", 42: "Narrow Pass", 43: "Snowy Peak", 44: "Frozen River", 45: "Avalanche Zone", 46: "Cliff Edge",
        51: "Open Plains", 52: "Rolling Hills", 53: "Farmland", 54: "Battlefield", 55: "Crater", 56: "Lone Monolith",
        61: "Alien Flora", 62: "Volcanic Vent", 63: "Crystal Cave", 64: "Bandit Camp", 65: "Tribal Village", 66: "Ruined Outpost"
    }
}

ENCOUNTER_DISCOVERY = {
    (11, 23): "Empty / Eerily quiet",
    (24, 36): "Environmental Hazard",
    (41, 53): "Hostile Encounter (Ambush/Patrol)",
    (54, 62): "NPC Encounter (Hiding/Resting)",
    (63, 66): "Unprotected Loot / Resource Cache"
}

REWARD_TYPE = {
    (11, 23): "Trash / Flavor Item (Letters, personal effects)",
    (24, 36): "Consumable (Healing item, rations, ammo, tool)",
    (41, 52): "Valuables (Gold, credits, trade goods)",
    (53, 62): "Useful Gear (New armor, climbing gear, scanner, map)",
    (63, 65): "Standard Weapon",
    (66, 66): "Rare Artifact / Unique Weapon"
}

# ==========================================
# 2. MAIN APP CLASS (Tkinter)
# ==========================================

class SoloRPGApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lonelog Command Center - Solo RPG v1.22")
        self.geometry("1200x800")
        
        # Style Configuration
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        # --- State Variables ---
        self.char_name = tk.StringVar(value="Wanderer")
        self.pl = tk.IntVar(value=1)
        self.xp = tk.IntVar(value=0)

        self.attrs = {
            "Brawn": tk.IntVar(value=1),
            "Agility": tk.IntVar(value=1),
            "Intellect": tk.IntVar(value=1),
            "Awareness": tk.IntVar(value=1),
            "Willpower": tk.IntVar(value=1),
            "Presence": tk.IntVar(value=1)
        }
        self.hp = tk.IntVar(value=12)
        self.strain = tk.IntVar(value=0)
        
        self.action_desc = tk.StringVar(value="")
        self.adv_disadv = tk.StringVar(value="Normal")
        self.selected_attr = tk.StringVar(value="Brawn")
        
        self.enemy_name = tk.StringVar(value="")
        self.enemy_level = tk.StringVar(value="Standard")

        self.use_ai = tk.BooleanVar(value=False)
        self.genre_setting = tk.StringVar(value="Generic Fantasy")
        self.gemini_api_key = tk.StringVar(value="")
        
        self.selected_model = tk.StringVar(value="")
        self.available_models = []
        
        self.selected_biome = tk.StringVar(value="Wilderness")
        self.current_npc_context = None
        
        # Codex Data Structure
        self.codex = {}
        
        # --- Build UI & Start ---
        self.create_menu()
        self.build_ui()
        self.start_session_log()
        
        self.fetch_models()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Campaign...", command=self.save_campaign)
        file_menu.add_command(label="Load Campaign...", command=self.load_campaign)
        file_menu.add_separator()
        file_menu.add_command(label="Export Log as TXT...", command=self.save_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        
        menubar.add_cascade(label="File", menu=file_menu)

    def build_ui(self):
        # 3-Column Layout
        self.columnconfigure(0, weight=1, minsize=250)
        self.columnconfigure(1, weight=1, minsize=350)
        self.columnconfigure(2, weight=3, minsize=500)
        self.rowconfigure(0, weight=1)

        # ==========================================
        # LEFT PANEL: Character Sheet
        # ==========================================
        left_frame = ttk.LabelFrame(self, text="Character Sheet", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ttk.Label(left_frame, text="Name:").grid(row=0, column=0, sticky="w")
        ttk.Entry(left_frame, textvariable=self.char_name).grid(row=0, column=1, sticky="ew", pady=5)
        
        # NEW: Player Level (PL) and XP tracking
        lvl_frame = ttk.Frame(left_frame)
        lvl_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        ttk.Label(lvl_frame, text="Level (PL):").pack(side=tk.LEFT)
        ttk.Spinbox(lvl_frame, from_=1, to=20, textvariable=self.pl, width=3).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(lvl_frame, text="XP:").pack(side=tk.LEFT)
        ttk.Spinbox(lvl_frame, from_=0, to=999, textvariable=self.xp, width=4).pack(side=tk.LEFT)

        attr_frame = ttk.LabelFrame(left_frame, text="Attributes", padding=5)
        attr_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        for i, (attr, var) in enumerate(self.attrs.items()):
            ttk.Label(attr_frame, text=attr).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Spinbox(attr_frame, from_=1, to=5, textvariable=var, width=5, command=self.update_hp).grid(row=i, column=1, sticky="e")
        
        stats_frame = ttk.Frame(left_frame)
        stats_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(stats_frame, text="HP:").pack(side=tk.LEFT)
        ttk.Spinbox(stats_frame, from_=0, to=50, textvariable=self.hp, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(stats_frame, text="Strain:").pack(side=tk.LEFT, padx=10)
        ttk.Spinbox(stats_frame, from_=0, to=10, textvariable=self.strain, width=5).pack(side=tk.LEFT)
        
        ttk.Label(left_frame, text="Gear / Status Conditions:").grid(row=4, column=0, columnspan=2, sticky="w", pady=(10,0))
        self.gear_text = scrolledtext.ScrolledText(left_frame, height=10, width=20, wrap=tk.WORD)
        self.gear_text.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=5)
        left_frame.rowconfigure(5, weight=1)
        
        ttk.Button(left_frame, text="Log Character State", command=self.log_pc_state).grid(row=6, column=0, columnspan=2, sticky="ew")

        # ==========================================
        # MIDDLE PANEL: Tools & Generators (Scrollable)
        # ==========================================
        mid_container = ttk.Frame(self)
        mid_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        mid_container.rowconfigure(0, weight=1)
        mid_container.columnconfigure(0, weight=1)

        mid_canvas = tk.Canvas(mid_container, highlightthickness=0)
        mid_scrollbar = ttk.Scrollbar(mid_container, orient="vertical", command=mid_canvas.yview)
        
        mid_frame = ttk.Frame(mid_canvas, padding=10)
        
        mid_canvas.configure(yscrollcommand=mid_scrollbar.set)
        mid_canvas.grid(row=0, column=0, sticky="nsew")
        mid_scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas_window = mid_canvas.create_window((0, 0), window=mid_frame, anchor="nw")
        
        def configure_mid_frame(event):
            mid_canvas.configure(scrollregion=mid_canvas.bbox("all"))
            
        def configure_mid_canvas(event):
            mid_canvas.itemconfig(canvas_window, width=event.width)
            
        mid_frame.bind("<Configure>", configure_mid_frame)
        mid_canvas.bind("<Configure>", configure_mid_canvas)
        
        def _on_mousewheel(event):
            if mid_canvas.yview() == (0.0, 1.0): return 
            if event.num == 4 or event.delta > 0:
                mid_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                mid_canvas.yview_scroll(1, "units")

        def _bind_to_mousewheel(event):
            mid_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            mid_canvas.bind_all("<Button-4>", _on_mousewheel)
            mid_canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            mid_canvas.unbind_all("<MouseWheel>")
            mid_canvas.unbind_all("<Button-4>")
            mid_canvas.unbind_all("<Button-5>")

        mid_canvas.bind("<Enter>", _bind_to_mousewheel)
        mid_canvas.bind("<Leave>", _unbind_from_mousewheel)

        # --- 1. Core Action Roller ---
        action_lf = ttk.LabelFrame(mid_frame, text="Core Action Roll", padding=10)
        action_lf.pack(fill=tk.X, pady=5)
        
        ttk.Label(action_lf, text="Action:").grid(row=0, column=0, sticky="w")
        ttk.Entry(action_lf, textvariable=self.action_desc).grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 5))
        
        ttk.Label(action_lf, text="Attribute:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(action_lf, textvariable=self.selected_attr, values=list(self.attrs.keys()), state="readonly", width=12).grid(row=1, column=1, sticky="w")
        
        ttk.Radiobutton(action_lf, text="Adv", variable=self.adv_disadv, value="Adv").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(action_lf, text="Normal", variable=self.adv_disadv, value="Normal").grid(row=2, column=1, sticky="w")
        ttk.Radiobutton(action_lf, text="Disadv", variable=self.adv_disadv, value="Disadv").grid(row=2, column=2, sticky="w")
        
        ttk.Button(action_lf, text="Roll Action", command=self.roll_action).grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")
        
        # --- 2. The Fate Oracle ---
        oracle_lf = ttk.LabelFrame(mid_frame, text="The Fate Oracle (Yes/No)", padding=10)
        oracle_lf.pack(fill=tk.X, pady=5)
        
        ttk.Label(oracle_lf, text="Question:").pack(anchor=tk.W)
        self.oracle_q_entry = ttk.Entry(oracle_lf)
        self.oracle_q_entry.pack(fill=tk.X, pady=2)
        
        mod_frame = ttk.Frame(oracle_lf)
        mod_frame.pack(fill=tk.X, pady=2)
        self.oracle_mod = tk.IntVar(value=0)
        ttk.Radiobutton(mod_frame, text="Likely (+1)", variable=self.oracle_mod, value=1).pack(side=tk.LEFT)
        ttk.Radiobutton(mod_frame, text="Neutral", variable=self.oracle_mod, value=0).pack(side=tk.LEFT)
        ttk.Radiobutton(mod_frame, text="Unlikely (-1)", variable=self.oracle_mod, value=-1).pack(side=tk.LEFT)
        
        ttk.Button(oracle_lf, text="Ask Oracle", command=self.roll_oracle).pack(fill=tk.X, pady=(10,0))
        
        # --- 3. D66 Generators ---
        gen_lf = ttk.LabelFrame(mid_frame, text="Generators", padding=10)
        gen_lf.pack(fill=tk.X, pady=5)
        
        ttk.Button(gen_lf, text="The Muse (Action & Theme)", command=self.roll_muse).pack(fill=tk.X, pady=2)
        ttk.Button(gen_lf, text="Mission Board", command=self.roll_mission).pack(fill=tk.X, pady=2)
        
        ttk.Button(gen_lf, text="NPC Generator", command=self.roll_npc).pack(fill=tk.X, pady=2)
        self.btn_chat_npc = ttk.Button(gen_lf, text="Chat with Current NPC", state=tk.DISABLED, command=self.open_npc_chat)
        self.btn_chat_npc.pack(fill=tk.X, pady=2)

        biome_frame = ttk.Frame(gen_lf)
        biome_frame.pack(fill=tk.X, pady=5)
        ttk.Label(biome_frame, text="Biome:").pack(side=tk.LEFT)
        ttk.Combobox(biome_frame, textvariable=self.selected_biome, values=list(BIOMES.keys()), state="readonly", width=12).pack(side=tk.LEFT, padx=5)
        
        split_frame = ttk.Frame(gen_lf)
        split_frame.pack(fill=tk.X, pady=2)
        ttk.Button(split_frame, text="Location Only", command=self.roll_location_only).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        ttk.Button(split_frame, text="Encounter Only", command=self.roll_encounter_only).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        ttk.Button(gen_lf, text="Location & Encounter (Combined)", command=self.roll_location).pack(fill=tk.X, pady=2)
        ttk.Button(gen_lf, text="Roll Loot / Reward", command=self.roll_loot).pack(fill=tk.X, pady=2)

        # --- 4. Enemy Generator ---
        enemy_lf = ttk.LabelFrame(mid_frame, text="Enemy Encounter Generator", padding=10)
        enemy_lf.pack(fill=tk.X, pady=5)

        ttk.Label(enemy_lf, text="Name:").grid(row=0, column=0, sticky="w")
        ttk.Entry(enemy_lf, textvariable=self.enemy_name).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)

        ttk.Label(enemy_lf, text="Level:").grid(row=1, column=0, sticky="w")
        # Use simple string list now instead of keys from static ENEMY_STATS
        enemy_options = ["Minion", "Standard", "Elite", "Boss"]
        ttk.Combobox(enemy_lf, textvariable=self.enemy_level, values=enemy_options, state="readonly", width=12).grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)

        ttk.Button(enemy_lf, text="Generate Enemy Stats", command=self.roll_enemy).grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        enemy_lf.columnconfigure(1, weight=1)

        # --- 5. AI Toggle & Model Selection ---
        ai_frame = ttk.LabelFrame(mid_frame, text="AI Engine Settings", padding=10)
        ai_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(ai_frame, text="Enable AI Lore & Chat", variable=self.use_ai).pack(anchor=tk.W, pady=(0, 5))
        
        genre_frame = ttk.Frame(ai_frame)
        genre_frame.pack(fill=tk.X, pady=2)
        ttk.Label(genre_frame, text="Genre/Setting:").pack(side=tk.LEFT)
        ttk.Entry(genre_frame, textvariable=self.genre_setting, width=25).pack(side=tk.LEFT, padx=5)
        
        api_frame = ttk.Frame(ai_frame)
        api_frame.pack(fill=tk.X, pady=2)
        ttk.Label(api_frame, text="Gemini API Key:").pack(side=tk.LEFT)
        ttk.Entry(api_frame, textvariable=self.gemini_api_key, show="*", width=24).pack(side=tk.LEFT, padx=5)

        model_ctrl_frame = ttk.Frame(ai_frame)
        model_ctrl_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(model_ctrl_frame, text="Model:").pack(side=tk.LEFT)
        self.model_combo = ttk.Combobox(model_ctrl_frame, textvariable=self.selected_model, state="readonly", width=18)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(model_ctrl_frame, text="Refresh", command=self.fetch_models).pack(side=tk.LEFT)

        # ==========================================
        # RIGHT PANEL: Notebook (Journal & Codex)
        # ==========================================
        self.right_notebook = ttk.Notebook(self)
        self.right_notebook.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        # TAB 1: JOURNAL
        self.journal_frame = ttk.Frame(self.right_notebook, padding=10)
        self.right_notebook.add(self.journal_frame, text="Lonelog Journal")
        
        self.log_text = scrolledtext.ScrolledText(self.journal_frame, wrap=tk.WORD, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        entry_frame = ttk.Frame(self.journal_frame)
        entry_frame.pack(fill=tk.X)
        
        ttk.Button(entry_frame, text="@ Action", command=lambda: self.append_log("@ ")).pack(side=tk.LEFT)
        ttk.Button(entry_frame, text="=> Consequence", command=lambda: self.append_log("=> ")).pack(side=tk.LEFT, padx=5)
        ttk.Button(entry_frame, text="[Tag]", command=lambda: self.append_log("[Type:Name|details] ")).pack(side=tk.LEFT)
        
        self.custom_entry = ttk.Entry(entry_frame)
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.custom_entry.bind("<Return>", lambda e: self.submit_custom_log())

        bottom_frame = ttk.Frame(self.journal_frame)
        bottom_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Button(bottom_frame, text="End Session & Summarize", command=self.summarize_session).pack(side=tk.RIGHT)

        # TAB 2: CODEX VAULT
        self.codex_frame = ttk.Frame(self.right_notebook, padding=10)
        self.right_notebook.add(self.codex_frame, text="Codex Vault")
        
        codex_pw = ttk.PanedWindow(self.codex_frame, orient=tk.HORIZONTAL)
        codex_pw.pack(fill=tk.BOTH, expand=True)
        
        # Left Side of Codex: Entity List
        list_frame = ttk.Frame(codex_pw)
        codex_pw.add(list_frame, weight=1)
        
        ttk.Label(list_frame, text="Known Entities").pack(anchor=tk.W)
        self.codex_listbox = tk.Listbox(list_frame)
        self.codex_listbox.pack(fill=tk.BOTH, expand=True, pady=2)
        self.codex_listbox.bind('<<ListboxSelect>>', self.on_codex_select)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="New", command=self.add_new_codex_entry).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="Delete", command=self.delete_codex_entry).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Right Side of Codex: Details
        detail_frame = ttk.Frame(codex_pw)
        codex_pw.add(detail_frame, weight=3)
        
        ttk.Label(detail_frame, text="Entity Name:").pack(anchor=tk.W)
        self.codex_name_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.codex_name_var).pack(fill=tk.X, pady=2)
        
        ttk.Label(detail_frame, text="Memory / Description:").pack(anchor=tk.W)
        self.codex_desc_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.codex_desc_text.pack(fill=tk.BOTH, expand=True, pady=2)
        
        ttk.Button(detail_frame, text="Save Entry", command=self.save_manual_codex_entry).pack(fill=tk.X, pady=5)


    # ==========================================
    # CODEX LOGIC & RAG
    # ==========================================

    def update_codex_listbox(self):
        self.codex_listbox.delete(0, tk.END)
        for name in sorted(self.codex.keys()):
            self.codex_listbox.insert(tk.END, name)

    def on_codex_select(self, event):
        selection = self.codex_listbox.curselection()
        if selection:
            name = self.codex_listbox.get(selection[0])
            self.codex_name_var.set(name)
            self.codex_desc_text.delete("1.0", tk.END)
            self.codex_desc_text.insert(tk.END, self.codex[name])

    def add_new_codex_entry(self):
        self.codex_name_var.set("")
        self.codex_desc_text.delete("1.0", tk.END)

    def save_manual_codex_entry(self):
        name = self.codex_name_var.get().strip()
        desc = self.codex_desc_text.get("1.0", tk.END).strip()
        if name and desc:
            self.codex[name] = desc
            self.update_codex_listbox()
            messagebox.showinfo("Saved", f"Codex entry for '{name}' saved.")

    def delete_codex_entry(self):
        name = self.codex_name_var.get().strip()
        if name in self.codex:
            del self.codex[name]
            self.update_codex_listbox()
            self.add_new_codex_entry()

    def get_codex_injection(self, recent_log):
        if not self.codex: return ""
        injections = []
        lower_log = recent_log.lower()
        for name, desc in self.codex.items():
            if name.lower() in lower_log:
                injections.append(f"- {name}: {desc}")
        
        if injections:
            return "RELEVANT CODEX MEMORIES:\n" + "\n".join(injections) + "\n\n"
        return ""

    # ==========================================
    # SYSTEM LOGIC
    # ==========================================

    def update_hp(self):
        new_hp = 10 + self.attrs["Brawn"].get() + self.attrs["Willpower"].get()
        self.hp.set(new_hp)

    def append_log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        
    def stream_to_log(self, chunk):
        self.log_text.insert(tk.END, chunk)
        self.log_text.see(tk.END)

    def submit_custom_log(self):
        txt = self.custom_entry.get().strip()
        if txt:
            self.append_log(txt)
            self.custom_entry.delete(0, tk.END)

    def log_pc_state(self):
        name = self.char_name.get()
        pl = self.pl.get()
        xp = self.xp.get()
        hp = self.hp.get()
        strain = self.strain.get()
        self.append_log(f"[PC:{name} | PL {pl} | XP {xp} | HP {hp} | Strain {strain}]")

    def start_session_log(self):
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.append_log(f"=== Session Start ===")
        self.append_log(f"[Date] {date_str}")
        self.log_pc_state()
        self.append_log("\nS1 *The adventure begins...*")

    # ==========================================
    # PERSISTENCE (SAVE / LOAD)
    # ==========================================
    
    def save_campaign(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save Campaign"
        )
        if not filepath: return

        data = {
            "character": {
                "name": self.char_name.get(),
                "level": self.pl.get(),
                "xp": self.xp.get(),
                "attributes": {k: v.get() for k, v in self.attrs.items()},
                "hp": self.hp.get(),
                "strain": self.strain.get(),
                "gear": self.gear_text.get("1.0", tk.END).strip()
            },
            "settings": {
                "use_ai": self.use_ai.get(),
                "genre_setting": self.genre_setting.get(),
                "selected_model": self.selected_model.get(),
                "gemini_api_key": self.gemini_api_key.get()
            },
            "codex": self.codex,
            "npc_context": self.current_npc_context,
            "journal": self.log_text.get("1.0", tk.END).rstrip()
        }

        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Saved", "Campaign saved successfully!")
            self.append_log(f"\n--- Campaign Saved ---")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_campaign(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Load Campaign"
        )
        if not filepath: return

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            char_data = data.get("character", {})
            self.char_name.set(char_data.get("name", "Unknown"))
            self.pl.set(char_data.get("level", 1))
            self.xp.set(char_data.get("xp", 0))
            self.hp.set(char_data.get("hp", 12))
            self.strain.set(char_data.get("strain", 0))

            attrs_data = char_data.get("attributes", {})
            for k, v in self.attrs.items():
                if k in attrs_data: v.set(attrs_data[k])

            self.gear_text.delete("1.0", tk.END)
            self.gear_text.insert(tk.END, char_data.get("gear", "").strip())

            settings = data.get("settings", {})
            self.use_ai.set(settings.get("use_ai", settings.get("use_ollama", False)))
            self.genre_setting.set(settings.get("genre_setting", "Generic Fantasy"))
            self.gemini_api_key.set(settings.get("gemini_api_key", ""))
            
            if settings.get("selected_model"):
                self.selected_model.set(settings["selected_model"])
                if self.selected_model.get() not in self.available_models:
                    self.model_combo['values'] = list(self.model_combo['values']) + [self.selected_model.get()]
            
            self.codex = data.get("codex", {})
            self.update_codex_listbox()

            self.current_npc_context = data.get("npc_context", None)
            if self.current_npc_context:
                self.btn_chat_npc.config(state=tk.NORMAL, text=f"Chat with {self.current_npc_context['identity']}")
            else:
                self.btn_chat_npc.config(state=tk.DISABLED, text="Chat with Current NPC")

            self.log_text.delete("1.0", tk.END)
            self.log_text.insert(tk.END, data.get("journal", "").strip() + "\n")
            self.append_log(f"\n--- Campaign Loaded: {self.char_name.get()} ---")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load campaign: {e}")

    def save_log(self):
        filename = f"Lonelog_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        filepath = filedialog.asksaveasfilename(
            initialfile=filename,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Log as TXT"
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.log_text.get("1.0", tk.END))
                messagebox.showinfo("Exported", f"Log exported successfully to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export log: {e}")

    # ==========================================
    # ACTION & GENERATOR FUNCTIONS
    # ==========================================

    def roll_action(self):
        desc = self.action_desc.get().strip()
        attr = self.selected_attr.get()
        base_pool = self.attrs[attr].get()
        adv_state = self.adv_disadv.get()
        
        pool = base_pool
        if adv_state == "Adv": pool += 1
        elif adv_state == "Disadv": pool -= 1
        
        is_lowest = False
        if pool <= 0:
            rolls = [random.randint(1, 6), random.randint(1, 6)]
            result = min(rolls)
            is_lowest = True
            pool_str = "2d6(low)"
        else:
            rolls = [random.randint(1, 6) for _ in range(pool)]
            result = max(rolls)
            pool_str = f"{pool}d6"
            
        if result in [5, 6]:
            if not is_lowest and (rolls.count(5) + rolls.count(6)) > 1:
                outcome = "Critical Success"
            else:
                outcome = "Success"
        elif result == 4:
            outcome = "Stun / Tactical Hit"
        else:
            outcome = "Failure"
            
        roll_details = ",".join(map(str, rolls))
        
        if desc:
            self.append_log(f"@ {desc} ({attr})")
        else:
            self.append_log(f"@ Attempt Action ({attr})")
            
        self.append_log(f"d: {attr} {pool_str}={roll_details} -> {outcome}")
        
        if outcome == "Failure":
            self.append_log("=> Things go poorly. The situation escalates.")
        elif "Success" in outcome:
            self.append_log("=> You accomplish your goal.")
        else:
            self.append_log("=> You succeed, but suffer a minor consequence or complication.")
        self.action_desc.set("")

    def roll_oracle(self):
        q = self.oracle_q_entry.get().strip()
        mod = self.oracle_mod.get()
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d1_mod = max(1, min(6, d1 + mod))
        roll = d1_mod * 10 + d2
        ans = get_from_range(roll, FATE_ORACLE)
        
        if q: 
            self.append_log(f"? {q}")
        else: 
            self.append_log("? Asking the Oracle...")
            
        self.append_log(f"-> {ans}")
        self.append_log("=> ")
        
        self.oracle_q_entry.delete(0, tk.END)

    def roll_muse(self):
        v = MUSE_ACTION[roll_d66()]
        n = MUSE_THEME[roll_d66()]
        self.append_log(f"gen: The Muse -> {v} {n}")
        self.append_log("=> ")

    def roll_mission(self):
        obj = MISSION_OBJECTIVE[roll_d66()]
        tw = MISSION_TWIST[roll_d66()]
        self.append_log("gen: Mission Board")
        self.append_log(f"  Objective: -> {obj}")
        self.append_log(f"  Twist: -> {tw}")
        self.append_log(f"=> [Thread: {obj} | Open]")
        
        if self.use_ai.get():
            genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'. "
            prompt = f"{genre_ctx}You are a tabletop RPG Game Master giving a quest briefing. The objective is to {obj}. But here is the secret twist: {tw}. Write a 1-paragraph mission briefing in the voice of a shady client offering the job to the player. Do not ask questions."
            self.trigger_ai_generate(prompt, "Mission Briefing")

    def roll_npc(self):
        identity = NPC_IDENTITY[roll_d66()]
        verb = NPC_MOTIVATION_VERB[roll_d66()]
        noun = NPC_MOTIVATION_NOUN[roll_d66()]
        disp = get_from_range(roll_d66(), NPC_DISPOSITION)
        
        self.current_npc_context = {
            "identity": identity,
            "verb": verb,
            "noun": noun,
            "disp": disp
        }
        self.btn_chat_npc.config(state=tk.NORMAL, text=f"Chat with {identity}")
        
        self.append_log("gen: NPC Generator")
        self.append_log(f"  Identity: -> {identity}")
        self.append_log(f"  Motivation: -> {verb} {noun}")
        self.append_log(f"  Disposition: -> {disp}")
        self.append_log(f"=> [N:Unnamed {identity} | {disp} | wants to {verb} {noun}]")
        
        if self.use_ai.get():
            genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'. "
            prompt = f"{genre_ctx}You are a creative Game Master. I generated an NPC. Role: {identity}. Motivation: To {verb} {noun}. Disposition to player: {disp}. Write a vivid, interesting 1-paragraph description of this NPC's appearance and demeanor. Do not ask questions."
            self.trigger_ai_generate(prompt, f"NPC Lore: {identity}")

    def roll_location_only(self):
        biome_name = self.selected_biome.get()
        biome_table = BIOMES[biome_name]
        loc = biome_table[roll_d66()]
        
        self.append_log(f"gen: Location ({biome_name})")
        self.append_log(f"  Area: -> {loc}")
        self.append_log(f"=> [L:{loc} | {biome_name}]")
        
        if self.use_ai.get():
            genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'. "
            prompt = f"{genre_ctx}You are a creative Game Master. The player just arrived at a {loc} in a {biome_name} environment. Write a vivid 1-paragraph description setting the scene and describing the immediate sensory details. Do not ask questions."
            self.trigger_ai_generate(prompt, f"Scene: {loc}")

    def roll_encounter_only(self):
        enc_roll = roll_d66()
        enc = get_from_range(enc_roll, ENCOUNTER_DISCOVERY)
        
        self.append_log(f"gen: Encounter Discovery")
        self.append_log(f"  Encounter: -> {enc}")
        self.append_log(f"=> ")
        
        if self.use_ai.get():
            genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'. "
            prompt = f"{genre_ctx}You are a creative Game Master. The player just stumbled upon the following state/encounter: {enc}. Write a vivid 1-paragraph description setting the scene and describing the immediate tension or details. Do not ask questions."
            self.trigger_ai_generate(prompt, f"Encounter")

    def roll_location(self):
        biome_name = self.selected_biome.get()
        biome_table = BIOMES[biome_name]
        loc = biome_table[roll_d66()]
        enc_roll = roll_d66()
        enc = get_from_range(enc_roll, ENCOUNTER_DISCOVERY)
        
        self.append_log(f"gen: Location ({biome_name})")
        self.append_log(f"  Area: -> {loc}")
        self.append_log(f"  Encounter: -> {enc}")
        self.append_log(f"=> [L:{loc} | {biome_name}]")
        
        if self.use_ai.get():
            genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'. "
            prompt = f"{genre_ctx}You are a creative Game Master. The player just arrived at a {loc} in a {biome_name} environment. The current state/encounter is: {enc}. Write a vivid 1-paragraph description setting the scene and describing the immediate sensory details and tension. Do not ask questions."
            self.trigger_ai_generate(prompt, f"Scene: {loc}")

    def roll_loot(self):
        rew = get_from_range(roll_d66(), REWARD_TYPE)
        self.append_log(f"gen: Loot/Reward -> {rew}")
        self.append_log("=> ")
        
        if messagebox.askyesno("Loot Rolled", f"You found:\n{rew}\n\nAdd this to your Character Gear?"):
            current_gear = self.gear_text.get("1.0", tk.END).strip()
            new_gear = current_gear + f"\n- {rew}" if current_gear else f"- {rew}"
            self.gear_text.delete("1.0", tk.END)
            self.gear_text.insert(tk.END, new_gear)
            self.append_log(f"[@ Added {rew} to gear]")

    def roll_enemy(self):
        name = self.enemy_name.get().strip() or "Unknown Entity"
        level = self.enemy_level.get()
        if not level:
            level = "Standard"

        pl = self.pl.get()
        
        # Base Damage increases by +1 for every 3 Player Levels (i.e., at 4, 7, 10...)
        dmg_bonus = (pl - 1) // 3

        if level == "Minion":
            hp = pl + 2
            base_dmg = 3 + dmg_bonus
            armor = 0
        elif level == "Elite":
            hp = 20 + (pl * 3)
            base_dmg = 5 + dmg_bonus
            armor = 1
        elif level == "Boss":
            hp = 30 + (pl * 4)
            base_dmg = 7 + dmg_bonus
            armor = 2
        else: # Standard
            hp = 10 + (pl * 2)
            base_dmg = 4 + dmg_bonus
            armor = 0

        self.append_log(f"gen: Enemy Encounter ({level} | PL {pl})")
        self.append_log(f"  Name: -> {name}")
        self.append_log(f"  Stats: -> HP: {hp} | Base Dmg: {base_dmg} | Armor: {armor}")
        self.append_log(f"=> [E:{name} | Lvl:{level} | HP:{hp} | Dmg:{base_dmg} | Arm:{armor}]")

        self.enemy_name.set("")

    # ==========================================
    # AI INTEGRATION (Generate & Chat)
    # ==========================================

    def fetch_models(self):
        gemini_models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
        
        def worker():
            ollama_models = []
            try:
                resp = requests.get("http://localhost:11434/api/tags", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    ollama_models = [m.get("name") for m in data.get("models", [])]
            except Exception:
                pass 
                
            self.after(0, update_ui, gemini_models + ollama_models)
                
        def update_ui(models):
            self.available_models = models
            if models:
                self.model_combo['values'] = models
                if self.selected_model.get() not in models:
                    self.selected_model.set(models[0])
            else:
                self.model_combo['values'] = ["gemini-2.5-flash"]
                if not self.selected_model.get():
                    self.selected_model.set("gemini-2.5-flash")
                    
        threading.Thread(target=worker, daemon=True).start()

    def trigger_ai_generate(self, prompt, title):
        self.append_log(f"\n--- {title} (AI) ---")
        
        recent_log = self.log_text.get("1.0", tk.END)[-3000:]
        rag_context = self.get_codex_injection(recent_log)
        genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'.\n"
        
        final_prompt = genre_ctx + rag_context + prompt
        
        def worker():
            model = self.selected_model.get()
            
            if "gemini" in model.lower():
                api_key = self.gemini_api_key.get().strip()
                if not api_key:
                    self.after(0, self.append_log, "\n[Error: Missing Gemini API Key in settings.]\n------------------\n")
                    return
                    
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
                payload = {"contents": [{"parts": [{"text": final_prompt}]}]}
                
                try:
                    response = requests.post(url, json=payload, stream=True)
                    response.raise_for_status()
                    for line in response.iter_lines():
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            if data_str.strip() == "[DONE]": continue
                            data = json.loads(data_str)
                            if "candidates" in data and data["candidates"]:
                                parts = data["candidates"][0].get("content", {}).get("parts", [])
                                if parts:
                                    chunk = parts[0].get("text", "")
                                    self.after(0, self.stream_to_log, chunk)
                    self.after(0, self.append_log, "\n------------------\n")
                except Exception as e:
                    self.after(0, self.append_log, f"\n[Gemini Error: {e}]\n------------------\n")
            
            else: 
                if not model: model = "llama3.2:3b"
                url = "http://localhost:11434/api/generate"
                payload = {"model": model, "prompt": final_prompt, "stream": True}
                try:
                    response = requests.post(url, json=payload, stream=True)
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if "response" in data:
                                self.after(0, self.stream_to_log, data["response"])
                    self.after(0, self.append_log, "\n------------------\n")
                except Exception as e:
                    self.after(0, self.append_log, f"\n[Ollama Connection Error: {e}]\n------------------\n")
        
        threading.Thread(target=worker, daemon=True).start()

    def open_npc_chat(self):
        if not self.use_ai.get():
            messagebox.showwarning("AI Disabled", "Please enable AI in the main window to use the Chat feature.")
            return
        if not self.current_npc_context:
            return

        npc_id = self.current_npc_context["identity"]
        
        chat_win = tk.Toplevel(self)
        chat_win.title(f"Interactive Chat: {npc_id}")
        chat_win.geometry("550x650")

        chat_log = scrolledtext.ScrolledText(chat_win, wrap=tk.WORD, state=tk.NORMAL, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10))
        chat_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        entry_frame = ttk.Frame(chat_win)
        entry_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        msg_entry = ttk.Entry(entry_frame)
        msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        send_btn = ttk.Button(entry_frame, text="Send")
        send_btn.pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(chat_win)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        copy_btn = ttk.Button(btn_frame, text="Copy Conversation to Journal")
        copy_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        
        ai_codex_btn = ttk.Button(btn_frame, text="Summarize Chat & Save to Codex")
        ai_codex_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        history = []
        context_summary_ref = [""]
        genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'. "

        msg_entry.config(state=tk.DISABLED)
        send_btn.config(state=tk.DISABLED)
        chat_log.insert(tk.END, "* Synching NPC memory with current scene... *\n\n", "sys")
        chat_log.tag_config("sys", foreground="#98c379", font=("Consolas", 10, "italic"))
        chat_log.config(state=tk.DISABLED)

        def setup_chat_context():
            recent_log = self.log_text.get("1.0", tk.END).strip()[-3000:]
            rag_context = self.get_codex_injection(recent_log)
            model = self.selected_model.get()
            
            if len(recent_log) > 50:
                prompt = (
                    f"{genre_ctx}You are an AI assistant helping a Game Master. Summarize the following recent RPG session log in 2 to 3 sentences. "
                    "Focus on the immediate situation, who is present, and what is currently happening. Do not add fluff or conversational filler.\n\n"
                    f"{rag_context}\nRECENT LOG:\n{recent_log}"
                )
                
                if "gemini" in model.lower():
                    api_key = self.gemini_api_key.get().strip()
                    if not api_key:
                        context_summary_ref[0] = "[Error: Missing Gemini API Key]"
                    else:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                        payload = {"contents": [{"parts": [{"text": prompt}]}]}
                        try:
                            response = requests.post(url, json=payload, timeout=30)
                            response.raise_for_status()
                            data = response.json()
                            context_summary_ref[0] = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        except Exception as e:
                            context_summary_ref[0] = f"[Gemini Error: {e}]"
                else:
                    if not model: model = "llama3.2:3b"
                    url = "http://localhost:11434/api/generate"
                    payload = {"model": model, "prompt": prompt, "stream": False}
                    try:
                        response = requests.post(url, json=payload, timeout=30)
                        response.raise_for_status()
                        data = response.json()
                        if "response" in data:
                            context_summary_ref[0] = data["response"].strip()
                    except Exception as e:
                        context_summary_ref[0] = "[Could not generate recent context due to connection error]"
            else:
                context_summary_ref[0] = "No significant recent events have occurred."
                
            self.after(0, finish_setup)

        def finish_setup():
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, "* Memory synched. You may now speak. *\n\n", "sys")
            chat_log.config(state=tk.DISABLED)
            msg_entry.config(state=tk.NORMAL)
            send_btn.config(state=tk.NORMAL)
            msg_entry.focus()

        threading.Thread(target=setup_chat_context, daemon=True).start()

        def send_msg(event=None):
            user_msg = msg_entry.get().strip()
            if not user_msg: return
            msg_entry.delete(0, tk.END)

            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, f"You: {user_msg}\n\n", "user")
            chat_log.tag_config("user", foreground="#61afef")
            chat_log.config(state=tk.DISABLED)
            chat_log.see(tk.END)

            history.append({"role": "user", "content": user_msg})
            send_btn.config(state=tk.DISABLED)
            msg_entry.config(state=tk.DISABLED)
            threading.Thread(target=fetch_reply, args=(user_msg,), daemon=True).start()

        def fetch_reply(user_text):
            model = self.selected_model.get()
            system_prompt = (
                f"{genre_ctx}You are playing the role of an NPC in a tabletop RPG. "
                f"Your Identity/Role is: {self.current_npc_context['identity']}. "
                f"Your Motivation is: To {self.current_npc_context['verb']} {self.current_npc_context['noun']}. "
                f"Your Disposition towards the player is: {self.current_npc_context['disp']}.\n\n"
                f"CURRENT SITUATION / RECENT EVENTS:\n{context_summary_ref[0]}\n\n"
                f"Respond in character, keep it concise (1-3 sentences max). Do not break character."
            )
            
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, f"{npc_id}: ", "npc")
            chat_log.tag_config("npc", foreground="#e06c75")
            chat_log.config(state=tk.DISABLED)
            chat_log.see(tk.END)

            npc_reply = ""
            
            if "gemini" in model.lower():
                api_key = self.gemini_api_key.get().strip()
                if not api_key:
                    self.after(0, append_chunk, "[Error: Missing Gemini API Key]")
                    history.append({"role": "assistant", "content": "[Error: Missing API Key]"})
                    self.after(0, finalize_reply)
                    return
                
                gemini_msgs = []
                for msg in history:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_msgs.append({"role": role, "parts": [{"text": msg["content"]}]})
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
                payload = {
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": gemini_msgs
                }
                
                try:
                    response = requests.post(url, json=payload, stream=True)
                    response.raise_for_status()
                    for line in response.iter_lines():
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            if data_str.strip() == "[DONE]": continue
                            data = json.loads(data_str)
                            if "candidates" in data and data["candidates"]:
                                parts = data["candidates"][0].get("content", {}).get("parts", [])
                                if parts:
                                    chunk = parts[0].get("text", "")
                                    npc_reply += chunk
                                    self.after(0, append_chunk, chunk)
                except Exception as e:
                    self.after(0, append_chunk, f"[Gemini Error: {e}]")
            
            else: 
                if not model: model = "llama3.2:3b"
                messages = [{"role": "system", "content": system_prompt}] + history
                url = "http://localhost:11434/api/chat"
                payload = {"model": model, "messages": messages, "stream": True}
                try:
                    response = requests.post(url, json=payload, stream=True)
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                chunk = data["message"]["content"]
                                npc_reply += chunk
                                self.after(0, append_chunk, chunk)
                except Exception as e:
                    self.after(0, append_chunk, f"[Error: {e}]")

            history.append({"role": "assistant", "content": npc_reply})
            self.after(0, finalize_reply)

        def append_chunk(chunk):
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, chunk)
            chat_log.config(state=tk.DISABLED)
            chat_log.see(tk.END)

        def finalize_reply():
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, "\n\n")
            chat_log.config(state=tk.DISABLED)
            chat_log.see(tk.END)
            send_btn.config(state=tk.NORMAL)
            msg_entry.config(state=tk.NORMAL)
            msg_entry.focus()

        def copy_to_journal():
            content = chat_log.get("1.0", tk.END).strip()
            if content:
                self.append_log(f"\n--- Dialogue Log ({npc_id}) ---\n{content}\n--------------------")
                messagebox.showinfo("Copied", "Dialogue copied to your Lonelog Journal!")

        def summarize_to_codex():
            chat_history = chat_log.get("1.0", tk.END).strip()
            if not chat_history: return
            
            ai_codex_btn.config(state=tk.DISABLED, text="Summarizing...")
            
            def worker():
                prompt = (
                    f"You are an AI assistant helping a Game Master maintain a wiki. "
                    f"Read this chat log between the player and an NPC named '{npc_id}'. "
                    f"Write a concise, 1-3 sentence permanent memory entry for '{npc_id}'. "
                    f"Include their role, motivation, and specifically highlight any quests, promises, or alliances made.\n\n"
                    f"CHAT LOG:\n{chat_history}"
                )
                model = self.selected_model.get()
                
                if "gemini" in model.lower():
                    api_key = self.gemini_api_key.get().strip()
                    if not api_key:
                        self.after(0, finalize_codex_update, "Error: Missing Gemini API Key")
                        return
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    try:
                        resp = requests.post(url, json=payload, timeout=30)
                        resp.raise_for_status()
                        data = resp.json()
                        summary = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        self.after(0, finalize_codex_update, summary)
                    except Exception as e:
                        self.after(0, finalize_codex_update, f"Error: {e}")
                else:
                    if not model: model = "llama3.2:3b"
                    url = "http://localhost:11434/api/generate"
                    payload = {"model": model, "prompt": prompt, "stream": False}
                    try:
                        resp = requests.post(url, json=payload, timeout=30)
                        resp.raise_for_status()
                        data = resp.json()
                        if "response" in data:
                            summary = data["response"].strip()
                            self.after(0, finalize_codex_update, summary)
                    except Exception as e:
                        self.after(0, finalize_codex_update, f"Error: {e}")

            threading.Thread(target=worker, daemon=True).start()

        def finalize_codex_update(summary):
            if summary.startswith("Error:"):
                messagebox.showerror("Error", summary)
            else:
                self.codex[npc_id] = summary
                self.update_codex_listbox()
                messagebox.showinfo("Codex Updated", f"Codex entry for {npc_id} successfully saved!\n\nSummary:\n{summary}")
            
            ai_codex_btn.config(state=tk.NORMAL, text="Summarize Chat & Save to Codex")

        # BIND THE COMMANDS PROPERLY
        msg_entry.bind("<Return>", send_msg)
        send_btn.config(command=send_msg)
        copy_btn.config(command=copy_to_journal)
        ai_codex_btn.config(command=summarize_to_codex)

    def summarize_session(self):
        if not self.use_ai.get():
            messagebox.showwarning("AI Disabled", "Please enable AI in the settings to use the Summarize feature.")
            return
            
        log_content = self.log_text.get("1.0", tk.END).strip()
        if len(log_content) < 50:
            messagebox.showinfo("Log too short", "There isn't enough in the log to summarize yet!")
            return
            
        genre_ctx = f"The setting/genre of this RPG is '{self.genre_setting.get().strip() or 'Generic'}'. "
        prompt = (
            f"{genre_ctx}You are a tabletop RPG Game Master. Please summarize the following solo RPG session log "
            "into a punchy, 1-paragraph 'Previously on...' style recap. Focus on the main narrative events, "
            "character actions, and the current cliffhanger or situation. Do not ask questions or add conversational filler.\n\n"
            f"SESSION LOG:\n{log_content}"
        )
        self.trigger_ai_generate(prompt, "Previously On... (Session Summary)")

if __name__ == "__main__":
    app = SoloRPGApp()
    app.mainloop()