# 📝 Recommandations de Rédaction Statutaire

**Version** : 1.0  
**Date** : 2025-01-27

---

## 🎯 Objectif

Ce document fournit des **recommandations précises** pour la rédaction des statuts d'une SAS à mission EGOEJO, garantissant l'alignement avec le label "EGOEJO COMPLIANT".

---

## 📋 Structure Recommandée des Statuts

### 1. Préambule

**Texte Recommandé** :

```markdown
PRÉAMBULE

La société [NOM] a été constituée sous la forme d'une Société par Actions 
Simplifiée (SAS) à mission, conformément à l'article L210-10 du Code de commerce.

La société a pour objet de développer et exploiter une plateforme d'engagement 
citoyen pour la transition écologique et sociale, en respectant strictement 
les principes philosophiques définis dans le Manifeste SAKA/EUR et le label 
"EGOEJO COMPLIANT".

La société reconnaît la primauté de la structure relationnelle (SAKA) sur 
la structure instrumentale (EUR) et s'engage à maintenir cette séparation 
de manière permanente et irréversible.
```

---

### 2. Article X - Raison d'Être

**Texte Recommandé** :

```markdown
Article X - Raison d'Être

Conformément à l'article L210-10 du Code de commerce, la société a pour 
raison d'être de promouvoir une économie relationnelle où la structure 
relationnelle (SAKA) prime toujours sur la structure instrumentale (EUR).

La société s'engage à :

1. Maintenir une séparation stricte et permanente entre :
   - SAKA : Structure relationnelle, non-financière, non-monétaire, 
     non-convertible, dédiée à l'engagement et à la circulation
   - EUR : Structure instrumentale, monnaie fiduciaire, dédiée aux 
     transactions et à la gestion financière

2. Garantir l'anti-accumulation du SAKA par :
   - Le compostage obligatoire après [X] jours d'inactivité (taux minimum 
     de [Y]%)
   - La redistribution équitable du Silo Commun aux membres actifs
   - L'interdiction de toute accumulation passive

3. Assurer la circulation obligatoire du SAKA via :
   - La redistribution automatique du SAKA composté
   - Les limites quotidiennes de récolte
   - L'interdiction de toute thésaurisation

4. Ne jamais permettre, directement ou indirectement :
   - De conversion SAKA ↔ EUR
   - De calcul d'équivalent monétaire du SAKA
   - De présentation du SAKA comme instrument financier ou monétaire

5. Ne jamais présenter le SAKA comme :
   - Un instrument financier (au sens de l'AMF)
   - Une monnaie électronique (au sens de la DSP2)
   - Un actif financier ou un titre de capital

6. Maintenir des tests de compliance automatiques qui vérifient la 
   conformité philosophique (tests tagués @egoejo_compliance), avec un 
   minimum de [83] tests passants.

7. Garantir que la CI/CD bloque toute fusion violant la philosophie EGOEJO, 
   notamment via le workflow `.github/workflows/egoejo-compliance.yml`.

8. Protéger les settings critiques (compostage, redistribution) par 
   validation au démarrage (fail-fast), empêchant le démarrage de 
   l'application si ces settings sont désactivés en production.

Toute violation de cette raison d'être entraîne :
- Le retrait automatique du label "EGOEJO COMPLIANT"
- La notification immédiate au comité de mission
- Des sanctions statutaires pouvant aller jusqu'à la révocation des dirigeants
```

---

### 3. Article Y - Objectifs Statutaires

**Texte Recommandé** :

```markdown
Article Y - Objectifs Statutaires

Conformément à l'article L210-10 du Code de commerce, les objectifs sociaux 
de la société sont :

1. Développer et maintenir une plateforme d'engagement citoyen conforme à 
   la philosophie EGOEJO, telle que définie dans le Manifeste SAKA/EUR.

2. Garantir la conformité continue aux critères du label "EGOEJO COMPLIANT", 
   notamment :
   - Le maintien de la séparation SAKA / EUR
   - L'anti-accumulation et la circulation obligatoire
   - La non-monétisation et la non-financiarisation du SAKA

3. Documenter publiquement le statut de conformité via l'endpoint 
   `/api/public/egoejo-compliance.json`, accessible sans authentification.

4. Assurer la transparence des métriques et des scores, avec obligation 
   de métadonnées pour toute présentation de score "objectif".

5. Protéger la gouvernance contre toute dérive financière ou spéculative, 
   notamment via le comité de mission et la golden share de l'association 
   Guardian.

Ces objectifs sont incompatibles avec :
- Toute conversion SAKA ↔ EUR (directe ou indirecte)
- Tout rendement financier sur le SAKA
- Toute accumulation passive du SAKA
- Toute présentation du SAKA comme instrument financier ou monétaire
- Toute désactivation des mécanismes de compostage ou de redistribution
- Toute modification des tests de compliance sans validation du comité 
  de mission
```

---

### 4. Article Z - Comité de Mission

**Texte Recommandé** :

