import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

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
  const module = await import("../../src/pages/Rejoindre.jsx");
  RejoindreComponent = module.default;
});

vi.mock("../../src/config/api.js", () => ({
  api: {
    rejoindre: () => "/api/intents/rejoindre/",
  },
}));

describe("Rejoindre", () => {
  beforeEach(() => {
    global.fetch = vi.fn();

    window.matchMedia = window.matchMedia || function () {
      return {
        matches: false,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      };
    };
  });

  it("renders the form correctly", () => {
    render(<RejoindreComponent />);
    expect(screen.getByText("Rejoindre EGOEJO")).toBeInTheDocument();
    expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/profil/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
  });

  it("shows error when required fields are missing", async () => {
    const user = userEvent.setup();
    render(<RejoindreComponent />);

    const form = document.querySelector("form");
    if (form) form.setAttribute("novalidate", "true");

    const submitButton = screen.getByRole("button", { name: /envoyer/i });
    await user.click(submitButton);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/le nom est requis/i);
  });

  it("shows error when email is invalid", async () => {
    const user = userEvent.setup();
    render(<RejoindreComponent />);

    const form = document.querySelector("form");
    if (form) form.setAttribute("novalidate", "true");

    const nomInput = screen.getByLabelText(/nom/i);
    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole("button", { name: /envoyer/i });

    await user.type(nomInput, "Test User");
    await user.type(emailInput, "invalid-email");
    await user.click(submitButton);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/l'email n'est pas valide/i);
  });

  it("submits form successfully", async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        id: 1,
        created_at: "2025-01-27T10:00:00Z",
      }),
    });

    render(<RejoindreComponent />);

    const form = document.querySelector("form");
    if (form) form.setAttribute("novalidate", "true");

    const nomInput = screen.getByLabelText(/nom/i);
    const emailInput = screen.getByLabelText(/email/i);
    const profilSelect = screen.getByLabelText(/profil/i);
    const submitButton = screen.getByRole("button", { name: /envoyer/i });

    await user.type(nomInput, "Test User");
    await user.type(emailInput, "test@example.com");
    await user.selectOptions(profilSelect, "je-decouvre");
    await user.click(submitButton);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/merci/i);

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/intents/rejoindre/",
      expect.objectContaining({
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })
    );
  });

  it("shows error when submission fails", async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ ok: false, error: "Erreur serveur" }),
    });

    render(<RejoindreComponent />);

    const form = document.querySelector("form");
    if (form) form.setAttribute("novalidate", "true");

    const nomInput = screen.getByLabelText(/nom/i);
    const emailInput = screen.getByLabelText(/email/i);
    const profilSelect = screen.getByLabelText(/profil/i);
    const submitButton = screen.getByRole("button", { name: /envoyer/i });

    await user.type(nomInput, "Test User");
    await user.type(emailInput, "test@example.com");
    await user.selectOptions(profilSelect, "je-decouvre");
    await user.click(submitButton);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/erreur serveur/i);
  });
});
