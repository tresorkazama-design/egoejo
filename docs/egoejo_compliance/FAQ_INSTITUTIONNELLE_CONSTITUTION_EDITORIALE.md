# FAQ Institutionnelle
## Constitution Éditoriale Institutionnelle

**Version** : 1.0  
**Date** : 2025-01-27

---

## Questions Générales

### Q1 : Qu'est-ce que la Constitution Éditoriale ?

**R** : La Constitution Éditoriale est un document officiel définissant les règles de publication de contenus éducatifs et informationnels sur la plateforme. Elle garantit la qualité, la traçabilité, l'intégrité et la conformité réglementaire de tous les contenus publics.

### Q2 : Pourquoi une Constitution Éditoriale ?

**R** : La Constitution Éditoriale garantit :
- **Qualité** : Tous les contenus publics respectent des critères de conformité stricts
- **Traçabilité** : Tous les contenus sont traçables et vérifiables
- **Conformité** : Conformité aux principes UNESCO, gouvernance des communs, réglementation
- **Protection** : Protection contre les contenus non conformes ou frauduleux

### Q3 : À qui s'applique la Constitution Éditoriale ?

**R** : La Constitution Éditoriale s'applique à **tous les contenus publics** publiés sur la plateforme, qu'ils soient créés par des utilisateurs, des éditeurs, ou des administrateurs.

---

## Principes Fondamentaux

### Q4 : Pourquoi interdire le langage financier ?

**R** : L'interdiction du langage financier garantit la **neutralité et l'objectivité** des contenus éducatifs. Elle évite toute confusion entre contenu éducatif et contenu promotionnel ou commercial, conformément aux principes UNESCO.

### Q5 : Quels termes financiers sont interdits ?

**R** : Les termes suivants sont interdits (liste non exhaustive) :
- Retour sur investissement, ROI, profit, rentabilité
- Gain financier, dividende, rendement
- Garantie de retour, promesse financière

Voir l'Annexe A de la Constitution pour la liste complète.

### Q6 : Les symboles monétaires sont-ils toujours interdits ?

**R** : Les symboles monétaires (€, $, EUR, USD) sont interdits sauf dans un **contexte strictement informatif et non promotionnel**. Par exemple, "Le coût de production est de 10€" dans un article informatif est autorisé, mais "Investissez 100€ pour un retour garanti" est interdit.

### Q7 : Pourquoi exiger une source identifiable ?

**R** : L'exigence d'une source identifiable garantit la **vérifiabilité et la crédibilité** des contenus, conformément aux principes de gouvernance des communs numériques. Elle permet aux lecteurs de vérifier les informations et de remonter à la source originale.

### Q8 : Pourquoi exiger une licence explicite ?

**R** : L'exigence d'une licence explicite garantit le **respect des droits de propriété intellectuelle** et la **réutilisabilité** des contenus. Elle permet aux utilisateurs de savoir comment ils peuvent utiliser, reproduire ou modifier le contenu.

---

## Workflow de Publication

### Q9 : Pourquoi un workflow de publication strict ?

**R** : Le workflow de publication garantit que tous les contenus publics sont **validés** avant publication. Il évite la publication de contenus non conformes, incomplets ou de mauvaise qualité.

### Q10 : Quels sont les états autorisés ?

**R** : Les états autorisés sont :
1. **Brouillon** : Contenu en cours de rédaction, non accessible publiquement
2. **En attente** : Contenu soumis pour validation, non accessible publiquement
3. **Publié** : Contenu validé et accessible publiquement
4. **Rejeté** : Contenu non conforme, non accessible publiquement
5. **Archivé** : Contenu retiré de la publication, non accessible publiquement

### Q11 : Quelles sont les transitions autorisées ?

**R** : Les transitions autorisées sont :
- Brouillon → En attente (soumission)
- En attente → Publié (validation par administrateur)
- En attente → Rejeté (rejet par éditeur/administrateur)
- Publié → Archivé (retrait par administrateur)
- Rejeté → Brouillon (révision)

