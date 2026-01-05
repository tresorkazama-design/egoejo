"""
Matrice de conformité éditoriale pour le contenu EGOEJO

Cette matrice définit les critères de conformité obligatoires pour chaque contenu publié.
Elle est utilisée pour :
- Calculer le score de conformité par contenu
- Générer le rapport de compliance éditoriale
- Bloquer la publication de contenus non conformes
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from core.models import EducationalContent


class ComplianceCriterion(Enum):
    """Critères de conformité éditoriale EGOEJO"""
    
    # Statut et workflow
    STATUS_PUBLISHED_ONLY = "status_published_only"
    STATUS_WORKFLOW_VALID = "status_workflow_valid"
    
    # Source et traçabilité
    HAS_SOURCE = "has_source"
    HAS_LICENSE = "has_license"
    
    # Langage et promesses
    NO_FINANCIAL_LANGUAGE = "no_financial_language"
    NO_MONETARY_SYMBOLS = "no_monetary_symbols"
    
    # Audit et traçabilité
    AUDITLOG_EXISTS = "auditlog_exists"
    PUBLISHED_BY_TRACKED = "published_by_tracked"
    
    # Séparation SAKA/EUR
    NO_SAKA_EUR_CONVERSION = "no_saka_eur_conversion"
    NO_FINANCIAL_PROMISES = "no_financial_promises"


@dataclass
class ComplianceResult:
    """Résultat d'un critère de conformité"""
    criterion: ComplianceCriterion
    passed: bool
    message: str
    severity: str  # "critical" | "warning" | "info"
    details: Optional[Dict] = None


@dataclass
class ContentComplianceScore:
    """Score de conformité pour un contenu"""
    content_id: int
    content_title: str
    content_slug: str
    overall_score: float  # 0.0 à 1.0
    is_compliant: bool
    passed_criteria: int
    total_criteria: int
    critical_failures: int
    warnings: int
    results: List[ComplianceResult]
    last_audit: str  # ISO-8601