```markdown
Article Z - Comité de Mission

Conformément à l'article L210-10 du Code de commerce, un comité de mission 
est constitué pour surveiller l'exécution de la raison d'être.

Composition :
Le comité de mission est composé de [X] membres indépendants, dont :
- Au moins un représentant de l'association Guardian (golden share)
- Au moins un expert technique (développeur senior, minimum 5 ans d'expérience)
- Au moins un expert juridique (avocat spécialisé en droit des sociétés)
- [Optionnel] Un représentant des utilisateurs actifs

Mandat :
Les membres du comité de mission sont nommés pour une durée de [3] ans, 
renouvelable une fois. Ils sont rémunérés selon les modalités fixées par 
le conseil d'administration.

Mission :
Le comité de mission a pour mission de :

1. Vérifier que les tests de compliance passent (minimum 83/83)
2. S'assurer que le label "EGOEJO COMPLIANT" est maintenu
3. Auditer les logs de compliance (modifications directes SakaWallet, etc.)
4. Surveiller le monitoring temps réel (compostage, redistribution)
5. Recommander le retrait du label en cas de violation grave
6. Valider toute modification des tests de compliance
7. Valider toute activation de V2.0 (Investment) ou de feature flags critiques
8. Examiner les plaintes des utilisateurs concernant la conformité

Réunions :
Le comité de mission se réunit au moins [trimestriellement] et peut 
demander un audit technique à tout moment. Les réunions sont présidées par 
le représentant de l'association Guardian.

Décisions :
Les décisions sont prises à la majorité simple. En cas d'égalité, la voix 
du représentant de l'association Guardian est prépondérante.

Rapports :
Le comité de mission établit un rapport annuel sur l'exécution de la 
raison d'être, publié publiquement sur le site web de la société.
```

---

### 5. Article A - Pacte d'Associés - Golden Share

**Texte Recommandé** :

```markdown
Article A - Pacte d'Associés - Golden Share

L'association Guardian, association loi 1901 à but non lucratif, détient 
une "golden share" qui lui confère un droit de veto sur toute décision 
violant la philosophie EGOEJO.

Droit de Veto :
L'association Guardian peut exercer son droit de veto sur toute décision 
concernant :

1. L'activation de V2.0 (Investment) sans validation du comité de mission
2. La désactivation du compostage ou de la redistribution SAKA
3. L'introduction d'une conversion SAKA ↔ EUR (directe ou indirecte)
4. La modification des tests de compliance sans validation du comité 
   de mission
5. Le changement de la raison d'être sans validation du comité de mission
6. La présentation du SAKA comme instrument financier ou monétaire
7. L'introduction d'un rendement financier sur le SAKA
8. Toute décision violant les critères Core du label "EGOEJO COMPLIANT"

Caractéristiques de la Golden Share :
- Inaliénable : Ne peut être vendue ou transférée à un tiers
- Intransmissible : Ne peut être héritée (sauf à une autre association 
  à but non lucratif partageant la même mission)
- Irrévocable : Ne peut être révoquée que par dissolution de l'association 
  Guardian

Procédure d'Exercice du Veto :
1. L'association Guardian notifie par écrit son intention d'exercer le veto
2. Délai de réponse : 7 jours
3. Si le veto est exercé, la décision est bloquée immédiatement
4. Le comité de mission est saisi pour arbitrage
5. Décision finale : Conseil d'administration (majorité qualifiée)

Sanctions en Cas de Violation :
En cas de violation de la golden share, l'association Guardian peut :
1. Exercer son droit de veto (blocage immédiat)
2. Demander le retrait du label "EGOEJO COMPLIANT"
3. Saisir le comité de mission pour audit
4. Engager une procédure d'arbitrage
5. Demander la révocation des dirigeants
```

---

## ⚖️ Clause d'Arbitrage

**Texte Recommandé** :

```markdown
Article B - Arbitrage des Conflits

En cas de conflit concernant la conformité au label "EGOEJO COMPLIANT" 
ou la violation de la raison d'être, la procédure d'arbitrage suivante 
s'applique :

Étape 1 : Médiation Interne
- Conflit signalé au comité de mission
- Délai : 15 jours
- Objectif : Résolution amiable

Étape 2 : Arbitrage Technique
- Si conflit technique : Audit par un expert indépendant
- Délai : 30 jours
- Objectif : Vérification technique de la conformité
- Expert nommé par le comité de mission

Étape 3 : Arbitrage Juridique
- Si conflit juridique : Recours à un arbitre (CNUDCI)
- Délai : 60 jours
- Objectif : Décision juridique définitive
- Arbitre nommé par la Chambre de commerce et d'industrie

Étape 4 : Recours Judiciaire (Dernier recours)
- Si arbitrage insatisfaisant : Recours au tribunal compétent
- Délai : Variable
- Objectif : Décision judiciaire définitive
- Tribunal compétent : Tribunal de commerce de [VILLE]

Règles d'Arbitrage :
1. Primauté de la raison d'être : Toute décision doit respecter la raison d'être
2. Preuve technique : Les tests de compliance font foi
3. Principe de précaution : En cas de doute, le label est retiré
4. Transparence : Toutes les décisions sont publiques (sauf données sensibles)
```

---

## 📋 Checklist de Rédaction

### Statuts

- [ ] Préambule défini
- [ ] Raison d'être rédigée (Article X)
- [ ] Objectifs statutaires définis (Article Y)
- [ ] Comité de mission constitué (Article Z)
- [ ] Golden share définie (Article A)
- [ ] Clause d'arbitrage prévue (Article B)

### Pacte d'Associés

- [ ] Golden share inaliénable
- [ ] Droit de veto défini
- [ ] Procédure d'exercice du veto
- [ ] Sanctions en cas de violation

### Documentation

- [ ] Manifeste SAKA/EUR référencé
- [ ] Label EGOEJO COMPLIANT documenté
- [ ] Procédure de retrait documentée
- [ ] Matrice Label ↔ Statuts ↔ Code publiée

---

## 🔗 Références

- [Cadre Juridique du Label](CADRE_JURIDIQUE_LABEL.md)
- [Matrice Label ↔ Statuts ↔ Code](MATRICE_LABEL_STATUTS_CODE.md)
- [Label EGOEJO COMPLIANT](LABEL_EGOEJO_COMPLIANT.md)

---

**Fin des Recommandations**

*Dernière mise à jour : 2025-01-27*

