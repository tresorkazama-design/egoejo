# Clause Golden Share (Action G) - Pacte d'Associés EGOEJO

**Document** : Clause constitutionnelle pour Pacte d'Associés  
**Date** : 2025-12-19  
**Statut** : Texte juridique à valider par avocat

---

## ARTICLE [X] - ACTION G (GOLDEN SHARE) - DROITS DE VETO ABSOLU

### Section 1 - Détenteur de l'Action G

**1.1** L'Action G (Golden Share) est détenue exclusivement par l'**Association EGOEJO Guardian**, association loi 1901 à but non lucratif, immatriculée au [numéro RNA], dont le siège social est situé [adresse complète].

**1.2** L'Action G est une action de préférence non cessible, non transmissible, et non négociable. Elle ne peut être détenue que par l'Association EGOEJO Guardian ou, en cas de dissolution de celle-ci, par une association de substitution désignée par les statuts de l'Association EGOEJO Guardian.

**1.3** L'Action G confère à son détenteur un droit de vote avec **veto absolu** sur les décisions énumérées à l'article [X].2 ci-dessous, sans préjudice des autres droits attachés aux actions ordinaires.

---

### Section 2 - Champ d'Application du Veto Absolu

L'Action G confère à l'Association EGOEJO Guardian un **droit de veto absolu** sur les décisions suivantes :

#### 2.1 - Modifications de l'Algorithme de Compostage SAKA

**2.1.1** Toute modification, désactivation, ou contournement de l'algorithme de compostage SAKA tel que défini dans le code source de l'application EGOEJO, notamment :

- Toute modification des paramètres de compostage définis dans les variables d'environnement ou la configuration :
  - `SAKA_COMPOST_ENABLED`
  - `SAKA_COMPOST_INACTIVITY_DAYS`
  - `SAKA_COMPOST_RATE`
  - `SAKA_COMPOST_MIN_BALANCE`
  - `SAKA_COMPOST_MIN_AMOUNT`

- Toute modification du code source de la fonction `run_saka_compost_cycle()` ou de toute fonction équivalente dans le code source de l'application.

- Toute désactivation, même temporaire, du mécanisme de compostage automatique.

- Toute modification des règles de calcul de la dépréciation du SAKA inactif.

**2.1.2** Pour l'application de la présente clause, l'**algorithme de compostage SAKA** est défini comme le mécanisme automatique qui :
- Identifie les wallets SAKA inactifs (dont la dernière activité dépasse un seuil défini),
- Calcule et applique une dépréciation (compostage) sur le solde SAKA inactif,
- Transfère le SAKA composté vers le Silo Commun,
- Génère un log de compostage pour traçabilité.

**2.1.3** Toute modification de l'algorithme de compostage SAKA, qu'elle soit technique, paramétrique, ou procédurale, est soumise au veto de l'Action G.

---

#### 2.2 - Convertibilité SAKA/EUR

**2.2.1** Toute création, modification, ou activation d'un mécanisme de conversion, d'échange, ou d'équivalence entre le SAKA et l'EUR (ou toute autre devise monétaire), notamment :

- Toute fonction, service, ou API permettant de convertir du SAKA en EUR ou inversement.

- Toute création d'un taux de change, d'un prix, ou d'une valeur monétaire attribuée au SAKA.

- Toute modification du code source permettant une conversion directe ou indirecte entre SAKA et EUR.

- Toute intégration d'un système d'échange, de marché, ou de plateforme permettant l'échange SAKA/EUR.

**2.2.2** Pour l'application de la présente clause, la **convertibilité SAKA/EUR** est définie comme tout mécanisme, explicite ou implicite, permettant :
- D'échanger du SAKA contre de l'EUR (ou toute autre devise),
- D'attribuer une valeur monétaire au SAKA,
- De créer une équivalence, un taux de change, ou un prix pour le SAKA,
- De transférer de la valeur entre le système SAKA et le système EUR.

**2.2.3** Toute tentative de création d'un mécanisme de convertibilité SAKA/EUR, même partiel, conditionnel, ou futur, est soumise au veto de l'Action G.

---

#### 2.3 - Activation de la Version 2.0 sans Vote Conforme

**2.3.1** Toute activation, déploiement, ou mise en production de la **Version 2.0** (ou toute version ultérieure) de l'application EGOEJO est soumise au veto de l'Action G, sauf si les conditions suivantes sont réunies :

**a)** Un vote conforme a été organisé conformément à l'article [Y] des présents statuts.

**b)** Le vote conforme a obtenu :
- Une majorité qualifiée de [X]% des voix des associés présents ou représentés,
- L'approbation explicite de l'Association EGOEJO Guardian (détentrice de l'Action G),
- L'absence d'opposition de plus de [X]% des utilisateurs actifs de la plateforme (définis comme ayant une activité dans les 90 derniers jours).

**c)** Le vote conforme a été précédé d'une période de consultation publique d'au moins [X] jours, pendant laquelle :
- Les modifications proposées ont été documentées et rendues publiques,
- Les utilisateurs ont pu exprimer leur avis via un mécanisme de consultation,
- Les risques et impacts ont été évalués et communiqués.

