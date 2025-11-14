import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Polyfills jsdom pour GSAP + validation native
if (!globalThis.window) {
  globalThis.window = globalThis;
}
if (!window.matchMedia) {
  window.matchMedia = () => ({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  });
}

let RejoindreComponent;

beforeAll(async () => {
  await import("../../src/utils/gsap-extras.js");
  const module = await import("../../src/pages/Rejoindre.jsx");
  RejoindreComponent = module.default;
});

// Mock API
vi.mock("../../src/config/api.js", () => ({
  api: {
    rejoindre: () => "/api/intents/rejoindre/",
  },
}));

describe("Rejoindre", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    window.matchMedia = window.matchMedia || (() => ({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));
    HTMLFormElement.prototype.checkValidity = vi.fn(() => true);
    HTMLFormElement.prototype.reportValidity = vi.fn(() => true);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    delete HTMLFormElement.prototype.checkValidity;
    delete HTMLFormElement.prototype.reportValidity;
  });

  it("affiche le formulaire correctement", () => {
    render(<RejoindreComponent />);
    expect(screen.getByText("Rejoindre EGOEJO")).toBeInTheDocument();
    expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/profil/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
  });

  it("affiche une erreur si les champs requis manquent", async () => {
    const user = userEvent.setup();
    render(<RejoindreComponent />);

    const submitButton = screen.getByRole("button", { name: /envoyer/i });
    await user.click(submitButton);

    const alert = await screen.findByTestId("intent-error");
    expect(alert).toHaveTextContent(/le nom est requis/i);
  });

  it("affiche une erreur si l'email est invalide", async () => {
    const user = userEvent.setup();
    render(<RejoindreComponent />);

    await user.type(screen.getByLabelText(/nom/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "invalid-email");

    const submitButton = screen.getByRole("button", { name: /envoyer/i });
    await user.click(submitButton);

    const alert = await screen.findByTestId("intent-error");
    expect(alert).toHaveTextContent(/l'email n'est pas valide/i);
  });

  it("soumet le formulaire avec succès", async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ok: true, id: 1, created_at: "2025-01-27T10:00:00Z" }),
    });

    render(<RejoindreComponent />);

    await user.type(screen.getByLabelText(/nom/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.selectOptions(screen.getByLabelText(/profil/i), "je-decouvre");

    const submitButton = screen.getByRole("button", { name: /envoyer/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/merci/i)).toBeInTheDocument();
    });

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/intents/rejoindre/",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );
  });

  it("affiche une erreur quand l'envoi échoue", async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ ok: false, error: "Erreur serveur" }),
    });

    render(<RejoindreComponent />);

    await user.type(screen.getByLabelText(/nom/i), "Test User");
    await user.type(screen.getByLabelText(/email/i), "test@example.com");
    await user.selectOptions(screen.getByLabelText(/profil/i), "je-decouvre");

    const submitButton = screen.getByRole("button", { name: /envoyer/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/erreur serveur/i)).toBeInTheDocument();
    });
  });
});