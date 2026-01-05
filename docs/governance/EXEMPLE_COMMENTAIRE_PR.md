# 💬 Exemples de Commentaires PR Bot

**Documentation** : Exemples de commentaires générés par le bot EGOEJO PR Bot

---

## 🟢 Exemple 1 : PR Compatible

```markdown
## 🤖 EGOEJO PR Bot - Analyse de Conformité

### 📊 Résultat

**🟢 COMPATIBLE EGOEJO**

✅ CONFORME EGOEJO

Aucun risque philosophique ou technique détecté. 
Cette PR respecte les principes EGOEJO.

### 🔍 Détails

### 💡 Recommandation

**ACCEPT**

✅ **MERGE AUTORISÉ** - Cette PR peut être mergée.

---

*Ce commentaire est généré automatiquement par le bot de gouvernance EGOEJO.*
*Pour plus d'informations, voir [docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)*
```

---

## 🟡 Exemple 2 : PR Compatible Sous Conditions

```markdown
## 🤖 EGOEJO PR Bot - Analyse de Conformité

### 📊 Résultat

**🟡 COMPATIBLE SOUS CONDITIONS**

⚠️ RISQUES TECHNIQUES DÉTECTÉS

2 risque(s) technique(s) identifié(s). 
Review technique recommandée avant merge.

### 🔍 Détails

#### 🔧 Risques Techniques (2)

1. **Pattern 'wallet_mod' détecté: wallet.balance = new_value**
   - 📁 `backend/core/services/saka.py` (ligne 245)

2. **Pattern 'saka_service_modification' détecté: def harvest_saka**
   - 📁 `backend/core/services/saka.py` (ligne 120)

### 💡 Recommandation

**REFACTOR**

✅ **MERGE AUTORISÉ** - Cette PR peut être mergée.

---

*Ce commentaire est généré automatiquement par le bot de gouvernance EGOEJO.*
*Pour plus d'informations, voir [docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)*
```

---

## 🔴 Exemple 3 : PR Non Compatible

```markdown
## 🤖 EGOEJO PR Bot - Analyse de Conformité

### 📊 Résultat

**🔴 NON COMPATIBLE EGOEJO**

❌ VIOLATION PHILOSOPHIQUE DÉTECTÉE

3 risque(s) philosophique(s) identifié(s). 
Cette PR viole les principes fondamentaux d'EGOEJO.

### 🔍 Détails

#### ⚠️ Risques Philosophiques (3)

1. **Pattern 'conversion_saka_eur' détecté: def convert_saka_to_eur(amount)**
   - 📁 `backend/core/services/saka_conversion.py` (ligne 15)

2. **Pattern 'compost_disabled' détecté: SAKA_COMPOST_ENABLED = False**
   - 📁 `backend/config/settings.py` (ligne 499)

3. **Pattern 'monetary_display' détecté: formatSakaAmount(saka) + '€'**
   - 📁 `frontend/frontend/src/components/SakaBalance.jsx` (ligne 42)

### 💡 Recommandation

**REFUSE**

🚫 **MERGE BLOQUÉ** - Cette PR ne peut pas être mergée sans correction.

---

*Ce commentaire est généré automatiquement par le bot de gouvernance EGOEJO.*
*Pour plus d'informations, voir [docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)*
```

---

## 🔴 Exemple 4 : PR Non Compatible (Activation V2.0)

```markdown
## 🤖 EGOEJO PR Bot - Analyse de Conformité

### 📊 Résultat

**🔴 NON COMPATIBLE EGOEJO**

❌ VIOLATION PHILOSOPHIQUE DÉTECTÉE

1 risque(s) philosophique(s) identifié(s). 
Cette PR viole les principes fondamentaux d'EGOEJO.

### 🔍 Détails

#### ⚠️ Risques Philosophiques (1)

1. **Pattern 'investment_activation' détecté: ENABLE_INVESTMENT_FEATURES = True**
   - 📁 `backend/config/settings.py` (ligne 470)

### 💡 Recommandation

**REFUSE**

🚫 **MERGE BLOQUÉ** - Cette PR ne peut pas être mergée sans correction.

---

*Ce commentaire est généré automatiquement par le bot de gouvernance EGOEJO.*
*Pour plus d'informations, voir [docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)*
```

---

## 🔴 Exemple 5 : PR Non Compatible (Suppression Tests)

```markdown
## 🤖 EGOEJO PR Bot - Analyse de Conformité

### 📊 Résultat

**🔴 NON COMPATIBLE EGOEJO**

❌ VIOLATION PHILOSOPHIQUE DÉTECTÉE

1 risque(s) philosophique(s) identifié(s). 
Cette PR viole les principes fondamentaux d'EGOEJO.

### 🔍 Détails

#### ⚠️ Risques Philosophiques (1)

1. **Test de compliance supprimé ou désactivé**
   - Fichier non identifié

### 💡 Recommandation

**REFUSE**

🚫 **MERGE BLOQUÉ** - Cette PR ne peut pas être mergée sans correction.

---

*Ce commentaire est généré automatiquement par le bot de gouvernance EGOEJO.*
*Pour plus d'informations, voir [docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)*
```

---

## 📝 Notes

- **Max 10 risques** : Seuls les 10 premiers risques sont affichés pour éviter les commentaires trop longs
- **Fichier et ligne** : Le bot tente d'identifier le fichier et la ligne, mais peut échouer si le diff est complexe
- **Mise à jour** : Le bot met à jour le commentaire existant si la PR est modifiée

---

**Fin des Exemples**

