# Clause de Subordination - Définition Juridique du SAKA et Droit au Compostage

**Document** : Clause constitutionnelle pour CGU et Statuts SAS à Mission  
**Date** : 2025-12-19  
**Statut** : Texte juridique à valider par avocat

---

## ARTICLE [X] - DÉFINITION JURIDIQUE DU SAKA

### Section 1 - Nature Juridique du SAKA

**1.1** Le **SAKA** (acronyme de "Système d'Attribution de Karma d'Activité") est défini comme une **unité de compte de réputation non-monétaire**, exclusivement utilisée dans le cadre de la plateforme EGOEJO.

**1.2** Le SAKA n'est **pas une monnaie**, **pas un instrument financier**, **pas un titre de créance**, et **pas un actif numérique** au sens du droit financier ou monétaire.

**1.3** Le SAKA est une **unité de mesure de l'engagement relationnel** et de la **participation active** de l'utilisateur à la communauté EGOEJO.

---

### Section 2 - Caractéristiques Juridiques du SAKA

**2.1 - Non-Monétarité**

**2.1.1** Le SAKA ne peut pas être :
- Converti en EUR ou en toute autre devise monétaire,
- Échangé contre de l'argent ou des biens,
- Utilisé comme moyen de paiement,
- Cédé, vendu, ou transféré contre une contrepartie monétaire,
- Garanti, nanti, ou donné en garantie d'une créance monétaire.

**2.1.2** Toute tentative de monétisation, de conversion, ou d'échange du SAKA contre une contrepartie monétaire est **interdite** et **nulle de plein droit**.

**2.1.3** Le SAKA n'a **aucune valeur monétaire** et ne peut faire l'objet d'une évaluation financière.

---

**2.2 - Non-Négociabilité**

**2.2.1** Le SAKA est **strictement personnel** et **non transférable**, sauf dans les cas expressément prévus par les présentes conditions générales d'utilisation :
- Plantation dans un projet (transfert vers le projet),
- Compostage (transfert vers le Silo Commun),
- Redistribution (attribution depuis le Silo Commun).

**2.2.2** Le SAKA ne peut pas être :
- Cédé à un tiers,
- Transmis par succession,
- Fait l'objet d'un contrat de vente, de location, ou de prêt,
- Utilisé comme garantie ou collatéral.

**2.2.3** Toute cession, vente, ou transfert du SAKA en violation des présentes conditions est **nul et non avenue**.

---

**2.3 - Non-Garantie de Conservation**

**2.3.1** Le SAKA est soumis à un mécanisme de **dépréciation automatique** (compostage) en cas d'inactivité de l'utilisateur, conformément à l'article [X].3 ci-dessous.

**2.3.2** L'utilisateur **n'a aucun droit** à la conservation indéfinie de son solde SAKA.

**2.3.3** La Société **ne garantit pas** :
- La pérennité du solde SAKA,
- L'absence de dépréciation,
- La possibilité d'accumuler du SAKA indéfiniment.

---

**2.4 - Usage Exclusif dans la Plateforme**

**2.4.1** Le SAKA ne peut être utilisé que dans le cadre de la plateforme EGOEJO, exclusivement pour :
- La participation aux votes et décisions collectives,
- Le soutien aux projets (plantation),
- L'accès à certaines fonctionnalités de la plateforme.

**2.4.2** Le SAKA ne peut pas être utilisé en dehors de la plateforme EGOEJO.

---

**2.5 - Interdiction de Fusion de Données**

**2.5.1** Il est strictement interdit de fusionner, combiner, ou croiser les données SAKA avec les données EUR pour créer un profil utilisateur unifié, un scoring combiné, ou toute autre forme de traitement de données combinées.

**2.5.2** Toute fusion de données SAKA/EUR, même partielle, conditionnelle, ou à des fins d'analyse, est interdite et nulle de plein droit.

**2.5.3** La vente, la cession, ou le partage de données de profilage combinant SAKA et EUR est strictement interdite et constitue une violation de la constitution EGOEJO.

**2.5.4** Toute tentative de fusion de données SAKA/EUR, qu'elle soit technique (jointure SQL, fusion de bases de données) ou procédurale (export combiné, API unifiée), est soumise au veto de l'Action G conformément à l'article [X] des statuts.

**2.5.5** La présente interdiction s'applique également aux tiers (partenaires commerciaux, prestataires, sous-traitants) ayant accès aux données EGOEJO.

---

### Section 3 - Droit au Compostage (Dépréciation Automatique)

**3.1 - Principe du Compostage**

