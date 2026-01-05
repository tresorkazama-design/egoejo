#!/usr/bin/env python3
"""
EGOEJO PR Bot - Comité de Mission Automatisé + Gardien Éditorial

Analyse les Pull Requests selon les règles de gouvernance EGOEJO
et attribue un label de conformité BLOQUANT ou NON.

PRINCIPE : Le bot agit comme un Comité de Mission automatisé et un Gardien Éditorial.

FONCTIONNALITÉS :
- Vérification de la séparation SAKA/EUR
- Vérification du cycle SAKA (circulation, compostage)
- Vérification de la gouvernance (pouvoir limité, collectif protégé)
- Vérification de la transparence (métriques honnêtes)
- Vérification de la compliance éditoriale (vocabulaire financier, promesses, workflow)
"""

import os
import sys
import json
import re
import subprocess
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import requests
except ImportError:
    requests = None
    print("⚠️ Module 'requests' non installé. Les fonctionnalités GitHub API seront désactivées.", file=sys.stderr)


class ComplianceLevel(Enum):
    """Niveaux de conformité EGOEJO"""
    COMPATIBLE = "🟢 COMPATIBLE EGOEJO"
    COMPATIBLE_CONDITIONS = "🟡 COMPATIBLE SOUS CONDITIONS"
    NON_COMPATIBLE = "🔴 NON COMPATIBLE EGOEJO"


@dataclass
class Risk:
    """Risque identifié"""
    level: str  # "philosophique" ou "technique"
    description: str
    file: Optional[str] = None
    line: Optional[int] = None


@dataclass
class PRAnalysis:
    """Analyse complète d'une PR"""
    compliance_level: ComplianceLevel
    justification: str
    philosophical_risks: List[Risk]
    technical_risks: List[Risk]
    recommendation: str  # "accept", "refactor", "refuse"
    blocking: bool


