import os
import hashlib
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Fonction pour calculer le hash d'un fichier
def calculate_hash(file_path, hash_algorithm="md5"):
    """Calcule le hash d'un fichier."""
    hash_func = hashlib.new(hash_algorithm)
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
    except (PermissionError, FileNotFoundError):
        return None
    return hash_func.hexdigest()

# Fonction pour trouver les doublons avec barre de progression
def find_duplicates_with_progress(directory, progress_bar, hash_algorithm="md5"):
    """Parcourt un répertoire et identifie les doublons avec une barre de progression."""
    global stop_analysis
    hashes = defaultdict(list)
    all_files = []

    # Collecter tous les fichiers pour calculer la progression
    for root, _, files in os.walk(directory):
        for file in files:
            all_files.append(os.path.join(root, file))

    total_files = len(all_files)
    progress_bar["maximum"] = total_files
    progress_bar["value"] = 0

    for index, file_path in enumerate(all_files):
        if stop_analysis:  # Vérification pour arrêter
            break

        file_hash = calculate_hash(file_path, hash_algorithm)
        if file_hash:
            hashes[file_hash].append(file_path)
        progress_bar["value"] = index + 1
        progress_bar.update()

    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
    return duplicates

# Fonction pour sélectionner un répertoire
def select_directory():
    """Ouvre une boîte de dialogue pour sélectionner un répertoire."""
    folder = filedialog.askdirectory()
    if folder:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, folder)

# Fonction pour lancer l'analyse
def analyze():
    """Lance l'analyse des doublons."""
    global stop_analysis
    stop_analysis = False

    folder = entry_directory.get()
    if not os.path.isdir(folder):
        messagebox.showerror("Erreur", "Veuillez sélectionner un répertoire valide.")
        return

    # Réinitialiser l'affichage des résultats et de la barre de progression
    for widget in frame_results.winfo_children():
        widget.destroy()

    progress_bar.pack(fill="x", padx=10, pady=10)  # Afficher la barre
    duplicates = find_duplicates_with_progress(folder, progress_bar)
    progress_bar.pack_forget()  # Masquer la barre après analyse

    if stop_analysis:
        messagebox.showinfo("Interruption", "Analyse interrompue.")
        return

    if not duplicates:
        messagebox.showinfo("Résultat", "Aucun doublon trouvé.")
        return

    # Création d'une zone défilable pour les résultats
    global canvas
    canvas = tk.Canvas(frame_results)
    scrollbar = ttk.Scrollbar(frame_results, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configurer la zone défilable
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Lier la molette de la souris
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/macOS
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Affichage des doublons
    for hash_value, paths in duplicates.items():
        label_hash = tk.Label(scrollable_frame, text=f"Hash : {hash_value}", font=("Arial", 10, "bold"))
        label_hash.pack(anchor="w")
        for path in paths:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(scrollable_frame, text=path, variable=var, wraplength=500)
            chk.pack(anchor="w")
            selected_files[path] = var

# Fonction pour gérer le défilement avec la molette
def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * int(event.delta / 120), "units")

# Fonction pour arrêter l'analyse en cours
def stop_analysis_command():
    """Interrompt l'analyse en cours."""
    global stop_analysis
    stop_analysis = True

# Fonction pour supprimer les fichiers sélectionnés
def delete_selected():
    """Supprime les fichiers sélectionnés."""
    to_delete = [path for path, var in selected_files.items() if var.get()]
    if not to_delete:
        messagebox.showinfo("Info", "Aucun fichier sélectionné pour suppression.")
        return

    for file_path in to_delete:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Erreur lors de la suppression de {file_path} : {e}")

    messagebox.showinfo("Succès", "Les fichiers sélectionnés ont été supprimés.")
    analyze()

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Détecteur de Doublons")
root.configure(bg="#f0f4f7")

# Répertoire
frame_directory = ttk.LabelFrame(root, text="Sélection du répertoire")
frame_directory.pack(fill="x", padx=10, pady=10)

label_directory = ttk.Label(frame_directory, text="Répertoire :")
label_directory.pack(side="left")

entry_directory = ttk.Entry(frame_directory, width=50)
entry_directory.pack(side="left", padx=5)

btn_browse = ttk.Button(frame_directory, text="Parcourir", command=select_directory)
btn_browse.pack(side="left")

# Barre de progression
progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.pack(fill="x", padx=10, pady=10)
progress_bar.pack_forget()  # Masquer au démarrage

# Boutons d'action
frame_actions = ttk.LabelFrame(root, text="Actions")
frame_actions.pack(fill="x", padx=10, pady=10)

btn_analyze = tk.Button(frame_actions, text="Analyser", command=analyze)
btn_analyze.pack(side="left", padx=5)

btn_stop = tk.Button(frame_actions, text="Arrêter", command=stop_analysis_command)
btn_stop.pack(side="left", padx=5)

btn_delete = tk.Button(frame_actions, text="Supprimer les doublons", command=delete_selected)
btn_delete.pack(side="left", padx=5)

# Résultats
frame_results = ttk.LabelFrame(root, text="Résultats")
frame_results.pack(fill="both", expand=True, padx=10, pady=10)

selected_files = {}
stop_analysis = False  # Variable globale pour indiquer l'arrêt de l'analyse

root.mainloop()