### Q12 : Pourquoi interdire la publication directe ?

**R** : L'interdiction de la publication directe garantit que **tous les contenus publics sont validés** avant publication. Elle évite la publication de contenus non conformes, incomplets ou de mauvaise qualité.

---

## Critères de Conformité

### Q13 : Quels sont les critères obligatoires ?

**R** : Les critères obligatoires (bloquants) sont :
1. Statut de publication valide (workflow respecté)
2. Absence de langage financier
3. Absence de symboles monétaires (sauf contexte informatif strict)
4. Absence de promesses financières
5. Workflow respecté

**Un contenu ne peut être publié que si tous ces critères sont respectés.**

### Q14 : Quels sont les critères recommandés ?

**R** : Les critères recommandés (avertissements) sont :
1. Source identifiable
2. Licence explicite
3. Audit log
4. Traçabilité de publication

Ces critères sont recommandés mais non bloquants.

### Q15 : Que se passe-t-il si un contenu ne respecte pas les critères obligatoires ?

**R** : Si un contenu ne respecte pas les critères obligatoires, il est **automatiquement bloqué** et ne peut pas être publié, même par un administrateur. Un message d'erreur explicite indique les violations détectées.

### Q16 : Un administrateur peut-il contourner les critères obligatoires ?

**R** : **Non, aucun contournement n'est possible.** Les mécanismes techniques garantissent qu'aucun contenu non conforme ne peut être publié, même par un administrateur.

---

## Processus de Validation

### Q17 : Comment fonctionne la validation automatique ?

**R** : Lors de la soumission d'un contenu :
1. Vérification automatique des critères obligatoires
2. Blocage automatique si non conforme
3. Message d'erreur explicite avec détails des violations

### Q18 : Comment fonctionne la validation manuelle ?

**R** : Après vérification automatique :
1. Vérification manuelle par l'éditeur ou l'administrateur
2. Publication si conforme
3. Rejet si non conforme (avec raison explicite)

### Q19 : Qui peut valider un contenu ?

**R** : La validation peut être effectuée par :
- **Éditeurs** : Peuvent soumettre, rejeter, ou demander des modifications
- **Administrateurs** : Peuvent publier, archiver, ou rejeter

---

## Audit et Traçabilité

### Q20 : Quelles actions sont enregistrées dans les logs d'audit ?

**R** : Toutes les actions sur les contenus sont enregistrées :
- Création du contenu
- Soumission pour validation
- Publication
- Rejet
- Archivage
- Modifications

### Q21 : Quelles informations sont enregistrées ?

**R** : Les informations suivantes sont enregistrées :
- Utilisateur ayant effectué l'action
- Date et heure de l'action
- Type d'action
- Statut avant et après l'action

### Q22 : Comment accéder aux rapports de conformité ?

**R** : Les rapports de conformité sont accessibles via :
- **API publique** : Endpoint `/api/public/content-compliance.json`
- **Interface utilisateur** : Section "Conformité" dans l'interface d'administration
- **Rapport agrégé** : Rapport global de conformité de tous les contenus publiés

---

## Non-Conformité et Sanctions

### Q23 : Comment la non-conformité est-elle détectée ?

**R** : La non-conformité est détectée :
- **Automatiquement** : Par des tests automatisés lors de la soumission
- **Manuellement** : Par les éditeurs et administrateurs lors de la validation
- **A posteriori** : Par des audits réguliers des contenus publiés

### Q24 : Quelles sont les sanctions en cas de non-conformité ?

**R** : En cas de non-conformité :
1. **Blocage de publication** : Le contenu ne peut pas être publié
2. **Rejet** : Le contenu est rejeté avec une raison explicite
3. **Retrait** : Si détectée après publication, le contenu est retiré et archivé
4. **Correction** : L'auteur peut corriger le contenu et le resoumettre

### Q25 : Y a-t-il un recours en cas de rejet ?

