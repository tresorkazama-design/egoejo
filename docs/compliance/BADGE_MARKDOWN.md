# Badge Markdown EGOEJO Compliant

## Badge GitHub Actions

```markdown
[![EGOEJO Compliant](https://github.com/YOUR_OWNER/YOUR_REPO/actions/workflows/egoejo-guardian.yml/badge.svg)](https://github.com/YOUR_OWNER/YOUR_REPO/actions/workflows/egoejo-guardian.yml)
```

## Remplacement des placeholders

Remplacez :
- `YOUR_OWNER` : Nom d'utilisateur ou organisation GitHub
- `YOUR_REPO` : Nom du dépôt GitHub

## Exemple

Si votre dépôt est `https://github.com/egoejo/egoejo`, le badge sera :

```markdown
[![EGOEJO Compliant](https://github.com/egoejo/egoejo/actions/workflows/egoejo-guardian.yml/badge.svg)](https://github.com/egoejo/egoejo/actions/workflows/egoejo-guardian.yml)
```

## Phrase obligatoire

Ajoutez toujours cette phrase après le badge :

```markdown
> **Ce badge atteste du respect des règles EGOEJO. Il n'atteste ni d'un rendement financier, ni d'une performance économique.**
```

## Intégration dans README.md

```markdown
# EGOEJO

[![EGOEJO Compliant](https://github.com/YOUR_OWNER/YOUR_REPO/actions/workflows/egoejo-guardian.yml/badge.svg)](https://github.com/YOUR_OWNER/YOUR_REPO/actions/workflows/egoejo-guardian.yml)

> **Ce badge atteste du respect des règles EGOEJO. Il n'atteste ni d'un rendement financier, ni d'une performance économique.**

[Documentation du badge](docs/compliance/EGOEJO_COMPLIANT.md)
```

## Statut du badge

- **Vert** : Tous les tests de conformité passent
- **Rouge** : Au moins un test de conformité échoue

Le badge est mis à jour automatiquement à chaque exécution du workflow GitHub Actions.

