# Clause d'Inaliénabilité des Actifs
## Statuts Association EGOEJO - Clause X

**Document** : Clause juridique d'inaliénabilité des actifs de la mission  
**Date** : 2025-01-05  
**Version** : 1.0.0  
**Statut** : ⚠️ **À VALIDER PAR AVOCAT AVANT DÉPÔT**

---

## 📋 CLAUSE X - INALIÉNABILITÉ DES ACTIFS DE LA MISSION

### Article X.1 - Principe d'Inaliénabilité

**X.1.1** Les actifs de la mission de la Société EGOEJO sont **inaliénables** et ne peuvent être cédés, transférés, ou détournés de leur objet social sans validation préalable.

**X.1.2** Sont considérés comme **actifs de la mission** :

- Les fonds collectés via la plateforme pour le financement de projets sociaux
- Les actifs numériques (code source, bases de données) nécessaires au fonctionnement de la mission
- Les droits de propriété intellectuelle liés à la mission
- Les contrats d'escrow verrouillés (status = 'LOCKED')

**X.1.3** Les actifs de la mission sont **séparés** des actifs propres de la Société et ne peuvent être utilisés à d'autres fins que celles définies dans la mission.

---

### Article X.2 - Mécanisme de Validation

**X.2.1** Toute libération d'actifs de la mission requiert :

1. **Validation par le Comité de Mission** : Vote à la majorité qualifiée (2/3)
2. **Validation par l'Action G (Guardian)** : Droit de veto
3. **Validation par l'Assemblée Générale** : Vote à la majorité absolue

**X.2.2** Les actifs verrouillés dans un contrat d'escrow (status = 'LOCKED') ne peuvent être libérés que :

- Sur validation conforme à l'article X.2.1
- En cas de réalisation de l'objet du contrat (projet financé, objectif atteint)
- En cas de remboursement légitime aux contributeurs

**X.2.3** Aucune extraction de fonds vers des comptes externes n'est autorisée sans validation préalable conforme à l'article X.2.1.

---

### Article X.3 - Protection contre la Capture

**X.3.1** La Société s'interdit de :

- Convertir les actifs de la mission en actifs privés
- Utiliser les actifs de la mission pour des opérations non liées à la mission
- Détourner les fonds collectés vers des projets non conformes à la mission

**X.3.2** Toute tentative de capture ou de détournement des actifs de la mission est **nulle de plein droit** et peut donner lieu à des poursuites judiciaires.

**X.3.3** Les administrateurs et dirigeants de la Société sont **personnellement responsables** de la protection des actifs de la mission et peuvent être tenus responsables en cas de violation de la présente clause.

---

### Article X.4 - Vérification et Audit

**X.4.1** Un audit annuel des actifs de la mission est réalisé par un organisme indépendant.

**X.4.2** Les résultats de l'audit sont **publics** et accessibles via l'endpoint `/api/public/egoejo-constitution.json`.

**X.4.3** Toute anomalie détectée lors de l'audit doit être corrigée dans un délai de 30 jours, sous peine de sanctions prévues à l'article X.5.

---

### Article X.5 - Sanctions

**X.5.1** En cas de violation de la présente clause :

- **Niveau 1** : Avertissement et correction immédiate
- **Niveau 2** : Suspension des opérations financières
- **Niveau 3** : Dissolution de la Société et transfert des actifs à une structure conforme

**X.5.2** Les sanctions sont prononcées par le Comité de Mission après consultation de l'Action G (Guardian).

---

### Article X.6 - Irrévocabilité

**X.6.1** La présente clause est **irrévocable** et ne peut être modifiée que par :

- Un vote unanime de tous les associés
- L'approbation explicite de l'Action G (Guardian)
- L'approbation d'un organisme de contrôle indépendant

**X.6.2** Toute modification de la présente clause doit être **publiquement documentée** et accessible via l'endpoint `/api/public/egoejo-constitution.json`.

---

## 📚 RÉFÉRENCES

- **Constitution Juridique** : `docs/legal/CONSTITUTION_JURIDIQUE_FINALE_EGOEJO.md`
- **Constitution Technique** : `docs/constitution/CONSTITUTION_TRADUCTION_PHILOSOPHIQUE_TECHNIQUE.md`
- **Architecture Escrow** : `backend/finance/models.py` (EscrowContract)

---

**Cette clause est ENFORCÉE par des vérifications automatiques dans le code.  
Aucune exception n'est autorisée.**

---

*Dernière mise à jour : 2025-01-05*  
*⚠️ À VALIDER PAR AVOCAT AVANT DÉPÔT*

