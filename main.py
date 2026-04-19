import os
import csv
from datetime import datetime
import shutil
import tkinter as tk
from send2trash import send2trash
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict  

current_duplicates = {}
LOG_FILE = "deleted_files_log.csv"


def normalize_path(path):
    """Convertit un chemin en format Windows standard."""
    return os.path.normpath(os.path.abspath(path))


def calculate_hash(file_path, hash_algorithm="md5"):
    """Calcule le hash d'un fichier."""
    import hashlib
    hash_func = hashlib.new(hash_algorithm)
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
    except (PermissionError, FileNotFoundError):
        return None
    return hash_func.hexdigest()


def find_duplicates_with_progress(directory, file_types, progress_bar, hash_algorithm="md5"):
    """Parcourt un répertoire et identifie les doublons avec une barre de progression."""
    global stop_analysis
    hashes = defaultdict(list)
    all_files = []

    # Collecter tous les fichiers correspondant aux extensions choisies
    for root, _, files in os.walk(directory):
        for file in files:
            if not file_types or any(file.endswith(ft) for ft in file_types):
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


def log_file_deletion(file_path, trash_directory="DeletedItems"):
    """Journalise les informations sur le fichier supprimé."""
    os.makedirs(trash_directory, exist_ok=True)
    trashed_file = os.path.join(trash_directory, os.path.basename(file_path))
    shutil.move(file_path, trashed_file)

    # Écrire dans le journal
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([file_path, trashed_file, datetime.now()])

def send_to_trash(file_path):
    """Envoie le fichier dans la corbeille système."""
    try:
        send2trash(file_path)
    except Exception as e:
        print(f"Erreur lors de l'envoi à la corbeille : {e}")
        
def export_report(duplicates):
    """Exporte le rapport des doublons détectés dans un fichier CSV."""
    if not duplicates:
        messagebox.showinfo("Info", "Aucun doublon à exporter.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Fichier CSV", "*.csv")],
        title="Enregistrer le rapport"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Hash", "Fichiers"])
            for hash_value, paths in duplicates.items():
                writer.writerow([hash_value, ", ".join(paths)])
        messagebox.showinfo("Succès", "Rapport exporté avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exporter le rapport : {e}")


def delete_selected():
    """Supprime les fichiers sélectionnés."""
    to_delete = [path for path, var in selected_files.items() if var.get()]
    if not to_delete:
        messagebox.showinfo("Info", "Aucun fichier sélectionné pour suppression.")
        return

    if temp_delete_var.get():  # Suppression temporaire
        for file_path in to_delete:
            try:
                send_to_trash(normalize_path(file_path))
            except Exception as e:
                print(f"Erreur lors de la suppression temporaire de {file_path} : {e}")
        messagebox.showinfo("Succès", "Les fichiers sélectionnés ont été déplacés temporairement.")
    else:  # Suppression définitive
        for file_path in to_delete:
            try:
                os.remove(normalize_path(file_path))
            except Exception as e:
                print(f"Erreur lors de la suppression définitive de {file_path} : {e}")
        messagebox.showinfo("Succès", "Les fichiers sélectionnés ont été supprimés définitivement.")

    # Nettoyer avant de relancer l'analyse
    
    selected_files.clear()
    for widget in frame_results.winfo_children():
        widget.destroy()

    analyze()  # Met à jour la liste après suppression


def analyze():
    """Lance l'analyse des doublons."""
    global stop_analysis
    stop_analysis = False

    folder = entry_directory.get()
    if not os.path.isdir(folder):
        messagebox.showerror("Erreur", "Veuillez sélectionner un répertoire valide.")
        return

    file_types = [ft.strip() for ft in entry_file_types.get().split(",") if ft.strip()]
    for widget in frame_results.winfo_children():
        widget.destroy()

    progress_bar.pack(fill="x", padx=10, pady=10)
    duplicates = find_duplicates_with_progress(folder, file_types, progress_bar)
    global current_duplicates
    current_duplicates = duplicates
    progress_bar.pack_forget()

    if stop_analysis:
        messagebox.showinfo("Interruption", "Analyse interrompue.")
        return

    if not duplicates:
        messagebox.showinfo("Résultat", "Aucun doublon trouvé.")
        return

    canvas = tk.Canvas(frame_results)
    scrollbar = ttk.Scrollbar(frame_results, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for hash_value, paths in duplicates.items():
        label_hash = tk.Label(scrollable_frame, text=f"Hash : {hash_value}", font=("Arial", 10, "bold"))
        label_hash.pack(anchor="w")
        for path in paths:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(scrollable_frame, text=path, variable=var, wraplength=500)
            chk.pack(anchor="w")
            selected_files[path] = var


def select_directory():
    """Ouvre une boîte de dialogue pour sélectionner un répertoire."""
    folder = filedialog.askdirectory()
    if folder:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, folder)


def stop_analysis_command():
    """Interrompt l'analyse en cours."""
    global stop_analysis
    stop_analysis = True


root = tk.Tk()
root.title("Détecteur de Doublons")
root.configure(bg="#f0f4f7")

frame_directory = ttk.LabelFrame(root, text="Sélection du répertoire")
frame_directory.pack(fill="x", padx=10, pady=10)

label_directory = ttk.Label(frame_directory, text="Répertoire :")
label_directory.pack(side="left")

entry_directory = ttk.Entry(frame_directory, width=50)
entry_directory.pack(side="left", padx=5)

btn_browse = ttk.Button(frame_directory, text="Parcourir", command=select_directory)
btn_browse.pack(side="left")

frame_file_types = ttk.LabelFrame(root, text="Types de fichiers (séparés par des virgules, ex: .jpg, .png)")
frame_file_types.pack(fill="x", padx=10, pady=10)

entry_file_types = ttk.Entry(frame_file_types, width=50)
entry_file_types.pack(padx=5, pady=5)

frame_options = ttk.LabelFrame(root, text="Options de suppression")
frame_options.pack(fill="x", padx=10, pady=10)

temp_delete_var = tk.BooleanVar(value=True)
radio_temp = tk.Radiobutton(frame_options, text="Suppression temporaire (restaurable)", variable=temp_delete_var, value=True)
radio_temp.pack(anchor="w", padx=5, pady=2)

radio_permanent = tk.Radiobutton(frame_options, text="Suppression définitive (irréversible)", variable=temp_delete_var, value=False)
radio_permanent.pack(anchor="w", padx=5, pady=2)

progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress_bar.pack(fill="x", padx=10, pady=10)
progress_bar.pack_forget()

frame_actions = ttk.LabelFrame(root, text="Actions")
frame_actions.pack(fill="x", padx=10, pady=10)

btn_analyze = tk.Button(frame_actions, text="Analyser", command=analyze)
btn_analyze.pack(side="left", padx=5)

btn_stop = tk.Button(frame_actions, text="Arrêter", command=stop_analysis_command)
btn_stop.pack(side="left", padx=5)

btn_delete = tk.Button(frame_actions, text="Supprimer les doublons", command=delete_selected)
btn_delete.pack(side="left", padx=5)

btn_export = tk.Button(frame_actions, text="Exporter rapport", command=lambda: export_report(current_duplicates))
btn_export.pack(side="left", padx=5)

frame_results = ttk.LabelFrame(root, text="Résultats")
frame_results.pack(fill="both", expand=True, padx=10, pady=10)

selected_files = {}
stop_analysis = False

root.mainloop()
