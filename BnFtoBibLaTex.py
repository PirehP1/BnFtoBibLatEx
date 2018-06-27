#!/usr/bin/python3
# coding: utf-8

import requests
from requests.utils import requote_uri
import re
from lxml import etree
from collections import defaultdict
import argparse
import os
import sys
import timeit


def checkURL(url_ark):
    """ On vérifie que l'URL existe, puis on teste l'URL
    avec un regex pour savoir si l'URL est une Gallica ou
    bien Catalogue général."""
    checkGallica = re.search('^https?://gallica\.bnf\.fr/ark:/12148/', url_ark)
    checkCatalogueG = re.search('^https?://catalogue\.bnf\.fr/ark:/12148/', url_ark)
    try:
        checker = requests.get(url_ark)
        if checker.status_code is not 200:
            print("Erreur URL : url semble injoignable.")
            sys.exit()
        elif checkCatalogueG is None and checkGallica is None:
            print("Erreur URL : la chaîne ne correspond pas à une url ark Catalogue général ou Gallica.")
            sys.exit()
        elif checker.url == "http://catalogue.bnf.fr/error400.do":
            print("Erreur URL : erreur 404 renvoyée par catalogue.bnf.fr.")
            sys.exit()
        else:
            if checkGallica is not None:
                type_ark = "gallica"
            else:
                type_ark = "catalogueG"
    except:
        print("Erreur URL : la chaîne n'est pas une URL valide.")
        sys.exit()

    return type_ark


def GallicaToCatalogueG(url_ark, type_ark):
    """ Lorsque l'entrée est un ark Gallica, cette
    fonction va chercher l'ark correspondant dans
    catalogue G afin de travailler à partir de ce
    dernier pour la suite (meilleures qualités des
    métadonnées)"""
    if type_ark == "gallica":
        xmlGallica = getXML(url_ark, type_ark)
        arbre = etree.parse(xmlGallica)
        nsmap = {'dc': 'http://purl.org/dc/elements/1.1/'}
        element = arbre.xpath("//dc:relation", namespaces=nsmap)
        for tag in element:
            regex = re.search('(http://.*)', tag.text)
            url_ark = regex.group(0)
        type_ark = "catalogueG"
    else:
        url_ark = url_ark
        type_ark = "catalogueG"
    return url_ark, type_ark


def getArk(url_ark):
    """ On récupère l'identifiant ARK dans l'URL passée."""
    id_ark = re.search('(ark:/[0-9]*/.*)', url_ark)
    return id_ark.group(0)


def getXML(id_ark, type_ark):
    """ On récupère le XML du dublincore correspondant au ARK
    en passant par une requête SRU dont on récupère le contenu
    via requests (argument stream=True important car il permet
    de récupérer un flux non compressé parsable par lxml ensuite).
    Selon qu'il s'agisse d'un ARK Gallica ou
    Catalogue général, la requête SRU n'est pas la même.
    """
    if type_ark == "catalogueG":
        url_sru = "http://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=(bib.ark any \"{}\")&recordSchema=dublincore".format(id_ark)
    else:
        url_sru = "http://gallica.bnf.fr/SRU?operation=searchRetrieve&version=1.2&maximumRecords=10&       startRecord=1&query=dc.identifier adj \"{}\"".format(id_ark)

    url_sru = requote_uri(url_sru)
    response = requests.get(url_sru, timeout=60, verify=False, stream=True)
    response.raw.decode_content = True
    dc_xml = response.raw
    return dc_xml


def parseXML(dc_xml):
    """ On parse le XML qui contient les métadonnées
    dublincore. Après l'expression xpath j'efface les
    espaces de noms avec un regex, c'est pas très clean
    mais j'ai pas trouvé comment faire autrement. Ça renvoie
    un dictionnaire de type defaultdict avec toutes les métadonnées.
    Ce format permet de gérer le fait qu'il puisse y avoir plusieurs
    valeurs pour une même clé (auteurs multiples par exemple)"""
    arbre = etree.parse(dc_xml)
    # print(etree.tostring(arbre, pretty_print=True))
    # nsmap = {'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    #          'dc': 'http://purl.org/dc/elements/1.1/',
    #          'srw': 'http://www.loc.gov/zing/srw/'}
    # element = arbre.xpath("/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/oai_dc:dc/", namespaces=nsmap)
    element = arbre.xpath("//*[namespace-uri()='http://purl.org/dc/elements/1.1/']")
    metadonnees = defaultdict(list)
    for child in element:
        tag = re.sub('\{.*\}', '', child.tag)
        metadonnees[tag].append(child.text)
    return metadonnees


