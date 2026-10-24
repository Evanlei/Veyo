import { useEffect } from "react";
import {
  BrowserRouter,
  Link,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Header } from "./components/Header";
import { ToastProvider } from "./components/Toast";
import { Library } from "./pages/Library";
import { Workspace } from "./pages/Workspace";
import { Compare } from "./pages/Compare";
import { Guide } from "./pages/Guide";
import { Settings } from "./pages/Settings";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 10000, retry: 1, refetchOnWindowFocus: false },
    mutations: { retry: false },
  },
});
function ScrollReset() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ToastProvider>
          <ScrollReset />
          <Header />
          <main id="main-content">
            <Routes>
              <Route path="/" element={<Library />} />
              <Route path="/creative/:projectId" element={<Workspace />} />
              <Route path="/compare/:projectId" element={<Compare />} />
              <Route path="/guide" element={<Guide />} />
              <Route path="/settings" element={<Settings />} />
              <Route
                path="*"
                element={
                  <div className="state-block">
                    <h1>This view wandered off.</h1>
                    <Link className="button button-primary" to="/">
                      Back to your creative library
                    </Link>
                  </div>
                }
              />
            </Routes>
          </main>
        </ToastProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