**R** : Oui, tout auteur peut :
- Demander une révision de la décision de rejet
- Corriger le contenu et le resoumettre
- Contester la décision auprès de l'administrateur

---

## Transparence et Accessibilité

### Q26 : Les critères de conformité sont-ils publics ?

**R** : Oui, les critères de conformité, les règles éditoriales et les processus de validation sont :
- **Publics** : Accessibles à tous les utilisateurs
- **Documentés** : Documentés dans la documentation officielle
- **Vérifiables** : Vérifiables via des endpoints API publics

### Q27 : Comment vérifier la conformité d'un contenu ?

**R** : La conformité d'un contenu peut être vérifiée via :
- **API publique** : Endpoint `/api/public/content-compliance.json`
- **Badge de conformité** : Les contenus conformes affichent un badge de conformité
- **Rapport détaillé** : Score de conformité détaillé par contenu

### Q28 : Qu'est-ce que le badge de conformité ?

**R** : Le badge de conformité atteste :
- Le respect des critères obligatoires
- La traçabilité et la source
- La licence et les droits d'usage

---

## Opposabilité Juridique

### Q29 : La Constitution Éditoriale est-elle opposable juridiquement ?

**R** : Oui, la Constitution Éditoriale est **opposable juridiquement**. Toute violation des règles définies peut entraîner :
- Le retrait du contenu
- La suspension de l'auteur
- Des poursuites judiciaires si nécessaire

### Q30 : Comment interpréter une règle en cas de doute ?

**R** : En cas de doute sur l'interprétation d'une règle :
- La règle doit être interprétée de manière **restrictive**
- Le principe de **précaution** s'applique
- Le comité de gouvernance peut être consulté

---

## Conformité Réglementaire

### Q31 : Comment la Constitution s'aligne-t-elle avec les principes UNESCO ?

**R** : La Constitution s'aligne avec les principes UNESCO relatifs à :
- **L'accès à l'information** : Contenus accessibles, traçables, vérifiables
- **La liberté d'expression** : Respect de la diversité des opinions, sans censure arbitraire
- **L'éducation** : Promotion de l'apprentissage, de la connaissance, de la culture

### Q32 : Comment la Constitution s'aligne-t-elle avec la gouvernance des communs ?

**R** : La Constitution s'aligne avec les principes de gouvernance des communs numériques :
- **Transparence** : Processus de publication transparent et auditable
- **Participation** : Mécanismes de contribution et de validation ouverts
- **Redistribution** : Partage équitable des connaissances et des ressources
- **Protection** : Mécanismes de protection contre l'appropriation privée

### Q33 : Comment la Constitution s'aligne-t-elle avec la réglementation ?

**R** : La Constitution s'aligne avec :
- **RGPD/GDPR** : Protection des données personnelles
- **Droit d'auteur** : Respect des droits de propriété intellectuelle
- **Loi sur la presse** : Responsabilité éditoriale, droit de réponse
- **Loi sur la confiance numérique** : Authenticité, intégrité, traçabilité

---

## Évolutivité et Révision

### Q34 : La Constitution peut-elle être modifiée ?

**R** : Oui, la Constitution est révisée périodiquement pour :
- S'adapter aux évolutions réglementaires
- Intégrer les retours d'expérience
- Améliorer les processus de validation

### Q35 : Comment la Constitution est-elle versionnée ?

**R** : La Constitution est versionnée :
- **Version majeure** : Changements incompatibles avec les versions précédentes
- **Version mineure** : Ajouts de critères ou améliorations
- **Version patch** : Corrections et clarifications

### Q36 : Les modifications sont-elles rétrocompatibles ?

**R** : Les modifications sont généralement **rétrocompatibles** avec les contenus existants, sauf cas exceptionnels documentés et justifiés.

---

**Document officiel - Opposable juridiquement**  
**Version 1.0 - 2025-01-27**  
**Plateforme EGOEJO**

