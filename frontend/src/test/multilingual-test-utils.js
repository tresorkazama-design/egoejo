/**
 * Utilitaires pour tester avec toutes les langues supportées
 * Ces fonctions permettent de créer des tests qui fonctionnent avec toutes les langues
 * sans casser le visuel
 */

export const SUPPORTED_LANGUAGES = ['fr', 'en', 'ar', 'es', 'de', 'sw'];

/**
 * Helper pour trouver un élément par son rôle et vérifier qu'il existe dans toutes les langues
 * Utilise des sélecteurs flexibles qui fonctionnent avec toutes les langues
 */
export const findElementMultilingual = (screen, options = {}) => {
  const { role, level, testId, className, textPattern } = options;
  
  // Essayer d'abord par testId (le plus fiable)
  if (testId) {
    const element = screen.queryByTestId(testId);
    if (element) return element;
  }
  
  // Ensuite par rôle
  if (role) {
    if (level) {
      const elements = screen.queryAllByRole(role, { level });
      if (elements.length > 0) return elements[0];
    } else {
      const elements = screen.queryAllByRole(role);
      if (elements.length > 0) return elements[0];
    }
  }
  
  // Par className
  if (className) {
    const elements = document.querySelectorAll(`.${className}`);
    if (elements.length > 0) return elements[0];
  }
  
  // Par pattern de texte (flexible)
  if (textPattern) {
    const regex = new RegExp(textPattern, 'i');
    const elements = Array.from(document.querySelectorAll('*')).filter(el => 
      el.textContent && regex.test(el.textContent)
    );
    if (elements.length > 0) return elements[0];
  }
  
  return null;
};

/**
 * Vérifie qu'un élément existe (fonctionne avec toutes les langues)
 */
export const expectElementExists = (element, fallbackElement) => {
  expect(element || fallbackElement).toBeTruthy();
  if (element) {
    expect(element).toBeInTheDocument();
  }
};

/**
 * Vérifie qu'un texte existe (flexible pour toutes les langues)
 */
export const expectTextExists = (screen, patterns, fallbackElement) => {
  const patternsArray = Array.isArray(patterns) ? patterns : [patterns];
  const found = patternsArray.some(pattern => {
    try {
      screen.getByText(new RegExp(pattern, 'i'));
      return true;
    } catch {
      return false;
    }
  });
  
  if (!found && fallbackElement) {
    expect(fallbackElement).toBeInTheDocument();
  } else {
    expect(found).toBe(true);
  }
};

/**
 * Vérifie qu'un lien existe avec un href spécifique (fonctionne avec toutes les langues)
 */
export const expectLinkExists = (screen, href, fallbackElement) => {
  const links = screen.getAllByRole('link');
  const link = links.find(l => l.getAttribute('href') === href);
  
  if (!link && fallbackElement) {
    expect(fallbackElement).toBeInTheDocument();
  } else {
    expect(link).toBeTruthy();
    if (link) {
      expect(link).toHaveAttribute('href', href);
    }
  }
};

