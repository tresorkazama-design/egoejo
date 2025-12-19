#!/usr/bin/env python3
"""
EGOEJO Semantic Guardian - Analyse sémantique IA
Version complémentaire au guardian.py déterministe

RÔLE :
- Détecter des violations implicites
- Signaler des risques philosophiques
- Ne JAMAIS merger seule (non bloquant)

CONTRAINTES :
- Analyse IA non souveraine
- Complémentaire aux règles déterministes
- Sert à la gouvernance humaine
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from enum import Enum


class ConfidenceLevel(Enum):
    """Niveaux de confiance de l'analyse IA"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SemanticVerdict(Enum):
    """Verdicts suggérés par l'IA"""
    COMPATIBLE = "🟢 COMPATIBLE EGOEJO"
    COMPATIBLE_UNDER_CONDITIONS = "🟡 COMPATIBLE SOUS CONDITIONS"
    NON_COMPATIBLE = "🔴 NON COMPATIBLE EGOEJO"


class EGOEJOSemanticGuardian:
    """
    Analyseur sémantique IA pour détecter les violations implicites
    de la constitution EGOEJO
    """
    
    def __init__(self):
        """Initialise le Semantic Guardian"""
        self.manifesto_summary = self._load_manifesto_summary()
        self.api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')
        self.api_provider = self._detect_api_provider()
    
    def _load_manifesto_summary(self) -> str:
        """
        Charge le résumé du Manifeste EGOEJO
        
        Returns:
            Résumé du manifeste
        """
        return """
MANIFESTE EGOEJO - RÉSUMÉ

PHILOSOPHIE FONDAMENTALE :
- Double structure économique : SAKA (relationnelle, prioritaire) et EUR (instrumentale, dormante)
- Anti-accumulation absolue : le SAKA doit circuler, pas s'accumuler
- Primauté du collectif : le Silo redistribue aux actifs
- Subordination de la technologie : la structure instrumentale ne contraint jamais la relationnelle

RÈGLES ABSOLUES :
1. Aucune conversion SAKA ↔ EUR
2. Aucun rendement financier basé sur SAKA
3. Aucun affichage monétaire du SAKA
4. Le cycle SAKA est non négociable (Récolte → Usage → Compost → Silo → Redistribution)
5. En cas de conflit : SAKA > EUR (la structure relationnelle prime)

PRINCIPES :
- L'engagement ne peut pas devenir un rendement
- L'accumulation est interdite (compostage obligatoire)
- La banque instrumentale (EUR) ne contraint jamais SAKA
- La circulation prime sur l'accumulation
- Le collectif prime sur l'individu
"""
    
    def _detect_api_provider(self) -> str:
        """
        Détecte le fournisseur d'API IA disponible
        
        Returns:
            'openai' ou 'anthropic' ou None
        """
        if os.environ.get('OPENAI_API_KEY'):
            return 'openai'
        elif os.environ.get('ANTHROPIC_API_KEY'):
            return 'anthropic'
        return None
    
    def get_pr_diff(self, pr_number: Optional[int] = None, base_branch: str = "origin/main") -> str:
        """
        Récupère le diff d'une PR
        
        Args:
            pr_number: Numéro de la PR (optionnel, si None utilise git diff)
            base_branch: Branche de référence
        
        Returns:
            Contenu du diff
        """
        try:
            if pr_number:
                # En contexte GitHub Actions, utiliser l'API GitHub
                github_repo = os.environ.get('GITHUB_REPOSITORY')
                github_token = os.environ.get('GITHUB_TOKEN')
                
                if github_repo and github_token:
                    import requests
                    url = f"https://api.github.com/repos/{github_repo}/pulls/{pr_number}"
                    headers = {
                        'Authorization': f'token {github_token}',
                        'Accept': 'application/vnd.github.v3.diff'
                    }
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        return response.text
            
            # Fallback : git diff local
            result = subprocess.run(
                ["git", "diff", base_branch],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        
        except Exception as e:
            print(f"[AVERTISSEMENT] Impossible de recuperer le diff: {e}")
            return ""
    
    def analyze_with_ai(self, diff_content: str) -> Dict:
        """
        Analyse le diff avec l'IA pour détecter les violations implicites
        
        Args:
            diff_content: Contenu du diff de la PR
        
        Returns:
            Dictionnaire avec label, justification, confiance
        """
        if not self.api_key or not self.api_provider:
            return {
                'label': '⚠️ ANALYSE IA NON DISPONIBLE',
                'justification': 'Aucune clé API IA configurée (OPENAI_API_KEY ou ANTHROPIC_API_KEY)',
                'confidence': 'LOW',
                'error': True
            }
        
        # Préparer le prompt
        prompt = self._build_analysis_prompt(diff_content)
        
        # Appeler l'API IA
        try:
            if self.api_provider == 'openai':
                return self._call_openai_api(prompt)
            elif self.api_provider == 'anthropic':
                return self._call_anthropic_api(prompt)
        except Exception as e:
            return {
                'label': '⚠️ ERREUR ANALYSE IA',
                'justification': f'Erreur lors de l\'appel à l\'API IA: {str(e)}',
                'confidence': 'LOW',
                'error': True
            }
    
    def _build_analysis_prompt(self, diff_content: str) -> str:
        """
        Construit le prompt pour l'analyse IA
        
        Args:
            diff_content: Contenu du diff
        
        Returns:
            Prompt complet
        """
        # Limiter la taille du diff (max 8000 tokens environ)
        diff_truncated = diff_content[:15000]  # ~8000 tokens
        
        prompt = f"""Tu es un analyseur de code pour EGOEJO, une plateforme fondée sur une double structure économique :
- SAKA (relationnelle, prioritaire) : engagement, don, circulation, anti-accumulation
- EUR (instrumentale, dormante) : finance, wallets, escrow, toujours derrière feature flags

MANIFESTE EGOEJO :
{self.manifesto_summary}

DIFF DE LA PR :
```diff
{diff_truncated}
```

QUESTIONS À ANALYSER :
1. Cette PR transforme-t-elle l'engagement en rendement ? (ex: récompense SAKA basée sur investissement EUR)
2. Introduit-elle une logique d'accumulation ? (ex: désactivation du compostage, stockage permanent)
3. La banque instrumentale contraint-elle le SAKA ? (ex: condition SAKA basée sur ENABLE_INVESTMENT_FEATURES)

RÉPONSE ATTENDUE (JSON strict) :
{{
  "label": "🟢 COMPATIBLE EGOEJO" | "🟡 COMPATIBLE SOUS CONDITIONS" | "🔴 NON COMPATIBLE EGOEJO",
  "justification": "Explication en 3-6 lignes maximum, factuelle, sans marketing",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "risks": ["Liste des risques détectés (optionnel)"]
}}

IMPORTANT :
- Sois factuel, pas marketing
- Détecte les violations IMPLICITES (pas détectées par regex)
- Signale les RISQUES philosophiques
- Justification max 6 lignes
"""
        return prompt
    
    def _call_openai_api(self, prompt: str) -> Dict:
        """
        Appelle l'API OpenAI
        
        Args:
            prompt: Prompt à envoyer
        
        Returns:
            Résultat de l'analyse
        """
        try:
            import requests
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-4o-mini',  # Modèle économique
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Tu es un analyseur de code expert en philosophie logicielle. Réponds UNIQUEMENT en JSON valide.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3,  # Faible température pour plus de cohérence
                'max_tokens': 500
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parser le JSON de la réponse
            return self._parse_ai_response(content)
        
        except ImportError:
            return {
                'label': '⚠️ ERREUR ANALYSE IA',
                'justification': 'Bibliothèque requests non disponible',
                'confidence': 'LOW',
                'error': True
            }
        except Exception as e:
            return {
                'label': '⚠️ ERREUR ANALYSE IA',
                'justification': f'Erreur API OpenAI: {str(e)}',
                'confidence': 'LOW',
                'error': True
            }
    
    def _call_anthropic_api(self, prompt: str) -> Dict:
        """
        Appelle l'API Anthropic (Claude)
        
        Args:
            prompt: Prompt à envoyer
        
        Returns:
            Résultat de l'analyse
        """
        try:
            import requests
            
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'claude-3-haiku-20240307',  # Modèle économique
                'max_tokens': 500,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['content'][0]['text']
            
            # Parser le JSON de la réponse
            return self._parse_ai_response(content)
        
        except ImportError:
            return {
                'label': '⚠️ ERREUR ANALYSE IA',
                'justification': 'Bibliothèque requests non disponible',
                'confidence': 'LOW',
                'error': True
            }
        except Exception as e:
            return {
                'label': '⚠️ ERREUR ANALYSE IA',
                'justification': f'Erreur API Anthropic: {str(e)}',
                'confidence': 'LOW',
                'error': True
            }
    
    def _parse_ai_response(self, content: str) -> Dict:
        """
        Parse la réponse de l'IA (extrait le JSON)
        
        Args:
            content: Contenu de la réponse
        
        Returns:
            Dictionnaire parsé
        """
        try:
            # Chercher le JSON dans la réponse (peut être entouré de markdown)
            import re
            
            # Pattern pour extraire le JSON
            json_match = re.search(r'\{[^{}]*"label"[^{}]*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Valider et normaliser
                label = result.get('label', '⚠️ ANALYSE IA INCOMPLETE')
                justification = result.get('justification', 'Aucune justification fournie')
                confidence = result.get('confidence', 'LOW')
                risks = result.get('risks', [])
                
                return {
                    'label': label,
                    'justification': justification,
                    'confidence': confidence,
                    'risks': risks,
                    'error': False
                }
            else:
                # Fallback : essayer de parser tout le contenu
                result = json.loads(content)
                return {
                    'label': result.get('label', '⚠️ ANALYSE IA INCOMPLETE'),
                    'justification': result.get('justification', 'Aucune justification fournie'),
                    'confidence': result.get('confidence', 'LOW'),
                    'risks': result.get('risks', []),
                    'error': False
                }
        
        except json.JSONDecodeError as e:
            return {
                'label': '⚠️ ERREUR PARSING IA',
                'justification': f'Impossible de parser la réponse IA: {str(e)}',
                'confidence': 'LOW',
                'error': True
            }
    
    def format_comment(self, analysis_result: Dict) -> str:
        """
        Formate le résultat de l'analyse en commentaire PR
        
        Args:
            analysis_result: Résultat de l'analyse IA
        
        Returns:
            Commentaire formaté en Markdown
        """
        comment = "## 🤖 Analyse Sémantique IA - EGOEJO Guardian\n\n"
        comment += "> ⚠️ **DISCLAIMER** : Cette analyse IA est **non souveraine** et **non bloquante**.\n"
        comment += "> Elle complète les règles déterministes (`guardian.py`) et sert à la gouvernance humaine.\n\n"
        
        if analysis_result.get('error'):
            comment += f"### ⚠️ {analysis_result['label']}\n\n"
            comment += f"{analysis_result['justification']}\n\n"
        else:
            comment += f"### {analysis_result['label']}\n\n"
            comment += f"**Justification** :\n{analysis_result['justification']}\n\n"
            comment += f"**Niveau de confiance** : {analysis_result['confidence']}\n\n"
            
            if analysis_result.get('risks'):
                comment += "**Risques détectés** :\n"
                for risk in analysis_result['risks']:
                    comment += f"- {risk}\n"
                comment += "\n"
        
        comment += "---\n\n"
        comment += "**Note** : Cette analyse est complémentaire aux règles déterministes.\n"
        comment += "Seules les violations détectées par `guardian.py` bloquent le merge.\n"
        
        return comment


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EGOEJO Semantic Guardian - Analyse IA')
    parser.add_argument('pr_number', type=int, nargs='?', help='Numéro de la PR (optionnel)')
    parser.add_argument('--output', type=str, help='Fichier de sortie pour le commentaire')
    parser.add_argument('--base-branch', type=str, default='origin/main', help='Branche de référence')
    
    args = parser.parse_args()
    
    # Créer le Semantic Guardian
    guardian = EGOEJOSemanticGuardian()
    
    # Récupérer le diff
    print("Recuperation du diff de la PR...")
    diff_content = guardian.get_pr_diff(args.pr_number, args.base_branch)
    
    if not diff_content:
        print("[ERREUR] Impossible de recuperer le diff")
        sys.exit(1)
    
    # Analyser avec l'IA
    print("Analyse semantique IA en cours...")
    analysis_result = guardian.analyze_with_ai(diff_content)
    
    # Formater le commentaire
    comment = guardian.format_comment(analysis_result)
    
    # Afficher ou sauvegarder
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(comment)
        print(f"Commentaire sauvegarde dans {args.output}")
    else:
        print("\n" + "="*60)
        print(comment)
        print("="*60)
    
    # Ne jamais bloquer (exit 0 toujours)
    sys.exit(0)


if __name__ == "__main__":
    main()

