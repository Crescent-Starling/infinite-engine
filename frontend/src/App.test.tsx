import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test } from "vitest";
import App from "./App";

test("both entry points preserve honest unavailable status", async () => {
  render(<App />);
  const user = userEvent.setup();
  for (const name of ["Knowledge", "Sources", "My Learning", "Chat"]) {
    await user.click(screen.getByRole("button", { name }));
    expect(screen.getByRole("heading", { name, level: 2 })).toBeInTheDocument();
    expect(screen.getByRole("button", { name })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("status")).toHaveTextContent("Not implemented");
  }
});
