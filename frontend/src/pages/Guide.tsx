import { Link } from "react-router-dom";
import {
  ArrowUpRight,
  Crosshair,
  ImagePlus,
  Layers2,
  ScanEye,
} from "lucide-react";

export function Guide() {
  return (
    <div className="page guide-page">
      <div className="eyebrow">A NEW PERSPECTIVE ON YOUR CREATIVE</div>
      <h1>Attention is a starting point.</h1>
      <p className="guide-lead">
        Veyo helps you see what a visual attention model notices, so you can ask
        better questions about your design.
      </p>
      <div className="guide-steps">
        {[
          {
            icon: <ImagePlus />,
            title: "Bring a creative.",
            text: "Upload a static PNG or JPEG. Veyo orients it, composites transparency onto white, and prepares a consistent image for review.",
          },
          {
            icon: <Crosshair />,
            title: "Mark what matters.",
            text: "Draw targets around your product, headline, logo, or call to action. Give corresponding elements the same name when comparing revisions.",
          },
          {
            icon: <ScanEye />,
            title: "Take a closer look.",
            text: "Run a real DeepGaze IIE prediction. Explore the heatmap, attention shares, and competing regions alongside the original.",
          },
          {
            icon: <Layers2 />,
            title: "Compare your ideas.",
            text: "Upload a revision or try a controlled adjustment. Review its targets, analyze it, and compare the evidence side by side.",
          },
        ].map((step, i) => (
          <section key={step.title}>
            <span className="guide-step-number">0{i + 1}</span>
            <div className="guide-icon">{step.icon}</div>
            <h2>{step.title}</h2>
            <p>{step.text}</p>
          </section>
        ))}
      </div>
      <div className="guide-columns">
        <section>
          <span className="eyebrow">READING THE EVIDENCE</span>
          <h2>Share and size belong together.</h2>
          <p>
            <strong>Attention share</strong> is the sum of predicted fixation
            probability inside your target. A target with 20% share contains one
            fifth of the model’s predicted spatial probability.
          </p>
          <p>
            <strong>Area share</strong> tells you how much of the image the
            target occupies. A larger region can capture more attention simply
            because it covers more pixels.
          </p>
          <p>
            <strong>Relative attention</strong> divides attention share by area
            share. A value of 2× means twice the image-average predicted
            attention per pixel. This is not a viewer count or a performance
            grade.
          </p>
          <p>
            Overlapping targets are counted once in the total. Individual target
            shares can overlap and should not be added together.
          </p>
        </section>
        <section className="guide-limits">
          <span className="eyebrow">KEEP YOUR JUDGMENT IN THE LOOP</span>
          <h2>What the model can’t tell you.</h2>
          <ul>
            <li>Whether the ad will increase clicks, conversions, or sales.</li>
            <li>
              What people understand, remember, or feel about the message.
            </li>
            <li>The order or timing of human eye movements.</li>
            <li>
              Whether a small score change is meaningful in the real world.
            </li>
            <li>
              Whether the creative follows your brand and campaign strategy.
            </li>
          </ul>
          <p>
            The heatmap is an estimate from one learned model. Check the actual
            creative, and validate important decisions with people.
          </p>
        </section>
      </div>
      <section className="guide-cta">
        <div>
          <h2>Make room for a clearer view.</h2>
          <p>Start with your own creative or explore an example.</p>
        </div>
        <Link className="button button-primary" to="/">
          Open creative library <ArrowUpRight size={16} />
        </Link>
      </section>
      <p className="attribution">
        Workflow inspired by{" "}
        <a
          href="https://github.com/EnesYilmazcode/Pixel"
          target="_blank"
          rel="noreferrer"
        >
          Pixel
        </a>
        . Predictions by{" "}
        <a
          href="https://github.com/matthias-k/DeepGaze"
          target="_blank"
          rel="noreferrer"
        >
          DeepGaze IIE
        </a>
        , by Linardos, Kümmerer, Press, and Bethge. Veyo does not claim to have
        developed or trained the model.
      </p>
    </div>
  );
}
