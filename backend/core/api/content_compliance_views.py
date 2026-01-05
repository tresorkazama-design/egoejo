"""
Vues pour la compliance éditoriale du contenu EGOEJO

Génère un rapport JSON de conformité des contenus publiés.
Connecté au label EGOEJO Compliant.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import re

from core.models import EducationalContent


# Patterns interdits pour les promesses financières
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

COMPILED_FORBIDDEN_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in FORBIDDEN_FINANCIAL_PATTERNS]


def _check_financial_language(content):
    """Vérifie si un contenu contient des promesses financières"""
    violations = []
    
    # Scanner le titre
    title_text = content.title or ''
    for pattern in COMPILED_FORBIDDEN_PATTERNS:
        if pattern.search(title_text):
            violations.append({
                'field': 'title',
                'pattern': pattern.pattern,
                'snippet': title_text[:100],
            })
    
    # Scanner la description
    description_text = content.description or ''
    for pattern in COMPILED_FORBIDDEN_PATTERNS:
        if pattern.search(description_text):
            violations.append({
                'field': 'description',
                'pattern': pattern.pattern,
                'snippet': description_text[:200],
            })
    
    return violations


def _check_source_and_license(content):
    """Vérifie si un contenu a une source et une licence"""
    issues = []
    
    # Vérifier la source
    has_source = bool(
        content.external_url or 
        content.file or
        getattr(content, 'source', None) or
        getattr(content, 'source_url', None)
    )
    
    if not has_source:
        issues.append('missing_source')
    
    # Vérifier la licence (si le champ existe)
    model_fields = {f.name for f in EducationalContent._meta.get_fields()}
    has_license_field = 'license' in model_fields or 'license_type' in model_fields
    
    if has_license_field:
        license_value = getattr(content, 'license', None) or getattr(content, 'license_type', None)
        if not license_value:
            issues.append('missing_license')
    
    return issues


@api_view(['GET'])
@permission_classes([AllowAny])
def content_compliance_report(request):
    """
    Génère un rapport JSON de conformité éditoriale des contenus publiés.
    
    Endpoint : GET /api/public/content-compliance.json
    
    Retourne :
    {
        "compliance_status": "compliant" | "non-compliant" | "partial",
        "total_published": int,
        "compliant_count": int,
        "non_compliant_count": int,
        "violations": [
            {
                "content_id": int,
                "content_title": str,
                "content_slug": str,
                "issues": ["missing_source", "missing_license", "financial_language"],
                "details": {...}
            }
        ],
        "last_audit": "ISO-8601",
        "rules": {
            "public_content_must_be_published": bool,
            "source_required": bool,
            "license_required": bool,
            "no_financial_promises": bool,
        }
    }
    """
    published_contents = EducationalContent.objects.filter(status='published')
    total_published = published_contents.count()
    
    violations = []
    compliant_count = 0
    
    for content in published_contents:
        content_issues = []
        content_details = {}
        
        # Vérifier le langage financier
        financial_violations = _check_financial_language(content)
        if financial_violations:
            content_issues.append('financial_language')
            content_details['financial_violations'] = financial_violations
        
        # Vérifier source et licence
        source_license_issues = _check_source_and_license(content)
        if 'missing_source' in source_license_issues:
            content_issues.append('missing_source')
        if 'missing_license' in source_license_issues:
            content_issues.append('missing_license')
        
        if content_issues:
            violations.append({
                'content_id': content.id,
                'content_title': content.title,
                'content_slug': content.slug,
                'issues': content_issues,
                'details': content_details,
            })
        else:
            compliant_count += 1
    
    non_compliant_count = len(violations)
    
    # Déterminer le statut de compliance
    if non_compliant_count == 0:
        compliance_status = 'compliant'
    elif compliant_count == 0:
        compliance_status = 'non-compliant'
    else:
        compliance_status = 'partial'
    
    # Vérifier les règles
    rules = {
        'public_content_must_be_published': True,  # Vérifié par le filtre status='published'
        'source_required': True,
        'license_required': True,
        'no_financial_promises': True,
    }
    
    report = {
        'compliance_status': compliance_status,
        'total_published': total_published,
        'compliant_count': compliant_count,
        'non_compliant_count': non_compliant_count,
        'violations': violations,
        'last_audit': timezone.now().isoformat(),
        'rules': rules,
    }
    
    return Response(report, content_type='application/json')

