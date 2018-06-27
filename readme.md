# BnFtoBibLaTeX

Script python 3.6 de conversion de notices bibliographiques de la BnF vers des entrées BibLaTeX.

## Fonctionnalités

* Conversion à partir d'une URL ark http://catalogue.bnf.fr ou bien http://gallica.bnf.fr
* Utilisation des [API BnF](http://api.bnf.fr/accueil)
* Mapping des métadonnées BnF du format dublincore vers le format BibLaTex
* Détection de métadonnées supplémentaires (nombre de pages, ville d'édition...) quand possible
* Interface en ligne de commande (*CLI interface*)

## Installation

1. Cloner le dépôt :
```
git clone https://framagit.org/leodumont/BnFtoBibLaTeX.git
```
2. Se déplacer dans le répertoire du script :
```
cd BnFtoBibLaTex
```
3. Installer les dépendances avec pip :
```
pip3 install -r requirements.t
```

## Usage

Dans le répertoire du script :

* affichage de l'aide :
```
python3 BnFtoBibLaTex.py -h
```
* exemple à partir d'une URL ark vers fichier de sortie :
```
python3 BnFtoBibLaTex.py url "http://catalogue.bnf.fr/ark:/12148/cb30028011c" --sortie "/home/leo/Bureau/out.bib"
```
* exemple à partir d'un fichier d'URL ark vers fichier de sortie :
```
python3 BnFtoBibLaTex.py fichier "/home/leo/Bureau/in.txt" --sortie "/home/leo/reau/out.bib"
```
* exemple à partir d'une URL ark vers une sortie *stdout* :
```
 python3 BnFtoBibLaTex.py url "http://gallica.bnf.fr/ark:/12148/bpt6k6471872n"
```

## À faire

* Rajouter le support des notices de périodique
* Refactoriser l'ensemble...
* Revoir la génération des clés : en faire une
fonction propre et permettre la personnification ?
* Ajouter une option pour faire des pauses aléatoires
quand beaucoup d'url à parser ?
* Rajouter des options pour garder ISBN, EAN ?
* Idem pour les mots clés rameaux ?
* Ajouter une option pour intégrer des mots clés en série
sur toutes les entrées importées .