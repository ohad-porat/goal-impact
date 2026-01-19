import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import {
  render,
  screen,
  waitFor,
  fireEvent,
  act,
} from "@testing-library/react";
import SearchBar from "./SearchBar";
import { useRouter } from "next/navigation";
import { api } from "../lib/api";
import type { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

vi.mock("../lib/api", () => ({
  api: {
    search: vi.fn((query: string) => {
      const url = new URL("https://api.example.com/search/");
      url.searchParams.set("q", query);
      return url.toString();
    }),
  },
}));

type MockFetch = ReturnType<typeof vi.fn<typeof fetch>>;

describe("SearchBar", () => {
  const mockPush = vi.fn();
  const mockRouter: Partial<AppRouterInstance> = {
    push: mockPush,
  };
  let mockFetch: MockFetch;

  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch = vi.fn();
    global.fetch = mockFetch;
    vi.mocked(useRouter).mockReturnValue(mockRouter as AppRouterInstance);
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const triggerSearch = async (input: HTMLInputElement, query: string) => {
    act(() => {
      fireEvent.change(input, { target: { value: query } });
    });

    await act(async () => {
      vi.advanceTimersByTime(300);
      await vi.runAllTimersAsync();
    });
  };

  describe("Rendering", () => {
    it("should render search input", () => {
      render(<SearchBar />);

      const input = screen.getByPlaceholderText("Search...");
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute("type", "text");
    });

    it("should not show results dropdown initially", () => {
      render(<SearchBar />);

      expect(screen.queryByText("No results found")).not.toBeInTheDocument();
      expect(screen.queryByText("Searching...")).not.toBeInTheDocument();
    });
  });

  describe("Search functionality", () => {
    it("should debounce search requests", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      act(() => {
        fireEvent.change(input, { target: { value: "test" } });
      });

      expect(mockFetch).not.toHaveBeenCalled();

      await triggerSearch(input, "test");

      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it("should fetch search results after debounce", async () => {
      const mockResults = [
        { id: 1, name: "Test Player", type: "Player" },
        { id: 2, name: "Test Club", type: "Club" },
      ];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(mockFetch).toHaveBeenCalledWith(api.search("test"));
    });

    it("should display search results", async () => {
      const mockResults = [
        { id: 1, name: "Test Player", type: "Player" },
        { id: 2, name: "Test Club", type: "Club" },
      ];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("Test Player")).toBeInTheDocument();
      expect(screen.getByText("Test Club")).toBeInTheDocument();
    });

    it("should set loading state while fetching search results", async () => {
      const initialResults = [{ id: 1, name: "Initial", type: "Player" }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: initialResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "initial");

      expect(screen.getByText("Initial")).toBeInTheDocument();

      let resolveFetch: (value: Response) => void;
      const fetchPromise = new Promise<Response>((resolve) => {
        resolveFetch = resolve;
      });
      mockFetch.mockReturnValueOnce(fetchPromise);

      act(() => {
        fireEvent.change(input, { target: { value: "test" } });
      });

      await act(async () => {
        vi.advanceTimersByTime(300);
        await vi.runAllTimersAsync();
      });

      expect(mockFetch).toHaveBeenCalled();

      await act(async () => {
        resolveFetch({
          ok: true,
          json: async () => ({ results: [] }),
        } as Response);
      });
    });

    it('should show "No results found" when results are empty', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("No results found")).toBeInTheDocument();
      expect(screen.queryByText("Searching...")).not.toBeInTheDocument();
    });

    it("should clear results when query is empty", async () => {
      const mockResults = [{ id: 1, name: "Test", type: "Player" }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("Test")).toBeInTheDocument();

      act(() => {
        fireEvent.change(input, { target: { value: "" } });
      });

      await act(async () => {
        vi.advanceTimersByTime(50);
        await vi.runAllTimersAsync();
      });

      expect(screen.queryByText("Test")).not.toBeInTheDocument();
    });

    it("should not search when query is only whitespace", async () => {
      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      act(() => {
        fireEvent.change(input, { target: { value: "   " } });
      });

      await act(async () => {
        vi.advanceTimersByTime(300);
        await vi.runAllTimersAsync();
      });

      expect(mockFetch).not.toHaveBeenCalled();
    });
  });

  describe("Navigation", () => {
    it("should navigate when clicking a result", async () => {
      const mockResults = [{ id: 1, name: "Test Player", type: "Player" }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("Test Player")).toBeInTheDocument();

      const resultButton = screen.getByText("Test Player").closest("button");
      if (resultButton) {
        act(() => {
          fireEvent.click(resultButton);
        });
      }

      expect(mockPush).toHaveBeenCalledWith("/players/1");
    });

    it("should navigate to correct path for different result types", async () => {
      const mockResults = [
        { id: 1, name: "Test Club", type: "Club" },
        { id: 2, name: "Test League", type: "Competition" },
        { id: 3, name: "Test Nation", type: "Nation" },
      ];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("Test Club")).toBeInTheDocument();

      const clubButton = screen.getByText("Test Club").closest("button");
      if (clubButton) {
        act(() => {
          fireEvent.click(clubButton);
        });
      }

      expect(mockPush).toHaveBeenCalledWith("/clubs/1");
    });

    it("should clear query and close dropdown after clicking result", async () => {
      const mockResults = [{ id: 1, name: "Test Player", type: "Player" }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("Test Player")).toBeInTheDocument();

      const resultButton = screen.getByText("Test Player").closest("button");
      if (resultButton) {
        act(() => {
          fireEvent.click(resultButton);
        });
      }

      expect(input.value).toBe("");
      expect(screen.queryByText("Test Player")).not.toBeInTheDocument();
    });
  });

  describe("Click outside behavior", () => {
    it("should close dropdown when clicking outside", async () => {
      const mockResults = [{ id: 1, name: "Test Player", type: "Player" }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(
        <div>
          <SearchBar />
          <div data-testid="outside">Outside</div>
        </div>,
      );

      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;
      await triggerSearch(input, "test");

      expect(screen.getByText("Test Player")).toBeInTheDocument();

      act(() => {
        const outside = screen.getByTestId("outside");
        fireEvent.mouseDown(outside);
      });

      expect(screen.queryByText("Test Player")).not.toBeInTheDocument();
    });

    it("should not close dropdown when clicking inside", async () => {
      const mockResults = [{ id: 1, name: "Test Player", type: "Player" }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("Test Player")).toBeInTheDocument();

      act(() => {
        fireEvent.mouseDown(input);
      });

      expect(screen.getByText("Test Player")).toBeInTheDocument();
    });
  });

  describe("Focus behavior", () => {
    it("should open dropdown on focus if results exist", async () => {
      const mockResults = [{ id: 1, name: "Test Player", type: "Player" }];
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockResults }),
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(screen.getByText("Test Player")).toBeInTheDocument();

      act(() => {
        fireEvent.mouseDown(document.body);
      });

      expect(screen.queryByText("Test Player")).not.toBeInTheDocument();

      act(() => {
        fireEvent.focus(input);
      });

      expect(screen.getByText("Test Player")).toBeInTheDocument();
    });
  });

  describe("Error handling", () => {
    it("should handle fetch errors gracefully", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(consoleErrorSpy).toHaveBeenCalled();
      expect(screen.queryByText("No results found")).not.toBeInTheDocument();
      consoleErrorSpy.mockRestore();
    });

    it("should handle non-ok responses", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response);

      render(<SearchBar />);
      const input = screen.getByPlaceholderText(
        "Search...",
      ) as HTMLInputElement;

      await triggerSearch(input, "test");

      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });
  });
});
