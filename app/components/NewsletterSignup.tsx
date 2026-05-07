"use client";

import { useState } from "react";

interface NewsletterSignupProps {
    variant?: "inline" | "card";
}

export default function NewsletterSignup({ variant = "card" }: NewsletterSignupProps) {
    const [email, setEmail] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("loading");

        // TODO: Replace with your email service (ConvertKit, Buttondown, Resend, etc.)
        // Example with ConvertKit:
        // const res = await fetch("https://api.convertkit.com/v3/forms/YOUR_FORM_ID/subscribe", {
        //     method: "POST",
        //     headers: { "Content-Type": "application/json" },
        //     body: JSON.stringify({ api_key: "YOUR_API_KEY", email }),
        // });

        // Simulate success for now
        await new Promise((resolve) => setTimeout(resolve, 800));
        setStatus("success");
        setEmail("");
    };

    if (variant === "inline") {
        return (
            <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    required
                    aria-label="Email address"
                    style={{
                        padding: "8px 12px",
                        border: "1px solid #d1d5db",
                        borderRadius: "6px",
                        fontSize: "14px",
                        width: "220px",
                    }}
                />
                <button
                    type="submit"
                    disabled={status === "loading"}
                    style={{
                        padding: "8px 16px",
                        background: "#111",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        fontSize: "14px",
                        cursor: status === "loading" ? "wait" : "pointer",
                    }}
                >
                    {status === "loading" ? "..." : "Subscribe"}
                </button>
                {status === "success" && (
                    <span style={{ fontSize: "13px", color: "#16a34a" }}>✓ Subscribed!</span>
                )}
            </form>
        );
    }

    return (
        <div
            style={{
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                borderRadius: "12px",
                padding: "32px",
                textAlign: "center",
                maxWidth: "480px",
                margin: "0 auto",
            }}
        >
            <h3 style={{ fontSize: "18px", fontWeight: "600", color: "#111", marginBottom: "8px" }}>
                Get weekly tutorials in your inbox
            </h3>
            <p style={{ fontSize: "14px", color: "#6b7280", marginBottom: "20px" }}>
                No spam. Unsubscribe anytime. New posts on React Native, Next.js, algorithms, and building real products.
            </p>
            {status === "success" ? (
                <p style={{ fontSize: "15px", color: "#16a34a", fontWeight: "500" }}>
                    ✓ You&apos;re in! Check your inbox.
                </p>
            ) : (
                <form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="your@email.com"
                        required
                        aria-label="Email address"
                        style={{
                            padding: "10px 14px",
                            border: "1px solid #d1d5db",
                            borderRadius: "8px",
                            fontSize: "14px",
                            width: "240px",
                        }}
                    />
                    <button
                        type="submit"
                        disabled={status === "loading"}
                        style={{
                            padding: "10px 20px",
                            background: "#111",
                            color: "white",
                            border: "none",
                            borderRadius: "8px",
                            fontSize: "14px",
                            fontWeight: "500",
                            cursor: status === "loading" ? "wait" : "pointer",
                        }}
                    >
                        {status === "loading" ? "Subscribing..." : "Subscribe"}
                    </button>
                </form>
            )}
            {status === "error" && (
                <p style={{ fontSize: "13px", color: "#dc2626", marginTop: "8px" }}>
                    Something went wrong. Try again.
                </p>
            )}
        </div>
    );
}
