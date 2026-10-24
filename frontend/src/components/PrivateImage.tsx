import { ImageOff } from "lucide-react";
import { usePrivateImage } from "../hooks/usePrivateImage";

export function PrivateImage({
  path,
  alt,
  className = "",
}: {
  path: string;
  alt: string;
  className?: string;
}) {
  const image = usePrivateImage(path);
  if (image?.error)
    return (
      <div
        className="image-placeholder"
        role="img"
        aria-label="Image unavailable"
      >
        <ImageOff size={24} />
      </div>
    );
  return image?.url ? (
    <img className={className} src={image.url} alt={alt} draggable={false} />
  ) : (
    <div className="image-placeholder shimmer" aria-label="Loading creative" />
  );
}
