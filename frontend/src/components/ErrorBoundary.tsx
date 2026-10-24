import { Component } from 'react';
import type { ReactNode } from 'react';

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <main className="state-block fatal-error"><h1>Let’s get you back to your creative.</h1><p>Veyo couldn’t open this screen. Check that browser storage is enabled, then reload.</p><button className="button button-primary" onClick={() => location.assign('/')}>Open Veyo again</button></main> : this.props.children; }
}
