import { Link } from "react-router-dom";
import { ArrowUpRight, Layers2, CircleCheck } from "lucide-react";
import { PrivateImage } from "./PrivateImage";
import { date } from "../lib/format";
import type { ProjectSummary } from "../types";

export function ProjectCard({ project }: { project: ProjectSummary }) {
  return (
    <Link to={`/creative/${project.id}`} className="project-card">
      <div className="project-cover">
        {project.cover_asset && (
          <PrivateImage
            path={`/assets/${project.cover_asset.id}/image`}
            alt={project.name}
          />
        )}
        <span
          className={`status-pill ${project.analysis_count ? "analyzed" : ""}`}
        >
          {project.analysis_count ? (
            <CircleCheck size={12} />
          ) : (
            <span className="tiny-dot" />
          )}
          {project.analysis_count ? "Analyzed" : "Ready to review"}
        </span>
        <span className="card-open">
          <ArrowUpRight size={19} />
        </span>
      </div>
      <div className="project-card-copy">
        <h3>{project.name}</h3>
        <p>
          <span>
            <Layers2 size={13} />
            {project.asset_count}{" "}
            {project.asset_count === 1 ? "version" : "versions"}
          </span>
          <span>{date(project.created_at)}</span>
        </p>
      </div>
    </Link>
  );
}
