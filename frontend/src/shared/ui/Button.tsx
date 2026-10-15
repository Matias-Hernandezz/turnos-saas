import type { ButtonHTMLAttributes } from "react";

export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      style={{
        padding: "8px 16px",
        borderRadius: 8,
        border: "1px solid #333",
        background: "#fff",
        cursor: "pointer",
      }}
      {...props}
    />
  );
}
