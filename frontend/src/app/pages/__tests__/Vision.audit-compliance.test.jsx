import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../../test/test-utils';
import Vision from '../Vision';

describe('Vision - Audit Compliance (BLOQUANTS)', () => {
  describe('B4) Section "Principes fondamentaux" avec 3 principes', () => {
    it('devrait contenir une section "Principes fondamentaux" explicite', () => {
      const { container } = renderWithProviders(<Vision />);
      
      // Chercher par data-testid
      const principlesSection = container.querySelector('[data-testid="vision-principles"]');
      
      if (!principlesSection) {
        // Chercher par titre H2
        const h2Principles = Array.from(container.querySelectorAll('h2')).find(h2 => 
          /principes.*fondamentaux|fundamental.*principles/i.test(h2.textContent || '')
        );
        
        if (!h2Principles) {
          throw new Error(
            'BLOQUANT : La section "Principes fondamentaux" est absente de la page Vision.\n' +
            'Exigence audit : Vision doit contenir une section explicite avec 3 principes :\n' +
            '  - Structure relationnelle > instrumentale\n' +
            '  - Anti-accumulation\n' +
            '  - Logique de cycle\n' +
            'Ajouter data-testid="vision-principles" ou un H2 avec le titre "Principes fondamentaux".'
          );
        }
      }
      
      // Vérifier que la section est visible
      expect(principlesSection || container.querySelector('h2')).toBeTruthy();
    });

    it('devrait contenir les 3 principes : Structure relationnelle > instrumentale, Anti-accumulation, Logique de cycle', () => {
      const { container } = renderWithProviders(<Vision />);
      const pageContent = container.textContent || '';
      
      const principles = [
        {
          name: 'Structure relationnelle > instrumentale',
          patterns: [
            /structure.*relationnelle.*instrumentale|relational.*structure.*instrumental/i,
            /relationnel.*>.*instrumental|relational.*>.*instrumental/i,
            /SAKA.*relationnel|relational.*SAKA/i,
          ],
        },
        {
          name: 'Anti-accumulation',
          patterns: [
            /anti.*accumulation|anti.*accumulation/i,
            /pas.*accumulation|no.*accumulation/i,
            /refus.*accumulation|refuse.*accumulation/i,
          ],
        },
        {
          name: 'Logique de cycle',
          patterns: [
            /logique.*cycle|cycle.*logic/i,
            /cycle.*régénératif|regenerative.*cycle/i,
            /compostage|composting/i,
          ],
        },
      ];
      
      for (const principle of principles) {
        const found = principle.patterns.some(pattern => pattern.test(pageContent));
        
        if (!found) {
          throw new Error(
            `BLOQUANT : Principe "${principle.name}" manquant dans la section "Principes fondamentaux".\n` +
            `Exigence audit : Les 3 principes doivent être présents explicitement :\n` +
            `  - Structure relationnelle > instrumentale\n` +
            `  - Anti-accumulation\n` +
            `  - Logique de cycle`
          );
        }
      }
    });
  });

  describe('B5) Glossaire (définitions) pour : vivant, gardiens, alliance', () => {
    it('devrait contenir une section "Glossaire" explicite', () => {
      const { container } = renderWithProviders(<Vision />);
      
      // Chercher par data-testid
      const glossarySection = container.querySelector('[data-testid="vision-glossary"]');
      
      if (!glossarySection) {
        // Chercher par titre H2
        const h2Glossary = Array.from(container.querySelectorAll('h2')).find(h2 => 
          /glossaire|glossary/i.test(h2.textContent || '')
        );
        
        if (!h2Glossary) {
          throw new Error(
            'BLOQUANT : La section "Glossaire" est absente de la page Vision.\n' +
            'Exigence audit : Vision doit contenir un glossaire avec définitions pour :\n' +
            '  - vivant\n' +
            '  - gardiens\n' +
            '  - alliance\n' +
            'Ajouter data-testid="vision-glossary" ou un H2 avec le titre "Glossaire".'
          );
        }
      }
      
      // Vérifier que la section est visible
      expect(glossarySection || container.querySelector('h2')).toBeTruthy();
    });

    it('devrait contenir des définitions pour : vivant, gardiens, alliance', () => {
      const { container } = renderWithProviders(<Vision />);
      const pageContent = container.textContent || '';
      
      const terms = [
        {
          name: 'vivant',
          patterns: [/vivant|living|vivo|lebend/i],
        },
        {
          name: 'gardiens',
          patterns: [/gardiens|guardians|guardianes/i],
        },
        {
          name: 'alliance',
          patterns: [/alliance|alliances/i],
        },
      ];
      
      for (const term of terms) {
        const found = term.patterns.some(pattern => pattern.test(pageContent));
        
        if (!found) {
          throw new Error(
            `BLOQUANT : Terme "${term.name}" absent du glossaire.\n` +
            `Exigence audit : Le glossaire doit définir explicitement : vivant, gardiens, alliance.`
          );
        }
      }
    });
  });

  describe('B6) Disclaimer contextuel sur les citations autochtones', () => {
    it('devrait contenir un disclaimer contextuel sur les citations autochtones', () => {
      const { container } = renderWithProviders(<Vision />);
      
      // Chercher par data-testid
      const disclaimer = container.querySelector('[data-testid="vision-disclaimer"]');
      
      if (!disclaimer) {
        // Chercher par texte dans le blockquote ou à proximité
        const blockquote = container.querySelector('blockquote');
        if (blockquote) {
          const blockquoteText = blockquote.textContent || '';
          const hasDisclaimerNearby = /autorisation|authorization|respect|respectful|autochtone|indigenous/i.test(blockquoteText);
          
          if (!hasDisclaimerNearby) {
            // Chercher dans tout le contenu
            const pageContent = container.textContent || '';
            const hasDisclaimerInPage = /autorisation.*citation|authorization.*citation|respect.*culture|respectful.*culture/i.test(pageContent);
            
            if (!hasDisclaimerInPage) {
              throw new Error(
                'BLOQUANT : Le disclaimer sur les citations autochtones est absent de la page Vision.\n' +
                'Exigence audit : Vision doit contenir un disclaimer contextuel expliquant que les citations\n' +
                'autochtones sont utilisées avec autorisation et dans le respect des cultures autochtones.\n' +
                'Ajouter data-testid="vision-disclaimer" ou inclure le texte dans la section des citations.'
              );
            }
          }
        } else {
          throw new Error(
            'BLOQUANT : Le blockquote des citations est absent, impossible de vérifier le disclaimer.'
          );
        }
      }
      
      // Vérifier que le disclaimer est visible
      expect(disclaimer || container.querySelector('blockquote')).toBeTruthy();
    });
  });
});