**3.1.1** L'utilisateur **accepte expressément** que son solde SAKA soit soumis à un mécanisme de **dépréciation automatique** (compostage) en cas d'inactivité.

**3.1.2** Le compostage est un **droit de la Société** et une **obligation de l'utilisateur** en tant que condition d'utilisation de la plateforme.

**3.1.3** L'utilisateur **renonce expressément** à tout recours contre la Société en cas de dépréciation de son solde SAKA due au compostage.

---

**3.2 - Conditions de Compostage**

**3.2.1** Le compostage s'applique automatiquement lorsque :
- L'utilisateur n'a pas eu d'activité sur la plateforme pendant une période supérieure à [X] jours (définie par la variable `SAKA_COMPOST_INACTIVITY_DAYS`),
- Le solde SAKA de l'utilisateur est supérieur à un seuil minimum (défini par la variable `SAKA_COMPOST_MIN_BALANCE`).

**3.2.2** Le compostage consiste en :
- Le calcul d'une dépréciation sur le solde SAKA inactif (définie par la variable `SAKA_COMPOST_RATE`),
- Le transfert du SAKA composté vers le Silo Commun,
- La génération d'un log de compostage pour traçabilité.

**3.2.3** Les paramètres du compostage (seuil d'inactivité, taux de dépréciation, seuil minimum) sont définis dans le code source de l'application et peuvent être modifiés par la Société, sous réserve du veto de l'Action G conformément à l'article [X] des statuts.

---

**3.3 - Acceptation du Compostage**

**3.3.1** En créant un compte sur la plateforme EGOEJO, l'utilisateur **accepte expressément** :
- Le mécanisme de compostage,
- La dépréciation de son solde SAKA en cas d'inactivité,
- Le transfert du SAKA composté vers le Silo Commun,
- L'absence de compensation ou d'indemnisation en cas de compostage.

**3.3.2** L'acceptation du compostage est une **condition sine qua non** de l'utilisation de la plateforme EGOEJO.

**3.3.3** Toute utilisation de la plateforme EGOEJO implique l'acceptation **irrévocable** du mécanisme de compostage.

---

**3.4 - Renonciation aux Recours**

**3.4.1** L'utilisateur **renonce expressément** à tout recours contre la Société, ses dirigeants, ses associés, ou ses prestataires, en cas de :
- Dépréciation de son solde SAKA due au compostage,
- Perte de SAKA résultant du mécanisme de compostage,
- Modification des paramètres de compostage,
- Application du compostage même en cas d'inactivité involontaire.

**3.4.2** Cette renonciation s'applique à tous les recours, qu'ils soient :
- Contractuels (résolution, dommages et intérêts),
- Délictuels (responsabilité civile),
- Réglementaires (réclamation auprès d'une autorité),
- Judiciaires (action en justice).

**3.4.3** La renonciation aux recours est **irrévocable** et s'applique à l'utilisateur, à ses héritiers, et à ses ayants droit.

---

**3.5 - Notification du Compostage**

**3.5.1** La Société s'engage à informer l'utilisateur du compostage de son solde SAKA :
- Par notification dans l'interface de la plateforme,
- Par courrier électronique si l'utilisateur a fourni une adresse email valide,
- Par affichage dans le tableau de bord de l'utilisateur.

**3.5.2** La notification indique :
- Le montant de SAKA composté,
- La date du compostage,
- Le solde SAKA restant,
- Le montant transféré au Silo Commun.

**3.5.3** L'absence de notification ne remet pas en cause la validité du compostage.

---

### Section 4 - Subordination du SAKA à la Structure Relationnelle

**4.1 - Priorité de la Structure Relationnelle**

**4.1.1** Le SAKA est un élément de la **structure relationnelle** EGOEJO, qui est **prioritaire** et **souveraine** par rapport à la structure instrumentale (EUR).

**4.1.2** Le SAKA ne peut **jamais** être subordonné, conditionné, ou dépendant de la structure instrumentale (EUR).

**4.1.3** Toute modification du SAKA qui le subordonnerait à l'EUR est **interdite** et **nulle de plein droit**.

---

**4.2 - Indépendance du SAKA**

**4.2.1** Le SAKA fonctionne de manière **indépendante** et **autonome** par rapport à l'EUR.

**4.2.2** Le SAKA ne peut pas être :
- Conditionné par un apport en EUR,
- Garanti par un dépôt en EUR,
- Converti en EUR,
- Évalué en EUR.

**4.2.3** Toute tentative de liaison, de conversion, ou de dépendance entre SAKA et EUR est **interdite** et **nulle de plein droit**.

---

### Section 5 - Dispositions Contractuelles

**5.1 - Intégration dans les CGU**

**5.1.1** La présente clause est **intégrée** aux Conditions Générales d'Utilisation (CGU) de la plateforme EGOEJO.

**5.1.2** L'acceptation des CGU implique l'acceptation **irrévocable** de la présente clause.

**5.1.3** Toute modification de la présente clause doit être notifiée aux utilisateurs avec un préavis de [X] jours.

---

**5.2 - Intégration dans les Statuts**

**5.2.1** La présente clause est **intégrée** aux statuts de la Société EGOEJO.

**5.2.2** La modification de la présente clause est soumise au veto de l'Action G conformément à l'article [X] des statuts.

---

**5.3 - Prévalence**

**5.3.1** En cas de contradiction entre la présente clause et toute autre disposition des CGU ou des statuts, la présente clause **prévaut**.

**5.3.2** La présente clause est **d'ordre public** et ne peut être écartée par accord des parties.

---

### Section 6 - Sanctions en Cas de Violation

**6.1** Toute violation de la présente clause, notamment :
- Tentative de monétisation du SAKA,
- Tentative de conversion SAKA/EUR,
- Refus d'accepter le compostage,
- Recours contre la Société en cas de compostage,

entraîne :

**a)** La résiliation immédiate du compte utilisateur.

**b)** La perte de tout solde SAKA.

