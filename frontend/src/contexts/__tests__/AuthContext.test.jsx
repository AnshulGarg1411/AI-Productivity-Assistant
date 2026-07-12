import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { AuthProvider, useAuth } from "../AuthContext";
import * as authApi from "../../api/authApi";

vi.mock("../../api/authApi");

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("starts unauthenticated with no stored token", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(authApi.getMe).not.toHaveBeenCalled();
  });

  it("loads the user automatically if a token already exists in localStorage", async () => {
    localStorage.setItem("token", "existing-token");
    authApi.getMe.mockResolvedValue({ id: 1, name: "Anshul", email: "a@x.com" });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user.name).toBe("Anshul");
  });

  it("removes an invalid/expired token and stays logged out if getMe fails", async () => {
    localStorage.setItem("token", "expired-token");
    authApi.getMe.mockRejectedValue(new Error("401"));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem("token")).toBeNull();
  });

  it("login() stores the token and fetches the user", async () => {
    authApi.getMe.mockResolvedValue({ id: 2, name: "New User", email: "n@x.com" });

    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.login("brand-new-token");
    });

    expect(localStorage.getItem("token")).toBe("brand-new-token");
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user.name).toBe("New User");
  });

  it("logout() clears the token and user state", async () => {
    localStorage.setItem("token", "existing-token");
    authApi.getMe.mockResolvedValue({ id: 1, name: "Anshul", email: "a@x.com" });

    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.isAuthenticated).toBe(true));

    act(() => {
      result.current.logout();
    });

    expect(localStorage.getItem("token")).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  it("throws if useAuth is used outside an AuthProvider", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => renderHook(() => useAuth())).toThrow(
      "useAuth must be used within an AuthProvider"
    );
    spy.mockRestore();
  });
});
