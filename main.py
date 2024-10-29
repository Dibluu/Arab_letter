from tkinter import *
import sys
import os
import pandas as pd

# Fonction pour obtenir le chemin des ressources
def resource_path(relative_path):
    """Obtenir le chemin absolu d'une ressource, compatible avec PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

BACKGROUND_COLOR = "#B1DDC6"
BUTTON_COLOR = "#A3C9B3"
BUTTON_HOVER_COLOR = "#8EB1A4"
SCORE = 0

# Variable globale pour le mot aléatoire
random_ar_word = {}
flip_timer = None  # Initialisation de la variable de timer
known_word = {}

def return_card():
    """Change le canvas pour afficher la carte arrière avec le mot français."""
    canvas.itemconfig(canvas_front, image=back_img)
    canvas.itemconfig(title, text="French word", fill="white")
    canvas.itemconfig(canvas_ar_word, text=random_ar_word["Phonetics"], fill="white")


def change_word_right():
    """Change le mot arabe et configure le retour à la carte arrière."""
    global random_ar_word
    global flip_timer
    global SCORE


    if flip_timer is not None:  # Annuler le précédent timer s'il existe
        window.after_cancel(flip_timer)

    # Lire les mots connus
    with open(resource_path("known_words_list"), "r") as known_list:
        known_words = known_list.read().strip().split("\n")  # Lire et diviser en lignes
    # Filtrer les mots vides
    known_words = [word for word in known_words if word]  # Supprimer les lignes vides
    # Score update
    SCORE = len(known_words)
    # Charger les mots arabes et français
    arab_word = pd.read_csv(resource_path("arabic_words.csv"))
    df = arab_word[["Arabic", "Phonetics"]]  # Chargez à la fois les mots arabes et français

    # Filtrer les mots connus
    df = df[~df["Arabic"].isin([word.split()[0] for word in known_words])]  # Exclure les mots connus

    if df.empty:  # Vérifier si tous les mots ont été appris
        print("Tous les mots ont été appris!")
        return  # Ne rien faire si tous les mots ont été appris

    # Sélectionnez un mot aléatoire
    random_ar_word = df.sample(1).iloc[0]  # Échantillonnage d'une seule ligne
    # Remettre le bon fond
    canvas.itemconfig(canvas_front, image=front_img)
    # Afficher le mot arabe et à nouveau le titre
    canvas.itemconfig(title, text="Arabic word", fill="black")
    canvas.itemconfig(canvas_ar_word, text=random_ar_word["Arabic"], fill="black")

    # Retourner à la carte arrière après 3 secondes
    flip_timer = window.after(3000, return_card)

    # Ajouter le mot à la liste des mots connus
    known_word_entry = f"{random_ar_word['Arabic']} {random_ar_word['Phonetics']}\n"

    # Vérifier si le mot est déjà dans le fichier (devrait toujours être nouveau ici)
    with open(resource_path("known_words_list"), "a") as known_list:  # Ouvrir le fichier en mode append
        known_list.write(known_word_entry)
    canvas.itemconfig(canvas_score, text=f"{SCORE}/1000 mots connus")
# IF the answer is wrong
def change_word_wrong():
    """Change le mot arabe et configure le retour à la carte arrière."""
    global random_ar_word
    global flip_timer

    if flip_timer is not None:  # Annuler le précédent timer s'il existe
        window.after_cancel(flip_timer)

    arab_word = pd.read_csv(resource_path("arabic_words.csv"))
    df = arab_word[["Arabic", "Phonetics"]]  # Chargez à la fois les mots arabes et français

    # Sélectionnez un mot aléatoire
    random_ar_word = df.sample(1).iloc[0]  # Échantillonnage d'une seule ligne
    # Remettre le bon fond
    canvas.itemconfig(canvas_front, image=front_img)
    # Afficher le mot arabe et à nouveau le titre
    canvas.itemconfig(title, text="Arabic word", fill="black")
    canvas.itemconfig(canvas_ar_word, text=random_ar_word["Arabic"], fill="black")

    # Retourner à la carte arrière après 3 secondes
    flip_timer = window.after(3000, return_card)
    # Ajouter le mot à la liste des mots connus
    known_word_entry = f"{random_ar_word['Arabic']} {random_ar_word['Phonetics']}\n"

    # Vérifier si le mot est déjà dans le fichier
    with open(resource_path("list_to_learn"), "a") as unknown_list:  # Ouvrir le fichier en mode append
        unknown_list.seek(0)
        unknown_list.write(known_word_entry)

# Configuration de la fenêtre
window = Tk()
window.title("Apprendre l'arabe du Coran")
window.config(pady=25, padx=25, bg=BACKGROUND_COLOR)

# Dimensions de l'image
image_width = 800
image_height = 526

# Configuration du canvas
canvas = Canvas(width=image_width, height=image_height, highlightthickness=0, bg=BACKGROUND_COLOR)
front_img = PhotoImage(file=resource_path("./images/card_front.png"))
canvas_front = canvas.create_image(0, 0, anchor=NW, image=front_img)
title = canvas.create_text(400, 150, text="Mot arabe", font=("Ariel", 40, "italic"), fill="black")
canvas_ar_word = canvas.create_text(400, 263, text="click to start", font=("Ariel", 45, "bold"), fill="black")
canvas.grid(column=0, row=0, columnspan=3, rowspan=2)

#Configuration du score
canvas_score = canvas.create_text(100, 50, text=f"{SCORE}/150 mots connus", font=("Ariel", 15, "bold"), fill="black")

# Configuration de la carte arrière
back_img = PhotoImage(file=resource_path("./images/card_back.png"))

# Styles des boutons
def create_button(image_path, command):
    """Crée un bouton avec une image et une commande."""
    img = PhotoImage(file=resource_path(image_path))
    button = Button(image=img, highlightthickness=0, borderwidth=0, bg=BUTTON_COLOR, activebackground=BUTTON_HOVER_COLOR, command=command)
    button.image = img  # Gardez une référence pour éviter la collecte des déchets
    return button

# Bouton Droit
right_button = create_button("./images/right.png", command=change_word_right)
right_button.grid(column=2, row=3, padx=10, pady=10)

# Bouton Faux
wrong_button = create_button("./images/wrong.png", command=change_word_wrong)
wrong_button.grid(column=0, row=3, padx=10, pady=10)

# Ajuster la taille de la fenêtre
window.geometry(f"{image_width + 50}x{image_height + 150}")

window.mainloop()