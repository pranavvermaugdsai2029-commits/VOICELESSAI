import { ReactNode } from "react";

interface VideoPanelProps {
  label: string;
  icon: string;
  children: ReactNode;
}

const VideoPanel = ({ label, icon, children }: VideoPanelProps) => {
  return (
    <div className="flex flex-col">
      <div className="panel-label">
        <span className="panel-label-icon" />
        <span>{icon}</span>
        <span>{label}</span>
      </div>
      <div className="video-panel glass-panel p-2">

        {children}
      </div>
    </div>
  );
};

export default VideoPanel;