**2.3.2** Pour l'application de la présente clause, la **Version 2.0** est définie comme toute version de l'application EGOEJO qui :
- Active la fonctionnalité `ENABLE_INVESTMENT_FEATURES=True` (ou équivalent),
- Introduit des mécanismes de rendement financier sur le SAKA,
- Modifie la structure économique fondamentale (SAKA/EUR) de manière incompatible avec la Version 1.0,
- Introduit des fonctionnalités d'investissement, de prêt, ou de rendement financier.

**2.3.3** Toute activation de la Version 2.0, même partielle, progressive, ou conditionnelle, sans respect des conditions énumérées à l'article [X].2.3.1, est soumise au veto de l'Action G.

---

### Section 3 - Modalités d'Exercice du Veto

**3.1** Le veto de l'Action G est exercé par l'Association EGOEJO Guardian dans un délai de [X] jours ouvrés à compter de la notification de la décision soumise au veto.

**3.2** Le veto est exercé par une décision formelle de l'Association EGOEJO Guardian, communiquée par écrit (courrier recommandé avec accusé de réception ou courrier électronique avec accusé de réception) au représentant légal de la Société.

**3.3** Le veto de l'Action G est **irrévocable** et **sans appel**. Aucune décision soumise au veto ne peut être mise en œuvre tant que le veto n'a pas été levé par l'Association EGOEJO Guardian.

**3.4** En cas d'exercice du veto, la décision concernée est **suspendue** jusqu'à ce que :
- Soit le veto soit levé par l'Association EGOEJO Guardian,
- Soit la décision soit modifiée pour respecter les exigences constitutionnelles EGOEJO.

---

### Section 4 - Obligations de Notification

**4.1** La Société s'engage à notifier à l'Association EGOEJO Guardian, dans un délai de [X] jours ouvrés, toute décision relevant du champ d'application du veto de l'Action G.

**4.2** La notification doit inclure :
- La description détaillée de la décision,
- Les modifications techniques ou procédurales envisagées,
- Les justifications et motivations,
- Les impacts attendus sur le système SAKA et la structure économique EGOEJO.

**4.3** L'absence de notification dans les délais prévus constitue une violation des présents statuts et peut entraîner l'exercice rétroactif du veto.

---

### Section 5 - Protection Constitutionnelle

**5.1** La présente clause est **irrévocable** et ne peut être modifiée, suspendue, ou contournée que par :
- Un vote unanime de tous les associés,
- L'approbation explicite de l'Association EGOEJO Guardian,
- Une modification des statuts de l'Association EGOEJO Guardian elle-même.

**5.2** Toute tentative de contournement, de modification, ou de suppression de la présente clause, par quelque moyen que ce soit (modification des statuts, fusion, scission, etc.), est **nulle et non avenue**.

**5.3** La présente clause s'applique à la Société, à ses filiales, à ses successeurs, et à toute entité résultant d'une fusion, d'une scission, ou d'une transformation.

---

### Section 6 - Sanctions en Cas de Violation

**6.1** Toute violation de la présente clause, notamment :
- La mise en œuvre d'une décision soumise au veto sans l'approbation de l'Action G,
- La modification de l'algorithme de compostage sans notification et approbation,
- La création d'un mécanisme de convertibilité SAKA/EUR,
- L'activation de la Version 2.0 sans vote conforme,

entraîne :

**a)** La nullité de la décision ou de l'action concernée.

**b)** L'obligation de rétablir l'état antérieur dans un délai de [X] jours.

**c)** Le versement d'une indemnité forfaitaire de [montant] EUR à l'Association EGOEJO Guardian, sans préjudice des dommages et intérêts.

**d)** La possibilité pour l'Association EGOEJO Guardian de demander la dissolution de la Société en cas de violation répétée ou grave.

---

### Section 7 - Dispositions Finales

**7.1** La présente clause est rédigée en français. En cas de traduction, seule la version française fait foi.

**7.2** La présente clause est régie par le droit français. Tout litige relatif à son interprétation ou à son application relève de la compétence exclusive des tribunaux de [ville, département].

**7.3** La présente clause entre en vigueur à compter de la date de signature des présents statuts et s'applique à toutes les décisions prises postérieurement à cette date.

---

**Fait à [ville], le [date]**

**Pour l'Association EGOEJO Guardian :**
[Signature du Président]

**Pour la Société EGOEJO :**
[Signature du représentant légal]

---

## NOTES POUR L'AVOCAT

### Points à valider juridiquement :

1. **Conformité avec le droit des sociétés** : Vérifier que la clause Golden Share est conforme au droit français (Code de commerce, notamment articles L225-1 et suivants).

2. **Irrévocabilité** : Vérifier la validité juridique de l'irrévocabilité de la clause et les conditions de modification.

3. **Sanctions** : Adapter les sanctions (nullité, indemnité, dissolution) selon le droit applicable.

4. **Délais** : Définir les délais de notification et d'exercice du veto selon les pratiques usuelles.

5. **Majorités qualifiées** : Définir les majorités requises pour le vote conforme (article [Y]).

6. **Définition de la Version 2.0** : Préciser la définition technique de la Version 2.0 en référence au code source.

7. **Compétence territoriale** : Définir le tribunal compétent selon le siège social de la Société.

---

*Document généré le : 2025-12-19*  
*À valider par un avocat spécialisé en droit des sociétés et droit numérique*

