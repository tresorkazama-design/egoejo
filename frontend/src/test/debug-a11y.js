import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import { Home } from '../app/pages/Home';
import { renderWithProviders } from './test-utils';

async function debugA11y() {
  const { container } = renderWithProviders(<Home />);
  const results = await axe(container);
  
  if (results.violations.length > 0) {
    console.log('\n=== VIOLATIONS D\'ACCESSIBILITÉ ===\n');
    results.violations.forEach((violation, index) => {
      console.log(`${index + 1}. ${violation.id} (${violation.impact}):`);
      console.log(`   ${violation.description}`);
      console.log(`   Aide: ${violation.help}`);
      console.log(`   Éléments affectés: ${violation.nodes.length}`);
      violation.nodes.forEach((node, nodeIndex) => {
        console.log(`   - ${nodeIndex + 1}. ${node.html}`);
      });
      console.log('');
    });
  } else {
    console.log('✅ Aucune violation d\'accessibilité !');
  }
}

debugA11y().catch(console.error);

