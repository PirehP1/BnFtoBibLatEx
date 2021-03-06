# BnFtoBibLaTeX

Script python 3.6 de conversion de notices bibliographiques de la BnF vers des entrées BibLaTeX à partir d'URL pérenne de type ARK.

## Fonctionnalités

* Conversion à partir d'une URL ark http://catalogue.bnf.fr ou bien http://gallica.bnf.fr
* Utilisation des [API BnF](http://api.bnf.fr/accueil)
* Mapping des métadonnées BnF du format dublincore vers le format BibLaTex
* Détection de métadonnées supplémentaires (nombre de pages, ville d'édition, préfacier/postfacier, traducteur...) quand possible
* Interface en ligne de commande (*CLI interface*)

## Installation

1. Cloner le dépôt :
`git clone https://framagit.org/leodumont/BnFtoBibLaTeX.git`
2. Se déplacer dans le répertoire du script :
`cd BnFtoBibLaTex`
3. Installer les dépendances avec pip :
`pip3 install -r requirements.txt`

## Utilisation

* affichage de l'aide :
`python3 BnFtoBibLaTex.py -h`

### Options disponibles

* Appel du script :
`python3 BnFtoBibLatex.py`
* Arguments obligatoires :
  * `url` ou `fichier` : précise si l'entrée est une URL ark ou bien un fichier contenant une URL ark par ligne
  * `input_ark` : chemin vers le fichier d'entrée ou URL ark
* Argument optionnel :
  * `--sortie` : chemin vers le fichier de sortie dans lequel seronts enregistrées les entrées BibLaTeX

### Exemples d'utilisation

Dans le répertoire du script :

* exemple à partir d'une URL ark vers fichier de sortie :
`python3 BnFtoBibLaTex.py url "http://catalogue.bnf.fr/ark:/12148/cb30028011c" --sortie "/home/user/Bureau/out.bib"`
* exemple à partir d'un fichier d'URL ark vers fichier de sortie :
`python3 BnFtoBibLaTex.py fichier "/home/user/Bureau/in.txt" --sortie "/home/user/reau/out.bib"`
* exemple à partir d'une URL ark vers une sortie *stdout* :
`python3 BnFtoBibLaTex.py url "http://gallica.bnf.fr/ark:/12148/bpt6k6471872n"`

## À faire

* Rajouter le support des notices de périodique (ex. : http://catalogue.bnf.fr/ark:/12148/cb39294634r ou http://catalogue.bnf.fr/ark:/12148/cb410738678)
* Refactoriser l'ensemble...
* Revoir la génération des clés : en faire une
fonction propre et permettre la personnification ?
* Ajouter une option pour faire des pauses aléatoires
quand beaucoup d'url à parser ?
* Rajouter des options pour garder ISBN, EAN ?
* Idem pour les mots clés rameaux ?
* Ajouter une option pour intégrer des mots clés en série
sur toutes les entrées importées .