class EGOEJOPRBot:
    """
    Bot de gouvernance EGOEJO pour analyse des Pull Requests.
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.base_ref = os.environ.get("GITHUB_BASE_REF", "main")
        self.head_ref = os.environ.get("GITHUB_HEAD_REF", "")
        self.pr_number = os.environ.get("GITHUB_PR_NUMBER", "")
        
        # GitHub API configuration
        self.github_token = os.environ.get("GITHUB_TOKEN", "")
        self.github_repo = os.environ.get("GITHUB_REPOSITORY", "")
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}"
        
        # Patterns interdits (violations philosophiques)
        self.forbidden_patterns = {
            "conversion_saka_eur": [
                r"convert.*saka.*eur",
                r"convert.*eur.*saka",
                r"saka.*\*\s*exchange_rate",
                r"exchange_rate.*\*\s*saka",
                r"def\s+convert.*saka",
                r"def\s+convert.*eur",
            ],
            "monetary_display": [
                r"saka.*€",
                r"saka.*\$",
                r"saka.*USD",
                r"saka.*EUR",
                r"saka.*GBP",
                r"formatSakaAmount.*€",
            ],
            "direct_wallet_modification": [
                r"wallet\.balance\s*=",
                r"SakaWallet\.objects\.update\(.*balance",
                r"\.save\(\)\s*#.*admin",
            ],
            "compost_disabled": [
                r"SAKA_COMPOST_ENABLED\s*=\s*False",
                r"SAKA_COMPOST_RATE\s*=\s*0",
                r"SAKA_COMPOST_INACTIVITY_DAYS\s*>\s*365",
            ],
            "accumulation": [
                r"SAKA_COMPOST_ENABLED\s*=\s*False",
                r"#.*disable.*compost",
                r"#.*remove.*compost",
            ],
            "investment_activation": [
                r"ENABLE_INVESTMENT_FEATURES\s*=\s*True",
                r"enable.*investment",
                r"activate.*v2\.0",
            ],
        }
        
        # Patterns suspects (nécessitent review)
        self.suspicious_patterns = {
            "saka_service_modification": [
                r"def\s+(harvest_saka|spend_saka|run_saka_compost)",
            ],
            "settings_modification": [
                r"SAKA_.*=\s*",
                r"ENABLE_SAKA\s*=",
            ],
            "test_removal": [
                r"^-.*test.*compliance",
                r"^-.*@egoejo_compliance",
            ],
        }
        
        # Patterns interdits pour la gouvernance éditoriale
        self.editorial_forbidden_patterns = {
            "financial_language": [
                r'\bretour\s+sur\s+investissement\b',
                r'\bROI\b',
                r'\bprofit\b',
                r'\bprofitabilit[ée]\b',
                r'\brentabilit[ée]\b',
                r'\bgain\s+financier\b',
                r'\bplus-value\b',
                r'\bint[ée]r[êe]t\s+financier\b',
                r'\bdividende\b',
                r'\br[ée]mun[ée]ration\b',
                r'\bretour\s+garanti\b',
                r'\bgarantie\s+de\s+retour\b',
                r'\btaux\s+de\s+retour\b',
                r'\brendement\b',
                r'\bperformance\s+financi[èe]re\b',
                r'\bvalorisation\b',
                r'\bappr[ée]ciation\s+financi[èe]re\b',
            ],
            "monetary_symbols": [
                r'€',
                r'\$',
                r'\bEUR\b',
                r'\bUSD\b',
                r'\bGBP\b',
            ],
            "workflow_bypass": [
                r'status\s*=\s*["\']published["\']',  # Direct status assignment
                r'\.status\s*=\s*["\']published["\']',  # Direct status assignment
                r'EducationalContent\.objects\.create\(.*status\s*=\s*["\']published["\']',  # Direct creation with published
                r'EducationalContent\.objects\.update\(.*status\s*=\s*["\']published["\']',  # Direct update to published
                r'#.*bypass.*workflow',  # Explicit bypass comment
                r'#.*skip.*workflow',  # Explicit skip comment
            ],
            "implicit_promises": [
                r'\bgarantie\b',
                r'\bassur[ée]\b',
                r'\bcertain\b.*\bretour\b',
                r'\bpromis\b',
                r'\bgaranti\b.*\bprofit\b',
            ],
        }
        
        # Patterns suspects pour la gouvernance éditoriale
        self.editorial_suspicious_patterns = {
            "missing_source": [
                r'EducationalContent\.objects\.create\([^)]*status\s*=\s*["\']published["\'][^)]*(?!external_url|file|source)',
            ],
            "missing_license": [
                r'EducationalContent\.objects\.create\([^)]*status\s*=\s*["\']published["\'][^)]*(?!license)',
            ],
        }
        
        # Fichiers à scanner pour la gouvernance éditoriale
        self.editorial_file_patterns = [
            r'.*content.*\.py$',  # Fichiers de contenu Python
            r'.*cms.*\.py$',  # Fichiers CMS
            r'.*seed.*\.py$',  # Fichiers de seed
            r'.*fixture.*\.json$',  # Fixtures JSON
            r'.*fixture.*\.yaml$',  # Fixtures YAML
            r'.*management/commands/.*\.py$',  # Commandes Django
            r'.*migrations/.*\.py$',  # Migrations (peuvent contenir du seed)
        ]
    
    def get_diff(self) -> str:
        """
        Récupère le diff entre base_ref et head_ref.
        """
        try:
            result = subprocess.run(
                ["git", "diff", f"{self.base_ref}..{self.head_ref}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la récupération du diff: {e}", file=sys.stderr)
            return ""
    
    def get_modified_files(self) -> List[str]:
        """
        Récupère la liste des fichiers modifiés.
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{self.base_ref}..{self.head_ref}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la récupération des fichiers modifiés: {e}", file=sys.stderr)
            return []
    
    def check_patterns(self, diff: str, patterns: Dict[str, List[str]], risk_level: str) -> List[Risk]:
        """
        Vérifie les patterns dans le diff.
        
        Args:
            diff: Contenu du diff
            patterns: Dictionnaire de patterns à vérifier
            risk_level: "philosophique" ou "technique"
        
        Returns:
            Liste des risques identifiés
        """
        risks = []
        
        for pattern_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, diff, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extraire le fichier et la ligne depuis le diff
                    lines = diff[:match.start()].split("\n")
                    file_line = None
                    line_num = None
                    
                    for i, line in enumerate(reversed(lines)):
                        if line.startswith("+++") or line.startswith("---"):
                            # Extraire le nom du fichier
                            file_match = re.search(r"[ab]/(.+)", line)
                            if file_match:
                                file_line = file_match.group(1)
                            break
                        elif line.startswith("@@"):
                            # Extraire le numéro de ligne
                            line_match = re.search(r"\+(\d+)", line)
                            if line_match:
                                line_num = int(line_match.group(1))
                            break
                    
                    risks.append(Risk(
                        level=risk_level,
                        description=f"Pattern '{pattern_name}' détecté: {match.group(0)[:50]}",
                        file=file_line,
                        line=line_num,
                    ))
        
        return risks
    
    def check_test_removal(self, diff: str) -> List[Risk]:
        """
        Vérifie si des tests de compliance sont supprimés.
        """
        risks = []
        
        # Vérifier suppression de tests compliance
        test_removal_pattern = r"^-.*(test.*compliance|@egoejo_compliance)"
        matches = re.finditer(test_removal_pattern, diff, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            risks.append(Risk(
                level="philosophique",
                description="Test de compliance supprimé ou désactivé",
                file=None,
                line=None,
            ))
        
        return risks
    
    def check_double_structure(self, diff: str) -> List[Risk]:
        """
        Vérifie le respect de la double structure (SAKA / EUR).
        """
        risks = []
        
        # Vérifier séparation SAKA / EUR
        forbidden = self.check_patterns(
            diff,
            {"conversion": self.forbidden_patterns["conversion_saka_eur"]},
            "philosophique"
        )
        risks.extend(forbidden)
        
        # Vérifier affichage monétaire
        monetary = self.check_patterns(
            diff,
            {"monetary": self.forbidden_patterns["monetary_display"]},
            "philosophique"
        )
        risks.extend(monetary)
        
        return risks
    
    def check_saka_cycle(self, diff: str) -> List[Risk]:
        """
        Vérifie le cycle SAKA (circulation, compostage, anti-accumulation).
        """
        risks = []
        
        # Vérifier compostage
        compost = self.check_patterns(
            diff,
            {"compost": self.forbidden_patterns["compost_disabled"]},
            "philosophique"
        )
        risks.extend(compost)
        
        # Vérifier accumulation
        accumulation = self.check_patterns(
            diff,
            {"accumulation": self.forbidden_patterns["accumulation"]},
            "philosophique"
        )
        risks.extend(accumulation)
        
        return risks
    
    def check_governance(self, diff: str) -> List[Risk]:
        """
        Vérifie la gouvernance (pouvoir individuel limité, collectif protégé).
        """
        risks = []
        
        # Vérifier modification directe wallet
        wallet_mod = self.check_patterns(
            diff,
            {"wallet_mod": self.forbidden_patterns["direct_wallet_modification"]},
            "technique"
        )
        risks.extend(wallet_mod)
        
        # Vérifier activation V2.0
        investment = self.check_patterns(
            diff,
            {"investment": self.forbidden_patterns["investment_activation"]},
            "philosophique"
        )
        risks.extend(investment)
        
        return risks
    
    def check_transparency(self, diff: str) -> List[Risk]:
        """
        Vérifie la transparence (score arbitraire, métrique honnête).
        """
        risks = []
        
        # Patterns suspects pour transparence
        suspicious = [
            r"score.*\*\s*random",
            r"random.*score",
            r"#.*fake.*metric",
            r"#.*arbitrary.*score",
        ]
        
        for pattern in suspicious:
            matches = re.finditer(pattern, diff, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                risks.append(Risk(
                    level="philosophique",
                    description=f"Score ou métrique suspecte détectée: {match.group(0)[:50]}",
                    file=None,
                    line=None,
                ))
        
        return risks
    
    def is_editorial_file(self, file_path: str) -> bool:
        """
        Vérifie si un fichier est un fichier éditorial (CMS, contenu, seed).
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            True si le fichier est éditorial, False sinon
        """
        for pattern in self.editorial_file_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True
        return False
    
    def check_editorial_compliance(self, diff: str, modified_files: List[str]) -> List[Risk]:
        """
        Vérifie la conformité éditoriale (vocabulaire financier, promesses, workflow).
        
        Args:
            diff: Contenu du diff
            modified_files: Liste des fichiers modifiés
            
        Returns:
            Liste des risques éditoriaux identifiés
        """
        risks = []
        
        # Filtrer les fichiers éditoriaux
        editorial_files = [f for f in modified_files if self.is_editorial_file(f)]
        
        if not editorial_files:
            return risks  # Aucun fichier éditorial modifié
        
        # 1. Vérifier le vocabulaire financier
        financial_risks = self.check_patterns(
            diff,
            {"financial_language": self.editorial_forbidden_patterns["financial_language"]},
            "philosophique"
        )
        for risk in financial_risks:
            risk.description = f"Vocabulaire financier interdit détecté: {risk.description}"
        risks.extend(financial_risks)
        
        # 2. Vérifier les symboles monétaires
        monetary_risks = self.check_patterns(
            diff,
            {"monetary": self.editorial_forbidden_patterns["monetary_symbols"]},
            "philosophique"
        )
        for risk in monetary_risks:
            risk.description = f"Symbole monétaire interdit détecté: {risk.description}"
        risks.extend(monetary_risks)
        
        # 3. Vérifier le contournement du workflow
        workflow_risks = self.check_patterns(
            diff,
            {"workflow_bypass": self.editorial_forbidden_patterns["workflow_bypass"]},
            "philosophique"
        )
        for risk in workflow_risks:
            risk.description = f"Contournement du workflow détecté: {risk.description}"
        risks.extend(workflow_risks)
        
        # 4. Vérifier les promesses implicites
        promise_risks = self.check_patterns(
            diff,
            {"implicit_promises": self.editorial_forbidden_patterns["implicit_promises"]},
            "philosophique"
        )
        for risk in promise_risks:
            risk.description = f"Promesse implicite détectée: {risk.description}"
        risks.extend(promise_risks)
        
        # 5. Vérifier les patterns suspects (avertissements)
        suspicious_risks = []
        for pattern_name, pattern_list in self.editorial_suspicious_patterns.items():
            pattern_risks = self.check_patterns(
                diff,
                {pattern_name: pattern_list},
                "technique"
            )
            for risk in pattern_risks:
                risk.description = f"Pattern suspect éditorial ({pattern_name}): {risk.description}"
            suspicious_risks.extend(pattern_risks)
        risks.extend(suspicious_risks)
        
        return risks
    
    def check_finance_files_require_label(self, modified_files: List[str]) -> List[Risk]:
        """
        Vérifie que les PRs modifiant des fichiers financiers ont le label 'Finance-Audit'.
        
        Args:
            modified_files: Liste des fichiers modifiés
            
        Returns:
            Liste des risques si label manquant
        """
        risks = []
        
        # Fichiers financiers critiques
        finance_file_patterns = [
            r'finance/.*\.py',
            r'finance/.*\.js',
            r'finance/.*\.ts',
            r'.*stripe.*',
            r'.*payment.*',
            r'.*wallet.*',
            r'.*ledger.*',
        ]
        
        # Vérifier si des fichiers financiers sont modifiés
        finance_files_modified = False
        for file_path in modified_files:
            for pattern in finance_file_patterns:
                if re.search(pattern, file_path, re.IGNORECASE):
                    finance_files_modified = True
                    break
            if finance_files_modified:
                break
        
        if finance_files_modified:
            # Vérifier si le label 'Finance-Audit' est présent
            if not self.has_label('Finance-Audit'):
                risks.append(Risk(
                    level="philosophique",
                    description="Fichiers financiers modifiés sans label 'Finance-Audit'. Toute modification de fichiers financiers requiert une revue d'audit.",
                    file=None,
                    line=None,
                ))
        
        return risks
    
    def has_label(self, label_name: str) -> bool:
        """
        Vérifie si la PR a un label spécifique.
        
        Args:
            label_name: Nom du label à vérifier
            
        Returns:
            True si le label est présent, False sinon
        """
        if not requests or not self.github_token or not self.github_repo or not self.pr_number:
            # Si pas d'API disponible, on suppose que le label est présent (pas de blocage)
            return True
        
        url = f"{self.github_api_url}/issues/{self.pr_number}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            issue_data = response.json()
            labels = [label['name'] for label in issue_data.get('labels', [])]
            return label_name in labels
        except requests.exceptions.RequestException:
            # En cas d'erreur API, on suppose que le label est présent (pas de blocage)
            return True
    
    def analyze_pr(self) -> PRAnalysis:
        """
        Analyse complète de la PR.
        
        Returns:
            PRAnalysis avec niveau de conformité et recommandations
        """
        diff = self.get_diff()
        if not diff:
            return PRAnalysis(
                compliance_level=ComplianceLevel.NON_COMPATIBLE,
                justification="Impossible de récupérer le diff de la PR.",
                philosophical_risks=[],
                technical_risks=[],
                recommendation="refuse",
                blocking=True,
            )
        
        modified_files = self.get_modified_files()
        
        # Collecter tous les risques
        all_risks = []
        
        # 1. Double structure (SAKA / EUR)
        double_structure_risks = self.check_double_structure(diff)
        all_risks.extend(double_structure_risks)
        
        # 2. Cycle SAKA
        saka_cycle_risks = self.check_saka_cycle(diff)
        all_risks.extend(saka_cycle_risks)
        
        # 3. Gouvernance
        governance_risks = self.check_governance(diff)
        all_risks.extend(governance_risks)
        
        # 4. Transparence
        transparency_risks = self.check_transparency(diff)
        all_risks.extend(transparency_risks)
        
        # 5. Suppression de tests
        test_removal_risks = self.check_test_removal(diff)
        all_risks.extend(test_removal_risks)
        
        # 6. Compliance éditoriale (NOUVEAU - Gardien éditorial)
        modified_files = self.get_modified_files()
        editorial_risks = self.check_editorial_compliance(diff, modified_files)
        all_risks.extend(editorial_risks)
        
        # 7. Vérification Finance-Audit (PRs modifiant fichiers financiers)
        finance_audit_risks = self.check_finance_files_require_label(modified_files)
        all_risks.extend(finance_audit_risks)
        
        # Séparer risques philosophiques et techniques
        philosophical_risks = [r for r in all_risks if r.level == "philosophique"]
        technical_risks = [r for r in all_risks if r.level == "technique"]
        
        # Déterminer le niveau de conformité
        if philosophical_risks:
            # Risques philosophiques = NON COMPATIBLE
            compliance_level = ComplianceLevel.NON_COMPATIBLE
            recommendation = "refuse"
            blocking = True
            justification = (
                f"❌ VIOLATION PHILOSOPHIQUE DÉTECTÉE\n\n"
                f"{len(philosophical_risks)} risque(s) philosophique(s) identifié(s). "
                f"Cette PR viole les principes fondamentaux d'EGOEJO."
            )
        elif technical_risks:
            # Risques techniques = SOUS CONDITIONS
            compliance_level = ComplianceLevel.COMPATIBLE_CONDITIONS
            recommendation = "refactor"
            blocking = False
            justification = (
                f"⚠️ RISQUES TECHNIQUES DÉTECTÉS\n\n"
                f"{len(technical_risks)} risque(s) technique(s) identifié(s). "
                f"Review technique recommandée avant merge."
            )
        else:
            # Aucun risque = COMPATIBLE
            compliance_level = ComplianceLevel.COMPATIBLE
            recommendation = "accept"
            blocking = False
            justification = (
                f"✅ CONFORME EGOEJO\n\n"
                f"Aucun risque philosophique ou technique détecté. "
                f"Cette PR respecte les principes EGOEJO."
            )
        
        return PRAnalysis(
            compliance_level=compliance_level,
            justification=justification,
            philosophical_risks=philosophical_risks,
            technical_risks=technical_risks,
            recommendation=recommendation,
            blocking=blocking,
        )
    
    def format_comment(self, analysis: PRAnalysis) -> str:
        """
        Formate le commentaire du bot pour la PR.
        
        Args:
            analysis: Analyse de la PR
        
        Returns:
            Commentaire formaté en Markdown
        """
        comment = f"""## 🤖 EGOEJO PR Bot - Analyse de Conformité

### 📊 Résultat

**{analysis.compliance_level.value}**

{analysis.justification}

### 🔍 Détails

"""
        
        if analysis.philosophical_risks:
            # Séparer risques généraux et risques éditoriaux
            general_risks = [r for r in analysis.philosophical_risks if not any(
                keyword in r.description.lower() for keyword in [
                    "vocabulaire financier", "symbole monétaire", "workflow", "promesse"
                ]
            )]
            editorial_risks = [r for r in analysis.philosophical_risks if r not in general_risks]
            
            if general_risks:
                comment += f"#### ⚠️ Risques Philosophiques ({len(general_risks)})\n\n"
                for i, risk in enumerate(general_risks[:10], 1):  # Max 10 risques
                    file_info = f"`{risk.file}`" if risk.file else "Fichier non identifié"
                    line_info = f"ligne {risk.line}" if risk.line else ""
                    comment += f"{i}. **{risk.description}**\n"
                    if risk.file or risk.line:
                        comment += f"   - 📁 {file_info}"
                        if line_info:
                            comment += f" ({line_info})"
                        comment += "\n"
                comment += "\n"
            
            if editorial_risks:
                comment += f"#### 📝 Violations Éditoriales ({len(editorial_risks)})\n\n"
                comment += "**🛡️ Gardien Éditorial EGOEJO**\n\n"
                comment += "Les violations suivantes ont été détectées dans les fichiers CMS, contenus ou seed :\n\n"
                for i, risk in enumerate(editorial_risks[:10], 1):  # Max 10 risques
                    file_info = f"`{risk.file}`" if risk.file else "Fichier non identifié"
                    line_info = f"ligne {risk.line}" if risk.line else ""
                    comment += f"{i}. **{risk.description}**\n"
                    if risk.file or risk.line:
                        comment += f"   - 📁 {file_info}"
                        if line_info:
                            comment += f" ({line_info})"
                        comment += "\n"
                comment += "\n"
                comment += "**Rappel Constitution Éditoriale :**\n"
                comment += "- ❌ Aucun vocabulaire financier (ROI, profit, rentabilité, etc.)\n"
                comment += "- ❌ Aucun symbole monétaire (€, $, EUR, USD, etc.)\n"
                comment += "- ❌ Aucune promesse implicite (garantie, retour garanti, etc.)\n"
                comment += "- ❌ Aucun contournement du workflow (status='published' direct)\n"
                comment += "- ✅ Tous les contenus publiés doivent avoir une source et une licence\n\n"
        
        if analysis.technical_risks:
            comment += f"#### 🔧 Risques Techniques ({len(analysis.technical_risks)})\n\n"
            for i, risk in enumerate(analysis.technical_risks[:10], 1):  # Max 10 risques
                file_info = f"`{risk.file}`" if risk.file else "Fichier non identifié"
                line_info = f"ligne {risk.line}" if risk.line else ""
                comment += f"{i}. **{risk.description}**\n"
                if risk.file or risk.line:
                    comment += f"   - 📁 {file_info}"
                    if line_info:
                        comment += f" ({line_info})"
                    comment += "\n"
            comment += "\n"
        
        comment += f"""### 💡 Recommandation

**{analysis.recommendation.upper()}**

"""
        
        if analysis.blocking:
            comment += "🚫 **MERGE BLOQUÉ** - Cette PR ne peut pas être mergée sans correction.\n\n"
        else:
            comment += "✅ **MERGE AUTORISÉ** - Cette PR peut être mergée.\n\n"
        
        comment += """---

*Ce commentaire est généré automatiquement par le bot de gouvernance EGOEJO (incluant le Gardien Éditorial).*
*Pour plus d'informations, voir :*
*- [docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)*
*- [docs/egoejo_compliance/MATRICE_CONTENU_CRITERES.md](../../docs/egoejo_compliance/MATRICE_CONTENU_CRITERES.md)*
"""
        
        return comment
    
    def post_comment(self, analysis: PRAnalysis) -> bool:
        """
        Poste un commentaire sur la PR GitHub via l'API.
        
        Args:
            analysis: Analyse de la PR
        
        Returns:
            True si le commentaire a été posté avec succès, False sinon
        """
        if not requests:
            print("⚠️ Module 'requests' non disponible. Commentaire GitHub non posté.", file=sys.stderr)
            return False
        
        if not self.github_token or not self.github_repo or not self.pr_number:
            print("⚠️ Variables GitHub manquantes (GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_PR_NUMBER).", file=sys.stderr)
            return False
        
        comment = self.format_comment(analysis)
        
        url = f"{self.github_api_url}/issues/{self.pr_number}/comments"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "body": comment
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            print(f"✅ Commentaire posté sur la PR #{self.pr_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur lors du post du commentaire: {e}", file=sys.stderr)
            return False
    
    def set_label(self, analysis: PRAnalysis) -> bool:
        """
        Définit le label GitHub pour la PR via l'API.
        
        Args:
            analysis: Analyse de la PR
        
        Returns:
            True si le label a été ajouté avec succès, False sinon
        """
        if not requests:
            print("⚠️ Module 'requests' non disponible. Label GitHub non ajouté.", file=sys.stderr)
            return False
        
        if not self.github_token or not self.github_repo or not self.pr_number:
            print("⚠️ Variables GitHub manquantes (GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_PR_NUMBER).", file=sys.stderr)
            return False
        
        # Mapping des labels selon le niveau de conformité
        if analysis.compliance_level == ComplianceLevel.COMPATIBLE:
            label_name = "egoejo:compliant"
        elif analysis.compliance_level == ComplianceLevel.NON_COMPATIBLE:
            label_name = "egoejo:violation"
        else:  # COMPATIBLE_CONDITIONS
            label_name = "egoejo:review-needed"
        
        # Vérifier si le label existe, sinon le créer
        self.ensure_label_exists(label_name)
        
        # Ajouter le label à la PR
        url = f"{self.github_api_url}/issues/{self.pr_number}/labels"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "labels": [label_name]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            print(f"✅ Label '{label_name}' ajouté à la PR #{self.pr_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur lors de l'ajout du label: {e}", file=sys.stderr)
            return False
    
    def ensure_label_exists(self, label_name: str) -> None:
        """
        S'assure que le label existe dans le dépôt GitHub.
        
        Args:
            label_name: Nom du label
        """
        if not requests or not self.github_token or not self.github_repo:
            return
        
        url = f"{self.github_api_url}/labels/{label_name}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        # Vérifier si le label existe
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return  # Label existe déjà
        except requests.exceptions.RequestException:
            pass
        
        # Créer le label s'il n'existe pas
        label_colors = {
            "egoejo:compliant": "28a745",  # Vert
            "egoejo:violation": "d73a49",  # Rouge
            "egoejo:review-needed": "fbca04",  # Jaune
        }
        
        color = label_colors.get(label_name, "ededed")
        url = f"{self.github_api_url}/labels"
        data = {
            "name": label_name,
            "color": color,
            "description": f"Label EGOEJO: {label_name}"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 201:
                print(f"✅ Label '{label_name}' créé")
            elif response.status_code == 422:
                # Label existe peut-être déjà (conflit)
                pass
        except requests.exceptions.RequestException:
            pass
    
    def block_merge(self, analysis: PRAnalysis) -> bool:
        """
        Bloque le merge de la PR si violation critique.
        
        Args:
            analysis: Analyse de la PR
        
        Returns:
            True si le merge a été bloqué, False sinon
        """
        if not analysis.blocking:
            return False
        
        if not requests or not self.github_token or not self.github_repo or not self.pr_number:
            print("⚠️ Variables GitHub manquantes. Merge non bloqué via API.", file=sys.stderr)
            return False
        
        # Créer une review "REQUEST_CHANGES" pour bloquer le merge
        url = f"{self.github_api_url}/pulls/{self.pr_number}/reviews"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "event": "REQUEST_CHANGES",
            "body": (
                "🚫 **MERGE BLOQUÉ PAR EGOEJO PR BOT**\n\n"
                "Cette PR contient des violations critiques de la constitution EGOEJO.\n"
                "Le merge est bloqué jusqu'à correction des violations.\n\n"
                "Voir le commentaire du bot pour plus de détails."
            )
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            print(f"✅ Merge bloqué pour la PR #{self.pr_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur lors du blocage du merge: {e}", file=sys.stderr)
            return False
    
    def run(self) -> int:
        """
        Exécute l'analyse de la PR.
        
        Returns:
            Code de sortie (0 = succès, 1 = échec)
        """
        print("🤖 EGOEJO PR Bot - Analyse de conformité...")
        print(f"📋 PR #{self.pr_number}: {self.base_ref}..{self.head_ref}")
        
        analysis = self.analyze_pr()
        
        # Afficher le résultat
        print(f"\n📊 Résultat: {analysis.compliance_level.value}")
        print(f"💡 Recommandation: {analysis.recommendation}")
        print(f"🚫 Bloquant: {analysis.blocking}")
        
        # Générer le commentaire
        comment = self.format_comment(analysis)
        
        # Écrire le commentaire dans un fichier pour GitHub Actions
        comment_file = os.environ.get("GITHUB_STEP_SUMMARY", "/tmp/pr_comment.md")
        try:
            with open(comment_file, "w", encoding="utf-8") as f:
                f.write(comment)
            print(f"\n💬 Commentaire généré: {comment_file}")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'écriture du commentaire: {e}", file=sys.stderr)
        
        # Poster le commentaire sur GitHub
        self.post_comment(analysis)
        
        # Ajouter le label approprié
        self.set_label(analysis)
        
        # Bloquer le merge si violation critique
        if analysis.blocking:
            self.block_merge(analysis)
        
        # Retourner le code de sortie (1 si bloquant)
        return 1 if analysis.blocking else 0


def main():
    """Point d'entrée principal"""
    bot = EGOEJOPRBot()
    exit_code = bot.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

