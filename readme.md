# Fuck DBL – Suppression de doublons par hash

**Fuck DBL** est un petit utilitaire Windows qui détecte et supprime les fichiers doublons en utilisant leur **hash MD5** (pas seulement le nom). Il offre une suppression temporaire (corbeille) ou définitive, ainsi qu'un export CSV.

---

## ✨ Fonctionnalités

- Analyse récursive d’un dossier
- Détection fiable par hash MD5
- Filtrage par type de fichiers (`.jpg`, `.pdf`, etc.)
- Suppression **temporaire** (corbeille Windows) ou **définitive**
- Export des doublons détectés au format CSV
- Journal automatique des suppressions (date, hash, type)
- Interface graphique simple (Tkinter)

---

## ⚙️ Configuration requise

- Windows 10 ou 11
- Aucune installation requise (fichier `.exe` autonome)

---

## 🛒 Version prête à l’emploi (recommandée)

Téléchargez l’exécutable prêt à l’emploi sur **Gumroad** :  
👉 [Acheter Fuck DBL – 3 €](https://gumroad.com/l/fuckdbl) *(remplacez par votre vrai lien)*

La version payante inclut :
- Fichier `.exe` sans installation
- Icône et interface propre
- Support par email
- Mises à jour futures

---

## 🐍 Version gratuite (code source)

Vous pouvez exécuter le script Python vous-même si vous avez les connaissances techniques.

## Dépendances

```bash
pip install send2trash tkinter 
```

---

## 📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.

---

## 🙏 Remerciements
Merci à la bibliothèque send2trash pour la gestion de la corbeille.

Merci à la biliothèque tkinter pour l'interface graphique.

Développé par Jean-Sébastien Sainte-Rose.

---

## 📫 Support
Pour toute question ou suggestion, veuillez ouvrir une issue sur GitHub ou me contacter à jeanseb.sainterose@gmail.com.
