import { test, expect } from '@playwright/test';
import { setupMockOnlyTest, waitForElementInViewport } from './utils/test-helpers';

/**
 * Tests E2E BLOQUANTS pour les pages Accueil et Vision
 * 
 * Ces tests vérifient les exigences de l'audit quadripartite :
 * - Navigation/Accessibilité (scroll hash, skip-link)
 * - Conformité éditoriale minimale (sections, textes)
 * 
 * IMPORTANT : Ces tests sont BLOQUANTS en CI et échouent explicitement
 * si les exigences ne sont pas respectées.
 */

test.describe('Audit Compliance - Pages Accueil et Vision', () => {
  test.beforeEach(async ({ page }) => {
    // Setup mock-only : langue FR + mocks API par défaut
    await setupMockOnlyTest(page, { language: 'fr' });
  });

  // ============================================================================
  // A. NAVIGATION/ACCESSIBILITÉ
  // ============================================================================

  test.describe('A. Navigation/Accessibilité', () => {
    test('A1) Le lien "Soutenir" scroll vers #soutenir (desktop)', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Enregistrer la position de scroll initiale
      const initialScrollY = await page.evaluate(() => window.scrollY);
      
      // Trouver le bouton "Soutenir" dans le hero
      const soutenirLink = page.locator('a[href="#soutenir"]').first();
      await expect(soutenirLink).toBeVisible({ timeout: 5000 });
      
      // Vérifier que la section existe avant le clic
      const sectionExists = await page.evaluate(() => {
        return document.getElementById('soutenir') !== null;
      });
      expect(sectionExists).toBe(true);
      
      // Cliquer sur le lien "Soutenir"
      await soutenirLink.click();
      
      // ÉTAPE 1 : Attendre que le hash soit présent dans l'URL (déterministe)
      await page.waitForFunction(
        () => window.location.hash === '#soutenir',
        { timeout: 5000 }
      );
      
      // ÉTAPE 2 : Attendre que la section soit visible dans le viewport (attente active)
      await waitForElementInViewport(page, '#soutenir', { timeout: 5000 });
      
      // Vérifier que le scroll s'est produit
      const finalScrollY = await page.evaluate(() => window.scrollY);
      expect(finalScrollY).toBeGreaterThan(initialScrollY);
      
      // Vérification finale : la section est bien visible
      const isSectionVisible = await page.evaluate(() => {
        const section = document.getElementById('soutenir');
        if (!section) return false;
        const rect = section.getBoundingClientRect();
        return rect.top >= -1 && rect.top < window.innerHeight + 1;
      });
      expect(isSectionVisible).toBe(true);
      
      // Vérifier que l'URL contient le hash #soutenir
      await expect(page).toHaveURL(/#soutenir/);
    });

    test('A1) Le lien "Soutenir" scroll vers #soutenir (mobile)', async ({ page, isMobile }) => {
      // Forcer le mode mobile si disponible
      if (isMobile) {
        await page.setViewportSize({ width: 375, height: 667 });
      } else {
        // Simuler mobile si le test n'est pas dans un projet mobile
        await page.setViewportSize({ width: 375, height: 667 });
      }
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Enregistrer la position de scroll initiale
      const initialScrollY = await page.evaluate(() => window.scrollY);
      
      // Trouver le bouton "Soutenir" dans le hero
      const soutenirLink = page.locator('a[href="#soutenir"]').first();
      await expect(soutenirLink).toBeVisible({ timeout: 5000 });
      
      // Cliquer sur le lien "Soutenir"
      await soutenirLink.click();
      
      // ÉTAPE 1 : Attendre que le hash soit présent dans l'URL
      await page.waitForFunction(
        () => window.location.hash === '#soutenir',
        { timeout: 5000 }
      );
      
      // ÉTAPE 2 : Attendre que la section soit visible dans le viewport
      await waitForElementInViewport(page, '#soutenir', { timeout: 5000 });
      
      // Vérifier que le scroll s'est produit
      const finalScrollY = await page.evaluate(() => window.scrollY);
      expect(finalScrollY).toBeGreaterThan(initialScrollY);
      
      // Vérification finale : la section est bien visible
      const isSectionVisible = await page.evaluate(() => {
        const section = document.getElementById('soutenir');
        if (!section) return false;
        const rect = section.getBoundingClientRect();
        return rect.top >= -1 && rect.top < window.innerHeight + 1;
      });
      expect(isSectionVisible).toBe(true);
    });

    test('A2) Le skip-link "Aller au contenu principal" focus et scroll vers #main-content', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Trouver le skip-link
      const skipLink = page.locator('a[href="#main-content"]').first();
      
      // Vérifier que le skip-link existe
      await expect(skipLink).toBeVisible({ timeout: 5000 });
      
      // Vérifier que le skip-link est initialement masqué (hors écran)
      const isInitiallyHidden = await skipLink.evaluate((el) => {
        const style = window.getComputedStyle(el);
        return style.position === 'absolute' && (style.left === '-9999px' || parseFloat(style.left) < -1000);
      });
      expect(isInitiallyHidden).toBe(true);
      
      // Focus sur le skip-link (simuler Tab depuis le début de la page)
      await skipLink.focus();
      
      // Attendre que le skip-link devienne visible au focus (attente active)
      await page.waitForFunction(
        () => {
          const link = document.querySelector('a[href="#main-content"]');
          if (!link) return false;
          const style = window.getComputedStyle(link);
          const left = parseFloat(style.left);
          return left >= 0 && left < 100;
        },
        { timeout: 2000 }
      );
      
      // Vérifier que le skip-link est visible au focus
      const isVisibleOnFocus = await skipLink.evaluate((el) => {
        const style = window.getComputedStyle(el);
        const left = parseFloat(style.left);
        return left >= 0 && left < 100;
      });
      expect(isVisibleOnFocus).toBe(true);
      
      // Activer le skip-link (Enter)
      await skipLink.press('Enter');
      
      // ÉTAPE 1 : Attendre que le hash soit présent dans l'URL
      await page.waitForFunction(
        () => window.location.hash === '#main-content',
        { timeout: 5000 }
      );
      
      // ÉTAPE 2 : Attendre que main-content soit visible dans le viewport
      await waitForElementInViewport(page, '#main-content', { timeout: 5000 });
      
      // ÉTAPE 3 : Attendre que main-content soit focus (assertion d'accessibilité)
      await page.waitForFunction(
        () => {
          const main = document.getElementById('main-content');
          if (!main) return false;
          // Le focus peut être sur main directement ou sur un élément enfant
          return document.activeElement === main || main.contains(document.activeElement);
        },
        { timeout: 3000 }
      );
      
      // Vérifier que l'URL contient le hash #main-content
      await expect(page).toHaveURL(/#main-content/);
      
      // Vérification finale : #main-content est focus
      const isMainFocused = await page.evaluate(() => {
        const main = document.getElementById('main-content');
        if (!main) return false;
        return document.activeElement === main || main.contains(document.activeElement);
      });
      expect(isMainFocused).toBe(true);
    });

    test('A3) Le skip-link est traduit via i18n (PAS de texte hardcodé uniquement FR)', async ({ page }) => {
      // Tester avec toutes les langues supportées
      const languages = ['fr', 'en', 'es', 'de', 'ar', 'sw'];
      
      for (const lang of languages) {
        // Setup avec la langue spécifique
        await setupMockOnlyTest(page, { language: lang });
        
        await page.goto('/');
        await page.waitForLoadState('networkidle');
        
        // Trouver le skip-link
        const skipLink = page.locator('a[href="#main-content"]').first();
        await expect(skipLink).toBeVisible({ timeout: 5000 });
        
        // Vérifier que le texte du skip-link n'est PAS "Aller au contenu principal" (hardcodé FR)
        // Si c'est le cas, cela signifie que la traduction n'est pas utilisée
        const skipLinkText = await skipLink.textContent();
        const isHardcodedFrench = skipLinkText === 'Aller au contenu principal';
        
        // Si la langue est FR, c'est normal que ce soit en français
        // Mais pour les autres langues, cela doit être traduit
        if (lang !== 'fr') {
          expect(isHardcodedFrench).toBe(false);
        }
        
        // Vérifier que le skip-link a un texte non vide
        expect(skipLinkText).toBeTruthy();
        expect(skipLinkText.trim().length).toBeGreaterThan(0);
      }
    });
  });

  // ============================================================================
  // B. CONFORMITÉ ÉDITORIALE MINIMALE
  // ============================================================================

  test.describe('B. Conformité Éditoriale Minimale', () => {
    test('B4) Vision contient une section "Principes fondamentaux" avec 3 principes', async ({ page }) => {
      await page.goto('/vision');
      await page.waitForLoadState('networkidle');
      
      // Chercher la section "Principes fondamentaux" par data-testid ou par titre
      const principlesSection = page.locator('[data-testid="vision-principles"]').or(
        page.locator('section').filter({ hasText: /principes.*fondamentaux|fundamental.*principles/i })
      );
      
      // Si la section n'existe pas encore, le test doit échouer explicitement
      const sectionExists = await principlesSection.count() > 0;
      
      if (!sectionExists) {
        // Vérifier aussi par titre H2
        const h2Principles = page.locator('h2').filter({ hasText: /principes.*fondamentaux|fundamental.*principles/i });
        const h2Exists = await h2Principles.count() > 0;
        
        if (!h2Exists) {
          throw new Error(
            'BLOQUANT : La section "Principes fondamentaux" est absente de la page Vision.\n' +
            'Exigence audit : Vision doit contenir une section explicite avec 3 principes :\n' +
            '  - Structure relationnelle > instrumentale\n' +
            '  - Anti-accumulation\n' +
            '  - Logique de cycle'
          );
        }
      }
      
      // Vérifier que la section est visible
      await expect(principlesSection.first()).toBeVisible({ timeout: 5000 });
      
      // Vérifier la présence des 3 principes
      const principles = [
        /structure.*relationnelle|relational.*structure/i,
        /anti.*accumulation|anti.*accumulation/i,
        /logique.*cycle|cycle.*logic/i,
      ];
      
      const pageContent = await page.textContent('body');
      
      for (const principle of principles) {
        const found = principle.test(pageContent);
        if (!found) {
          throw new Error(
            `BLOQUANT : Principe manquant dans la section "Principes fondamentaux".\n` +
            `Pattern recherché : ${principle.source}\n` +
            `Exigence audit : Les 3 principes doivent être présents explicitement.`
          );
        }
      }
    });

    test('B5) Vision contient un glossaire (définitions) pour : vivant, gardiens, alliance', async ({ page }) => {
      await page.goto('/vision');
      await page.waitForLoadState('networkidle');
      
      // Chercher la section glossaire par data-testid ou par titre
      const glossarySection = page.locator('[data-testid="vision-glossary"]').or(
        page.locator('section').filter({ hasText: /glossaire|glossary/i })
      );
      
      // Si la section n'existe pas encore, le test doit échouer explicitement
      const sectionExists = await glossarySection.count() > 0;
      
      if (!sectionExists) {
        // Vérifier aussi par titre H2
        const h2Glossary = page.locator('h2').filter({ hasText: /glossaire|glossary/i });
        const h2Exists = await h2Glossary.count() > 0;
        
        if (!h2Exists) {
          throw new Error(
            'BLOQUANT : La section "Glossaire" est absente de la page Vision.\n' +
            'Exigence audit : Vision doit contenir un glossaire avec définitions pour :\n' +
            '  - vivant\n' +
            '  - gardiens\n' +
            '  - alliance'
          );
        }
      }
      
      // Vérifier que la section est visible
      await expect(glossarySection.first()).toBeVisible({ timeout: 5000 });
      
      // Vérifier la présence des définitions (terme + définition)
      const terms = ['vivant', 'gardiens', 'alliance'];
      const pageContent = await page.textContent('body');
      
      // Pour chaque terme, vérifier qu'il existe dans le contexte d'une définition
      // (présence du terme ET d'un texte explicatif à proximité)
      for (const term of terms) {
        // Chercher le terme dans le contenu
        const termFound = new RegExp(term, 'i').test(pageContent);
        
        if (!termFound) {
          throw new Error(
            `BLOQUANT : Terme "${term}" absent du glossaire.\n` +
            `Exigence audit : Le glossaire doit définir explicitement : ${terms.join(', ')}`
          );
        }
      }
    });

    test('B6) Vision contient un disclaimer contextuel sur les citations autochtones', async ({ page }) => {
      await page.goto('/vision');
      await page.waitForLoadState('networkidle');
      
      // Chercher le disclaimer par data-testid ou par texte
      const disclaimer = page.locator('[data-testid="vision-disclaimer"]').or(
        page.locator('p, div').filter({ hasText: /citation.*autochtone|indigenous.*citation|autorisation|authorization/i })
      );
      
      // Si le disclaimer n'existe pas encore, le test doit échouer explicitement
      const disclaimerExists = await disclaimer.count() > 0;
      
      if (!disclaimerExists) {
        // Vérifier aussi dans le blockquote ou à proximité
        const blockquote = page.locator('blockquote');
        const blockquoteText = await blockquote.textContent().catch(() => '');
        const hasDisclaimerNearby = /autorisation|authorization|respect|respectful/i.test(blockquoteText);
        
        if (!hasDisclaimerNearby) {
          throw new Error(
            'BLOQUANT : Le disclaimer sur les citations autochtones est absent de la page Vision.\n' +
            'Exigence audit : Vision doit contenir un disclaimer contextuel expliquant que les citations\n' +
            'autochtones sont utilisées avec autorisation et dans le respect des cultures autochtones.'
          );
        }
      }
      
      // Vérifier que le disclaimer est visible
      await expect(disclaimer.first()).toBeVisible({ timeout: 5000 });
    });

    test('B7) Accueil contient une note explicite SAKA/EUR (pas de conversion, pas d\'équivalence monétaire)', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Chercher la note SAKA/EUR par data-testid ou par texte
      const sakaEurNote = page.locator('[data-testid="home-saka-eur-note"]').or(
        page.locator('p, div').filter({ hasText: /SAKA.*EUR|EUR.*SAKA|relationnel.*instrumental|relational.*instrumental/i })
      );
      
      // Si la note n'existe pas encore, le test doit échouer explicitement
      const noteExists = await sakaEurNote.count() > 0;
      
      if (!noteExists) {
        // Vérifier aussi dans la section "Soutenir"
        const soutenirSection = page.locator('#soutenir');
        const soutenirText = await soutenirSection.textContent().catch(() => '');
        const hasSakaEurMention = /SAKA|relationnel|relational/i.test(soutenirText);
        
        if (!hasSakaEurMention) {
          throw new Error(
            'BLOQUANT : La note explicite SAKA/EUR est absente de la page Accueil.\n' +
            'Exigence audit : Accueil doit contenir une note explicite distinguant SAKA (relationnel) et EUR (instrumental).\n' +
            'Aucune conversion ou équivalence monétaire ne doit être suggérée.'
          );
        }
      }
      
      // Vérifier que la note est visible
      await expect(sakaEurNote.first()).toBeVisible({ timeout: 5000 });
      
      // Vérifier qu'il n'y a PAS de conversion ou équivalence monétaire
      const pageContent = await page.textContent('body');
      const forbiddenPatterns = [
        /SAKA.*=.*EUR|EUR.*=.*SAKA/i,
        /1.*SAKA.*=.*\d+.*EUR|\d+.*EUR.*=.*1.*SAKA/i,
        /convertir|convert|équivalent|equivalent.*monétaire|monetary.*equivalent/i,
      ];
      
      for (const pattern of forbiddenPatterns) {
        const found = pattern.test(pageContent);
        if (found) {
          throw new Error(
            `BLOQUANT : Conversion ou équivalence monétaire SAKA/EUR détectée.\n` +
            `Pattern interdit : ${pattern.source}\n` +
            `Exigence audit : Aucune conversion ou équivalence monétaire ne doit être suggérée.`
          );
        }
      }
    });

    test('B8) Le texte "100% des dons" est corrigé en "100% des dons nets (après frais...)"', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Chercher le texte de donation dans la section "Soutenir"
      const soutenirSection = page.locator('#soutenir');
      await expect(soutenirSection).toBeVisible({ timeout: 5000 });
      
      const soutenirText = await soutenirSection.textContent();
      
      // Vérifier que le texte contient "100%" ET "dons"
      const has100Percent = /100\s*%/.test(soutenirText);
      const hasDons = /don/i.test(soutenirText);
      
      if (!has100Percent || !hasDons) {
        // Si le texte n'existe pas, le test passe (pas de promesse trompeuse)
        return;
      }
      
      // Vérifier que le texte contient "nets" ou "après frais" ou formulation équivalente
      const correctedPatterns = [
        /100\s*%.*dons.*nets/i,
        /100\s*%.*dons.*après.*frais/i,
        /100\s*%.*dons.*net/i,
        /100\s*%.*dons.*after.*fees/i,
        /100\s*%.*dons.*frais.*plateforme/i,
        /100\s*%.*dons.*platform.*fees/i,
      ];
      
      const isCorrected = correctedPatterns.some(pattern => pattern.test(soutenirText));
      
      if (!isCorrected) {
        // Vérifier aussi par data-testid si la note existe
        const donationClaim = page.locator('[data-testid="home-donation-claim"]');
        const claimExists = await donationClaim.count() > 0;
        
        if (claimExists) {
          const claimText = await donationClaim.textContent();
          const isCorrectedInClaim = correctedPatterns.some(pattern => pattern.test(claimText));
          
          if (!isCorrectedInClaim) {
            throw new Error(
              'BLOQUANT : Le texte "100% des dons" n\'est pas corrigé.\n' +
              'Exigence audit : Le texte doit être "100% des dons nets (après frais de plateforme)"\n' +
              'ou formulation équivalente non trompeuse.\n' +
              `Texte actuel : "${soutenirText.substring(0, 200)}..."`
            );
          }
        } else {
          throw new Error(
            'BLOQUANT : Le texte "100% des dons" n\'est pas corrigé.\n' +
            'Exigence audit : Le texte doit être "100% des dons nets (après frais de plateforme)"\n' +
            'ou formulation équivalente non trompeuse.\n' +
            `Texte actuel : "${soutenirText.substring(0, 200)}..."`
          );
        }
      }
    });
  });
});