def DCtoBibLaTex(metadonnees):
    """ Fonction de mapping entre les catégories Dublin Core
    et les champs BibLaTeX. Pour ça, définition d'un dictionnaire
    python qui contien les équivalences. Génération d'une clé
    sur le modèle AuteurAnnée en prenant toujours le premier
    auteur/directeur listé en cas d'auteurs/directeurs multiples"""

    mapping = {
        'creator': 'author',
        'contributor': 'editor',
        'title': 'title',
        'date': 'year',
        'publisher': 'publisher',
        'description': 'series',
        'format': 'note',
        'identifier': 'url',
        'subject': 'keywords'
    }

    BibLaTeX_values = {}
    for key in metadonnees.keys() & mapping.keys():
        BibLaTeX_values[mapping[key]] = metadonnees[key]

    ## Génération de la clé
    if "author" in BibLaTeX_values:
        nom_cle = BibLaTeX_values["author"][0]
        # if len(nom_cle) > 12:
        #     nom_cle = BibLaTeX_values["author"][0][:10]
    elif "editor" in BibLaTeX_values:
        nom_cle = BibLaTeX_values["editor"][0]
        # if len(nom_cle) > 12:
        #     nom_cle = BibLaTeX_values["editor"][0][:10]
    else:
        nom_cle = BibLaTeX_values["title"][0]

    if "year" in BibLaTeX_values:
        annee = BibLaTeX_values["year"][0]
    else:
        annee = ""

    nom_cle = re.search('(\w+)', nom_cle)
    cle = nom_cle.group(0) + annee
    cle = re.sub('\s', '', cle)

    BibLaTeX_values["key"] = cle

    return BibLaTeX_values


def BetterMapping(BibLaTeX_values):
    """ Fonction qui tente d'améliorer le mapping vers BibLaTeX
    en repérant les auteurs multiples, les directeurs/auteurs,
    les pages, les éditeurs/villes de publication, nettoie
    certaines données inutiles, etc. C'est un énorme bordel
    mal codé sans aucun doute..."""

    if "author" in BibLaTeX_values:
        auteurs = BibLaTeX_values["author"]
        auteurs_propre = []
        for contenu in auteurs:
            nom = re.match('(.*)(?=\.)', contenu)
            nom = nom.group(0)
            nom = re.sub('\s\(.*\)', '', nom)
            auteurs_propre.append(nom)
        BibLaTeX_values["author"] = auteurs_propre

    if "editor" in BibLaTeX_values:
        editeurs = BibLaTeX_values["editor"]
        editeurs_propre = []
        preface_propre = []
        postface_propre = []
        trad_propre = []
        for contenu in editeurs:
            nom = re.match('(.*)(?=\.)', contenu)
            nom = nom.group(0)
            nom = re.sub('\s\(.*\)', '', nom)
            editeurs_propre.append(nom)
            if re.search('Préfacier', contenu) is not None:
                preface_propre.append(nom)
                BibLaTeX_values["foreword"] = preface_propre
                editeurs_propre.remove(nom)
            elif re.search('Traducteur', contenu) is not None:
                trad_propre.append(nom)
                BibLaTeX_values["translator"] = trad_propre
                editeurs_propre.remove(nom)
            elif re.search('Postfacier', contenu) is not None:
                postface_propre.append(nom)
                BibLaTeX_values["afterword"] = postface_propre
                editeurs_propre.remove(nom)
        if len(editeurs_propre) > 0:
            BibLaTeX_values["editor"] = editeurs_propre
        else:
            del BibLaTeX_values["editor"]

    if "note" in BibLaTeX_values:
        notes = BibLaTeX_values["note"]
        for contenu in notes:
            pages = re.search('(\d+)(?=\sp\.)', contenu)
            if pages is not None:
                pages_final = pages.group(0)
            else:
                pages_final = None
        if pages_final is not None:
            BibLaTeX_values["pagetotal"] = pages_final
        del BibLaTeX_values["note"]

    if "url" in BibLaTeX_values:
        url = BibLaTeX_values["url"]
        url_good = []
        for contenu in url:
            if re.match('^http://.*$', contenu) is not None:
                url_good.append(contenu)
        BibLaTeX_values["url"] = url_good

    if "publisher" in BibLaTeX_values:
        publisher = BibLaTeX_values["publisher"]
        ville_propre = []
        editeur_propre = []
        for contenu in publisher:
            edition = re.search('(.*)\s\((.*)\)', contenu)
            if edition is not None:
                ville_finale = edition.group(2)
                editeur_final = edition.group(1)
            else:
                ville_finale = None
                editeur_final = None

            if ville_finale is not None:
                ville_propre.append(ville_finale)
                BibLaTeX_values["location"] = ville_propre
            if editeur_final is not None:
                editeur_propre.append(editeur_final)
                BibLaTeX_values["publisher"] = editeur_propre

    if "keywords" in BibLaTeX_values:
        keywords = BibLaTeX_values["keywords"]
        for contenu in keywords:
            if re.search('Actes? de congrès', contenu) is not None:
                type_notice = "proceedings"
                # del BibLaTeX_values["keywords"]
            else:
                type_notice = "book"
        del BibLaTeX_values["keywords"]
    else:
        type_notice = "book"

    if "series" in BibLaTeX_values:
        series = BibLaTeX_values["series"]
        for contenu in series:
            if re.search('^Code à', contenu) is not None:
                series.remove(contenu)

    return BibLaTeX_values, type_notice


