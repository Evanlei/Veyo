import { NavLink, Link } from "react-router-dom";
import { Settings2, ArrowUpRight } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { IS_DEMO } from "../lib/mode";
import { DemoNotice } from "./DemoNotice";

export function Header() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: IS_DEMO ? false : 15000,
    retry: 1,
  });
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="site-header">
        <Link to="/" className="wordmark" aria-label="Veyo home">
          <span className="brand-symbol" />
          veyo<span className="studio-label">ATTENTION STUDIO</span>
        </Link>
        <nav aria-label="Main navigation">
          <NavLink to="/" end>
            Creative library
          </NavLink>
          <NavLink to="/guide">
            How it works <ArrowUpRight size={12} />
          </NavLink>
        </nav>
        <div className="header-right">
          <span
            className={`engine-badge ${health.isError ? "offline" : ""}`}
            title={
              IS_DEMO
                ? "Real DeepGaze IIE results recorded locally. No live analysis service is running."
                : health.isError
                  ? "The analysis service is unavailable"
                  : health.data?.loaded
                    ? "DeepGaze IIE is loaded and ready"
                    : "DeepGaze IIE loads when you run your first analysis"
            }
          >
            <span />
            {IS_DEMO
              ? "Recorded demo"
              : health.isError
                ? "Service offline"
                : health.data?.busy
                  ? "Analyzing"
                  : "DeepGaze IIE"}
          </span>
          <NavLink
            className="icon-button"
            to="/settings"
            aria-label={IS_DEMO ? "About this demo" : "Workspace settings"}
          >
            <Settings2 size={19} />
          </NavLink>
        </div>
      </header>
      {IS_DEMO && <DemoNotice />}
    </>
  );
}
