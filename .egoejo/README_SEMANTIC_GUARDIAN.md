# EGOEJO Semantic Guardian - Analyse IA

## Description

Le **EGOEJO Semantic Guardian** est un complément au `guardian.py` déterministe. Il utilise l'IA pour détecter les violations **implicites** de la constitution EGOEJO.

## Rôle

- ✅ Détecter des violations implicites (non détectées par regex)
- ✅ Signaler des risques philosophiques
- ❌ **Ne JAMAIS merger seule** (non bloquant)

## Séparation claire

### Règles dures (`guardian.py`)
- ✅ Analyse déterministe (regex)
- ✅ **Bloquant** : Exit 1 si violation critique
- ✅ Vérifie les patterns explicites

### Analyse IA (`semantic_guardian.py`)
- ✅ Analyse sémantique (IA)
- ❌ **Non bloquant** : Exit 0 toujours
- ✅ Détecte les violations implicites
- ✅ Sert à la gouvernance humaine

## Configuration

### Variables d'environnement

Le Semantic Guardian nécessite une clé API IA :

- `OPENAI_API_KEY` : Pour utiliser OpenAI (GPT-4o-mini)
- `ANTHROPIC_API_KEY` : Pour utiliser Anthropic (Claude Haiku)

**Note** : Si aucune clé n'est configurée, l'analyse IA sera désactivée (non bloquant).

### Configuration GitHub Actions

Ajoutez les secrets dans GitHub :
- Settings → Secrets and variables → Actions
- Ajoutez `OPENAI_API_KEY` ou `ANTHROPIC_API_KEY`

## Usage

### Exécution locale

```bash
# Avec numéro de PR
python .egoejo/semantic_guardian.py 123

# Avec diff local
python .egoejo/semantic_guardian.py --base-branch origin/main

# Sauvegarder le commentaire
python .egoejo/semantic_guardian.py 123 --output semantic-analysis.md
```

### Exécution en CI

Le Semantic Guardian est automatiquement exécuté via GitHub Actions (`.github/workflows/egoejo-guardian.yml`).

## Questions analysées

L'IA analyse trois questions clés :

1. **Cette PR transforme-t-elle l'engagement en rendement ?**
   - Ex: Récompense SAKA basée sur investissement EUR
   - Ex: Conversion implicite engagement → profit

2. **Introduit-elle une logique d'accumulation ?**
   - Ex: Désactivation du compostage
   - Ex: Stockage permanent sans redistribution

3. **La banque instrumentale contraint-elle le SAKA ?**
   - Ex: Condition SAKA basée sur `ENABLE_INVESTMENT_FEATURES`
   - Ex: Dépendance SAKA → EUR

## Format de réponse

L'IA retourne :

```json
{
  "label": "🟢 COMPATIBLE EGOEJO" | "🟡 COMPATIBLE SOUS CONDITIONS" | "🔴 NON COMPATIBLE EGOEJO",
  "justification": "Explication en 3-6 lignes maximum, factuelle",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "risks": ["Liste des risques détectés (optionnel)"]
}
```

## Commentaire PR

Le résultat de l'analyse IA est ajouté comme **commentaire PR** (non bloquant) avec :

- Label suggéré
- Justification textuelle (≤ 6 lignes)
- Niveau de confiance
- Liste des risques détectés
- **Disclaimer** : "Analyse IA non souveraine"

## Disclaimer

> ⚠️ **DISCLAIMER** : Cette analyse IA est **non souveraine** et **non bloquante**.
> Elle complète les règles déterministes (`guardian.py`) et sert à la gouvernance humaine.

## Exemples

### Exemple 1 : Violation implicite détectée

**Code** :
```python
# backend/core/services/saka.py
def calculate_user_reward(user, investment_amount):
    # Récompense SAKA proportionnelle à l'investissement EUR
    saka_reward = investment_amount * 0.1
    return harvest_saka(user, SakaReason.INVEST_BONUS, amount=saka_reward)
```

**Analyse IA** :
```
🔴 NON COMPATIBLE EGOEJO

Justification :
Cette PR transforme l'engagement en rendement en liant directement
la récompense SAKA à l'investissement EUR. Cela viole le principe
de séparation stricte SAKA/EUR et introduit une logique de rendement.

Confiance : HIGH
```

### Exemple 2 : Risque philosophique détecté

**Code** :
```python
# backend/core/services/saka.py
def harvest_saka(user, reason, amount):
    if settings.ENABLE_INVESTMENT_FEATURES:
        # Bonus pour utilisateurs premium
        amount *= 1.5
    # ... reste du code
```

**Analyse IA** :
```
🟡 COMPATIBLE SOUS CONDITIONS

Justification :
Cette PR introduit une condition SAKA basée sur ENABLE_INVESTMENT_FEATURES,
ce qui crée une dépendance implicite SAKA → EUR. Bien que non bloquant,
cela va à l'encontre du principe SAKA > EUR.

Confiance : MEDIUM
```

## Limitations

- L'analyse IA peut produire des faux positifs
- Le niveau de confiance peut être LOW pour des changements complexes
- L'IA ne remplace pas l'analyse humaine
- Les coûts API peuvent varier selon le volume de PRs

## Coûts

- **OpenAI GPT-4o-mini** : ~$0.001 par analyse (diff moyen)
- **Anthropic Claude Haiku** : ~$0.0005 par analyse (diff moyen)

## Références

- **Guardian déterministe** : `.egoejo/guardian.py`
- **Workflow CI/CD** : `.github/workflows/egoejo-guardian.yml`
- **Constitution EGOEJO** : `docs/compliance/EGOEJO_CONSTITUTION_EXECUTABLE.md`

