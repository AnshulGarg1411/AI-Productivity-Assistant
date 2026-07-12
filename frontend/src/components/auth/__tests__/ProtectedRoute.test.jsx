import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "../ProtectedRoute";
import * as AuthContext from "../../../contexts/AuthContext";

vi.mock("../../../contexts/AuthContext", async () => {
  const actual = await vi.importActual("../../../contexts/AuthContext");
  return { ...actual, useAuth: vi.fn() };
});

const renderWithRoute = () =>
  render(
    <MemoryRouter initialEntries={["/dashboard"]}>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<div>Protected Content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );

describe("ProtectedRoute", () => {
  it("shows a loading state while auth status is being determined", () => {
    AuthContext.useAuth.mockReturnValue({ isAuthenticated: false, isLoading: true });

    renderWithRoute();

    expect(screen.getByText("Loading...")).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });

  it("redirects to /login when not authenticated", () => {
    AuthContext.useAuth.mockReturnValue({ isAuthenticated: false, isLoading: false });

    renderWithRoute();

    expect(screen.getByText("Login Page")).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });

  it("renders the protected content when authenticated", () => {
    AuthContext.useAuth.mockReturnValue({ isAuthenticated: true, isLoading: false });

    renderWithRoute();

    expect(screen.getByText("Protected Content")).toBeInTheDocument();
    expect(screen.queryByText("Login Page")).not.toBeInTheDocument();
  });
});
