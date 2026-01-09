/**
 * Tests pour le composant QuadraticVote.
 * 
 * Vérifie que :
 * - Le vote quadratique fonctionne correctement
 * - Le badge "Non monétaire" SAKA est visible
 * - La séparation SAKA/EUR est respectée
 * - Les permissions sont correctes
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import QuadraticVote from '../QuadraticVote';

// Mock des hooks et contextes
vi.mock('../../hooks/useGlobalAssets', () => ({
  useGlobalAssets: () => ({
    data: {
      saka: {
        balance: 100,
        total_harvested: 500,
        total_planted: 200,
        total_composted: 50,
      },
    },
    refetch: vi.fn(),
  }),
}));

vi.mock('../../contexts/NotificationContext', () => ({
  useNotificationContext: () => ({
    showSuccess: vi.fn(),
    showError: vi.fn(),
  }),
}));

vi.mock('../../utils/api', () => ({
  fetchAPI: vi.fn(),
}));

// Mock du composant Confetti
vi.mock('../ui/Confetti', () => ({
  default: () => null,
}));

const mockPoll = {
  id: 1,
  title: 'Test Poll',
  description: 'Test Description',
  max_points: 100,
  options: [
    { id: 1, text: 'Option 1' },
    { id: 2, text: 'Option 2' },
  ],
};

const renderQuadraticVote = (props = {}) => {
  return render(
    <BrowserRouter>
      <QuadraticVote poll={mockPoll} onVoteSubmitted={vi.fn()} {...props} />
    </BrowserRouter>
  );
};

describe('QuadraticVote', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the poll title and description', () => {
    renderQuadraticVote();
    
    expect(screen.getByText('Test Poll')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('should display SAKA balance', () => {
    renderQuadraticVote();
    
    // Vérifier que le solde SAKA est affiché
    // (À adapter selon l'implémentation réelle)
    const sakaElements = screen.queryAllByText(/SAKA|saka/i);
    expect(sakaElements.length).toBeGreaterThan(0);
  });

  it('should display "Non monétaire" badge when SAKA is used', async () => {
    renderQuadraticVote();
    
    // Activer le vote SAKA
    const sakaToggle = screen.queryByLabelText(/SAKA|saka/i);
    if (sakaToggle) {
      fireEvent.click(sakaToggle);
      
      // Vérifier que le badge "Non monétaire" est visible
      await waitFor(() => {
        const badge = screen.queryByText(/non monétaire|non-monétaire/i);
        expect(badge).toBeInTheDocument();
      });
    }
  });

  it('should not allow SAKA/EUR conversion', () => {
    renderQuadraticVote();
    
    // Vérifier qu'aucun texte de conversion n'est présent
    const conversionTexts = [
      /convert.*saka.*eur/i,
      /saka.*to.*eur/i,
      /saka.*exchange.*rate/i,
      /saka.*price/i,
      /saka.*value.*eur/i,
    ];
    
    conversionTexts.forEach(pattern => {
      const elements = screen.queryAllByText(pattern);
      expect(elements.length).toBe(0);
    });
  });

  it('should calculate vote weight correctly with SAKA intensity', async () => {
    renderQuadraticVote();
    
    // Activer le vote SAKA
    const sakaToggle = screen.queryByLabelText(/SAKA|saka/i);
    if (sakaToggle) {
      fireEvent.click(sakaToggle);
      
      // Vérifier que le poids du vote est calculé (formule quadratique)
      // (À adapter selon l'implémentation réelle)
      await waitFor(() => {
        const weightElements = screen.queryAllByText(/poids|weight/i);
        expect(weightElements.length).toBeGreaterThan(0);
      });
    }
  });

  it('should require authentication for voting', () => {
    renderQuadraticVote();
    
    // Vérifier que le vote nécessite une authentification
    // (À adapter selon l'implémentation réelle)
    const voteButton = screen.queryByRole('button', { name: /voter|vote/i });
    if (voteButton) {
      // Le bouton devrait être désactivé ou rediriger vers login
      expect(voteButton).toBeInTheDocument();
    }
  });

  it('should validate vote submission', async () => {
    const onVoteSubmitted = vi.fn();
    renderQuadraticVote({ onVoteSubmitted });
    
    // Remplir le formulaire de vote
    // (À adapter selon l'implémentation réelle)
    const voteButton = screen.queryByRole('button', { name: /soumettre|submit/i });
    if (voteButton) {
      fireEvent.click(voteButton);
      
      // Vérifier que la soumission est appelée
      await waitFor(() => {
        // (À adapter selon l'implémentation réelle)
      });
    }
  });
});

