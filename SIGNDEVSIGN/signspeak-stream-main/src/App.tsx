import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import { useState } from "react";
import LoadingScreen from "@/components/LoadingScreen";


const queryClient = new QueryClient();

const App = () => {
  const [loading, setLoading] = useState(true);

  return (
 <>
  {loading ? (
    <LoadingScreen onFinish={() => setLoading(false)} />
  ) : (
    <div className={!loading ? "main-fade-in" : "opacity-0"}>

      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </QueryClientProvider>
    </div>
  )}
</>

);

};


export default App;
