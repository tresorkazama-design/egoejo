# Matrice de Conformité : Contenu → Critères EGOEJO Compliant

## Vue d'ensemble

Cette matrice définit la correspondance entre les contenus publiés et les critères de conformité du label EGOEJO Compliant.

## Matrice de Conformité

| Critère | Type | Bloquant | Description | Test |
|---------|------|----------|-------------|------|
| `status_published_only` | Critique | ✅ OUI | Seuls les contenus avec `status='published'` sont accessibles publiquement | `test_contenu_public_est_published_uniquement` |
| `status_workflow_valid` | Critique | ✅ OUI | Le workflow de statut respecte les transitions autorisées | `test_content_status_workflow` |
| `has_source` | Avertissement | ⚠️ NON | Le contenu a une source identifiable (external_url, file, source, source_url) | `test_content_has_source_and_license` |
| `has_license` | Avertissement | ⚠️ NON | Le contenu a une licence explicite (license, license_type) | `test_content_has_source_and_license` |
| `no_financial_language` | Critique | ✅ OUI | Aucun langage financier interdit (ROI, profit, rentabilité, etc.) | `test_content_no_financial_language` |
| `no_monetary_symbols` | Critique | ✅ OUI | Aucun symbole monétaire (€, $, EUR, USD, etc.) | `test_content_no_financial_language` |
| `auditlog_exists` | Avertissement | ⚠️ NON | Un audit log existe pour le contenu publié | `test_auditlog_exists` |
| `published_by_tracked` | Avertissement | ⚠️ NON | Le champ `published_by` est tracké pour les contenus publiés | `test_content_status_workflow` |
| `no_saka_eur_conversion` | Critique | ✅ OUI | Aucune mention de conversion SAKA/EUR | `test_content_no_financial_language` |
| `no_financial_promises` | Critique | ✅ OUI | Aucune promesse financière (garantie de retour, etc.) | `test_content_no_financial_language` |

## Score de Conformité

Le score de conformité est calculé comme suit :

- **Score = 0.0** si au moins un critère critique échoue
- **Score = 1.0** si tous les critères critiques passent et tous les avertissements passent
- **Score = 0.8 - 0.99** si tous les critères critiques passent mais certains avertissements échouent

### Formule

```
Si critical_failures > 0:
    score = 0.0
    is_compliant = False
Sinon:
    critical_score = critical_passed / total_critical  # 100% du score
    warning_score = warning_passed / total_warning * 0.2  # Bonus de 20% max
    score = min(1.0, critical_score + warning_score)
    is_compliant = True
```

## Connexion au Label EGOEJO Compliant

Les critères de compliance éditoriale sont intégrés dans le label EGOEJO Compliant :

- **Core** : Tous les critères critiques doivent passer
- **Extended** : Tous les critères critiques + avertissements doivent passer

### Critères Core (Bloquants)

1. `status_published_only`
2. `status_workflow_valid`
3. `no_financial_language`
4. `no_monetary_symbols`
5. `no_saka_eur_conversion`
6. `no_financial_promises`

### Critères Extended (Recommandés)

1. `has_source`
2. `has_license`
3. `auditlog_exists`
4. `published_by_tracked`

## Publication Bloquante

**AUCUN CONTOURNEMENT POSSIBLE** : La méthode `publish()` dans `EducationalContentViewSet` vérifie systématiquement la compliance avant publication.

Si un contenu n'est pas conforme (échecs critiques), la publication est **BLOQUÉE** avec une erreur 400 Bad Request.

## Endpoints

### API Interne (Authentifié)

- `GET /api/contents/{content_id}/compliance/` : Score de conformité détaillé pour un contenu

### API Publique (Sans authentification)

- `GET /api/public/content-compliance.json` : Rapport agrégé de conformité éditoriale
- `GET /api/public/egoejo-compliance.json` : Label EGOEJO Compliant (inclut compliance éditoriale)

## Tests Bloquants en CI

Tous les tests de compliance éditoriale sont exécutés dans `.github/workflows/egoejo-compliance.yml` et sont **BLOQUANTS**.

Si un test échoue, le workflow échoue et le merge est bloqué.