def BibLaTeXWriter(BibLaTeX_propre, type_notice):

    if type_notice is "book":
        head = "@book{{{},\n".format(BibLaTeX_propre["key"])
    else:
        head = "@proceedings{{{},\n".format(BibLaTeX_propre["key"])
    del BibLaTeX_propre["key"]

    export = []
    for key, value in sorted(BibLaTeX_propre.items()):
        if type(value) is list:
            if len(value) > 1:
                chaine = " AND ".join(value)
                champ = "{} = {{{}}},\n".format(key, chaine.rstrip())
                export.append(champ)
            else:
                champ = "{} = {{{}}},\n".format(key, value[0].rstrip())
                export.append(champ)
        else:
            champ = "{} = {{{}}},\n".format(key, value.rstrip())
            export.append(champ)

    # on efface la virgule du dernier champ
    last = re.sub(',\n', '\n', export[-1])
    export[-1] = last
    foot = "}\n"
    export = "".join(export)
    entry = head + export + foot

    return entry


def wraper(entree):
    type_ark = checkURL(entree)
    conversion = GallicaToCatalogueG(entree, type_ark)
    url_ark = conversion[0]
    type_ark_final = conversion[1]
    ark = getArk(url_ark)
    xml = getXML(ark, type_ark_final)
    metadonnees = parseXML(xml)
    valeurs_biblatex = DCtoBibLaTex(metadonnees)
    valeurs_propres = BetterMapping(valeurs_biblatex)
    donnees = valeurs_propres[0]
    type_notice = valeurs_propres[1]

    return BibLaTeXWriter(donnees, type_notice)


def main(input_type, input_ark):
    entrees = []
    if input_type == "url":
        entrees.append(wraper(input_ark))
    elif input_type == "fichier":
        if not os.path.isfile(input_ark):
            print("Erreur fichier : la chaîne ({}) ne correspond pas à un fichier.".format(input_ark))
            sys.exit()
        else:
            with open(input_ark, 'r') as fichier:
                lignes = fichier.readlines()
                for url in lignes:
                    entrees.append(wraper(url.rstrip()))

    if args.sortie is not None:
        if not os.path.isfile(args.sortie):
            print("Erreur fichier : la chaîne ({}) ne correspond pas à un dossier.".format(args.sortie))
        else:
            with open(args.sortie, 'w') as fichier:
                for item in entrees:
                    fichier.write(item)
    else:
        for item in entrees:
            print(item)


start_time = timeit.default_timer()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conversion de notices BnF vers entrées BibLaTeX à partir d'URL ark Gallica ou Catalogue général.")
    parser.add_argument("input_type", help="Permet de spécifier le type d'entrée (\"fichier\" ou \"url\")", choices=["url", "fichier"])
    parser.add_argument("input_ark", help="URL du catalogue général de la BnF ou de Gallica ou bien chemin vers un fichier texte contenant les URL (une par ligne)", type=str)
    parser.add_argument("--sortie", help="Chemin vers un fichier texte de sortie.", type=str)
    args = parser.parse_args()
    main(args.input_type, args.input_ark)
elapsed = timeit.default_timer() - start_time
print(elapsed)

""" TODO
- Rajouter le support des notices de périodique
- Revoir la génération des clés : en faire une
fonction propre et permettre la personnification ?
- Ajouter une option pour faire des pauses aléatoires
quand beaucoup d'url à parser
- rajouter des options pour garder ISBN, EAN ?
- idem pour les mots clés rameaux
- créer l'interface graphique
- refactoriser l'ensemble, avec notamment une gestion
des exceptions et des erreurs...
- ajouter une option pour intégrer des mots clés en série
sur toutes les entrées importées.
"""