**c)** L'interdiction d'accès à la plateforme.

**d)** Le versement d'une indemnité forfaitaire de [montant] EUR à la Société, sans préjudice des dommages et intérêts.

---

### Section 7 - Dispositions Finales

**7.1** La présente clause est rédigée en français. En cas de traduction, seule la version française fait foi.

**7.2** La présente clause est régie par le droit français. Tout litige relatif à son interprétation ou à son application relève de la compétence exclusive des tribunaux de [ville, département].

**7.3** La présente clause entre en vigueur à compter de la date de signature des CGU et s'applique à tous les utilisateurs de la plateforme EGOEJO.

---

**Fait à [ville], le [date]**

**Pour la Société EGOEJO :**
[Signature du représentant légal]

---

## NOTES POUR L'AVOCAT

### Points à valider juridiquement :

1. **Nature juridique du SAKA** : Vérifier que la qualification d'"unité de compte de réputation non-monétaire" est conforme au droit français et ne relève pas de la réglementation financière (AMF, Banque de France).

2. **Renonciation aux recours** : Vérifier la validité juridique de la renonciation aux recours, notamment en cas de faute lourde ou dolosive de la Société.

3. **Clause d'ordre public** : Vérifier que la clause peut être qualifiée d'ordre public et ne peut être écartée par accord des parties.

4. **Sanctions** : Adapter les sanctions (résiliation, indemnité) selon le droit applicable et les pratiques usuelles.

5. **Notification** : Définir les modalités de notification du compostage selon les exigences légales (RGPD, droit de la consommation).

6. **Délai de préavis** : Définir le délai de préavis pour modification de la clause selon les pratiques usuelles.

7. **Compétence territoriale** : Définir le tribunal compétent selon le siège social de la Société.

8. **Conformité RGPD** : Vérifier que le mécanisme de compostage et la notification sont conformes au RGPD.

9. **Droit de la consommation** : Vérifier que la clause est conforme au droit de la consommation (clauses abusives, information du consommateur).

10. **Définition technique** : Préciser les références techniques (variables, fonctions) en annexe pour éviter toute ambiguïté.

---

## ANNEXE - Définitions Techniques

### Variables de Configuration SAKA

- `SAKA_COMPOST_ENABLED` : Activation/désactivation du compostage (True/False)
- `SAKA_COMPOST_INACTIVITY_DAYS` : Nombre de jours d'inactivité avant éligibilité au compostage
- `SAKA_COMPOST_RATE` : Taux de dépréciation (ex: 0.1 = 10% du solde)
- `SAKA_COMPOST_MIN_BALANCE` : Solde minimum requis pour compostage
- `SAKA_COMPOST_MIN_AMOUNT` : Montant minimum composté par cycle

### Fonctions Techniques

- `run_saka_compost_cycle()` : Fonction principale de compostage
- `SakaWallet` : Modèle de données représentant le wallet SAKA d'un utilisateur
- `SakaSilo` : Modèle de données représentant le Silo Commun

---

*Document généré le : 2025-12-19*  
*À valider par un avocat spécialisé en droit numérique, droit de la consommation, et réglementation financière*

