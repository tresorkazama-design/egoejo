import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import SakaSeasonsPage from "../SakaSeasons";

// Mock des hooks pour éviter les problèmes d'authentification
const mockUseSakaCycles = vi.fn();
const mockUseSakaSilo = vi.fn();

vi.mock("@/hooks/useSakaCycles", () => ({
  useSakaCycles: mockUseSakaCycles,
}));

vi.mock("@/hooks/useSakaSilo", () => ({
  useSakaSilo: mockUseSakaSilo,
}));

describe("SakaSeasonsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le niveau du Silo commun et les cycles SAKA", async () => {
    // Mock des données du Silo
    mockUseSakaSilo.mockReturnValue({
      silo: {
        total_balance: 1234,
        last_compost_at: "2025-12-16T10:00:00Z",
      },
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    // Mock des données des cycles
    mockUseSakaCycles.mockReturnValue({
      cycles: [
        {
          id: 1,
          name: "Cycle Automne 2025",
          start_date: "2025-09-01",
          end_date: "2025-11-30",
          is_active: false,
          stats: {
            saka_harvested: 500,
            saka_planted: 300,
            saka_composted: 50,
          },
        },
      ],
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<SakaSeasonsPage />);

    // Titre principal
    expect(screen.getByText(/Saisons SAKA/i)).toBeInTheDocument();

    // Silo commun
    expect(screen.getByText(/Silo commun/i)).toBeInTheDocument();

    // Vérifie que le total apparaît bien formaté (format français: 1 234)
    await waitFor(() => {
      expect(screen.getByText(/1 234 grains/i)).toBeInTheDocument();
    });

    // Cycle
    expect(screen.getByText(/Cycle Automne 2025/i)).toBeInTheDocument();

    // Vérifie les valeurs des stats du cycle
    expect(screen.getByText(/500 grains/i)).toBeInTheDocument();
    expect(screen.getByText(/300 grains/i)).toBeInTheDocument();
    expect(screen.getByText(/50 grains/i)).toBeInTheDocument();
  });

  it("affiche un message de chargement pour le Silo", () => {
    mockUseSakaSilo.mockReturnValue({
      silo: null,
      loading: true,
      error: null,
      refetch: vi.fn(),
    });

    mockUseSakaCycles.mockReturnValue({
      cycles: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<SakaSeasonsPage />);

    expect(screen.getByText(/Chargement du niveau du Silo/i)).toBeInTheDocument();
  });

  it("affiche un message d'erreur si le chargement du Silo échoue", () => {
    mockUseSakaSilo.mockReturnValue({
      silo: null,
      loading: false,
      error: "Erreur de chargement",
      refetch: vi.fn(),
    });

    mockUseSakaCycles.mockReturnValue({
      cycles: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<SakaSeasonsPage />);

    expect(screen.getByText(/Erreur de chargement/i)).toBeInTheDocument();
  });

  it("affiche un message quand aucun cycle n'est disponible", () => {
    mockUseSakaSilo.mockReturnValue({
      silo: {
        total_balance: 0,
        last_compost_at: null,
      },
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    mockUseSakaCycles.mockReturnValue({
      cycles: [],
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<SakaSeasonsPage />);

    expect(
      screen.getByText(/Aucun cycle SAKA n'a encore été enregistré/i)
    ).toBeInTheDocument();
  });

  it("affiche le badge 'Actif' pour un cycle actif", () => {
    mockUseSakaSilo.mockReturnValue({
      silo: {
        total_balance: 1000,
        last_compost_at: "2025-12-16T10:00:00Z",
      },
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    mockUseSakaCycles.mockReturnValue({
      cycles: [
        {
          id: 1,
          name: "Cycle Hiver 2025",
          start_date: "2025-12-01",
          end_date: "2026-02-28",
          is_active: true,
          stats: {
            saka_harvested: 200,
            saka_planted: 150,
            saka_composted: 10,
          },
        },
      ],
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<SakaSeasonsPage />);

    expect(screen.getByText(/Actif/i)).toBeInTheDocument();
  });
});