class ContentComplianceMatrix:
    """
    Matrice de conformité éditoriale pour le contenu EGOEJO.
    
    Cette classe implémente tous les critères de conformité et calcule
    le score de conformité pour chaque contenu.
    """
    
    # Critères obligatoires (bloquants)
    CRITICAL_CRITERIA = [
        ComplianceCriterion.STATUS_PUBLISHED_ONLY,
        ComplianceCriterion.NO_FINANCIAL_LANGUAGE,
        ComplianceCriterion.NO_SAKA_EUR_CONVERSION,
        ComplianceCriterion.NO_FINANCIAL_PROMISES,
    ]
    
    # Critères recommandés (avertissements)
    WARNING_CRITERIA = [
        ComplianceCriterion.HAS_SOURCE,
        ComplianceCriterion.HAS_LICENSE,
        ComplianceCriterion.AUDITLOG_EXISTS,
        ComplianceCriterion.PUBLISHED_BY_TRACKED,
    ]
    
    # Patterns interdits pour le langage financier
    FORBIDDEN_FINANCIAL_PATTERNS = [
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
    ]
    
    @classmethod
    def check_content_compliance(cls, content: EducationalContent) -> ContentComplianceScore:
        """
        Vérifie la conformité d'un contenu selon tous les critères.
        
        Args:
            content: Le contenu à vérifier
            
        Returns:
            ContentComplianceScore: Score de conformité détaillé
        """
        results = []
        
        # 1. Vérifier le statut (critique)
        status_result = cls._check_status_published_only(content)
        results.append(status_result)
        
        # 2. Vérifier le workflow (critique)
        workflow_result = cls._check_status_workflow_valid(content)
        results.append(workflow_result)
        
        # 3. Vérifier la source (avertissement)
        source_result = cls._check_has_source(content)
        results.append(source_result)
        
        # 4. Vérifier la licence (avertissement)
        license_result = cls._check_has_license(content)
        results.append(license_result)
        
        # 5. Vérifier le langage financier (critique)
        financial_language_result = cls._check_no_financial_language(content)
        results.append(financial_language_result)
        
        # 6. Vérifier les symboles monétaires (critique)
        monetary_symbols_result = cls._check_no_monetary_symbols(content)
        results.append(monetary_symbols_result)
        
        # 7. Vérifier l'audit log (avertissement)
        auditlog_result = cls._check_auditlog_exists(content)
        results.append(auditlog_result)
        
        # 8. Vérifier le tracking published_by (avertissement)
        published_by_result = cls._check_published_by_tracked(content)
        results.append(published_by_result)
        
        # 9. Vérifier la conversion SAKA/EUR (critique)
        saka_eur_result = cls._check_no_saka_eur_conversion(content)
        results.append(saka_eur_result)
        
        # 10. Vérifier les promesses financières (critique)
        financial_promises_result = cls._check_no_financial_promises(content)
        results.append(financial_promises_result)
        
        # Calculer le score
        passed_criteria = sum(1 for r in results if r.passed)
        total_criteria = len(results)
        critical_failures = sum(1 for r in results if not r.passed and r.severity == "critical")
        warnings = sum(1 for r in results if not r.passed and r.severity == "warning")
        
        # Score : 1.0 si tous les critères critiques passent, sinon 0.0
        # Les avertissements réduisent le score mais ne bloquent pas
        if critical_failures > 0:
            overall_score = 0.0
            is_compliant = False
        else:
            # Score basé sur les critères critiques (100%) + avertissements (bonus)
            critical_passed = sum(1 for r in results if r.passed and r.severity == "critical")
            total_critical = sum(1 for r in results if r.severity == "critical")
            warning_passed = sum(1 for r in results if r.passed and r.severity == "warning")
            total_warning = sum(1 for r in results if r.severity == "warning")
            
            if total_critical > 0:
                critical_score = critical_passed / total_critical
            else:
                critical_score = 1.0
            
            if total_warning > 0:
                warning_score = warning_passed / total_warning * 0.2  # Bonus de 20% max
            else:
                warning_score = 0.0
            
            overall_score = min(1.0, critical_score + warning_score)
            is_compliant = critical_failures == 0
        
        from django.utils import timezone
        
        return ContentComplianceScore(
            content_id=content.id,
            content_title=content.title,
            content_slug=content.slug,
            overall_score=overall_score,
            is_compliant=is_compliant,
            passed_criteria=passed_criteria,
            total_criteria=total_criteria,
            critical_failures=critical_failures,
            warnings=warnings,
            results=results,
            last_audit=timezone.now().isoformat(),
        )
    
    @classmethod
    def _check_status_published_only(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie que le contenu est publié (status='published')"""
        if content.status == 'published':
            return ComplianceResult(
                criterion=ComplianceCriterion.STATUS_PUBLISHED_ONLY,
                passed=True,
                message="Le contenu est publié",
                severity="critical",
            )
        else:
            return ComplianceResult(
                criterion=ComplianceCriterion.STATUS_PUBLISHED_ONLY,
                passed=False,
                message=f"Le contenu a le statut '{content.status}' au lieu de 'published'",
                severity="critical",
            )
    
    @classmethod
    def _check_status_workflow_valid(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie que le workflow de statut est valide"""
        valid_statuses = ['draft', 'pending', 'published', 'rejected', 'archived']
        if content.status in valid_statuses:
            return ComplianceResult(
                criterion=ComplianceCriterion.STATUS_WORKFLOW_VALID,
                passed=True,
                message="Le workflow de statut est valide",
                severity="critical",
            )
        else:
            return ComplianceResult(
                criterion=ComplianceCriterion.STATUS_WORKFLOW_VALID,
                passed=False,
                message=f"Statut invalide: '{content.status}'",
                severity="critical",
            )
    
    @classmethod
    def _check_has_source(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie que le contenu a une source (external_url, file, ou champ source)"""
        has_source = bool(
            content.external_url or
            content.file or
            getattr(content, 'source', None) or
            getattr(content, 'source_url', None)
        )
        
        if has_source:
            return ComplianceResult(
                criterion=ComplianceCriterion.HAS_SOURCE,
                passed=True,
                message="Le contenu a une source",
                severity="warning",
            )
        else:
            return ComplianceResult(
                criterion=ComplianceCriterion.HAS_SOURCE,
                passed=False,
                message="Le contenu n'a pas de source (external_url, file, source ou source_url requis)",
                severity="warning",
            )
    
    @classmethod
    def _check_has_license(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie que le contenu a une licence"""
        model_fields = {f.name for f in EducationalContent._meta.get_fields()}
        has_license_field = 'license' in model_fields or 'license_type' in model_fields
        
        if has_license_field:
            license_value = getattr(content, 'license', None) or getattr(content, 'license_type', None)
            if license_value:
                return ComplianceResult(
                    criterion=ComplianceCriterion.HAS_LICENSE,
                    passed=True,
                    message=f"Le contenu a une licence: {license_value}",
                    severity="warning",
                )
            else:
                return ComplianceResult(
                    criterion=ComplianceCriterion.HAS_LICENSE,
                    passed=False,
                    message="Le contenu n'a pas de licence (license ou license_type requis)",
                    severity="warning",
                )
        else:
            # Champ n'existe pas encore - on retourne un avertissement mais on ne bloque pas
            return ComplianceResult(
                criterion=ComplianceCriterion.HAS_LICENSE,
                passed=False,
                message="Le champ 'license' n'existe pas encore dans le modèle (à ajouter dans une migration)",
                severity="info",
            )
    
    @classmethod
    def _check_no_financial_language(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie qu'il n'y a pas de langage financier interdit"""
        import re
        
        violations = []
        compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in cls.FORBIDDEN_FINANCIAL_PATTERNS]
        
        # Scanner le titre
        title_text = content.title or ''
        for pattern in compiled_patterns:
            if pattern.search(title_text):
                violations.append({
                    'field': 'title',
                    'pattern': pattern.pattern,
                    'snippet': title_text[:100],
                })
        
        # Scanner la description
        description_text = content.description or ''
        for pattern in compiled_patterns:
            if pattern.search(description_text):
                violations.append({
                    'field': 'description',
                    'pattern': pattern.pattern,
                    'snippet': description_text[:200],
                })
        
        if violations:
            return ComplianceResult(
                criterion=ComplianceCriterion.NO_FINANCIAL_LANGUAGE,
                passed=False,
                message=f"Langage financier interdit détecté ({len(violations)} violation(s))",
                severity="critical",
                details={'violations': violations},
            )
        else:
            return ComplianceResult(
                criterion=ComplianceCriterion.NO_FINANCIAL_LANGUAGE,
                passed=True,
                message="Aucun langage financier interdit détecté",
                severity="critical",
            )
    
    @classmethod
    def _check_no_monetary_symbols(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie qu'il n'y a pas de symboles monétaires"""
        import re
        
        monetary_patterns = [
            r'€',
            r'\$',
            r'\bEUR\b',
            r'\bUSD\b',
            r'\bGBP\b',
            r'\bCHF\b',
            r'\bJPY\b',
            r'\bCAD\b',
            r'\bAUD\b',
        ]
        
        violations = []
        text_to_check = f"{content.title} {content.description}"
        
        for pattern in monetary_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                violations.append({
                    'pattern': pattern,
                    'snippet': text_to_check[:200],
                })
        
        if violations:
            return ComplianceResult(
            criterion=ComplianceCriterion.NO_MONETARY_SYMBOLS,
            passed=False,
            message=f"Symboles monétaires détectés ({len(violations)} violation(s))",
            severity="critical",
            details={'violations': violations},
        )
        else:
            return ComplianceResult(
                criterion=ComplianceCriterion.NO_MONETARY_SYMBOLS,
                passed=True,
                message="Aucun symbole monétaire détecté",
                severity="critical",
            )
    
    @classmethod
    def _check_auditlog_exists(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie qu'un audit log existe pour ce contenu"""
        try:
            from core.models import AuditLog
            
            # Vérifier s'il existe un audit log pour ce contenu
            audit_logs = AuditLog.objects.filter(
                object_type='educational_content',
                object_id=content.id,
            )
            
            if audit_logs.exists():
                return ComplianceResult(
                    criterion=ComplianceCriterion.AUDITLOG_EXISTS,
                    passed=True,
                    message=f"Audit log existe ({audit_logs.count()} entrée(s))",
                    severity="warning",
                )
            else:
                return ComplianceResult(
                    criterion=ComplianceCriterion.AUDITLOG_EXISTS,
                    passed=False,
                    message="Aucun audit log trouvé pour ce contenu",
                    severity="warning",
                )
        except Exception as e:
            # Si le modèle AuditLog n'existe pas ou erreur, on retourne un avertissement
            return ComplianceResult(
                criterion=ComplianceCriterion.AUDITLOG_EXISTS,
                passed=False,
                message=f"Impossible de vérifier l'audit log: {str(e)}",
                severity="info",
            )
    
    @classmethod
    def _check_published_by_tracked(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie que published_by est tracké"""
        if content.status == 'published' and content.published_by:
            return ComplianceResult(
                criterion=ComplianceCriterion.PUBLISHED_BY_TRACKED,
                passed=True,
                message=f"Publié par: {content.published_by.username or content.published_by.email}",
                severity="warning",
            )
        elif content.status == 'published' and not content.published_by:
            return ComplianceResult(
                criterion=ComplianceCriterion.PUBLISHED_BY_TRACKED,
                passed=False,
                message="Le contenu est publié mais published_by n'est pas tracké",
                severity="warning",
            )
        else:
            return ComplianceResult(
                criterion=ComplianceCriterion.PUBLISHED_BY_TRACKED,
                passed=True,
                message="N/A (contenu non publié)",
                severity="warning",
            )
    
    @classmethod
    def _check_no_saka_eur_conversion(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie qu'il n'y a pas de conversion SAKA/EUR mentionnée"""
        import re
        
        conversion_patterns = [
            r'saka.*eur|eur.*saka',
            r'saka.*€|€.*saka',
            r'convertir.*saka',
            r'conversion.*saka',
            r'équivalent.*saka',
            r'valeur.*saka',
        ]
        
        text_to_check = f"{content.title} {content.description}".lower()
        
        for pattern in conversion_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return ComplianceResult(
                    criterion=ComplianceCriterion.NO_SAKA_EUR_CONVERSION,
                    passed=False,
                    message=f"Conversion SAKA/EUR détectée: {pattern}",
                    severity="critical",
                    details={'pattern': pattern, 'snippet': text_to_check[:200]},
                )
        
        return ComplianceResult(
            criterion=ComplianceCriterion.NO_SAKA_EUR_CONVERSION,
            passed=True,
            message="Aucune conversion SAKA/EUR détectée",
            severity="critical",
        )
    
    @classmethod
    def _check_no_financial_promises(cls, content: EducationalContent) -> ComplianceResult:
        """Vérifie qu'il n'y a pas de promesses financières"""
        # Utilise les mêmes patterns que _check_no_financial_language
        # mais avec un focus sur les "promesses"
        import re
        
        promise_patterns = [
            r'garant.*retour',
            r'garant.*profit',
            r'promet.*retour',
            r'promet.*profit',
            r'assur.*retour',
            r'assur.*profit',
        ]
        
        text_to_check = f"{content.title} {content.description}".lower()
        
        violations = []
        for pattern in promise_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                violations.append({
                    'pattern': pattern,
                    'snippet': text_to_check[:200],
                })
        
        if violations:
            return ComplianceResult(
                criterion=ComplianceCriterion.NO_FINANCIAL_PROMISES,
                passed=False,
                message=f"Promesses financières détectées ({len(violations)} violation(s))",
                severity="critical",
                details={'violations': violations},
            )
        else:
            return ComplianceResult(
                criterion=ComplianceCriterion.NO_FINANCIAL_PROMISES,
                passed=True,
                message="Aucune promesse financière détectée",
                severity="critical",
            )

